"""The only permitted addition to the immutable site is an empty Pages marker."""

from pathlib import Path
import tempfile
import unittest

from scripts.check_site import check_member_set


class SiteDeploymentMarkerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.site = Path(self.temporary.name)
        (self.site / "index.html").write_text("original", encoding="utf-8")
        self.expected = {"index.html"}

    def test_absent_or_empty_regular_marker_is_accepted_and_explicitly_reported(self):
        _, marker, errors = check_member_set(self.site, self.expected)
        self.assertFalse(marker["present"])
        self.assertEqual(errors, [])
        (self.site / ".nojekyll").write_bytes(b"")
        actual, marker, errors = check_member_set(self.site, self.expected)
        self.assertEqual(actual, {"index.html", ".nojekyll"})
        self.assertTrue(marker["accepted"])
        self.assertEqual(marker["bytes"], 0)
        self.assertEqual(errors, [])

    def test_nonempty_marker_is_rejected(self):
        (self.site / ".nojekyll").write_text("unexpected content", encoding="utf-8")
        _, marker, errors = check_member_set(self.site, self.expected)
        self.assertFalse(marker["accepted"])
        self.assertTrue(errors)

    def test_unknown_extra_is_rejected_even_with_valid_marker(self):
        (self.site / ".nojekyll").write_bytes(b"")
        (self.site / "unexpected.json").write_text("{}", encoding="utf-8")
        _, marker, errors = check_member_set(self.site, self.expected)
        self.assertTrue(marker["accepted"])
        self.assertTrue(any("unexpected.json" in error for error in errors))

    def test_symlink_marker_is_rejected_even_if_target_is_empty(self):
        target = self.site.parent / (self.site.name + "-empty")
        target.write_bytes(b"")
        self.addCleanup(lambda: target.unlink(missing_ok=True))
        try:
            (self.site / ".nojekyll").symlink_to(target)
        except OSError as exc:
            self.skipTest(f"Creating symlinks is unavailable: {exc}")
        _, marker, errors = check_member_set(self.site, self.expected)
        self.assertTrue(marker["is_symlink"])
        self.assertFalse(marker["accepted"])
        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
