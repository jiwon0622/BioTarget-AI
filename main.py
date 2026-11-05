
import streamlit as st
import requests
import html
import re
from urllib.parse import quote
from deep_translator import GoogleTranslator, MyMemoryTranslator
from Bio.Align import PairwiseAligner

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

UNIPROT_API = "https://rest.uniprot.org"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest"


# =========================================================
# 다국어 UI
# =========================================================
TEXT = {
    "한국어": {
        "subtitle": "AI 기반 신약 후보 탐색 및 표적 단백질 분석",
        "language": "🌐 Language / 언어",
        "home": "🏠 홈",
        "search": "🔎 단백질 검색",
        "compare": "⚖️ 단백질 비교",
        "hero_title": "생명과학 연구를 위한 단백질 탐색 플랫폼",
        "hero_desc": "단백질 기능, 아미노산 서열, 관련 연구 논문을 한곳에서 탐색하세요.",
        "home_search": "단백질 탐색",
        "home_search_desc": "단백질명이나 유전자명으로 단백질의 기능과 서열 정보를 찾아보세요.",
        "home_compare": "단백질 비교",
        "home_compare_desc": "두 단백질의 아미노산 서열과 서열 일치도를 비교하세요.",
        "home_papers": "연구 논문 탐색",
        "home_papers_desc": "관심 있는 단백질과 관련된 연구 자료를 찾아보세요.",
        "start_search": "단백질 검색하기",
        "start_compare": "단백질 비교하기",
        "search_title": "단백질 검색",
        "search_desc": "단백질명 또는 유전자명을 입력하세요.",
        "protein_input": "단백질명 또는 유전자명",
        "protein_placeholder": "예: insulin, TP53, hemoglobin",
        "search_button": "단백질 검색",
        "search_results": "검색 결과",
        "select_protein": "상세 정보를 확인할 단백질을 선택하세요.",
        "details": "단백질 상세 정보",
        "accession": "UniProt accession",
        "gene": "유전자명",
        "organism": "생물종",
        "length": "아미노산 길이",
        "function": "단백질 기능",
        "no_function": "UniProt에 등록된 기능 설명이 없습니다.",
        "show_sequence": "아미노산 서열 보기",
        "uniprot_link": "UniProt에서 자세히 보기",
        "papers": "관련 연구 논문",
        "papers_desc": "선택한 단백질과 관련된 논문을 검색합니다.",
        "paper_keyword": "논문 검색 키워드",
        "paper_button": "관련 논문 검색",
        "paper_placeholder": "단백질명 또는 연구 주제",
        "paper_count": "검색 결과",
        "paper_open": "논문 페이지 열기",
        "no_papers": "관련 논문을 찾지 못했습니다. 다른 검색어를 입력해 보세요.",
        "compare_title": "단백질 비교",
        "compare_desc": "두 단백질을 이름으로 검색한 뒤 각각 선택하세요.",
        "protein_a": "첫 번째 단백질",
        "protein_b": "두 번째 단백질",
        "search_a": "첫 번째 단백질 검색어",
        "search_b": "두 번째 단백질 검색어",
        "find_a": "첫 번째 단백질 검색",
        "find_b": "두 번째 단백질 검색",
        "choose_a": "첫 번째 단백질 선택",
        "choose_b": "두 번째 단백질 선택",
        "run_compare": "서열 비교 실행",
        "compare_result": "비교 결과",
        "identity": "서열 일치도",
        "aligned_length": "정렬된 서열 길이",
        "match_count": "일치하는 아미노산 수",
        "compare_note": "서열 일치도는 전역 정렬에서 동일한 아미노산이 차지하는 비율입니다. 단백질의 구조적 유사성이나 기능의 동일성을 직접 의미하지는 않습니다.",
        "same_protein": "동일한 단백질이 선택되었습니다. 서로 다른 단백질을 선택해 주세요.",
        "translation_failed": "자동 번역에 실패하여 영어 원문을 표시합니다.",
        "empty_search": "검색어를 입력해 주세요.",
        "no_results": "검색 결과가 없습니다. 다른 이름이나 유전자명을 입력해 보세요.",
        "api_error": "외부 데이터 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.",
        "footer": "BioTarget AI · 교육 및 연구 탐색용 도구",
        "loading": "데이터를 불러오는 중...",
        "no_sequence": "비교할 아미노산 서열이 충분하지 않습니다.",
        "paper_year": "발행 연도",
        "paper_authors": "저자",
        "paper_journal": "학술지",
        "abstract": "초록 보기",
        "navigation": "메뉴",
        "alignment": "서열 정렬 결과 보기",
        "alignment_note": "정렬된 두 아미노산 서열입니다.",
    },
    "English": {
        "subtitle": "AI-Assisted Drug Discovery & Target Protein Analysis",
        "language": "🌐 Language / 언어",
        "home": "🏠 Home",
        "search": "🔎 Protein Search",
        "compare": "⚖️ Protein Comparison",
        "hero_title": "A Protein Exploration Platform for Life Science Research",
        "hero_desc": "Explore protein functions, amino acid sequences, and related research papers in one place.",
        "home_search": "Protein Exploration",
        "home_search_desc": "Find protein functions and sequence information by protein or gene name.",
        "home_compare": "Protein Comparison",
        "home_compare_desc": "Compare amino acid sequences and sequence identity between two proteins.",
        "home_papers": "Research Papers",
        "home_papers_desc": "Explore research papers related to your protein of interest.",
        "start_search": "Search Proteins",
        "start_compare": "Compare Proteins",
        "search_title": "Protein Search",
        "search_desc": "Enter a protein name or gene name.",
        "protein_input": "Protein name or gene name",
        "protein_placeholder": "e.g. insulin, TP53, hemoglobin",
        "search_button": "Search Proteins",
        "search_results": "Search Results",
        "select_protein": "Select a protein to view its details.",
        "details": "Protein Details",
        "accession": "UniProt accession",
        "gene": "Gene",
        "organism": "Organism",
        "length": "Sequence length",
        "function": "Protein Function",
        "no_function": "No function description is available in UniProt.",
        "show_sequence": "Show Amino Acid Sequence",
        "uniprot_link": "View on UniProt",
        "papers": "Related Research Papers",
        "papers_desc": "Search for papers related to the selected protein.",
        "paper_keyword": "Paper search keyword",
        "paper_button": "Search Related Papers",
        "paper_placeholder": "Protein name or research topic",
        "paper_count": "Search Results",
        "paper_open": "Open Paper",
        "no_papers": "No related papers found. Try another search term.",
        "compare_title": "Protein Comparison",
        "compare_desc": "Search by protein name and select one protein for each comparison field.",
        "protein_a": "First Protein",
        "protein_b": "Second Protein",
        "search_a": "First protein search term",
        "search_b": "Second protein search term",
        "find_a": "Search First Protein",
        "find_b": "Search Second Protein",
        "choose_a": "Select First Protein",
        "choose_b": "Select Second Protein",
        "run_compare": "Compare Sequences",
        "compare_result": "Comparison Results",
        "identity": "Sequence Identity",
        "aligned_length": "Aligned Sequence Length",
        "match_count": "Identical Amino Acids",
        "compare_note": "Sequence identity is the proportion of identical amino acids in a global alignment. It does not directly establish structural similarity or identical biological function.",
        "same_protein": "The same protein was selected twice. Please select two different proteins.",
        "translation_failed": "Automatic translation failed. The original English description is shown.",
        "empty_search": "Please enter a search term.",
        "no_results": "No results found. Try another protein or gene name.",
        "api_error": "Unable to connect to the external data service. Please try again later.",
        "footer": "BioTarget AI · For educational and research exploration",
        "loading": "Loading data...",
        "no_sequence": "There is insufficient amino acid sequence data for comparison.",
        "paper_year": "Publication year",
        "paper_authors": "Authors",
        "paper_journal": "Journal",
        "abstract": "View abstract",
        "navigation": "Navigation",
        "alignment": "View Sequence Alignment",
        "alignment_note": "The two aligned amino acid sequences.",
    },
}


