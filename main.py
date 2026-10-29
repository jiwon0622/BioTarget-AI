
import streamlit as st
import pandas as pd
import requests
from deep_translator import GoogleTranslator

st.set_page_config(
    page_title="BioTarget AI | Research Lab",
    page_icon="🧬",
    layout="wide"
)

# -----------------------------
# 언어 설정
# -----------------------------
if "language" not in st.session_state:
    st.session_state.language = "ko"

LANG = st.session_state.language

TEXT = {
    "ko": {
        "app_name": "BioTarget AI",
        "subtitle": "AI 기반 표적 단백질 분석 연구 플랫폼",
        "language": "🌐 English로 전환",
        "menu": "RESEARCH MENU",
        "home": "연구실 홈",
        "search": "단백질 검색",
        "compare": "단백질 비교",
        "explore": "신약 연구 탐색",
        "status": "시스템 상태",
        "online": "UniProt 데이터 연결 준비 완료",
        "hero_tag": "BIOINFORMATICS · PROTEIN RESEARCH",
        "hero_title": "단백질에서 시작하는\n신약 연구",
        "hero_desc": "단백질 정보를 검색하고, 특성을 비교하며,\n생명과학 데이터를 탐구해 보세요.",
        "search_title": "단백질 데이터 검색",
        "search_desc": "UniProt 데이터베이스에서 표적 단백질을 찾아보세요.",
        "query": "검색할 단백질 또는 유전자",
        "query_hint": "예: TP53, EGFR, insulin",
        "search_button": "단백질 검색",
        "results": "검색 결과",
        "no_results": "검색 결과가 없습니다. 검색어를 바꿔 보세요.",
        "gene": "유전자",
        "organism": "생물종",
        "length": "아미노산 길이",
        "function": "기능 설명",
        "accession": "UniProt ID",
        "sequence": "아미노산 서열",
        "open_uniprot": "UniProt 원본 데이터 열기",
        "compare_title": "표적 단백질 비교실",
        "compare_desc": "두 단백질의 기본 정보와 아미노산 서열을 비교하세요.",
        "protein_a": "단백질 A 검색어",
        "protein_b": "단백질 B 검색어",
        "search_a": "단백질 A 검색",
        "search_b": "단백질 B 검색",
        "select_a": "단백질 A 선택",
        "select_b": "단백질 B 선택",
        "comparison": "비교 결과",
        "property": "비교 항목",
        "name": "단백질 이름",
        "length_diff": "아미노산 길이 차이",
        "sequence_note": "서열 유사도 분석은 다음 단계에서 추가할 예정입니다.",
        "explore_title": "신약 연구 탐색실",
        "explore_desc": "단백질 정보와 생물학적 기능을 바탕으로 신약 연구 질문을 정리해 보세요.",
        "idea_title": "연구 질문 예시",
        "idea1": "암 관련 단백질의 기능은 무엇인가?",
        "idea2": "두 단백질의 서열 차이는 기능 차이와 어떤 관련이 있을까?",
        "idea3": "표적 단백질을 억제하면 세포 신호 전달에 어떤 변화가 생길까?",
        "notice": "교육·탐구용 플랫폼입니다. 분석 결과만으로 약물의 효과나 안전성을 판단할 수 없습니다.",
        "translating": "데이터를 불러오는 중...",
        "translate_error": "번역에 실패해 원문을 표시합니다.",
        "no_function": "등록된 기능 설명이 없습니다.",
        "home_caption": "BIOLOGY × CHEMISTRY × AI",
        "data_source": "데이터 출처: UniProt",
        "choose_first": "먼저 검색어를 입력하고 검색 결과를 선택하세요.",
        "search_error": "데이터를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.",
        "empty": "검색어를 입력해 주세요."
    },
    "en": {
        "app_name": "BioTarget AI",
        "subtitle": "AI-powered Target Protein Research Platform",
        "language": "🌐 Switch to Korean",
        "menu": "RESEARCH MENU",
        "home": "Research Home",
        "search": "Protein Search",
        "compare": "Protein Comparison",
        "explore": "Drug Discovery",
        "status": "SYSTEM STATUS",
        "online": "UniProt data connection ready",
        "hero_tag": "BIOINFORMATICS · PROTEIN RESEARCH",
        "hero_title": "Drug Discovery\nStarts with Proteins",
        "hero_desc": "Search protein records, compare properties,\nand explore biological data.",
        "search_title": "Protein Data Search",
        "search_desc": "Find target proteins in the UniProt database.",
        "query": "Protein or gene to search",
        "query_hint": "e.g. TP53, EGFR, insulin",
        "search_button": "Search Proteins",
        "results": "Search Results",
        "no_results": "No results found. Try a different query.",
        "gene": "Gene",
        "organism": "Organism",
        "length": "Amino Acid Length",
        "function": "Function",
        "accession": "UniProt ID",
        "sequence": "Amino Acid Sequence",
        "open_uniprot": "Open original UniProt record",
        "compare_title": "Target Protein Comparison Lab",
        "compare_desc": "Compare basic information and amino acid sequences of two proteins.",
        "protein_a": "Protein A search query",
        "protein_b": "Protein B search query",
        "search_a": "Search Protein A",
        "search_b": "Search Protein B",
        "select_a": "Select Protein A",
        "select_b": "Select Protein B",
        "comparison": "Comparison Results",
        "property": "Property",
        "name": "Protein Name",
        "length_diff": "Amino acid length difference",
        "sequence_note": "Sequence similarity analysis will be added in the next step.",
        "explore_title": "Drug Discovery Lab",
        "explore_desc": "Develop research questions using protein data and biological functions.",
        "idea_title": "Example Research Questions",
        "idea1": "What is the function of cancer-related proteins?",
        "idea2": "How might sequence differences relate to functional differences?",
        "idea3": "How could inhibiting a target protein affect cell signaling?",
        "notice": "For education and research exploration. These results alone cannot establish drug efficacy or safety.",
        "translating": "Loading data...",
        "translate_error": "Translation failed; showing the original text.",
        "no_function": "No function description available.",
        "home_caption": "BIOLOGY × CHEMISTRY × AI",
        "data_source": "Data source: UniProt",
        "choose_first": "Enter a query and select a search result first.",
        "search_error": "Unable to retrieve data. Please try again later.",
        "empty": "Please enter a search query."
    }
}


