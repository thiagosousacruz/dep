"""Gera o cheatsheets.html a partir dos Markdown de SQL e PySpark.

Os arquivos Markdown sao a fonte de verdade. Nao edite cheatsheets.html.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "cheatsheets.html"
PLACEHOLDERS = ("{{ SIDEBAR_SQL }}", "{{ SIDEBAR_PYSPARK }}", "{{ CONTENT_INJECT }}")


@dataclass(frozen=True)
class Area:
    directory: Path
    label: str
    css_class: str


AREAS = (
    Area(ROOT / "01_cheatsheets" / "01_sql", "SQL", "sql"),
    Area(ROOT / "01_cheatsheets" / "02_pyspark", "PySpark", "pyspark"),
)


def markdown_files(area: Area) -> list[Path]:
    return sorted(
        path
        for path in area.directory.glob("*.md")
        if path.name.casefold() != "readme.md"
    )


def title_from(markdown_text: str, path: Path) -> str:
    match = re.search(r"^#{1,2}\s+(.+)$", markdown_text, flags=re.MULTILINE)
    return match.group(1).strip() if match else path.stem.replace("_", " ").title()


def search_text(title: str) -> str:
    return re.sub(r"[^\w\s-]", " ", title, flags=re.UNICODE).casefold()


def validate_inputs(files_by_area: dict[Area, list[Path]], template: str) -> None:
    errors: list[str] = []
    for area, files in files_by_area.items():
        if not area.directory.is_dir():
            errors.append(f"Diretorio ausente: {area.directory.relative_to(ROOT)}")
        if not files:
            errors.append(f"Nenhum Markdown encontrado em {area.directory.relative_to(ROOT)}")

    for placeholder in PLACEHOLDERS:
        count = template.count(placeholder)
        if count != 1:
            errors.append(f"Placeholder {placeholder!r}: esperado 1, encontrado {count}")

    if errors:
        raise RuntimeError("Falha na validacao de entrada:\n- " + "\n- ".join(errors))


def build_id_map(files_by_area: dict[Area, list[Path]]) -> dict[Path, str]:
    result: dict[Path, str] = {}
    for area, files in files_by_area.items():
        for index, path in enumerate(files, 1):
            result[path.resolve()] = f"#{area.css_class}-{index:02d}"
    return result


def rewrite_local_link(href: str, source: Path, id_map: dict[Path, str]) -> str:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return href

    target = (source.parent / unquote(parsed.path)).resolve()
    if target in id_map:
        anchor = id_map[target]
        return f"{anchor}-{parsed.fragment}" if parsed.fragment else anchor
    return href


def render_section(
    path: Path,
    index: int,
    area: Area,
    id_map: dict[Path, str],
) -> tuple[str, str]:
    markdown_text = path.read_text(encoding="utf-8")
    title = title_from(markdown_text, path)
    rendered = markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")

    heading = soup.find(["h1", "h2"])
    if heading:
        heading.name = "h2"
        heading.clear()
        number = soup.new_tag("span", attrs={"class": f"sec-num {area.css_class}"})
        number.string = f"{area.label} {index:02d}"
        heading.extend((number, f" {title}"))

    for link in soup.find_all("a", href=True):
        link["href"] = rewrite_local_link(link["href"], path, id_map)

    # Preserva pre > code e apenas acrescenta a moldura visual.
    for pre in list(soup.find_all("pre")):
        code = pre.find("code")
        if code is None:
            continue
        classes = code.get("class", [])
        language = next(
            (item.removeprefix("language-") for item in classes if item.startswith("language-")),
            "sql" if area.css_class == "sql" else "python",
        )
        wrapper = soup.new_tag("div", attrs={"class": "code-wrap"})
        label = soup.new_tag("div", attrs={"class": f"code-lang {area.css_class}-lang"})
        label.string = language.upper()
        button = soup.new_tag("button", attrs={"class": "copy-btn", "type": "button", "onclick": "copyCode(this)"})
        button.string = "Copiar"
        pre.wrap(wrapper)
        wrapper.insert(0, label)
        wrapper.insert(1, button)

    section_id = id_map[path.resolve()].removeprefix("#")
    section = f'<section id="{section_id}" class="cheat-section">\n{soup}\n</section>'
    nav = (
        f'<a class="nav-item {area.css_class}-item" href="#{section_id}" '
        f'data-search="{search_text(title)}"><span class="num">{index:02d}</span>{title}</a>'
    )
    return section, nav


def validate_output(html: str, files_by_area: dict[Area, list[Path]]) -> None:
    errors = [placeholder for placeholder in PLACEHOLDERS if placeholder in html]
    soup = BeautifulSoup(html, "html.parser")
    ids = {tag["id"] for tag in soup.find_all(id=True)}
    broken_anchors = sorted(
        {
            link["href"]
            for link in soup.find_all("a", href=True)
            if link["href"].startswith("#") and link["href"][1:] not in ids
        }
    )
    expected = sum(len(files) for files in files_by_area.values())
    actual = len(soup.select("section.cheat-section"))

    messages: list[str] = []
    if errors:
        messages.append("Placeholders residuais: " + ", ".join(errors))
    if broken_anchors:
        messages.append("Links internos quebrados: " + ", ".join(broken_anchors))
    if actual != expected:
        messages.append(f"Secoes geradas: esperado {expected}, encontrado {actual}")
    if soup.select("section[id^='modeling-']"):
        messages.append("Modeling nao deve fazer parte do HTML principal")
    if messages:
        raise RuntimeError("Falha na validacao da saida:\n- " + "\n- ".join(messages))


def build() -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    files_by_area = {area: markdown_files(area) for area in AREAS}
    validate_inputs(files_by_area, template)
    id_map = build_id_map(files_by_area)

    content: list[str] = []
    navigation: dict[str, list[str]] = {area.css_class: [] for area in AREAS}
    for area, files in files_by_area.items():
        for index, path in enumerate(files, 1):
            section, nav = render_section(path, index, area, id_map)
            content.append(section)
            navigation[area.css_class].append(nav)

    html = template
    html = html.replace("{{ SIDEBAR_SQL }}", "\n    ".join(navigation["sql"]))
    html = html.replace("{{ SIDEBAR_PYSPARK }}", "\n    ".join(navigation["pyspark"]))
    html = html.replace("{{ CONTENT_INJECT }}", "\n\n".join(content))
    html = re.sub(
        r'(<span>SQL</span> <span class="badge">)\d+(</span>)',
        rf"\g<1>{len(navigation['sql'])}\g<2>",
        html,
    )
    html = re.sub(
        r'(<span>PySpark</span> <span class="badge">)\d+(</span>)',
        rf"\g<1>{len(navigation['pyspark'])}\g<2>",
        html,
    )
    validate_output(html, files_by_area)
    OUTPUT_PATH.write_text(html, encoding="utf-8", newline="\n")
    return f"Build concluido: {len(navigation['sql'])} SQL + {len(navigation['pyspark'])} PySpark."


if __name__ == "__main__":
    print(build())
