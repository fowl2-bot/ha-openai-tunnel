"""Regression tests for multi-app discovery and independent releases."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

import haos_apps


class AppPlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.before = Path.cwd()
        os.chdir(self.temp.name)
        self.git("init", "-q")
        self.git("config", "user.name", "CI")
        self.git("config", "user.email", "ci@example.invalid")
        for name in ("one", "two", "three"):
            path = Path(name)
            path.mkdir()
            (path / "config.yaml").write_text(
                f'name: "{name}"\nslug: {name}\nversion: "0.1.0"\n'
                'arch:\n  - amd64\n'
            )
            (path / "Dockerfile").write_text("FROM scratch\n")
        self.git("add", ".")
        self.git("commit", "-qm", "initial apps")
        self.git("tag", "v0.1.10")

    def tearDown(self):
        os.chdir(self.before)
        self.temp.cleanup()

    @staticmethod
    def git(*args):
        return subprocess.check_output(["git", *args], text=True).strip()

    def commit(self, path, content):
        Path(path).write_text(content)
        self.git("add", path)
        self.git("commit", "-qm", f"change {path}")

    def plan(self, event="push", base=None):
        options = {"event": event, "base": base, "output": None}
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            haos_apps.plan(type("Arguments", (), options)())
        return dict(line.split(": ", 1) for line in out.getvalue().splitlines())

    def test_three_apps_discovered_without_hardcoding(self):
        self.assertEqual([a["slug"] for a in haos_apps.apps()], ["one", "three", "two"])

    def test_single_app_change_does_not_release_others(self):
        self.commit("two/Dockerfile", "FROM scratch\n# changed\n")
        result = self.plan(base="HEAD^")
        self.assertEqual(json.loads(result["releases"]), ["two"])
        self.assertEqual([x["app"] for x in json.loads(result["matrix"])["include"]], ["two"])
        self.assertEqual(json.loads(result["matrix"])["include"][0]["version"], "0.1.1")

    def test_changelog_and_version_only_changes_do_not_release(self):
        self.commit("one/CHANGELOG.md", "# History\n")
        self.commit("one/config.yaml", 'name: "one"\nslug: one\nversion: "0.1.1"\narch:\n  - amd64\n')
        result = self.plan(base="HEAD~2")
        self.assertEqual(json.loads(result["releases"]), [])

    def test_shared_workflow_change_builds_all_without_releasing(self):
        Path("scripts").mkdir()
        self.commit("scripts/helper.py", "print(1)\n")
        result = self.plan(base="HEAD^")
        self.assertEqual(json.loads(result["releases"]), [])
        self.assertEqual(len(json.loads(result["matrix"])["include"]), 3)

    def test_per_app_tag_is_stronger_than_legacy_tag(self):
        self.git("tag", "one/v0.1.0")
        self.commit("one/Dockerfile", "FROM scratch\n# version 2\n")
        result = self.plan(base="HEAD^")
        self.assertEqual(json.loads(result["releases"]), ["one"])

    def test_release_updates_only_selected_app(self):
        self.commit("two/Dockerfile", "FROM scratch\\n# new package\\n")
        tags = Path("app-tags.txt")
        with contextlib.redirect_stdout(io.StringIO()):
            haos_apps.release(type("Args", (), {
                "apps_json": '["two"]', "tags_output": str(tags)
            })())
        self.assertIn('version: "0.1.1"', Path("two/config.yaml").read_text())
        self.assertIn('version: "0.1.0"', Path("one/config.yaml").read_text())
        self.assertIn("change two/Dockerfile", Path("two/CHANGELOG.md").read_text())
        self.assertEqual(tags.read_text(), "two/v0.1.1\\n")

    def test_external_image_app_does_not_require_build(self):
        Path("three/Dockerfile").unlink()
        self.commit("three/config.yaml", (
            'name: "three"\\nslug: three\\nversion: "0.1.0"\\n'
            'arch:\\n  - amd64\\nimage: "example.invalid/media:1"\\n'
        ))
        result = self.plan(base="HEAD^")
        self.assertEqual(json.loads(result["releases"]), ["three"])
        self.assertEqual(json.loads(result["matrix"])["include"], [])

    def test_pr_changed_app_and_shared_change(self):
        self.commit("three/Dockerfile", "FROM scratch\n# PR\n")
        result = self.plan(event="pr", base="v0.1.10")
        self.assertEqual(json.loads(result["releases"]), [])
        self.assertEqual([x["app"] for x in json.loads(result["matrix"])["include"]], ["three"])


if __name__ == "__main__":
    unittest.main()
