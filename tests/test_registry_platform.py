from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PLATFORM_FILES = (
    "_config.yml",
    "Gemfile",
    "_layouts/default.html",
    "_layouts/decision.html",
    "_includes/decision-card.html",
    "assets/rejestr.css",
    "assets/rejestr.js",
    ".github/DISCUSSION_TEMPLATE/propozycje-zmian-regulaminu.yml",
    ".github/workflows/validate.yml",
    ".github/workflows/pages.yml",
)


class RegistryPlatformTests(unittest.TestCase):
    def test_required_platform_files_exist(self):
        missing = [path for path in REQUIRED_PLATFORM_FILES if not (ROOT / path).is_file()]
        self.assertEqual(missing, [], f"Brak plików platformy rejestru: {missing}")

    def test_index_exposes_search_and_agreed_filters(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        required = (
            'id="search"',
            'id="filter-type"',
            'id="filter-status"',
            'id="filter-season"',
            'id="filter-subject"',
            'id="filter-effect"',
            'id="page-size"',
            'id="pagination-top"',
            'id="pagination-bottom"',
            "site.decyzje",
            "decision-card.html",
        )
        missing = [fragment for fragment in required if fragment not in index]
        self.assertEqual(missing, [], f"Indeks nie zawiera wyszukiwarki lub filtrów: {missing}")

    def test_newest_decisions_are_rendered_first(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn("site.decyzje | sort: 'slug' | reverse", index)

    def test_header_links_to_discussions_and_new_proposal(self):
        layout = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
        self.assertIn("Otwarte dyskusje", layout)
        self.assertIn("Otwórz nową dyskusję", layout)
        self.assertTrue((ROOT / "dyskusje.html").is_file())

    def test_config_publishes_decision_collection(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        for fragment in ("decyzje:", "output: true", "permalink: /decyzje/:name/", "- .DS_Store"):
            self.assertIn(fragment, config)

    def test_source_link_uses_the_explicit_repository_url(self):
        config = (ROOT / "_config.yml").read_text(encoding="utf-8")
        layout = (ROOT / "_layouts" / "decision.html").read_text(encoding="utf-8")
        self.assertIn(
            "repository_url: https://github.com/Fencer4Life/Regulamin_Kadry-SPWS",
            config,
        )
        self.assertIn("site.repository_url", layout)
        self.assertNotIn("site.github.repository_url", layout)

    def test_views_derive_the_public_decision_number_from_the_slug(self):
        card = (ROOT / "_includes" / "decision-card.html").read_text(encoding="utf-8")
        layout = (ROOT / "_layouts" / "decision.html").read_text(encoding="utf-8")
        self.assertIn("include.decision.slug | slice: 0, 6 | upcase", card)
        self.assertNotIn("include.decision.id", card)
        self.assertIn("page.slug | slice: 0, 6 | upcase", layout)
        self.assertNotIn("page.id", layout)

    def test_pull_requests_validate_but_only_main_deploys_pages(self):
        validate = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
        pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", validate)
        self.assertIn("python -m unittest discover -s tests -v", validate)
        self.assertIn("bundle exec jekyll build --strict_front_matter", validate)
        self.assertIn("branches: [main]", pages)
        self.assertIn("pages: write", pages)
        self.assertIn("id-token: write", pages)
        self.assertIn("bundle exec jekyll build --strict_front_matter", pages)
        self.assertNotIn("actions/jekyll-build-pages", pages)
        self.assertNotIn("pull_request:", pages)

    def test_pages_refreshes_discussions_safely(self):
        pages = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", pages)
        self.assertIn("*/15", pages)
        self.assertIn("discussion:", pages)
        self.assertIn("discussions: read", pages)
        self.assertIn("sync_discussions.py", pages)

    def test_decision_creation_workflow_is_idempotent_and_serialized(self):
        workflow = ROOT / ".github" / "workflows" / "create-decision.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for fragment in ("do rozstrzygnięcia", "concurrency:", "discussion_url", "--draft", "decyzja"):
            self.assertIn(fragment, text)

    def test_merged_decision_closes_its_discussion_as_resolved(self):
        workflow = ROOT / ".github" / "workflows" / "resolve-discussion.yml"
        self.assertTrue(workflow.is_file())
        text = workflow.read_text(encoding="utf-8")
        for fragment in ("pull_request:", "closed", "merged", "discussion_url", "RESOLVED", "closeDiscussion"):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
