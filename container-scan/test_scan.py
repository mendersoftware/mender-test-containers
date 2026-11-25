import base64
import datetime
import json
import os
import tempfile
import unittest

import scan


def pod(containers, init=None, node_selector=None):
    spec = {
        "containers": [
            {"name": f"c{i}", "image": im} for i, im in enumerate(containers)
        ]
    }
    if init:
        spec["initContainers"] = [
            {"name": f"i{i}", "image": im} for i, im in enumerate(init)
        ]
    if node_selector:
        spec["nodeSelector"] = node_selector
    return {"spec": spec}


def workload(kind, template):
    if kind == "cronjobs":
        return {"spec": {"jobTemplate": {"spec": {"template": template}}}}
    return {"spec": {"template": template}}


class TestImages(unittest.TestCase):
    def test_containers_init_cronjobs_dedup_sorted(self):
        items = {
            "deployments": [
                workload("deployments", pod(["b:1", "a:1"], init=["init:1"]))
            ],
            "statefulsets": [workload("statefulsets", pod(["a:1"]))],
            "daemonsets": [],
            "cronjobs": [workload("cronjobs", pod(["cron:1"]))],
        }
        self.assertEqual(
            scan.images_from_workloads(items), ["a:1", "b:1", "cron:1", "init:1"]
        )

    def test_windows_excluded_by_node_selector_and_name(self):
        items = {
            "daemonsets": [
                workload(
                    "daemonsets",
                    pod(
                        ["mcr.microsoft.com/x:1"],
                        node_selector={"kubernetes.io/os": "windows"},
                    ),
                ),
                workload(
                    "daemonsets", pod(["mcr.microsoft.com/oss/kube-proxy-Windows:1"])
                ),
                workload("daemonsets", pod(["linux:1"])),
            ]
        }
        self.assertEqual(scan.images_from_workloads(items), ["linux:1"])

    def test_list_workloads_follows_pagination(self):
        pages = {
            "/apis/apps/v1/deployments?limit=500": {
                "items": [1],
                "metadata": {"continue": "t"},
            },
            "/apis/apps/v1/deployments?limit=500&continue=t": {
                "items": [2],
                "metadata": {},
            },
        }
        got = scan.list_all(lambda path: pages[path], "/apis/apps/v1/deployments")
        self.assertEqual(got, [1, 2])


class TestNames(unittest.TestCase):
    def test_report_name_keeps_registry_and_path(self):
        name = scan.report_name(
            "registry.gitlab.com/northern.tech/mender/x:1.2@sha256:ab"
        )
        self.assertRegex(
            name,
            r"^trivy-scan-registry\.gitlab\.com_northern\.tech_mender_x_1\.2_sha256_ab-[0-9a-f]{8}\.json$",
        )

    def test_report_name_no_collision_on_sanitisation(self):
        self.assertNotEqual(scan.report_name("a/b:1"), scan.report_name("a_b_1"))

    def test_report_name_no_collision_across_registries(self):
        self.assertNotEqual(
            scan.report_name("dhi.io/redis:7"),
            scan.report_name("docker.io/library/redis:7"),
        )

    def test_s3_prefix_layout(self):
        now = datetime.datetime(2026, 11, 1, 4, 0, 5, tzinfo=datetime.timezone.utc)
        self.assertEqual(
            scan.s3_prefix("prod-us", "hm-us-prod-1-35-green", now),
            "prod-us/2026/11/hm-us-prod-1-35-green/20261101-040005/",
        )


def dockerconfig(auths):
    return json.dumps(
        {
            "auths": {
                k: {
                    "username": u,
                    "password": p,
                    "auth": base64.b64encode(f"{u}:{p}".encode()).decode(),
                }
                for k, (u, p) in auths.items()
            }
        }
    )


class TestValidation(unittest.TestCase):
    def test_valid(self):
        for ok in (
            "alpine",
            "alpine:3.24",
            "dhi.io/redis:8@sha256:" + "a" * 64,
            "602401143452.dkr.ecr.us-east-1.amazonaws.com/eks/coredns:v1.11.4-eksbuild.2",
            "registry:5000/g/p/app:1",
        ):
            self.assertTrue(scan.valid_image(ok), ok)

    def test_invalid(self):
        for bad in ("--config=/x", "-x", "a b", "a;rm", "", "x" * 600, "a\nb"):
            self.assertFalse(scan.valid_image(bad), bad)

    def test_trivy_argv_separates_image(self):
        argv = scan.trivy_argv("alpine:1", "/out/r.json")
        self.assertEqual(argv[-2:], ["--", "alpine:1"])


