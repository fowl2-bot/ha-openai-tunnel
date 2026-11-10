#!/usr/bin/env python3
"""Discover HAOS apps, plan OCI builds and create independent app releases.

An app is any top-level directory with a config.yaml and either a Dockerfile
or an external image declared in its config.yaml.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess

import yaml

PLATFORMS = {
    "amd64": "linux/amd64",
    "aarch64": "linux/arm64",
    "armv7": "linux/arm/v7",
    "armhf": "linux/arm/v6",
    "i386": "linux/386",
}
VERSION = re.compile(r"\d+\.\d+\.\d+")
SLUG = re.compile(r"[a-z][a-z0-9_-]*")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
NON_RELEASE_FILES = {"CHANGELOG.md", "smoke-test.sh"}


def git(*args: str, check: bool = True) -> str:
    p = subprocess.run(["git", *args], text=True, capture_output=True)
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout.strip() if p.returncode == 0 else ""


def apps() -> list[dict]:
    found = []
    slugs = set()
    for directory in sorted(Path(".").iterdir()):
        config_file = directory / "config.yaml"
        if not directory.is_dir() or not config_file.is_file():
            continue
        obj = yaml.safe_load(config_file.read_text())
        if not isinstance(obj, dict):
            raise ValueError(f"{config_file}: expected YAML mapping")
        slug = obj.get("slug")
        arch = obj.get("arch")
        version = str(obj.get("version", ""))
        if not isinstance(slug, str) or not SLUG.fullmatch(slug) or slug in slugs:
            raise ValueError(f"{config_file}: invalid or duplicate slug {slug!r}")
        if not isinstance(arch, list) or not arch or any(x not in PLATFORMS for x in arch) or len(set(arch)) != len(arch):
            raise ValueError(f"{config_file}: missing/invalid/duplicate architectures: {arch!r}")
        if not VERSION.fullmatch(version):
            raise ValueError(f"{config_file}: expected numeric MAJOR.MINOR.PATCH, got {version!r}")
        if not (directory / "Dockerfile").is_file() and not obj.get("image"):
            raise ValueError(f"{directory}: needs Dockerfile or config.yaml image")
        found.append({"path": directory.name, "slug": slug, "arch": arch, "version": version,
                      "build": (directory / "Dockerfile").is_file()})
        slugs.add(slug)
    if not found:
        raise ValueError("No HAOS apps (*/config.yaml) found")
    return found


def current_baseline(app: dict) -> str:
    # New namespaced tags isolate each app. Retain legacy global tags as the
    # baseline for apps that predate the multi-app release workflow.
    tags = git("tag", "--list", f"{app['slug']}/v*", "--sort=-version:refname").splitlines()
    for tag in tags:
        if re.fullmatch(re.escape(app["slug"]) + r"/v\d+\.\d+\.\d+", tag):
            return tag
    legacy = git("tag", "--list", "v[0-9]*", "--sort=-version:refname").splitlines()
    for tag in legacy:
        if re.fullmatch(r"v\d+\.\d+\.\d+", tag):
            return tag
    return EMPTY_TREE


def manifest_at(ref: str, app: dict):
    raw = git("show", f"{ref}:{app['path']}/config.yaml", check=False)
    if not raw:
        return None
    old = yaml.safe_load(raw)
    if isinstance(old, dict):
        old.pop("version", None)
    return old


def relevant_changes(app: dict, ref: str) -> bool:
    paths = git("diff", "--name-only", ref, "HEAD", "--", f"{app['path']}/").splitlines()
    for path in paths:
        relative = Path(path).relative_to(app["path"])
        if relative.as_posix() in NON_RELEASE_FILES:
            continue
        if relative.as_posix() == "config.yaml":
            current = yaml.safe_load((Path(app["path"]) / "config.yaml").read_text())
            current.pop("version", None)
            if manifest_at(ref, app) == current:
                continue
        return True
    return False


def bump(version: str) -> str:
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def release_note(app: dict, ref: str, version: str) -> None:
    raw = git("log", "--format=%s", f"{ref}..HEAD", "--", f"{app['path']}/")
    subjects = [x for x in raw.splitlines() if x and not x.startswith("chore(release):")]
    if not subjects:
        subjects = ["Update application package"]
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    heading = f"## {version} - {today}\n\n"
    entry = heading + "".join(f"- {subject}\n" for subject in subjects)
    dest = Path(app["path"]) / "CHANGELOG.md"
    old = dest.read_text() if dest.exists() else ""
    if old.startswith("# Changelog"):
        old = old[len("# Changelog"):].strip()
    dest.write_text("# Changelog\n\n" + entry + ("\n" + old + "\n" if old else ""))


def plan(args):
    discovered = apps()
    if args.event == "pr":
        if not args.base:
            raise ValueError("--base required for PR planning")
        base = args.base
        shared = git("diff", "--name-only", base, "HEAD", "--",
                     "scripts/", ".github/workflows/", "repository.yaml").splitlines()
        selected = [app for app in discovered if shared or relevant_changes(app, base)]
    else:
        selected = [app for app in discovered if relevant_changes(app, current_baseline(app))]
    builds = []
    for app in selected:
        if not app["build"]:
            continue
        version = app["version"] if args.event == "pr" else bump(app["version"])
        for arch in app["arch"]:
            builds.append({"app": app["path"], "arch": arch, "platform": PLATFORMS[arch],
                           "slug": app["slug"], "version": version})
    releases = [app["path"] for app in selected]
    payload = {"matrix": {"include": builds}, "build_count": str(len(builds)),
               "releases": releases, "app_count": str(len(discovered))}
    for key, value in payload.items():
        print(f"{key}: {json.dumps(value, separators=(',', ':'))}")
    if args.output:
        with open(args.output, "a") as output:
            for key, value in payload.items():
                serialized = value if isinstance(value, str) else json.dumps(value, separators=(",", ":"))
                output.write(f"{key}={serialized}\n")


def release(args):
    discovered = {app["path"]: app for app in apps()}
    selected = json.loads(args.apps_json)
    if not isinstance(selected, list) or len(set(selected)) != len(selected):
        raise ValueError("Invalid release app list")
    tags = []
    for name in selected:
        if name not in discovered:
            raise ValueError(f"Unknown app {name!r}")
        app = discovered[name]
        ref = current_baseline(app)
        if not relevant_changes(app, ref):
            raise ValueError(f"No unreleased changes for {name}; refusing unnecessary bump")
        new_version = bump(app["version"])
        config = Path(name) / "config.yaml"
        original = config.read_text()
        edited, count = re.subn(
            r'(?m)^(version:\s*)[^\n#]+',
            lambda m: m.group(1) + f'"{new_version}"',
            original, count=1,
        )
        if count != 1:
            raise ValueError(f"{config}: exactly one version line required")
        config.write_text(edited)
        release_note(app, ref, new_version)
        tags.append(f"{app['slug']}/v{new_version}")
        print(f"Prepared {name}: {app['version']} -> {new_version}")
    Path(args.tags_output).write_text("\n".join(tags) + ("\n" if tags else ""))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    planning = sub.add_parser("plan")
    planning.add_argument("--event", choices=["pr", "push"], required=True)
    planning.add_argument("--base")
    planning.add_argument("--output")
    publishing = sub.add_parser("release")
    publishing.add_argument("--apps-json", required=True)
    publishing.add_argument("--tags-output", required=True)
    args = parser.parse_args()
    if args.command == "plan":
        plan(args)
    else:
        release(args)


if __name__ == "__main__":
    main()
