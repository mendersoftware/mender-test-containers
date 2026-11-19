"""Weekly Trivy scan of the images used by a cluster's workloads.

Two steps, run as two containers of the same pod so the process parsing
untrusted image content never holds the Kubernetes token:

  scan.py list-images   init container: list deployments, statefulsets,
                        daemonsets and cronjobs, write $WORK_DIR/images.txt
  scan.py scan          main container: `trivy image --format cyclonedx
                        --scanners vuln` per image, upload to S3 under
                        <env>/<YYYY>/<MM>/<cluster>/<YYYYMMDD-HHMMSS>/
"""

import base64
import datetime
import glob
import hashlib
import json
import logging
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request

log = logging.getLogger("container-scan")

WORKLOADS = {
    "deployments": "/apis/apps/v1/deployments",
    "statefulsets": "/apis/apps/v1/statefulsets",
    "daemonsets": "/apis/apps/v1/daemonsets",
    "cronjobs": "/apis/batch/v1/cronjobs",
}
IMAGE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,500}")
ATTEMPTS = 3


# --- image listing -----------------------------------------------------------


def list_all(api_get, path):
    items, cont = [], None
    while True:
        query = {"limit": 500}
        if cont:
            query["continue"] = cont
        page = api_get(f"{path}?{urllib.parse.urlencode(query)}")
        items += page.get("items", [])
        cont = page.get("metadata", {}).get("continue")
        if not cont:
            return items


def _pod_spec(kind, item):
    spec = item.get("spec", {})
    if kind == "cronjobs":
        spec = spec.get("jobTemplate", {}).get("spec", {})
    return spec.get("template", {}).get("spec", {})


def images_from_workloads(items_by_kind):
    images = set()
    for kind, items in items_by_kind.items():
        for item in items:
            spec = _pod_spec(kind, item)
            if spec.get("nodeSelector", {}).get("kubernetes.io/os") == "windows":
                continue
            for c in spec.get("containers", []) + spec.get("initContainers", []):
                image = c.get("image", "")
                if image and "windows" not in image.lower():
                    images.add(image)
    return sorted(images)


def list_images(api_get, path):
    images = images_from_workloads(
        {k: list_all(api_get, p) for k, p in WORKLOADS.items()}
    )
    with open(path, "w") as f:
        f.writelines(f"{i}\n" for i in images)
    log.info("listed %d images", len(images))


def _kube_api_get():
    base = f"https://{os.environ['KUBERNETES_SERVICE_HOST']}:{os.environ.get('KUBERNETES_SERVICE_PORT', '443')}"
    base = os.environ.get("KUBE_API_URL", base)
    ctx = ssl.create_default_context(cafile=os.environ["KUBE_CA_FILE"])

    def get(path):
        with open(os.environ["KUBE_TOKEN_FILE"]) as f:
            token = f.read().strip()
        req = urllib.request.Request(
            base + path, headers={"Authorization": f"Bearer {token}"}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=60) as resp:
            return json.load(resp)

    return get


# --- scanning -------------------------------------------------------------------


def valid_image(image):
    return bool(IMAGE_RE.fullmatch(image))


def report_name(image):
    digest = hashlib.sha256(image.encode()).hexdigest()[:8]
    return f"trivy-scan-{re.sub(r'[^A-Za-z0-9._-]', '_', image)}-{digest}.json"


def s3_prefix(env, cluster, now):
    return f"{env}/{now:%Y}/{now:%m}/{cluster}/{now:%Y%m%d-%H%M%S}/"


def _user_pass(entry):
    if "username" in entry and "password" in entry:
        return entry["username"], entry["password"]
    user, _, password = base64.b64decode(entry["auth"]).decode().partition(":")
    return user, password


def load_registry_secrets(directory):
    """Host keys go to one docker config; keys with a path are prefix-scoped."""
    merged, scoped = {"auths": {}}, {}
    for path in sorted(glob.glob(os.path.join(directory, "*", ".dockerconfigjson"))):
        with open(path) as f:
            auths = json.load(f).get("auths", {})
        for key, entry in auths.items():
            host_part = re.sub(r"^https?://", "", key).split("/", 1)
            is_scoped = len(host_part) == 2 and host_part[1] not in ("", "v1/", "v2/")
            target = scoped if is_scoped else merged["auths"]
            if key in target:
                raise ValueError(f"duplicate registry credential for {key} ({path})")
            target[key] = _user_pass(entry) if is_scoped else entry
    return merged, scoped


def credentials_for(image, scoped):
    best = None
    for prefix in scoped:
        if image == prefix or (
            image.startswith(prefix) and image[len(prefix)] in "/:@"
        ):
            if best is None or len(prefix) > len(best):
                best = prefix
    return scoped[best] if best else None


def aws_config(reports_role_arn, ecr_role_arn, token_file):
    out = f"[profile reports]\nrole_arn = {reports_role_arn}\nweb_identity_token_file = {token_file}\n"
    if ecr_role_arn:
        out += f"\n[profile ecr]\nrole_arn = {ecr_role_arn}\nweb_identity_token_file = {token_file}\n"
    return out


