
import streamlit as st
import requests
import html
import re
from urllib.parse import quote
from deep_translator import GoogleTranslator, MyMemoryTranslator
from Bio.Align import PairwiseAligner

# =========================================================
# 설정
# =========================================================
st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide",
)

UNIPROT_API = "https://rest.uniprot.org"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest"

TEXT = {
    "한국어": {
        "subtitle": "AI 기반 신약 후보 탐색 및 표적 단백질 분석",
        "language": "🌐 언어 / Language",
        "navigation": "메뉴",
        "home": "🏠 홈",
        "search": "🔎 단백질 검색",
        "compare": "⚖️ 단백질 비교",
        "hero_title": "생명과학 연구를 위한 단백질 탐색 플랫폼",
        "hero_desc": "단백질 기능, 아미노산 서열, 관련 연구 논문을 탐색하세요.",
        "home_search": "단백질 탐색",
        "home_search_desc": "단백질명이나 유전자명으로 기능과 서열 정보를 찾아보세요.",
        "home_compare": "단백질 비교",
        "home_compare_desc": "두 단백질의 아미노산 서열과 일치도를 비교하세요.",
        "home_papers": "연구 논문 탐색",
        "home_papers_desc": "관심 있는 단백질과 관련된 논문을 찾아보세요.",
        "start_search": "단백질 검색하기",
        "start_compare": "단백질 비교하기",
        "search_title": "단백질 검색",
        "search_desc": "단백질명 또는 유전자명을 입력하세요.",
        "protein_input": "단백질명 또는 유전자명",
        "protein_placeholder": "예: insulin, TP53, hemoglobin",
        "search_button": "검색",
        "search_results": "검색 결과",
        "select_protein": "상세 정보를 확인할 단백질 선택",
        "details": "단백질 상세 정보",
        "accession": "UniProt accession",
        "gene": "유전자명",
        "organism": "생물종",
        "length": "아미노산 길이",
        "function": "단백질 기능",
        "no_function": "등록된 기능 설명이 없습니다.",
        "show_sequence": "아미노산 서열 보기",
        "uniprot_link": "UniProt에서 자세히 보기",
        "papers": "관련 연구 논문",
        "papers_desc": "선택한 단백질의 이름과 유전자명을 바탕으로 관련 논문을 자동으로 표시합니다.",
        "paper_keyword": "논문 검색어",
        "paper_button": "관련 논문 검색",
        "paper_placeholder": "단백질명 또는 연구 주제",
        "paper_count": "검색 결과",
        "paper_open": "논문 페이지 열기",
        "no_papers": "논문을 찾지 못했습니다. 다른 검색어를 입력해 보세요.",
        "compare_title": "단백질 비교",
        "compare_desc": "두 단백질을 이름으로 검색하고 각각 선택하세요.",
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
        "compare_note": "일치도는 전역 정렬에서 동일한 아미노산이 차지하는 비율입니다. 단백질의 구조나 기능이 동일하다는 뜻은 아닙니다.",
        "same_protein": "동일한 단백질입니다. 서로 다른 단백질을 선택하세요.",
        "translation_failed": "번역에 실패하여 영어 원문을 표시합니다.",
        "empty_search": "검색어를 입력해 주세요.",
        "no_results": "검색 결과가 없습니다. 다른 이름을 입력해 보세요.",
        "api_error": "외부 데이터 서비스에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.",
        "footer": "BioTarget AI · 교육 및 연구 탐색용 도구",
        "loading": "데이터를 불러오는 중...",
        "no_sequence": "비교할 아미노산 서열이 없습니다.",
        "paper_year": "발행 연도",
        "paper_authors": "저자",
        "paper_journal": "학술지",
        "abstract": "초록 보기",
        "alignment": "서열 정렬 결과 보기",
    },
    "English": {
        "subtitle": "AI-Assisted Drug Discovery & Target Protein Analysis",
        "language": "🌐 Language / 언어",
        "navigation": "Navigation",
        "home": "🏠 Home",
        "search": "🔎 Protein Search",
        "compare": "⚖️ Protein Comparison",
        "hero_title": "A Protein Exploration Platform for Life Science Research",
        "hero_desc": "Explore protein functions, amino acid sequences, and related research papers.",
        "home_search": "Protein Exploration",
        "home_search_desc": "Find protein functions and sequences by protein or gene name.",
        "home_compare": "Protein Comparison",
        "home_compare_desc": "Compare amino acid sequences and sequence identity.",
        "home_papers": "Research Papers",
        "home_papers_desc": "Find papers related to your protein of interest.",
        "start_search": "Search Proteins",
        "start_compare": "Compare Proteins",
        "search_title": "Protein Search",
        "search_desc": "Enter a protein name or gene name.",
        "protein_input": "Protein name or gene name",
        "protein_placeholder": "e.g. insulin, TP53, hemoglobin",
        "search_button": "Search",
        "search_results": "Search Results",
        "select_protein": "Select a protein to view details",
        "details": "Protein Details",
        "accession": "UniProt accession",
        "gene": "Gene",
        "organism": "Organism",
        "length": "Sequence length",
        "function": "Protein Function",
        "no_function": "No function description is available.",
        "show_sequence": "Show Amino Acid Sequence",
        "uniprot_link": "View on UniProt",
        "papers": "Related Research Papers",
        "papers_desc": "Related papers are displayed automatically using the selected protein and gene names.",
        "paper_keyword": "Paper search term",
        "paper_button": "Search Related Papers",
        "paper_placeholder": "Protein name or research topic",
        "paper_count": "Results",
        "paper_open": "Open Paper",
        "no_papers": "No papers found. Try another search term.",
        "compare_title": "Protein Comparison",
        "compare_desc": "Search by name and select a protein for each field.",
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
        "compare_note": "Identity is the proportion of identical amino acids in a global alignment. It does not establish identical structure or function.",
        "same_protein": "The same protein was selected twice. Choose different proteins.",
        "translation_failed": "Translation failed. The original English text is shown.",
        "empty_search": "Please enter a search term.",
        "no_results": "No results found. Try another name.",
        "api_error": "Unable to connect to the external data service. Please try again later.",
        "footer": "BioTarget AI · For educational and research exploration",
        "loading": "Loading data...",
        "no_sequence": "No amino acid sequence is available for comparison.",
        "paper_year": "Year",
        "paper_authors": "Authors",
        "paper_journal": "Journal",
        "abstract": "View abstract",
        "alignment": "View Sequence Alignment",
    },
}


