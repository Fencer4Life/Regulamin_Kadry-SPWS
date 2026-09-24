import tempfile
import unittest
from pathlib import Path

from narzedzia.resolve_discussion import discussion_number_from_card


class ResolveDiscussionTests(unittest.TestCase):
    def test_reads_discussion_number_from_crlf_card(self):
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "DR-028-test.md"
            card.write_bytes(
                b"---\r\nid: DR-028\r\n"
                b"discussion_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS/discussions/75\r\n"
                b"---\r\n"
            )

            self.assertEqual(discussion_number_from_card(card), 75)

    def test_rejects_missing_or_invalid_discussion_number(self):
        with tempfile.TemporaryDirectory() as directory:
            card = Path(directory) / "DR-028-test.md"
            card.write_text("discussion_url: https://example.com/discussions/not-a-number\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Niepoprawny discussion_url"):
                discussion_number_from_card(card)


if __name__ == "__main__":
    unittest.main()
