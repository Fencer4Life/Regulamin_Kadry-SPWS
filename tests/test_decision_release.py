from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from narzedzia.publish_decision_release import publish_release, release_spec
from narzedzia.regulation_registry import get_regulation


class DecisionReleaseTests(unittest.TestCase):
    def test_shared_decision_creates_one_release_with_card_and_two_docx_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / "_decyzje" / "DR-099-test.md"
            card.parent.mkdir()
            card.write_text(
                '---\nid: DR-099\nstatus: przyjęta\ndokumenty: ["reprezentacja", "zawody"]\n'
                "zmiana_regulaminu: true\n---\n",
                encoding="utf-8",
            )
            for identifier in ("reprezentacja", "zawody"):
                output = get_regulation(identifier).docx_path(root)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"docx")

            spec = release_spec(card, root)

            self.assertEqual(spec.tag, "decyzja-DR-099")
            self.assertEqual(spec.files[0], card)
            self.assertEqual(len(spec.files), 3)

    def test_retry_reuses_release_tag_and_uploads_the_same_assets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            card = root / "DR-099.md"
            card.write_text(
                '---\nid: DR-099\nstatus: odrzucona\ndokumenty: ["zawody"]\n'
                "zmiana_regulaminu: false\n---\n",
                encoding="utf-8",
            )
            command = Mock(return_value=Mock(returncode=0, stdout="", stderr=""))

            publish_release("owner/repo", "a" * 40, card, root, run=command)

            commands = [call.args[0] for call in command.call_args_list]
            self.assertEqual(sum(args[:3] == ["gh", "release", "view"] for args in commands), 1)
            self.assertEqual(sum(args[:3] == ["gh", "release", "create"] for args in commands), 0)
            uploads = [args for args in commands if args[:3] == ["gh", "release", "upload"]]
            self.assertEqual(len(uploads), 1)
            self.assertIn(str(card), uploads[0])
            self.assertNotIn(".docx", " ".join(uploads[0]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