def t(key):
    return TEXT[LANG].get(key, key)


# -----------------------------
# 외부 데이터 번역
# 단백질 ID와 아미노산 서열은 번역하지 않음
# -----------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def translate_annotation(text, target_language):
    if not text or not text.strip():
        return text

    try:
        target = "ko" if target_language == "ko" else "en"
        return GoogleTranslator(
            source="auto",
            target=target
        ).translate(text)
    except Exception:
        return text


def display_annotation(text):
    if not text:
        return t("no_function")

    # UniProt 설명이 영어이면 한국어 모드에서 번역
    # 한국어 설명은 영어 모드에서 번역
    return translate_annotation(text, LANG)


# -----------------------------
# UniProt API
# -----------------------------
def extract_protein(entry):
    description = entry.get("proteinDescription", {})
    recommended = description.get("recommendedName", {})
    protein_name = recommended.get("fullName", {}).get("value")

    if not protein_name:
        alternatives = description.get("alternativeNames", [])
        if alternatives:
            protein_name = (
                alternatives[0].get("fullName", {}).get("value")
            )

    if not protein_name:
        submissions = description.get("submissionNames", [])
        if submissions:
            protein_name = (
                submissions[0].get("fullName", {}).get("value")
            )

    genes = entry.get("genes", [])
    gene_name = "N/A"
    if genes:
        gene_name = genes[0].get(
            "geneName", {}
        ).get("value", "N/A")

    organism = entry.get("organism", {}).get(
        "scientificName", "N/A"
    )

    sequence_data = entry.get("sequence", {})
    sequence = sequence_data.get("value", "")
    length = sequence_data.get("length", len(sequence))

    function_text = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            texts = []
            for item in comment.get("texts", []):
                value = item.get("value", "")
                if value:
                    texts.append(value)
            function_text = " ".join(texts)
            if function_text:
                break

    accession = entry.get("primaryAccession", "")

    return {
        "name": protein_name or accession,
        "gene": gene_name,
        "organism": organism,
        "length": length,
        "function": function_text,
        "accession": accession,
        "sequence": sequence,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}/entry"
    }


@st.cache_data(ttl=3600, show_spinner=False)
def search_proteins(query):
    response = requests.get(
        "https://rest.uniprot.org/uniprotkb/search",
        params={
            "query": query,
            "format": "json",
            "size": 10
        },
        timeout=25
    )
    response.raise_for_status()
    data = response.json()

    proteins = []
    for entry in data.get("results", []):
        protein = extract_protein(entry)
        if protein["accession"] and protein["sequence"]:
            proteins.append(protein)

    return proteins


def protein_label(protein):
    return (
        f'{protein["name"]} | {protein["gene"]} | '
        f'{protein["organism"]} | {protein["accession"]}'
    )