def tr(key):
    return TEXT[st.session_state.get("language", "한국어")].get(key, key)


# =========================================================
# 페이지 이동: 모든 버튼과 메뉴가 같은 상태 사용
# =========================================================
PAGE_KEYS = ["home", "search", "compare"]


def go_to_page(page):
    """홈 버튼에서 호출. 사이드바 선택 상태도 함께 변경."""
    st.session_state["page"] = page
    st.session_state["nav_page"] = page


def sync_page_from_navigation():
    """사이드바 메뉴 선택을 실제 페이지 상태에 반영."""
    st.session_state["page"] = st.session_state["nav_page"]


if "language" not in st.session_state:
    st.session_state["language"] = "한국어"

if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "nav_page" not in st.session_state:
    st.session_state["nav_page"] = st.session_state["page"]


# =========================================================
# 디자인
# =========================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 5% 0%, rgba(130,207,255,.16), transparent 30%),
            linear-gradient(180deg,#f4faff 0%,#fff 58%,#f5faff 100%);
        color: #173b59;
    }

    [data-testid="stHeader"] {
        background: rgba(244,250,255,.85);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg,#e8f5ff,#f5faff);
        border-right: 1px solid #d8eaf6;
    }

    [data-testid="stSidebar"] * {
        color: #173b59;
    }

    .hero {
        padding: 2rem;
        border-radius: 25px;
        background: linear-gradient(125deg,#dff2ff,#b8e1ff 52%,#edf8ff);
        border: 1px solid #c5e6fb;
        box-shadow: 0 10px 35px rgba(66,144,194,.10);
        margin-bottom: 1.5rem;
    }

    .hero-kicker {
        color: #287eb7;
        font-weight: 800;
        font-size: .78rem;
        letter-spacing: .12em;
        margin-bottom: .6rem;
    }

    .hero h1 {
        color: #173b59;
        font-size: clamp(1.65rem,3vw,2.35rem);
        line-height: 1.3;
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
        background: #fff;
        border: 1px solid #d8eaf6;
        border-radius: 18px;
        padding: 1.2rem;
        min-height: 145px;
        box-shadow: 0 6px 22px rgba(41,111,158,.055);
        margin-bottom: .7rem;
    }

    .info-card h3 {
        color: #173b59;
        font-size: 1.05rem;
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
        padding: .9rem;
        min-height: 85px;
        margin-bottom: .4rem;
    }

    .metric-label {
        color: #627f95;
        font-size: .82rem;
        margin-bottom: .35rem;
    }

    .metric-value {
        color: #173b59;
        font-size: 1.08rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .paper-card {
        background: white;
        border: 1px solid #d8eaf6;
        border-radius: 15px;
        padding: 1rem;
        margin: .65rem 0;
    }

    .paper-title {
        color: #176fa8;
        font-weight: 700;
        line-height: 1.55;
        margin-bottom: .45rem;
    }

    .paper-meta {
        color: #627f95;
        font-size: .83rem;
        line-height: 1.7;
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
        min-height: 2.7rem;
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
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# UniProt API
# =========================================================
@st.cache_data(ttl=3600, show_spinner=False)
def uniprot_search(query, limit=10):
    if not query or not query.strip():
        return []

    params = {
        "query": query.strip(),
        "format": "json",
        "size": limit,
        "fields": "accession,id,protein_name,gene_names,organism_name,length",
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
        gene = genes[0].get("geneName", {}).get("value", "") if genes else ""

        results.append({
            "accession": accession,
            "id": item.get("uniProtkbId", ""),
            "name": description or item.get("uniProtkbId", accession),
            "gene": gene,
            "organism": item.get("organism", {}).get("scientificName", ""),
            "length": item.get("sequence", {}).get("length", ""),
            "url": f"https://www.uniprot.org/uniprotkb/{accession}/entry",
        })

    return results


@st.cache_data(ttl=3600, show_spinner=False)
def uniprot_detail(accession):
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
    gene = genes[0].get("geneName", {}).get("value", "") if genes else ""

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
        "gene": gene,
        "organism": item.get("organism", {}).get("scientificName", ""),
        "sequence": sequence,
        "length": item.get("sequence", {}).get("length", len(sequence)),
        "function": " ".join(functions).strip(),
        "url": f"https://www.uniprot.org/uniprotkb/{accession}/entry",
    }


# =========================================================
# 기능 설명 번역
# =========================================================
@st.cache_data(ttl=86400, show_spinner=False)
def translate_function_to_korean(text):
    if not text:
        return ""

    try:
        result = GoogleTranslator(
            source="auto", target="ko"
        ).translate(text[:4500])
        if result:
            return result
    except Exception:
        pass

    try:
        result = MyMemoryTranslator(
            source="en-GB", target="ko-KR"
        ).translate(text[:4500])
        if result:
            return result
    except Exception:
        pass

    return text


def display_function(function_text):
    if not function_text:
        st.info(tr("no_function"))
        return

    if st.session_state["language"] == "English":
        st.write(function_text)
    else:
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
    """Europe PMC의 일반 검색창과 같은 방식으로 단순 검색어를 전달합니다."""
    query = (query or "").strip()
    if not query:
        return []

    # 필드 지정, 따옴표, AND/OR 등을 임의로 덧붙이지 않습니다.
    # sort를 지정하지 않아 Europe PMC의 기본 관련도 순서를 사용합니다.
    params = {
        "query": query,
        "format": "json",
        "pageSize": max(1, min(int(limit), 25)),
        "resultType": "core",
    }

    try:
        response = requests.get(
            f"{EUROPE_PMC_API}/search",
            params=params,
            timeout=30,
            headers={"User-Agent": "BioTargetAI/1.0"},
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    result_list = data.get("resultList", {}).get("result", [])
    papers = []
    for item in result_list:
        title = (item.get("title") or "").strip()
        if not title:
            continue

        pmcid = (item.get("pmcid") or "").strip()
        pmid = (item.get("pmid") or "").strip()
        doi = (item.get("doi") or "").strip()

        if pmcid:
            url = f"https://europepmc.org/articles/{pmcid}"
        elif pmid:
            url = f"https://europepmc.org/article/MED/{pmid}"
        elif doi:
            url = f"https://doi.org/{doi}"
        else:
            url = "https://europepmc.org/search?query=" + quote(query, safe="")

        journal = item.get("journalTitle", "") or ""
        # core 응답에서는 journalTitle 대신 journalInfo 안에 저널명이 들어올 수도 있습니다.
        if not journal:
            journal = (
                item.get("journalInfo", {})
                .get("journal", {})
                .get("title", "")
            )

        papers.append({
            "title": title,
            "authors": item.get("authorString", "") or "",
            "journal": journal,
            "year": item.get("pubYear", "") or "",
            "abstract": item.get("abstractText", "") or "",
            "url": url,
            "paper_id": pmid or pmcid or doi or title.lower(),
        })

    return papers


@st.cache_data(ttl=1800, show_spinner=False)
def search_related_papers(gene, protein_name, limit=8):
    """유전자명과 단백질명을 각각 검색해 결과를 합치고 중복을 제거합니다."""
    queries = []
    for term in (gene, protein_name):
        term = (term or "").strip()
        if term and term.lower() not in [q.lower() for q in queries]:
            queries.append(term)

    combined = []
    seen = set()
    for query in queries:
        for paper in search_papers(query, limit=limit):
            key = paper.get("paper_id") or paper.get("title", "").strip().lower()
            if key and key not in seen:
                seen.add(key)
                combined.append(paper)
        if len(combined) >= limit:
            break

    return combined[:limit]


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

        if paper.get("abstract"):
            with st.expander(tr("abstract")):
                st.write(paper["abstract"])


# =========================================================
# 공통 화면 요소
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
        parts.append("Gene: " + protein["gene"])
    parts.append(protein.get("accession", ""))
    return " · ".join(x for x in parts if x)


def render_protein_details(protein):
    detail = uniprot_detail(protein.get("accession", ""))

    if not detail:
        st.error(tr("api_error"))
        return None

    st.markdown(f"### {tr('details')}: {detail['name']}")

    cols = st.columns(4)
    metrics = [
        (tr("accession"), detail["accession"]),
        (tr("gene"), detail["gene"] or "—"),
        (tr("organism"), detail["organism"] or "—"),
        (tr("length"), detail["length"]),
    ]

    for col, (label, value) in zip(cols, metrics):
        with col:
            render_metric(label, value)

    st.markdown(f"#### 🧬 {tr('function')}")
    display_function(detail["function"])

    with st.expander(tr("show_sequence")):
        sequence = detail["sequence"]
        if sequence:
            st.code(
                "\n".join(sequence[i:i + 60] for i in range(0, len(sequence), 60)),
                language=None,
            )
        else:
            st.info(tr("no_sequence"))

    st.markdown(f"[{tr('uniprot_link')}]({detail['url']})")
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

        st.button(
            tr("start_search"),
            key="home_go_search",
            use_container_width=True,
            on_click=go_to_page,
            args=("search",),
        )

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

        st.button(
            tr("start_compare"),
            key="home_go_compare",
            use_container_width=True,
            on_click=go_to_page,
            args=("compare",),
        )

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
            <p>Protein records, amino acid sequences, functional annotations, and research articles.</p>
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

    with st.form("protein_search_form"):
        query = st.text_input(
            tr("protein_input"),
            placeholder=tr("protein_placeholder"),
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
                st.session_state["protein_results"] = uniprot_search(query)
            st.session_state["protein_query"] = query.strip()
            st.session_state.pop("paper_results", None)

    results = st.session_state.get("protein_results", [])

    if results:
        st.markdown(f"### {tr('search_results')} ({len(results)})")

        selected_index = st.selectbox(
            tr("select_protein"),
            options=list(range(len(results))),
            format_func=lambda i: protein_label(results[i]),
            key="search_selected_index",
        )

        selected = results[selected_index]
        accession = selected["accession"]

        if st.session_state.get("current_detail_accession") != accession:
            st.session_state.pop("paper_results", None)
            st.session_state["current_detail_accession"] = accession

        detail = render_protein_details(selected)

        if detail:
            st.markdown("---")
            st.markdown(f"### 📚 {tr('papers')}")
            st.markdown(
                f'<p style="color:#627f95">{html.escape(tr("papers_desc"))}</p>',
                unsafe_allow_html=True,
            )

            # 선택된 단백질의 이름과 유전자명을 조합해 관련 논문을 자동 검색합니다.
            # accession이 바뀌었을 때만 다시 검색하며, search_papers의 캐시를 활용합니다.
            saved = st.session_state.get("paper_results")
            if not saved or saved.get("accession") != accession:
                gene_name = detail.get("gene", "")
                protein_name = detail.get("name", "")
                if gene_name or protein_name:
                    with st.spinner(tr("loading")):
                        papers = search_related_papers(
                            gene_name,
                            protein_name,
                            limit=8,
                        )
                    st.session_state["paper_results"] = {
                        "accession": accession,
                        "query": gene_name or protein_name,
                        "papers": papers,
                    }
                else:
                    st.session_state["paper_results"] = {
                        "accession": accession,
                        "query": "",
                        "papers": [],
                    }

            saved = st.session_state.get("paper_results")
            if saved and saved.get("accession") == accession:
                render_papers(saved.get("papers", []))

    elif "protein_results" in st.session_state:
        st.info(tr("no_results"))

    st.markdown(
        f'<div class="footer">{html.escape(tr("footer"))}</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# 서열 정렬 및 일치도
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
        if not columns:
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
def search_comparison_proteins(query, key):
    if not query.strip():
        st.warning(tr("empty_search"))
        st.session_state[key] = []
        return

    with st.spinner(tr("loading")):
        st.session_state[key] = uniprot_search(query)

    if not st.session_state[key]:
        st.info(tr("no_results"))


def render_comparison_protein(title, detail):
    st.markdown(f"### {title}")

    if not detail:
        st.error(tr("api_error"))
        return

    cols = st.columns(2)
    with cols[0]:
        render_metric(tr("accession"), detail["accession"])
    with cols[1]:
        render_metric(tr("length"), detail["length"])

    st.markdown(f"**{tr('function')}**")
    display_function(detail["function"])

    with st.expander(tr("show_sequence")):
        sequence = detail["sequence"]
        if sequence:
            st.code(
                "\n".join(sequence[i:i + 60] for i in range(0, len(sequence), 60)),
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
            )
            submit_a = st.form_submit_button(
                tr("find_a"),
                use_container_width=True,
            )
        if submit_a:
            search_comparison_proteins(query_a, "compare_results_a")

    with col_b:
        st.markdown(f"### 🧬 {tr('protein_b')}")
        with st.form("compare_form_b"):
            query_b = st.text_input(
                tr("search_b"),
                placeholder=tr("protein_placeholder"),
            )
            submit_b = st.form_submit_button(
                tr("find_b"),
                use_container_width=True,
            )
        if submit_b:
            search_comparison_proteins(query_b, "compare_results_b")

    results_a = st.session_state.get("compare_results_a", [])
    results_b = st.session_state.get("compare_results_b", [])

    st.markdown("---")

    select_a, select_b = st.columns(2, gap="large")
    protein_a = None
    protein_b = None

    with select_a:
        if results_a:
            idx_a = st.selectbox(
                tr("choose_a"),
                options=list(range(len(results_a))),
                format_func=lambda i: protein_label(results_a[i]),
                key="comparison_choice_a",
            )
            protein_a = results_a[idx_a]

    with select_b:
        if results_b:
            idx_b = st.selectbox(
                tr("choose_b"),
                options=list(range(len(results_b))),
                format_func=lambda i: protein_label(results_b[i]),
                key="comparison_choice_b",
            )
            protein_b = results_b[idx_b]

    if protein_a and protein_b:
        st.button(
            tr("run_compare"),
            key="execute_comparison",
            use_container_width=True,
            on_click=run_comparison_callback,
            args=(protein_a["accession"], protein_b["accession"]),
        )

    result = st.session_state.get("comparison_result")

    if result:
        detail_a = result["detail_a"]
        detail_b = result["detail_b"]
        alignment = result["alignment"]

        st.markdown("---")
        st.markdown(f"## {tr('compare_result')}")

        c1, c2, c3 = st.columns(3)
        with c1:
            render_metric(tr("identity"), f"{alignment['identity']:.2f}%")
        with c2:
            render_metric(tr("match_count"), alignment["matches"])
        with c3:
            render_metric(tr("aligned_length"), alignment["columns"])

        st.progress(min(max(alignment["identity"] / 100, 0), 1))
        st.info(tr("compare_note"))

        left, right = st.columns(2, gap="large")
        with left:
            render_comparison_protein(tr("protein_a"), detail_a)
        with right:
            render_comparison_protein(tr("protein_b"), detail_b)

        with st.expander(tr("alignment")):
            width = 60
            for start in range(0, len(alignment["aligned_a"]), width):
                end = start + width
                st.code(
                    f"A: {alignment['aligned_a'][start:end]}\n"
                    f"B: {alignment['aligned_b'][start:end]}",
                    language=None,
                )

    st.markdown(
        f'<div class="footer">{html.escape(tr("footer"))}</div>',
        unsafe_allow_html=True,
    )


def run_comparison_callback(accession_a, accession_b):
    if accession_a == accession_b:
        st.session_state["comparison_error"] = "same"
        return

    detail_a = uniprot_detail(accession_a)
    detail_b = uniprot_detail(accession_b)

    if not detail_a or not detail_b:
        st.session_state["comparison_error"] = "api"
        return

    alignment = calculate_sequence_identity(
        detail_a["sequence"],
        detail_b["sequence"],
    )

    if not alignment:
        st.session_state["comparison_error"] = "sequence"
        return

    st.session_state["comparison_result"] = {
        "detail_a": detail_a,
        "detail_b": detail_b,
        "alignment": alignment,
    }
    st.session_state.pop("comparison_error", None)


# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div style="padding:.6rem 0 1rem">
            <div style="font-size:2rem">🧬</div>
            <div style="font-size:1.45rem;font-weight:800">BioTarget AI</div>
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

    # 라디오 위젯의 실제 값이 페이지 상태의 기준이 됨.
    # 홈 버튼도 nav_page를 변경하므로 두 이동 방식이 동기화됨.
    st.radio(
        tr("navigation"),
        options=PAGE_KEYS,
        format_func=lambda key: tr(key),
        key="nav_page",
        on_change=sync_page_from_navigation,
    )

    st.markdown("---")
    st.caption(tr("subtitle"))


# =========================================================
# 현재 페이지 표시
# =========================================================
# nav_page와 page를 매번 동기화해 화면이 이전 페이지로 돌아가는
# 문제를 방지함.
if st.session_state["page"] != st.session_state["nav_page"]:
    st.session_state["page"] = st.session_state["nav_page"]

current_page = st.session_state["page"]

if current_page == "home":
    home_page()
elif current_page == "search":
    protein_search_page()
elif current_page == "compare":
    protein_comparison_page()

# 비교 오류 메시지 표시
comparison_error = st.session_state.get("comparison_error")
if comparison_error == "same":
    st.warning(tr("same_protein"))
elif comparison_error == "api":
    st.error(tr("api_error"))
elif comparison_error == "sequence":
    st.warning(tr("no_sequence"))