def trivy_argv(image, path):
    return [
        "trivy",
        "image",
        "--quiet",
        "--format",
        "cyclonedx",
        "--scanners",
        "vuln",
        "--skip-db-update",
        "--timeout",
        "15m",
        "--output",
        path,
        "--",
        image,
    ]


def _short(error):
    lines = [line.strip() for line in error.strip().splitlines() if line.strip()]
    return (lines[-1] if lines else "unknown error")[-300:]


def run(images, out_dir, trivy, upload, meta_base, scoped, base_env, sleep=time.sleep):
    meta = dict(
        meta_base,
        status="running",
        started=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        images={},
    )
    upload("images.txt", "".join(f"{i}\n" for i in images).encode())
    upload("scan-meta.json", json.dumps(meta, indent=2, sort_keys=True).encode())
    for image in images:
        if not valid_image(image):
            log.error("invalid image reference skipped: %r", image[:100])
            meta["images"][image] = {
                "status": "failed",
                "error": "invalid image reference",
            }
            continue
        env = dict(base_env)
        creds = credentials_for(image, scoped)
        if creds:
            env["TRIVY_USERNAME"], env["TRIVY_PASSWORD"] = creds
        path = os.path.join(out_dir, report_name(image))
        log.info("scanning %s", image)
        for attempt in range(1, ATTEMPTS + 1):
            error = trivy(image, path, env)
            if not error:
                break
            log.warning(
                "attempt %d/%d failed for %s: %s",
                attempt,
                ATTEMPTS,
                image,
                _short(error),
            )
            if attempt < ATTEMPTS:
                sleep(30 * attempt)
        if error:
            meta["images"][image] = {"status": "failed", "error": _short(error)}
            if os.path.exists(path):
                os.remove(path)
            continue
        meta["images"][image] = {"status": "ok", "report": report_name(image)}
        with open(path, "rb") as f:
            upload(report_name(image), f.read())
        os.remove(path)
    meta.update(
        status="complete",
        finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
    upload("scan-meta.json", json.dumps(meta, indent=2, sort_keys=True).encode())
    failed = [i for i, r in meta["images"].items() if r["status"] == "failed"]
    log.info("scanned %d images, %d failed", len(images), len(failed))
    return 1 if failed else 0


def _trivy(image, path, env):
    proc = subprocess.run(
        trivy_argv(image, path), env=env, capture_output=True, text=True
    )
    return None if proc.returncode == 0 else (proc.stderr or f"exit {proc.returncode}")


def scan_main(work):
    env_name, cluster = os.environ["SCAN_ENV"], os.environ["CLUSTER_NAME"]
    with open(f"{work}/images.txt") as f:
        images = [line.strip() for line in f if line.strip()]

    os.makedirs(f"{work}/docker", exist_ok=True)
    os.makedirs(f"{work}/reports", exist_ok=True)
    merged, scoped = load_registry_secrets(
        os.environ.get("REGISTRY_SECRETS_DIR", "/etc/scan-registries")
    )
    with open(f"{work}/docker/config.json", "w") as f:
        json.dump(merged, f)
    with open(f"{work}/aws-config", "w") as f:
        f.write(
            aws_config(
                os.environ["REPORTS_ROLE_ARN"],
                os.environ.get("ECR_ROLE_ARN", ""),
                os.environ.get("AWS_TOKEN_FILE", "/var/run/secrets/aws/token"),
            )
        )
    os.environ["AWS_CONFIG_FILE"] = f"{work}/aws-config"

    base_env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("TRIVY_USERNAME", "TRIVY_PASSWORD", "AWS_PROFILE")
    }
    base_env["DOCKER_CONFIG"] = f"{work}/docker"
    if os.environ.get("ECR_ROLE_ARN"):
        base_env["AWS_PROFILE"] = "ecr"

    for attempt in range(1, ATTEMPTS + 1):
        if (
            subprocess.run(
                ["trivy", "image", "--download-db-only", "--quiet"], env=base_env
            ).returncode
            == 0
        ):
            break
        if attempt == ATTEMPTS:
            log.error("trivy DB download failed")
            return 2
        time.sleep(60 * attempt)
    version = json.loads(
        subprocess.run(
            ["trivy", "version", "--format", "json"],
            env=base_env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )

    import boto3  # only the scan step needs it

    s3 = boto3.Session(profile_name="reports").client("s3")
    bucket = os.environ["REPORTS_BUCKET"]
    prefix = s3_prefix(env_name, cluster, datetime.datetime.now(datetime.timezone.utc))

    def upload(name, body):
        s3.put_object(
            Bucket=bucket, Key=prefix + name, Body=body, ChecksumAlgorithm="SHA256"
        )

    meta_base = {
        "env": env_name,
        "cluster": cluster,
        "trivy": version.get("Version"),
        "trivy_db": version.get("VulnerabilityDB", {}).get("UpdatedAt"),
        "s3_prefix": prefix,
    }
    log.info("uploading to s3://%s/%s", bucket, prefix)
    return run(images, f"{work}/reports", _trivy, upload, meta_base, scoped, base_env)


def main():
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}',
    )
    work = os.environ.get("WORK_DIR", "/work")
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "list-images":
        list_images(_kube_api_get(), f"{work}/images.txt")
        return 0
    if mode == "scan":
        return scan_main(work)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
