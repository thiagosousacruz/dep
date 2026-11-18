"""Gera cheatsheets.html, trilhas.html e desafio.html a partir dos Markdown e do banco de desafios.

Os arquivos Markdown e 02_desafios/*.json sao a fonte de verdade. Nao edite os HTML gerados.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

import markdown
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "cheatsheets.html"
PLACEHOLDERS = ("{{ SIDEBAR_SQL }}", "{{ SIDEBAR_PYSPARK }}", "{{ CONTENT_INJECT }}")

TRAIL_TEMPLATE_PATH = ROOT / "trilhas_template.html"
TRAIL_OUTPUT_PATH = ROOT / "trilhas.html"
TRAIL_PLACEHOLDERS = ("{{ SIDEBAR_TRILHAS }}", "{{ HOME_TRILHAS }}", "{{ TOTAL_TRILHAS }}", "{{ CONTENT_INJECT }}")

HAND_WRITTEN_PAGES = (
    "index.html",
    "plano-12-semanas.html",
    "plano_12_meses_engenheiro_dados.html",
    "framework_dominio_tecnico.html",
)

CHALLENGES_DIR = ROOT / "02_desafios"
CHALLENGE_TEMPLATE_PATH = ROOT / "desafio_template.html"
CHALLENGE_OUTPUT_PATH = ROOT / "desafio.html"
CHALLENGE_PLACEHOLDER = "{{ DESAFIOS_JSON }}"
LEVELS = ("basico", "intermediario", "avancado")
# Secoes conceituais ou de revisao nao viram desafio.
NON_TRAINABLE = re.compile(r"^(o que (e|sao)|checklist|cuidados.*|principio|fontes)$")


@dataclass(frozen=True)
class Area:
    directory: Path
    label: str
    css_class: str


AREAS = (
    Area(ROOT / "01_cheatsheets" / "01_sql", "SQL", "sql"),
    Area(ROOT / "01_cheatsheets" / "02_pyspark", "PySpark", "pyspark"),
)
TRAIL_AREA = Area(ROOT / "03_trilhas", "Trilha", "trilha")

# Mapa de links: arquivo Markdown -> (pagina HTML, id da secao).
LinkMap = dict[Path, tuple[str, str]]


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


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.casefold()).strip("-")


def h2_titles(markdown_text: str) -> list[str]:
    """Titulos '## ' fora de blocos de codigo, na ordem do arquivo."""
    titles: list[str] = []
    in_fence = False
    for line in markdown_text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence and line.startswith("## "):
            titles.append(line[3:].strip())
    return titles


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


def build_link_map() -> LinkMap:
    """Mapa global de links entre paginas geradas (cheatsheets e trilhas)."""
    cheats = build_id_map({area: markdown_files(area) for area in AREAS})
    trails = build_id_map({TRAIL_AREA: markdown_files(TRAIL_AREA)})
    result: LinkMap = {path: ("cheatsheets.html", anchor[1:]) for path, anchor in cheats.items()}
    result.update({path: ("trilhas.html", anchor[1:]) for path, anchor in trails.items()})
    return result


def rewrite_local_link(href: str, source: Path, link_map: LinkMap, page: str) -> str:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return href

    target = (source.parent / unquote(parsed.path)).resolve()
    if target in link_map:
        target_page, anchor = link_map[target]
        prefix = "" if target_page == page else target_page
        return f"{prefix}#{anchor}-{parsed.fragment}" if parsed.fragment else f"{prefix}#{anchor}"
    if target.parent == ROOT and target.suffix == ".html":
        # Paginas da raiz (desafio.html, planos): os HTML gerados ficam todos na raiz.
        query = f"?{parsed.query}" if parsed.query else ""
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        return f"{target.name}{query}{fragment}"
    if target.is_file() and target.is_relative_to(ROOT):
        # Arquivo do repositorio fora do build (ex.: Modeling): caminho relativo a raiz, onde ficam os HTML.
        fragment = f"#{parsed.fragment}" if parsed.fragment else ""
        return target.relative_to(ROOT).as_posix() + fragment
    return href


def render_section(
    path: Path,
    index: int,
    area: Area,
    link_map: LinkMap,
    page: str = "cheatsheets.html",
) -> tuple[str, str]:
    markdown_text = path.read_text(encoding="utf-8")
    title = title_from(markdown_text, path)
    rendered = markdown.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "sane_lists", "md_in_html"],
        output_format="html5",
    )
    soup = BeautifulSoup(rendered, "html.parser")

    section_id = link_map[path.resolve()][1]
    heading = soup.find(["h1", "h2"])
    for subheading in soup.find_all("h2"):
        if subheading is not heading:
            subheading["id"] = f"{section_id}-{slugify(subheading.get_text())}"
    if heading:
        heading.name = "h2"
        heading.clear()
        number = soup.new_tag("span", attrs={"class": f"sec-num {area.css_class}"})
        number.string = f"{area.label} {index:02d}"
        heading.extend((number, f" {title}"))

    for link in soup.find_all("a", href=True):
        link["href"] = rewrite_local_link(link["href"], path, link_map, page)

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
    link_map = build_link_map()

    content: list[str] = []
    navigation: dict[str, list[str]] = {area.css_class: [] for area in AREAS}
    for area, files in files_by_area.items():
        for index, path in enumerate(files, 1):
            section, nav = render_section(path, index, area, link_map)
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


def build_trails() -> str:
    template = TRAIL_TEMPLATE_PATH.read_text(encoding="utf-8")
    files = markdown_files(TRAIL_AREA)
    errors = [f"Placeholder {p!r}: esperado 1" for p in TRAIL_PLACEHOLDERS if template.count(p) != 1]
    if not files:
        errors.append(f"Nenhuma licao em {TRAIL_AREA.directory.relative_to(ROOT)}")
    if errors:
        raise RuntimeError("Falha na validacao das trilhas:\n- " + "\n- ".join(errors))

    link_map = build_link_map()
    content: list[str] = []
    navigation: list[str] = []
    home: list[str] = []
    for index, path in enumerate(files, 1):
        section, nav = render_section(path, index, TRAIL_AREA, link_map, page="trilhas.html")
        content.append(section)
        navigation.append(nav)
        title = title_from(path.read_text(encoding="utf-8"), path)
        home.append(f'<li><span class="num">{index:02d}</span> <a href="#trilha-{index:02d}">{title}</a></li>')

    html = template
    html = html.replace("{{ SIDEBAR_TRILHAS }}", "\n    ".join(navigation))
    html = html.replace("{{ HOME_TRILHAS }}", "\n        ".join(home))
    html = html.replace("{{ TOTAL_TRILHAS }}", f"{len(files)} lições")
    html = html.replace("{{ CONTENT_INJECT }}", "\n\n".join(content))
    html = re.sub(r'(<span>Trilhas</span> <span class="badge">)\d+(</span>)', rf"\g<1>{len(files)}\g<2>", html)

    soup = BeautifulSoup(html, "html.parser")
    ids = {tag["id"] for tag in soup.find_all(id=True)}
    broken = sorted(
        {a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("#") and a["href"][1:] not in ids}
    )
    if broken:
        raise RuntimeError("Links internos quebrados em trilhas.html: " + ", ".join(broken))
    TRAIL_OUTPUT_PATH.write_text(html, encoding="utf-8", newline="\n")
    return f"Trilhas: {len(files)} licoes."


def validate_cross_links(challenge_ids: set[str]) -> None:
    """Confere links entre paginas geradas: ancoras de outra pagina, ids de desafio e .md nao resolvidos."""
    soups = {
        path.name: BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for path in (OUTPUT_PATH, TRAIL_OUTPUT_PATH)
    }
    ids = {name: {tag["id"] for tag in soup.find_all(id=True)} for name, soup in soups.items()}
    # Paginas escritas a mao tambem linkam para ancoras das geradas: valide-as como origem.
    for name in HAND_WRITTEN_PAGES:
        soups[name] = BeautifulSoup((ROOT / name).read_text(encoding="utf-8"), "html.parser")
    errors: set[str] = set()
    for name, soup in soups.items():
        for link in soup.find_all("a", href=True):
            href = link["href"]
            parsed = urlsplit(href)
            if parsed.scheme or parsed.netloc:
                continue
            if parsed.path in ids and parsed.fragment and parsed.fragment not in ids[parsed.path]:
                errors.add(f"{name}: ancora inexistente {href}")
            elif parsed.path == "desafio.html" and parsed.query.startswith("id="):
                if parsed.query[3:].split("&")[0] not in challenge_ids:
                    errors.add(f"{name}: desafio inexistente {href}")
            elif parsed.path.endswith(".md"):
                if parsed.path.startswith("../"):
                    # Outro projeto do workspace (ex.: o curso em ../engenharia_dados): basta existir.
                    if not (ROOT / unquote(parsed.path)).resolve().is_file():
                        errors.add(f"{name}: Markdown inexistente {href}")
                elif not parsed.path.startswith("01_cheatsheets/03_modeling-e-analytics/"):
                    errors.add(f"{name}: link para Markdown fora do build {href}")
                elif not (ROOT / unquote(parsed.path)).is_file():
                    errors.add(f"{name}: Markdown inexistente {href}")
    if errors:
        raise RuntimeError("Falha na validacao de links entre paginas:\n- " + "\n- ".join(sorted(errors)))


def trainable_sections(files_by_area: dict[Area, list[Path]], id_map: dict[Path, str]) -> dict[str, dict]:
    """Mapeia 'pasta/arquivo.md#slug' para os dados da secao treinavel."""
    sections: dict[str, dict] = {}
    for area, files in files_by_area.items():
        for path in files:
            text = path.read_text(encoding="utf-8")
            anchor = id_map[path.resolve()]
            for title in h2_titles(text):
                slug = slugify(title)
                if NON_TRAINABLE.match(slug.replace("-", " ")):
                    continue
                ref = f"{area.directory.name}/{path.name}#{slug}"
                sections[ref] = {
                    "area": area.css_class,
                    "arquivo": title_from(text, path),
                    "secao": title,
                    "link": f"cheatsheets.html{anchor}-{slug}",
                }
    return sections


def load_challenges() -> tuple[list[dict], set[str], dict[str, int]]:
    challenges: list[dict] = []
    skipped: set[str] = set()
    weeks: dict[str, int] = {}
    for path in sorted(CHALLENGES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        challenges.extend(data.get("desafios", []))
        skipped.update(data.get("secoes_sem_desafio", []))
        weeks.update(data.get("semanas_por_arquivo", {}))
    return challenges, skipped, weeks


def validate_challenges(
    challenges: list[dict],
    skipped: set[str],
    weeks: dict[str, int],
    sections: dict[str, dict],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    seen: set[str] = set()
    covered: set[str] = set()
    for item in challenges:
        cid = item.get("id", "<sem id>")
        if cid in seen:
            errors.append(f"{cid}: id duplicado")
        seen.add(cid)
        ref = item.get("ref", "")
        if ref not in sections:
            errors.append(f"{cid}: ref inexistente ou nao treinavel: {ref}")
        covered.add(ref)
        if not item.get("ferramenta"):
            errors.append(f"{cid}: ferramenta vazia")
        week = item.get("semana", weeks.get(ref.split("#")[0]))
        if week is not None and not (isinstance(week, int) and 1 <= week <= 12):
            errors.append(f"{cid}: semana fora de 1..12: {week}")
        levels = item.get("niveis", {})
        for level in LEVELS:
            body = levels.get(level)
            if not body or not body.get("enunciado") or not body.get("solucao"):
                errors.append(f"{cid}: nivel '{level}' sem enunciado ou solucao")
                continue
            for table in body.get("dados") or []:
                width = len(table.get("colunas", []))
                rows = table.get("linhas", [])
                types = table.get("tipos")
                if not table.get("tabela") or not width or not rows or any(len(row) != width for row in rows):
                    errors.append(f"{cid}/{level}: tabela sem nome ou com colunas e linhas inconsistentes")
                if types is not None and len(types) != width:
                    errors.append(f"{cid}/{level}: 'tipos' com tamanho diferente de 'colunas'")
        extra = set(levels) - set(LEVELS)
        if extra:
            errors.append(f"{cid}: niveis desconhecidos {sorted(extra)}")
    for ref in sorted(skipped - set(sections)):
        errors.append(f"secoes_sem_desafio aponta para secao inexistente: {ref}")
    missing = sorted(set(sections) - covered - skipped)
    return errors, missing


def build_challenges(allow_incomplete: bool = False) -> str:
    files_by_area = {area: markdown_files(area) for area in AREAS}
    id_map = build_id_map(files_by_area)
    sections = trainable_sections(files_by_area, id_map)
    challenges, skipped, weeks = load_challenges()
    errors, missing = validate_challenges(challenges, skipped, weeks, sections)
    if missing and not allow_incomplete:
        errors.append("Secoes sem desafio:\n  " + "\n  ".join(missing))
    if errors:
        raise RuntimeError("Falha na validacao dos desafios:\n- " + "\n- ".join(errors))

    catalog = []
    for item in sorted(challenges, key=lambda c: c["id"]):
        meta = sections[item["ref"]]
        catalog.append({
            **item,
            **meta,
            "semana": item.get("semana", weeks.get(item["ref"].split("#")[0])),
        })
    payload = json.dumps(catalog, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    template = CHALLENGE_TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count(CHALLENGE_PLACEHOLDER) != 1:
        raise RuntimeError(f"Placeholder {CHALLENGE_PLACEHOLDER!r}: esperado 1 em {CHALLENGE_TEMPLATE_PATH.name}")
    CHALLENGE_OUTPUT_PATH.write_text(template.replace(CHALLENGE_PLACEHOLDER, payload), encoding="utf-8", newline="\n")

    validate_cross_links({item["id"] for item in catalog})

    trainable = len(sections) - len(skipped)
    coverage = 100 * (trainable - len(missing)) / trainable if trainable else 100
    message = f"Desafios: {len(catalog)} itens, cobertura {coverage:.0f}% de {trainable} secoes treinaveis."
    if missing:
        message += f"\nAviso: {len(missing)} secoes sem desafio:\n  " + "\n  ".join(missing)
    return message


if __name__ == "__main__":
    print(build())
    print(build_trails())
    print(build_challenges(allow_incomplete="--allow-incomplete" in sys.argv[1:]))
