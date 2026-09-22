import tempfile
import unittest
from pathlib import Path

from narzedzia.prepare_regulamin import normalize_and_build, verify
from tests.test_docx_current_contract import CANONICAL_SOURCE


class NoMarkdownPreviewTests(unittest.TestCase):
    def test_build_and_verify_need_only_source_and_docx(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'source.md', root / 'source.docx'
            source.write_bytes(CANONICAL_SOURCE.read_bytes())
            normalize_and_build(source, output)
            self.assertEqual({p.name for p in root.iterdir()}, {'source.md', 'source.docx'})
            verify(source, output)

    def test_repository_and_workflows_do_not_depend_on_preview(self):
        root = CANONICAL_SOURCE.parents[1]
        self.assertEqual(list((root / 'regulamin').glob('*.podglad.md')), [])
        self.assertFalse((root / 'narzedzia/markdown_preview.py').exists())
        for path in list((root / 'narzedzia').glob('*.py')) + list((root / '.github/workflows').glob('*.yml')):
            with self.subTest(path=path.name):
                self.assertNotIn('markdown_preview', path.read_text())
                self.assertNotIn('.podglad.md', path.read_text())
