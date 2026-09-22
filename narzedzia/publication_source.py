"""Visible Markdown blocks for every non-normative part of the document."""
import re

BLOCK = re.compile(r'<!-- publication:([a-z-]+) -->\n(.*?)\n<!-- /publication -->', re.S)
KEYS = {'cover', 'toc', 'outline', 'annex-heading', 'annex-note', 'history', 'running'}


def table_rows(block):
    rows = []
    for line in block.splitlines():
        if line.startswith('|'):
            cells = [v.strip() for v in line.strip('|').split('|')]
            if not all(re.fullmatch(r':?-{3,}:?', v) for v in cells):
                rows.append(cells)
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError('Niepoprawna tabela publikacyjna')
    return rows


def prose(block):
    return [re.sub(r'^#+ ', '', line) for line in block.splitlines() if line and not line.startswith('|')]


def extract(markdown, metadata):
    blocks = {}
    def take(match):
        key, text = match.groups()
        if key not in KEYS or key in blocks:
            raise ValueError(f'Nieznany lub powtórzony blok publikacyjny: {key}')
        blocks[key] = text
        return ''
    markdown = BLOCK.sub(take, markdown)
    if not blocks:
        return markdown, blocks
    if blocks.keys() != KEYS:
        raise ValueError(f'Brak bloków publikacyjnych: {KEYS - blocks.keys()}')
    cover = prose(blocks['cover'])
    if len(cover) != 3:
        raise ValueError('Okładka wymaga oznaczenia, tytułu i podtytułu')
    metadata.update(zip(('cover_label', 'title', 'subtitle'), cover))
    rows = table_rows(blocks['cover'])
    if len(rows) != 4 or len(rows[0]) != 2:
        raise ValueError('Okładka wymaga trzech wierszy danych')
    metadata.update(zip(('cover_version', 'status', 'cover_date'), (r[1] for r in rows[1:])))
    metadata.update({f'cover_label_{i}': r[0] for i, r in enumerate(rows[1:])})
    history = table_rows(blocks['history'])
    if len(history) != 2 or len(history[0]) != 4:
        raise ValueError('Historia wymaga czterech kolumn i jednego wiersza wersji')
    metadata.update(zip(('version', 'project_date', 'history_scope', 'history_status'), history[1]))
    metadata['history_title'] = prose(blocks['history'])[0]
    metadata['toc_title'] = prose(blocks['toc'])[0]
    outline = prose(blocks['outline'])
    if len(outline) != 2:
        raise ValueError('Konstrukcja wymaga tytułu i wprowadzenia')
    metadata['outline_title'], metadata['outline_intro'] = outline
    metadata['toc_note'] = ''
    annex = prose(blocks['annex-heading'])
    if len(annex) != 4:
        raise ValueError('Nagłówek załącznika wymaga czterech akapitów')
    metadata.update(zip(('annex_label', 'annex_title', 'annex_subtitle', 'annex_coefficient'), annex))
    metadata['annex_note'] = blocks['annex-note']
    running = prose(blocks['running'])
    if len(running) != 3:
        raise ValueError('Wymagane są trzy akapity nagłówka i stopek')
    metadata['header_text'], metadata['cover_footer'], footer = running
    match = re.fullmatch(r'(.*?)(\d+)<!-- field:PAGE -->(.*?)(\d+)<!-- field:NUMPAGES -->', footer)
    if not match:
        raise ValueError('Stopka wymaga pól PAGE i NUMPAGES')
    metadata.update(zip(('footer_text', 'page_cache', 'footer_join', 'pages_cache'), match.groups()))
    return markdown, blocks


def wrap(key, text):
    return f'<!-- publication:{key} -->\n{text}\n<!-- /publication -->\n\n'


def restore_tokens(markdown):
    markdown = re.sub(r'§ \d+(?: (?:ust\.|pkt|lit\.|tiret|podwójne tiret) [\da-z]+)*<!-- ref:([a-z0-9-]+/[a-z0-9-]+) -->',
                      lambda m: '{{ref:'+m[1]+'}}', markdown)
    markdown = re.sub(r'(?:T−\d+|T|\d+)<!-- (term|days):([a-z0-9-]+) -->',
                      lambda m: '{{'+m[1]+':'+m[2]+'}}', markdown)
    # Editorial IDs stay hidden in rendered Markdown, but are preserved for the parser.
    markdown = re.sub(r'<!-- (unit:[a-z0-9-]+) -->', r'[\1]', markdown)
    markdown = re.sub(r'^## Rozdział \d+ — (.*?) <!-- chapter:([a-z0-9-]+) -->$', r'## [chapter:\2] \1', markdown, flags=re.M)
    markdown = re.sub(r'^### § \d+(?: — (.*?))? <!-- section:([a-z0-9-]+) -->$',
                      lambda m: '### [section:'+m[2]+']'+(' '+m[1] if m[1] else ''), markdown, flags=re.M)
    return markdown


def make_visible(text, model):
    from narzedzia.normalize_regulamin_markdown import resolve_references
    text = re.sub(r'\{\{((?:ref|term|days):[^}]+)}}',
                  lambda m: resolve_references(model, m[0])+'<!-- '+m[1]+' -->', text)
    text = re.sub(r'\[unit:([a-z0-9-]+)]', r'<!-- unit:\1 -->', text)
    chapter_count = section_count = 0
    def chapter(m):
        nonlocal chapter_count
        chapter_count += 1
        return f'## Rozdział {chapter_count} — {m[2]} <!-- chapter:{m[1]} -->'
    def section(m):
        nonlocal section_count
        section_count += 1
        return f'### § {section_count}'+(f' — {m[2]}' if m[2] else '')+f' <!-- section:{m[1]} -->'
    text = re.sub(r'^## \[chapter:([^]]+)] (.+)$', chapter, text, flags=re.M)
    return re.sub(r'^### \[section:([^]]+)](?: (.*))?$', section, text, flags=re.M)