class TestCredentials(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def secret(self, name, auths):
        os.makedirs(os.path.join(self.d, name))
        with open(os.path.join(self.d, name, ".dockerconfigjson"), "w") as f:
            f.write(dockerconfig(auths))

    def test_host_keys_merged_path_keys_scoped(self):
        self.secret(
            "hub", {"https://index.docker.io/v1/": ("hu", "hp"), "dhi.io": ("hu", "hp")}
        )
        self.secret("mender", {"registry.mender.io": ("mu", "mp")})
        self.secret(
            "gl",
            {"registry.gitlab.com/northern.tech/mender/hm-tenant-sync": ("gu", "gp")},
        )
        merged, scoped = scan.load_registry_secrets(self.d)
        self.assertEqual(
            set(merged["auths"]),
            {"https://index.docker.io/v1/", "dhi.io", "registry.mender.io"},
        )
        self.assertEqual(
            scoped,
            {"registry.gitlab.com/northern.tech/mender/hm-tenant-sync": ("gu", "gp")},
        )

    def test_duplicate_host_is_an_error(self):
        self.secret("a", {"dhi.io": ("u", "p")})
        self.secret("b", {"dhi.io": ("u2", "p2")})
        with self.assertRaises(ValueError):
            scan.load_registry_secrets(self.d)

    def test_auth_field_only(self):
        os.makedirs(os.path.join(self.d, "x"))
        with open(os.path.join(self.d, "x", ".dockerconfigjson"), "w") as f:
            f.write(
                json.dumps(
                    {
                        "auths": {
                            "registry.gitlab.com/g/p": {
                                "auth": base64.b64encode(b"u:p:x").decode()
                            }
                        }
                    }
                )
            )
        _, scoped = scan.load_registry_secrets(self.d)
        self.assertEqual(scoped["registry.gitlab.com/g/p"], ("u", "p:x"))

    def test_scoped_credentials_longest_prefix_on_boundary(self):
        scoped = {
            "registry.gitlab.com/g/p": ("a", "1"),
            "registry.gitlab.com/g/p/sub": ("b", "2"),
        }
        self.assertEqual(
            scan.credentials_for("registry.gitlab.com/g/p:1", scoped), ("a", "1")
        )
        self.assertEqual(
            scan.credentials_for("registry.gitlab.com/g/p/sub@sha256:x", scoped),
            ("b", "2"),
        )
        self.assertEqual(
            scan.credentials_for("registry.gitlab.com/g/p/other:1", scoped), ("a", "1")
        )
        self.assertIsNone(scan.credentials_for("registry.gitlab.com/g/pp:1", scoped))
        self.assertIsNone(scan.credentials_for("docker.io/g/p:1", scoped))


class TestAwsConfig(unittest.TestCase):
    def test_profiles(self):
        cfg = scan.aws_config("arn:reports", "arn:ecr", "/tok")
        self.assertIn(
            "[profile reports]\nrole_arn = arn:reports\nweb_identity_token_file = /tok",
            cfg,
        )
        self.assertIn(
            "[profile ecr]\nrole_arn = arn:ecr\nweb_identity_token_file = /tok", cfg
        )

    def test_no_ecr_profile_on_aks(self):
        self.assertNotIn("[profile ecr]", scan.aws_config("arn:reports", "", "/tok"))


class TestRun(unittest.TestCase):
    def test_invalid_image_failed_not_scanned(self):
        called = []
        uploaded = {}
        rc = scan.run(
            images=["--config=/x"],
            out_dir=tempfile.mkdtemp(),
            trivy=lambda i, p, e: called.append(i),
            upload=lambda n, b: uploaded.__setitem__(n, b),
            meta_base={},
            scoped={},
            base_env={},
            sleep=lambda s: None,
        )
        self.assertEqual(rc, 1)
        self.assertEqual(called, [])
        self.assertEqual(
            json.loads(uploaded["scan-meta.json"])["images"]["--config=/x"]["status"],
            "failed",
        )

    def test_meta_written_first_running_then_complete(self):
        order = []
        scan.run(
            images=["ok:1"],
            out_dir=tempfile.mkdtemp(),
            trivy=lambda i, p, e: open(p, "w").close(),
            upload=lambda n, b: order.append(
                (n, json.loads(b)["status"] if n == "scan-meta.json" else None)
            ),
            meta_base={},
            scoped={},
            base_env={},
            sleep=lambda s: None,
        )
        self.assertEqual(order[0], ("images.txt", None))
        self.assertEqual(order[1], ("scan-meta.json", "running"))
        self.assertEqual(order[-1], ("scan-meta.json", "complete"))

    def test_retry_then_success(self):
        attempts = []

        def trivy(image, path, env):
            attempts.append(image)
            if len(attempts) < 3:
                return "TOOMANYREQUESTS"
            open(path, "w").close()

        rc = scan.run(
            images=["ok:1"],
            out_dir=tempfile.mkdtemp(),
            trivy=trivy,
            upload=lambda n, b: None,
            meta_base={},
            scoped={},
            base_env={},
            sleep=lambda s: None,
        )
        self.assertEqual((rc, len(attempts)), (0, 3))

    def test_error_truncated_to_last_line(self):
        uploaded = {}
        scan.run(
            images=["bad:1"],
            out_dir=tempfile.mkdtemp(),
            trivy=lambda i, p, e: "line1 internal.host\n" + "E" * 1000,
            upload=lambda n, b: uploaded.__setitem__(n, b),
            meta_base={},
            scoped={},
            base_env={},
            sleep=lambda s: None,
        )
        err = json.loads(uploaded["scan-meta.json"])["images"]["bad:1"]["error"]
        self.assertLessEqual(len(err), 300)
        self.assertNotIn("internal.host", err)

    def test_failures_recorded_uploaded_and_exit_nonzero(self):
        out = tempfile.mkdtemp()
        uploaded = {}

        def trivy(image, path, env):
            if image == "bad:1":
                return "UNAUTHORIZED: authentication required"
            with open(path, "w") as f:
                f.write("{}")
            return None

        rc = scan.run(
            images=["ok:1", "bad:1"],
            out_dir=out,
            trivy=trivy,
            upload=lambda name, body: uploaded.__setitem__(name, body),
            meta_base={"env": "staging", "cluster": "c"},
            scoped={},
            base_env={},
            sleep=lambda s: None,
        )
        self.assertEqual(rc, 1)
        meta = json.loads(uploaded["scan-meta.json"])
        self.assertEqual(meta["images"]["ok:1"]["status"], "ok")
        self.assertEqual(meta["images"]["bad:1"]["status"], "failed")
        self.assertIn("UNAUTHORIZED", meta["images"]["bad:1"]["error"])
        self.assertEqual(meta["status"], "complete")
        self.assertIn(scan.report_name("ok:1"), uploaded)
        self.assertNotIn(scan.report_name("bad:1"), uploaded)
        self.assertEqual(uploaded["images.txt"], b"ok:1\nbad:1\n")

    def test_scoped_credentials_passed_only_to_matching_image(self):
        seen = {}

        def trivy(image, path, env):
            seen[image] = (env.get("TRIVY_USERNAME"), env.get("TRIVY_PASSWORD"))
            with open(path, "w") as f:
                f.write("{}")

        rc = scan.run(
            images=["registry.gitlab.com/g/p:1", "docker.io/x:1"],
            out_dir=tempfile.mkdtemp(),
            trivy=trivy,
            upload=lambda n, b: None,
            meta_base={},
            scoped={"registry.gitlab.com/g/p": ("u", "t")},
            base_env={},
            sleep=lambda s: None,
        )
        self.assertEqual(rc, 0)
        self.assertEqual(seen["registry.gitlab.com/g/p:1"], ("u", "t"))
        self.assertEqual(seen["docker.io/x:1"], (None, None))


class TestListImages(unittest.TestCase):
    def test_writes_images_file(self):
        d = tempfile.mkdtemp()
        api = {
            "/apis/apps/v1/deployments": [workload("deployments", pod(["b:1", "a:1"]))]
        }
        scan.list_images(
            lambda path: {"items": api.get(path.split("?")[0], []), "metadata": {}},
            os.path.join(d, "images.txt"),
        )
        with open(os.path.join(d, "images.txt")) as f:
            self.assertEqual(f.read(), "a:1\nb:1\n")


if __name__ == "__main__":
    unittest.main()
