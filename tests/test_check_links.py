import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[1]
SCRIPT = ROOT / "scripts" / "check_links.py"
spec = importlib.util.spec_from_file_location("check_links", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


class CheckLinksTests(unittest.TestCase):
    def test_reports_missing_relative_markdown_link(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text("[broken](missing.md)\n", encoding="utf-8")
            self.assertEqual(module.missing_links(root), ["README.md: missing.md"])

    def test_ignores_external_and_existing_links(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "guide.md").write_text("ok\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[external](https://example.com) [local](guide.md) [anchor](#top)\n",
                encoding="utf-8",
            )
            self.assertEqual(module.missing_links(root), [])


if __name__ == "__main__":
    unittest.main()