# -----------------------------
# 연구실 스타일 CSS
# -----------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(145deg, #f2faff 0%, #e8f5ff 48%, #f8fcff 100%);
        color: #183b56;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d9efff 0%, #eaf7ff 100%);
        border-right: 1px solid #c1e0f5;
    }

    [data-testid="stSidebar"] * {
        color: #183b56;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    .lab-topline {
        color: #4187b7;
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 2.5px;
        margin-bottom: 0.5rem;
    }

    .lab-hero {
        background: linear-gradient(120deg, #d9f0ff, #fafdff);
        border: 1px solid #b9ddf4;
        border-radius: 20px;
        padding: 34px;
        box-shadow: 0 8px 24px rgba(57, 119, 158, 0.08);
        margin-bottom: 24px;
    }

    .lab-hero h1 {
        color: #164568;
        font-size: 2.45rem;
        line-height: 1.25;
        margin: 0.4rem 0 0.8rem 0;
        white-space: pre-line;
    }

    .lab-hero p {
        color: #466b85;
        font-size: 1.04rem;
        line-height: 1.8;
    }

    .lab-card {
        background: rgba(255,255,255,0.88);
        border: 1px solid #c9e3f4;
        border-radius: 15px;
        padding: 20px;
        min-height: 130px;
        box-shadow: 0 5px 18px rgba(41, 100, 140, 0.05);
    }

    .lab-card-label {
        color: #5d89a6;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }

    .lab-card-value {
        color: #174b70;
        font-size: 1.25rem;
        font-weight: 750;
    }

    .lab-section {
        color: #174b70;
        border-bottom: 1px solid #c4e1f3;
        padding-bottom: 9px;
        margin: 1.4rem 0 1rem 0;
        font-size: 1.35rem;
        font-weight: 750;
    }

    .lab-note {
        background: #e0f2ff;
        border-left: 4px solid #63a9d8;
        border-radius: 7px;
        padding: 13px 16px;
        color: #315d7a;
        margin: 14px 0;
    }

    .stButton > button {
        background: linear-gradient(135deg, #4d9dce, #317fb4);
        color: white;
        border: 1px solid #317fb4;
        border-radius: 9px;
        font-weight: 700;
        min-height: 42px;
        transition: 0.2s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #317fb4, #246b9b);
        color: white;
        border-color: #246b9b;
        transform: translateY(-1px);
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background-color: #ffffff;
        border-color: #bddced;
        border-radius: 8px;
    }

    div[data-testid="stExpander"] {
        background: rgba(255,255,255,0.78);
        border: 1px solid #c8e1f1;
        border-radius: 10px;
    }

    .small-footer {
        color: #6d91a9;
        font-size: 0.82rem;
        border-top: 1px solid #c9e3f4;
        padding-top: 16px;
        margin-top: 36px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown(
        f"<h2 style='color:#174b70;margin-bottom:0'>{t('app_name')} 🧬</h2>",
        unsafe_allow_html=True
    )
    st.caption(t("subtitle"))
    st.divider()

    if st.button(t("language"), use_container_width=True):
        st.session_state.language = (
            "en" if st.session_state.language == "ko" else "ko"
        )
        st.rerun()

    st.markdown(f"### {t('menu')}")

    page = st.radio(
        "Navigation",
        [
            t("home"),
            t("search"),
            t("compare"),
            t("explore")
        ],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown(f"**{t('status')}**")
    st.success(t("online"))
    st.caption("API: UniProt REST")


# -----------------------------
# 홈
# -----------------------------
if page == t("home"):
    st.markdown(
        f"""
        <div class="lab-hero">
            <div class="lab-topline">{t('hero_tag')}</div>
            <h1>{t('hero_title')}</h1>
            <p>{t('hero_desc').replace(chr(10), '<br>')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"### {t('home_caption')}")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            f"""
            <div class="lab-card">
                <div class="lab-card-label">01 / SEARCH</div>
                <div class="lab-card-value">🧬 {t('search')}</div>
                <p>{t('search_desc')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="lab-card">
                <div class="lab-card-label">02 / COMPARE</div>
                <div class="lab-card-value">🔬 {t('compare')}</div>
                <p>{t('compare_desc')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="lab-card">
                <div class="lab-card-label">03 / EXPLORE</div>
                <div class="lab-card-value">💊 {t('explore')}</div>
                <p>{t('explore_desc')}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="lab-note">🔎 {t("data_source")}</div>',
        unsafe_allow_html=True
    )


# -----------------------------
# 단백질 검색
# -----------------------------
elif page == t("search"):
    st.markdown(f"## 🧬 {t('search_title')}")
    st.write(t("search_desc"))

    with st.form("protein_search_form"):
        query = st.text_input(
            t("query"),
            placeholder=t("query_hint")
        )
        submitted = st.form_submit_button(
            t("search_button"),
            use_container_width=True
        )

    if submitted:
        if not query.strip():
            st.warning(t("empty"))
        else:
            try:
                with st.spinner(t("translating")):
                    results = search_proteins(query.strip())
                st.session_state.single_results = results
                st.session_state.single_query = query.strip()
            except Exception:
                st.error(t("search_error"))
                st.session_state.single_results = []

    results = st.session_state.get("single_results", [])

    if results:
        st.markdown(f"### {t('results')} ({len(results)})")

        for protein in results:
            with st.expander(
                f'{protein["name"]} — {protein["organism"]} '
                f'({protein["accession"]})'
            ):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**{t('gene')}:** {protein['gene']}")
                    st.markdown(
                        f"**{t('organism')}:** {protein['organism']}"
                    )
                with c2:
                    st.markdown(
                        f"**{t('length')}:** {protein['length']}"
                    )
                    st.markdown(
                        f"**{t('accession')}:** {protein['accession']}"
                    )

                st.markdown(f"**{t('function')}**")
                function_display = display_annotation(
                    protein["function"]
                )
                st.write(function_display)

                st.markdown(f"**{t('sequence')}**")
                st.code(protein["sequence"], language="text")

                st.link_button(
                    t("open_uniprot"),
                    protein["url"]
                )

    elif "single_results" in st.session_state:
        st.info(t("no_results"))


# -----------------------------
# 단백질 비교
# -----------------------------
elif page == t("compare"):
    st.markdown(f"## 🔬 {t('compare_title')}")
    st.write(t("compare_desc"))

    col_a, col_b = st.columns(2)

    with col_a:
        query_a = st.text_input(
            t("protein_a"),
            value="TP53",
            key="query_a"
        )
        if st.button(t("search_a"), use_container_width=True):
            try:
                st.session_state.results_a = search_proteins(
                    query_a.strip()
                )
            except Exception:
                st.error(t("search_error"))
                st.session_state.results_a = []

    with col_b:
        query_b = st.text_input(
            t("protein_b"),
            value="EGFR",
            key="query_b"
        )
        if st.button(t("search_b"), use_container_width=True):
            try:
                st.session_state.results_b = search_proteins(
                    query_b.strip()
                )
            except Exception:
                st.error(t("search_error"))
                st.session_state.results_b = []

    results_a = st.session_state.get("results_a", [])
    results_b = st.session_state.get("results_b", [])

    if results_a and results_b:
        labels_a = [protein_label(p) for p in results_a]
        labels_b = [protein_label(p) for p in results_b]

        selected_a = st.selectbox(t("select_a"), labels_a)
        selected_b = st.selectbox(t("select_b"), labels_b)

        protein_a = results_a[labels_a.index(selected_a)]
        protein_b = results_b[labels_b.index(selected_b)]

        st.markdown(f"### {t('comparison')}")

        comparison_data = [
            [t("name"), protein_a["name"], protein_b["name"]],
            [t("accession"), protein_a["accession"], protein_b["accession"]],
            [t("gene"), protein_a["gene"], protein_b["gene"]],
            [t("organism"), protein_a["organism"], protein_b["organism"]],
            [t("length"), protein_a["length"], protein_b["length"]],
            [
                t("function"),
                display_annotation(protein_a["function"]),
                display_annotation(protein_b["function"])
            ]
        ]

        df = pd.DataFrame(
            comparison_data,
            columns=[t("property"), "A", "B"]
        )
        st.dataframe(df, use_container_width=True, hide_index=True)

        length_difference = abs(
            protein_a["length"] - protein_b["length"]
        )

        st.markdown(
            f"""
            <div class="lab-card">
                <div class="lab-card-label">SEQUENCE LENGTH DIFFERENCE</div>
                <div class="lab-card-value">{length_difference} aa</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"### {t('sequence')}")
        seq_a, seq_b = st.columns(2)

        with seq_a:
            st.markdown(f"**A: {protein_a['name']}**")
            st.code(protein_a["sequence"], language="text")
            st.link_button(t("open_uniprot"), protein_a["url"])

        with seq_b:
            st.markdown(f"**B: {protein_b['name']}**")
            st.code(protein_b["sequence"], language="text")
            st.link_button(t("open_uniprot"), protein_b["url"])

        st.info(t("sequence_note"))

    else:
        st.info(t("choose_first"))


# -----------------------------
# 신약 연구 탐색
# -----------------------------
elif page == t("explore"):
    st.markdown(f"## 💊 {t('explore_title')}")
    st.write(t("explore_desc"))

    st.markdown(f"### {t('idea_title')}")

    for key in ["idea1", "idea2", "idea3"]:
        st.markdown(
            f'<div class="lab-card" style="min-height:0;margin-bottom:12px">'
            f'🧪 {t(key)}</div>',
            unsafe_allow_html=True
        )

    st.markdown(
        f'<div class="lab-note">⚠️ {t("notice")}</div>',
        unsafe_allow_html=True
    )


# -----------------------------
# 하단 정보
# -----------------------------
st.markdown(
    f'<div class="small-footer">'
    f'🧬 BioTarget AI &nbsp; | &nbsp; {t("data_source")} '
    f'&nbsp; | &nbsp; Educational Research Platform'
    f'</div>',
    unsafe_allow_html=True
)