def tr(key):
    language = st.session_state.get("language", "한국어")
    return TEXT[language].get(key, key)


# =========================================================
# 하늘색 연구실 디자인
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    :root {
        --sky: #55aee8;
        --sky-dark: #247dbb;
        --navy: #173b59;
        --muted: #627f95;
        --line: #d8eaf6;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 5% 0%, rgba(130,207,255,.16), transparent 30%),
            linear-gradient(180deg, #f4faff 0%, #ffffff 58%, #f5faff 100%);
        color: var(--navy);
    }

    [data-testid="stHeader"] {
        background: rgba(244,250,255,.85);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#e8f5ff 0%,#f5faff 100%);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        color: var(--navy);
    }

    .hero {
        padding: 2rem 2.1rem;
        border-radius: 25px;
        background: linear-gradient(125deg,#dff2ff 0%,#b8e1ff 52%,#edf8ff 100%);
        border: 1px solid #c5e6fb;
        box-shadow: 0 10px 35px rgba(66,144,194,.10);
        margin-bottom: 1.5rem;
    }

    .hero-kicker {
        color: #287eb7;
        font-weight: 800;
        font-size: .78rem;
        letter-spacing: .14em;
        margin-bottom: .6rem;
    }

    .hero h1 {
        color: #173b59;
        font-size: clamp(1.65rem,3vw,2.35rem);
        line-height: 1.25;
        font-weight: 800;
        margin: 0 0 .8rem;
    }

    .hero p {
        color: #426780;
        font-size: 1rem;
        line-height: 1.8;
        margin: 0;
    }

    .info-card {
        background: white;
        border: 1px solid #d8eaf6;
        border-radius: 18px;
        padding: 1.2rem 1.25rem;
        min-height: 150px;
        box-shadow: 0 6px 22px rgba(41,111,158,.055);
        margin-bottom: .7rem;
    }

    .info-card h3 {
        color: #173b59;
        font-size: 1.06rem;
        font-weight: 800;
        margin: 0 0 .55rem;
    }

    .info-card p {
        color: #627f95;
        font-size: .92rem;
        line-height: 1.65;
        margin: 0;
    }

    .metric-card {
        background: #f1f9ff;
        border: 1px solid #d7ecfa;
        border-radius: 14px;
        padding: .9rem 1rem;
        min-height: 88px;
        margin-bottom: .4rem;
    }

    .metric-label {
        color: #627f95;
        font-size: .82rem;
        margin-bottom: .35rem;
    }

    .metric-value {
        color: #173b59;
        font-size: 1.1rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .paper-card {
        background: white;
        border: 1px solid #d8eaf6;
        border-radius: 15px;
        padding: 1rem 1.15rem;
        margin: .65rem 0;
    }

    .paper-title {
        color: #176fa8;
        font-weight: 700;
        font-size: 1rem;
        line-height: 1.55;
        margin-bottom: .45rem;
    }

    .paper-meta {
        color: #627f95;
        font-size: .83rem;
        line-height: 1.6;
    }

    .footer {
        text-align: center;
        color: #7993a6;
        font-size: .8rem;
        padding: 2rem 0 1rem;
    }

    div.stButton > button, div.stFormSubmitButton > button {
        border-radius: 12px;
        border: 1px solid #a8d7f5;
        background: linear-gradient(135deg,#4aa8e6,#328bc9);
        color: white;
        font-weight: 700;
        min-height: 2.65rem;
    }

    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background: linear-gradient(135deg,#328bc9,#247bb6);
        border-color: #247bb6;
        color: white;
    }

    [data-testid="stExpander"] {
        border: 1px solid #d8eaf6;
        border-radius: 13px;
        background: rgba(255,255,255,.8);
    }

    hr {
        border-color: #d8eaf6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# UniProt 단백질 검색
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def uniprot_search(query, limit=10):
    query = query.strip()
    if not query:
        return []

    params = {
        "query": query,
        "format": "json",
        "size": limit,
        "fields": (
            "accession,id,protein_name,gene_names,organism_name,length"
        ),
    }

    try:
        response = requests.get(
            f"{UNIPROT_API}/uniprotkb/search",
            params=params,
            timeout=25,
            headers={"User-Agent": "BioTargetAI/1.0"},
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    results = []

    for item in data.get("results", []):
        accession = item.get("primaryAccession", "")
        if not accession:
            continue

        description = (
            item.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", "")
        )

        if not description:
            submissions = item.get("proteinDescription", {}).get(
                "submissionNames", []
            )
            if submissions:
                description = submissions[0].get(
                    "fullName", {}
                ).get("value", "")

        genes = item.get("genes", [])
        gene_name = ""
        if genes:
            gene_name = genes[0].get(
                "geneName", {}
            ).get("value", "")

        results.append({
            "accession": accession,
            "id": item.get("uniProtkbId", ""),
            "name": description or item.get("uniProtkbId", accession),
            "gene": gene_name,
            "organism": item.get("organism", {}).get(
                "scientificName", ""
            ),
            "length": item.get("sequence", {}).get("length", ""),
            "url": f"https://www.uniprot.org/uniprotkb/{accession}/entry",
        })

    return results


@st.cache_data(ttl=3600, show_spinner=False)
def uniprot_detail(accession):
    if not accession:
        return None

    try:
        response = requests.get(
            f"{UNIPROT_API}/uniprotkb/{quote(accession, safe='')}.json",
            timeout=25,
            headers={"User-Agent": "BioTargetAI/1.0"},
        )
        response.raise_for_status()
        item = response.json()
    except (requests.RequestException, ValueError):
        return None

    description = (
        item.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "")
    )

    if not description:
        submissions = item.get("proteinDescription", {}).get(
            "submissionNames", []
        )
        if submissions:
            description = submissions[0].get(
                "fullName", {}
            ).get("value", "")

    genes = item.get("genes", [])
    gene_name = ""
    if genes:
        gene_name = genes[0].get(
            "geneName", {}
        ).get("value", "")

    functions = []
    for comment in item.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            for entry in comment.get("texts", []):
                value = entry.get("value", "").strip()
                if value and value not in functions:
                    functions.append(value)

    sequence = item.get("sequence", {}).get("value", "")

    return {
        "accession": accession,
        "id": item.get("uniProtkbId", ""),
        "name": description or item.get("uniProtkbId", accession),
        "gene": gene_name,
        "organism": item.get("organism", {}).get(
            "scientificName", ""
        ),
        "sequence": sequence,
        "length": item.get("sequence", {}).get(
            "length", len(sequence)
        ),
        "function": " ".join(functions).strip(),
        "url": f"https://www.uniprot.org/uniprotkb/{accession}/entry",
    }


# =========================================================
# 단백질 기능 자동 번역
# =========================================================
@st.cache_data(ttl=86400, show_spinner=False)
def translate_function_to_korean(text):
    if not text or not text.strip():
        return ""

    try:
        translated = GoogleTranslator(
            source="auto",
            target="ko",
        ).translate(text[:4500])
        if translated and translated.strip():
            return translated.strip()
    except Exception:
        pass

    try:
        translated = MyMemoryTranslator(
            source="en-GB",
            target="ko-KR",
        ).translate(text[:4500])
        if translated and translated.strip():
            return translated.strip()
    except Exception:
        pass

    return text


def display_function(function_text):
    if not function_text:
        st.info(tr("no_function"))
        return

    if st.session_state["language"] == "English":
        st.write(function_text)
        return

    translated = translate_function_to_korean(function_text)

    if translated == function_text:
        st.warning(tr("translation_failed"))
        st.write(function_text)
    else:
        st.write(translated)


# =========================================================
# Europe PMC 논문 검색
# =========================================================
@st.cache_data(ttl=1800, show_spinner=False)
def search_papers(query, limit=8):
    if not query or not query.strip():
        return []

    params = {
        "query": query.strip(),
        "format": "json",
        "pageSize": limit,
        "resultType": "core",
        "sort": "RELEVANCE",
    }

    try:
        response = requests.get(
            f"{EUROPE_PMC_API}/search",
            params=params,
            timeout=25,
            headers={"User-Agent": "BioTargetAI/1.0"},
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    papers = []

    for item in data.get("resultList", {}).get("result", []):
        title = item.get("title", "").strip()
        if not title:
            continue

        pmcid = item.get("pmcid", "")
        pmid = item.get("pmid", "")
        doi = item.get("doi", "")

        if pmcid:
            url = f"https://europepmc.org/articles/{pmcid}"
        elif pmid:
            url = f"https://europepmc.org/article/MED/{pmid}"
        elif doi:
            url = f"https://doi.org/{doi}"
        else:
            url = (
                "https://europepmc.org/search?query="
                + quote(query.strip())
            )

        papers.append({
            "title": title,
            "authors": item.get("authorString", ""),
            "journal": item.get("journalTitle", ""),
            "year": item.get("pubYear", ""),
            "abstract": item.get("abstractText", ""),
            "url": url,
        })

    return papers


def render_papers(papers):
    if not papers:
        st.info(tr("no_papers"))
        return

    st.caption(f"{tr('paper_count')}: {len(papers)}")

    for paper in papers:
        title = html.escape(paper.get("title", ""))
        authors = html.escape(paper.get("authors", "") or "—")
        journal = html.escape(paper.get("journal", "") or "—")
        year = html.escape(str(paper.get("year", "") or "—"))
        url = html.escape(paper.get("url", "#"), quote=True)

        st.markdown(
            f"""
            <div class="paper-card">
                <div class="paper-title">{title}</div>
                <div class="paper-meta">
                    {tr("paper_year")}: {year}<br>
                    {tr("paper_journal")}: {journal}<br>
                    {tr("paper_authors")}: {authors}
                </div>
                <div style="margin-top:.7rem">
                    <a href="{url}" target="_blank"
                       style="color:#247dbb;font-weight:700;text-decoration:none">
                       ↗ {tr("paper_open")}
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        abstract = paper.get("abstract", "")
        if abstract:
            with st.expander(tr("abstract")):
                st.write(abstract)


# =========================================================
# 공통 UI
# =========================================================
def render_hero(title, description, kicker="BIOTARGET AI"):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">{html.escape(kicker)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def protein_label(protein):
    parts = [protein.get("name", "Unknown protein")]
    if protein.get("gene"):
        parts.append(f"Gene: {protein['gene']}")
    parts.append(protein.get("accession", ""))
    return " · ".join(part for part in parts if part)


def render_protein_details(protein, detail=None):
    if detail is None:
        detail = uniprot_detail(protein.get("accession", ""))

    if not detail:
        st.error(tr("api_error"))
        return None

    st.markdown(f"### {tr('details')}: {detail.get('name', '')}")

    columns = st.columns(4)
    metrics = [
        (tr("accession"), detail.get("accession", "—")),
        (tr("gene"), detail.get("gene", "") or "—"),
        (tr("organism"), detail.get("organism", "") or "—"),
        (tr("length"), detail.get("length", "—")),
    ]

    for column, (label, value) in zip(columns, metrics):
        with column:
            render_metric(label, value)

    st.markdown(f"#### 🧬 {tr('function')}")
    display_function(detail.get("function", ""))

    with st.expander(tr("show_sequence")):
        sequence = detail.get("sequence", "")
        if sequence:
            st.code(
                "\n".join(
                    sequence[i:i + 60]
                    for i in range(0, len(sequence), 60)
                ),
                language=None,
            )
        else:
            st.info(tr("no_sequence"))

    st.markdown(
        f"[{tr('uniprot_link')}]({detail.get('url', protein.get('url', '#'))})"
    )

    return detail


# =========================================================
# 홈 화면
# =========================================================
def home_page():
    render_hero(
        tr("hero_title"),
        tr("hero_desc"),
        "BIOLOGY × DATA × DISCOVERY",
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            f"""
            <div class="info-card">
                <h3>🧬 {tr("home_search")}</h3>
                <p>{tr("home_search_desc")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 홈 화면 버튼을 누르면 검색 페이지로 이동
        if st.button(
            tr("start_search"),
            key="home_go_search",
            use_container_width=True,
        ):
            st.session_state["page"] = "search"
            st.rerun()

    with col2:
        st.markdown(
            f"""
            <div class="info-card">
                <h3>⚖️ {tr("home_compare")}</h3>
                <p>{tr("home_compare_desc")}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 홈 화면 버튼을 누르면 비교 페이지로 이동
        if st.button(
            tr("start_compare"),
            key="home_go_compare",
            use_container_width=True,
        ):
            st.session_state["page"] = "compare"
            st.rerun()

    st.markdown("---")
    st.markdown(f"### 📚 {tr('home_papers')}")
    st.markdown(
        f'<p style="color:#627f95">{html.escape(tr("home_papers_desc"))}</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="info-card">
            <h3>🔬 UniProt + Europe PMC</h3>
            <p>
                UniProt protein records, amino acid sequences, functional
                annotations, and Europe PMC research articles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="footer">{html.escape(tr("footer"))}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 단백질 검색 화면
# =========================================================
def protein_search_page():
    render_hero(
        tr("search_title"),
        tr("search_desc"),
        "PROTEIN EXPLORER",
    )

    with st.form("protein_search_form", clear_on_submit=False):
        query = st.text_input(
            tr("protein_input"),
            placeholder=tr("protein_placeholder"),
            key="protein_query_input",
        )
        submitted = st.form_submit_button(
            tr("search_button"),
            use_container_width=True,
        )

    if submitted:
        if not query.strip():
            st.warning(tr("empty_search"))
        else:
            with st.spinner(tr("loading")):
                results = uniprot_search(query)

            st.session_state["protein_search_results"] = results
            st.session_state["protein_search_query"] = query.strip()
            st.session_state.pop("protein_detail_saved", None)
            st.session_state.pop("protein_papers_saved", None)

    results = st.session_state.get("protein_search_results", [])

    if results:
        st.markdown(f"### {tr('search_results')} ({len(results)})")

        selected_index = st.selectbox(
            tr("select_protein"),
            options=list(range(len(results))),
            format_func=lambda i: protein_label(results[i]),
            key="protein_search_selected",
        )

        selected = results[selected_index]
        accession = selected.get("accession", "")

        saved_detail = st.session_state.get("protein_detail_saved")

        if not saved_detail or saved_detail.get("accession") != accession:
            with st.spinner(tr("loading")):
                detail = uniprot_detail(accession)

            if detail:
                st.session_state["protein_detail_saved"] = detail
                st.session_state.pop("protein_papers_saved", None)
            else:
                st.error(tr("api_error"))
                detail = None
        else:
            detail = saved_detail

        if detail:
            render_protein_details(selected, detail)

            st.markdown("---")
            st.markdown(f"### 📚 {tr('papers')}")
            st.markdown(
                f'<p style="color:#627f95">{html.escape(tr("papers_desc"))}</p>',
                unsafe_allow_html=True,
            )

            default_query = (
                detail.get("name", "")
                or detail.get("gene", "")
                or accession
            )

            with st.form("protein_paper_form"):
                paper_query = st.text_input(
                    tr("paper_keyword"),
                    value=default_query,
                    placeholder=tr("paper_placeholder"),
                    key="protein_paper_query",
                )
                paper_submitted = st.form_submit_button(
                    tr("paper_button"),
                    use_container_width=True,
                )

            if paper_submitted:
                if not paper_query.strip():
                    st.warning(tr("empty_search"))
                else:
                    with st.spinner(tr("loading")):
                        papers = search_papers(paper_query)

                    st.session_state["protein_papers_saved"] = {
                        "query": paper_query.strip(),
                        "papers": papers,
                        "accession": accession,
                    }

            saved_papers = st.session_state.get("protein_papers_saved")

            if saved_papers and saved_papers.get("accession") == accession:
                render_papers(saved_papers.get("papers", []))

    elif "protein_search_results" in st.session_state:
        st.info(tr("no_results"))

    st.markdown(
        f'<div class="footer">{html.escape(tr("footer"))}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 서열 일치도 계산
# =========================================================
def calculate_sequence_identity(seq_a, seq_b):
    seq_a = re.sub(r"\s+", "", seq_a or "").upper()
    seq_b = re.sub(r"\s+", "", seq_b or "").upper()

    if not seq_a or not seq_b:
        return None

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    try:
        alignment = aligner.align(seq_a, seq_b)[0]
        aligned_a = str(alignment[0])
        aligned_b = str(alignment[1])

        columns = min(len(aligned_a), len(aligned_b))
        if columns == 0:
            return None

        matches = sum(
            1 for a, b in zip(aligned_a, aligned_b)
            if a == b and a != "-" and b != "-"
        )

        return {
            "identity": matches / columns * 100,
            "matches": matches,
            "columns": columns,
            "aligned_a": aligned_a,
            "aligned_b": aligned_b,
        }
    except Exception:
        return None


# =========================================================
# 단백질 비교 화면
# =========================================================
def search_comparison_proteins(query, state_key):
    if not query.strip():
        st.warning(tr("empty_search"))
        st.session_state[state_key] = []
        return

    with st.spinner(tr("loading")):
        results = uniprot_search(query)

    st.session_state[state_key] = results

    if not results:
        st.info(tr("no_results"))


def render_comparison_protein(title, detail):
    st.markdown(f"### {title}")

    if not detail:
        st.error(tr("api_error"))
        return

    columns = st.columns(2)

    with columns[0]:
        render_metric(tr("accession"), detail.get("accession", "—"))

    with columns[1]:
        render_metric(tr("length"), detail.get("length", "—"))

    st.markdown(f"**{tr('function')}**")
    display_function(detail.get("function", ""))

    with st.expander(tr("show_sequence")):
        sequence = detail.get("sequence", "")
        if sequence:
            st.code(
                "\n".join(
                    sequence[i:i + 60]
                    for i in range(0, len(sequence), 60)
                ),
                language=None,
            )
        else:
            st.info(tr("no_sequence"))


def protein_comparison_page():
    render_hero(
        tr("compare_title"),
        tr("compare_desc"),
        "SEQUENCE COMPARISON",
    )

    col_a, col_b = st.columns(2, gap="large")

    with col_a:
        st.markdown(f"### 🧬 {tr('protein_a')}")

        with st.form("compare_form_a"):
            query_a = st.text_input(
                tr("search_a"),
                placeholder=tr("protein_placeholder"),
                key="compare_query_a",
            )
            submitted_a = st.form_submit_button(
                tr("find_a"),
                use_container_width=True,
            )

        if submitted_a:
            search_comparison_proteins(
                query_a,
                "compare_results_a",
            )

    with col_b:
        st.markdown(f"### 🧬 {tr('protein_b')}")

        with st.form("compare_form_b"):
            query_b = st.text_input(
                tr("search_b"),
                placeholder=tr("protein_placeholder"),
                key="compare_query_b",
            )
            submitted_b = st.form_submit_button(
                tr("find_b"),
                use_container_width=True,
            )

        if submitted_b:
            search_comparison_proteins(
                query_b,
                "compare_results_b",
            )

    results_a = st.session_state.get("compare_results_a", [])
    results_b = st.session_state.get("compare_results_b", [])

    st.markdown("---")

    select_col_a, select_col_b = st.columns(2, gap="large")
    selected_a = None
    selected_b = None

    with select_col_a:
        if results_a:
            index_a = st.selectbox(
                tr("choose_a"),
                options=list(range(len(results_a))),
                format_func=lambda i: protein_label(results_a[i]),
                key="compare_selected_a",
            )
            selected_a = results_a[index_a]

    with select_col_b:
        if results_b:
            index_b = st.selectbox(
                tr("choose_b"),
                options=list(range(len(results_b))),
                format_func=lambda i: protein_label(results_b[i]),
                key="compare_selected_b",
            )
            selected_b = results_b[index_b]

    if selected_a and selected_b:
        if st.button(
            tr("run_compare"),
            key="run_protein_comparison",
            use_container_width=True,
        ):
            accession_a = selected_a.get("accession", "")
            accession_b = selected_b.get("accession", "")

            if accession_a == accession_b:
                st.warning(tr("same_protein"))
            else:
                with st.spinner(tr("loading")):
                    detail_a = uniprot_detail(accession_a)
                    detail_b = uniprot_detail(accession_b)

                if not detail_a or not detail_b:
                    st.error(tr("api_error"))
                else:
                    alignment = calculate_sequence_identity(
                        detail_a.get("sequence", ""),
                        detail_b.get("sequence", ""),
                    )

                    if not alignment:
                        st.warning(tr("no_sequence"))
                    else:
                        st.session_state["comparison_result"] = {
                            "detail_a": detail_a,
                            "detail_b": detail_b,
                            "alignment": alignment,
                        }

    saved = st.session_state.get("comparison_result")

    if saved:
        detail_a = saved["detail_a"]
        detail_b = saved["detail_b"]
        alignment = saved["alignment"]

        st.markdown("---")
        st.markdown(f"## {tr('compare_result')}")

        metric1, metric2, metric3 = st.columns(3)

        with metric1:
            render_metric(
                tr("identity"),
                f"{alignment['identity']:.2f}%",
            )

        with metric2:
            render_metric(
                tr("match_count"),
                alignment["matches"],
            )

        with metric3:
            render_metric(
                tr("aligned_length"),
                alignment["columns"],
            )

        st.progress(
            min(max(alignment["identity"] / 100, 0.0), 1.0)
        )

        st.info(tr("compare_note"))

        st.markdown("---")
        detail_col_a, detail_col_b = st.columns(2, gap="large")

        with detail_col_a:
            render_comparison_protein(tr("protein_a"), detail_a)

        with detail_col_b:
            render_comparison_protein(tr("protein_b"), detail_b)

        with st.expander(tr("alignment")):
            st.caption(tr("alignment_note"))

            aligned_a = alignment["aligned_a"]
            aligned_b = alignment["aligned_b"]
            width = 60

            for start in range(0, len(aligned_a), width):
                end = start + width
                st.code(
                    f"A: {aligned_a[start:end]}\n"
                    f"B: {aligned_b[start:end]}",
                    language=None,
                )

    st.markdown(
        f'<div class="footer">{html.escape(tr("footer"))}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 세션 상태 초기화
# =========================================================
if "language" not in st.session_state:
    st.session_state["language"] = "한국어"

if "page" not in st.session_state:
    st.session_state["page"] = "home"


# =========================================================
# 사이드바: 언어 전환 및 페이지 이동
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding:.6rem 0 1rem">
            <div style="font-size:2rem">🧬</div>
            <div style="font-size:1.45rem;font-weight:800;color:#173b59">
                BioTarget AI
            </div>
            <div style="font-size:.78rem;color:#627f95">
                Protein Research Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    language_choice = st.radio(
        tr("language"),
        options=["한국어", "English"],
        index=0 if st.session_state["language"] == "한국어" else 1,
        key="language_selector",
        horizontal=True,
    )

    if language_choice != st.session_state["language"]:
        st.session_state["language"] = language_choice
        st.rerun()

    st.markdown("---")

    page_keys = ["home", "search", "compare"]
    page_labels = [
        tr("home"),
        tr("search"),
        tr("compare"),
    ]

    current_page = st.session_state.get("page", "home")
    current_index = (
        page_keys.index(current_page)
        if current_page in page_keys
        else 0
    )

    selected_label = st.radio(
        tr("navigation"),
        options=page_labels,
        index=current_index,
        key=f"page_selector_{st.session_state['language']}",
    )

    selected_index = page_labels.index(selected_label)
    selected_page = page_keys[selected_index]

    if selected_page != st.session_state["page"]:
        st.session_state["page"] = selected_page
        st.rerun()

    st.markdown("---")
    st.caption(tr("subtitle"))


# =========================================================
# 페이지 라우팅
# 홈 버튼과 사이드바 메뉴가 동일한 페이지 상태를 사용함
# =========================================================
if st.session_state["page"] == "home":
    home_page()

elif st.session_state["page"] == "search":
    protein_search_page()

elif st.session_state["page"] == "compare":
    protein_comparison_page()
