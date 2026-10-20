
#!/usr/bin/env python3
"""Phase 0 self-check — probes your environment and writes a submission report.

Run this from the repository root once you have finished the setup tasks:

    python phase-0-setup/verify_setup.py

It inspects Python, gcloud config, Docker, and the Git remote,
then writes submission/phase0_report.json.

The two implemented functions are:
    parse_gcloud_config()
    parse_repo_slug()
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import urlparse

# Make the shared autograder package importable when run from anywhere.
REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from autograder import env_checks  # noqa: E402

REPORT_PATH = REPO_ROOT / "submission" / "phase0_report.json"


# ---------------------------------------------------------------------------
# Phase 0: Implemented functions
# ---------------------------------------------------------------------------

def parse_gcloud_config(raw: str) -> dict:
    """Extract the account and project from gcloud JSON output."""

    if not isinstance(raw, str) or not raw.strip():
        return {"account": "", "project": ""}

    try:
        config = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"account": "", "project": ""}

    if not isinstance(config, dict):
        return {"account": "", "project": ""}

    core = config.get("core", {})

    if not isinstance(core, dict):
        core = {}

    return {
        "account": str(core.get("account") or ""),
        "project": str(core.get("project") or ""),
    }


def parse_repo_slug(remote_url: str) -> str:
    """Convert a GitHub remote URL into owner/repo format."""

    if not isinstance(remote_url, str) or not remote_url.strip():
        return ""

    remote_url = remote_url.strip()

    # Handle SSH URLs in SCP-style format:
    # git@github.com:owner/repo.git
    if remote_url.startswith("git@github.com:"):
        path = remote_url[len("git@github.com:"):]

    else:
        # Handle HTTPS and ssh:// URLs.
        parsed = urlparse(remote_url)

        if (
            parsed.hostname != "github.com"
            or parsed.scheme not in {"https", "http", "ssh"}
        ):
            return ""

        path = parsed.path.lstrip("/")

    # Remove URL query strings and fragments.
    path = path.split("?", 1)[0].split("#", 1)[0]
    path = path.strip("/")

    # Remove the optional .git suffix.
    if path.endswith(".git"):
        path = path[:-4]

    parts = path.split("/")

    # A valid repository path must contain owner and repository.
    if len(parts) != 2 or not all(parts):
        return ""

    return f"{parts[0]}/{parts[1]}"


# ---------------------------------------------------------------------------
# Provided environment checks
# ---------------------------------------------------------------------------

def check_python() -> dict:
    major, minor, micro = env_checks.python_version()

    return {
        "version": f"{major}.{minor}.{micro}",
        "ok": env_checks.python_is_supported(),
    }


def check_environment() -> dict:
    """Record whether the script is running in Cloud Shell."""

    return {
        "cloud_shell": env_checks.in_cloud_shell()
    }


def check_gcloud() -> dict:
    code, out, err = env_checks.run(
        ["gcloud", "config", "list", "--format=json"]
    )

    if code != 0:
        return {
            "account": "",
            "project": "",
            "error": err or "gcloud not found",
        }

    try:
        parsed = parse_gcloud_config(out)
    except NotImplementedError as exc:
        return {
            "account": "",
            "project": "",
            "error": str(exc),
        }

    return {
        "account": parsed["account"],
        "project": parsed["project"],
        "error": None,
    }


def check_docker() -> dict:
    code, out, err = env_checks.run(["docker", "--version"])

    return {
        "version": out if code == 0 else "",
        "present": code == 0,
    }


def check_git() -> dict:
    url = env_checks.git_remote_url()

    try:
        slug = parse_repo_slug(url)
    except NotImplementedError:
        slug = ""

    return {
        "remote": url,
        "is_github": "github.com" in url,
        "slug": slug,
    }


def build_report() -> dict:
    return {
        "phase": "0",
        "environment": check_environment(),
        "python": check_python(),
        "gcloud": check_gcloud(),
        "docker": check_docker(),
        "git": check_git(),
    }


def _print_summary(report: dict) -> None:
    def mark(ok: bool) -> str:
        return "OK  " if ok else "MISS"

    py = report["python"]
    gc = report["gcloud"]
    dk = report["docker"]
    gt = report["git"]
    env = report["environment"]

    print("Phase 0 environment check")
    print("-" * 40)

    where = "Cloud Shell" if env["cloud_shell"] else "local machine"
    print(f"[OK  ] Running on: {where}")

    print(
        f"[{mark(py['ok'])}] Python {py['version']} "
        "(need 3.11 or 3.12)"
    )

    print(
        f"[{mark(bool(gc['account']))}] "
        f"gcloud account: {gc['account'] or '(unset)'}"
    )

    print(
        f"[{mark(bool(gc['project']))}] "
        f"gcloud project: {gc['project'] or '(unset)'}"
    )

    print(
        f"[{mark(dk['present'])}] "
        f"{dk['version'] or 'docker not found'}"
    )

    print(
        f"[{mark(gt['is_github'])}] "
        f"git remote: {gt['remote'] or '(unset)'}"
    )

    print("-" * 40)


def main() -> int:
    report = build_report()

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

    REPORT_PATH.write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    _print_summary(report)

    print(
        f"\nWrote {REPORT_PATH.relative_to(REPO_ROOT)} — commit it and push."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
