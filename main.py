
import streamlit as st
import requests
import pandas as pd
from deep_translator import GoogleTranslator
from Bio.Align import PairwiseAligner

st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide",
)

# -----------------------------
# 다국어 텍스트
# -----------------------------
TEXT = {
    "ko": {
        "title": "BioTarget AI",
        "subtitle": "단백질 탐색 및 비교 연구 플랫폼",
        "language": "언어 선택",
        "home": "연구실 홈",
        "search": "단백질 검색",
        "compare": "단백질 비교",
        "explore": "탐구 가이드",
        "welcome": "바이오 연구를 시작해 보세요!",
        "welcome_desc": "단백질 정보를 검색하고, 아미노산 서열을 비교해 생화학적 특징을 탐구할 수 있어요.",
        "search_title": "🔎 단백질 검색",
        "search_help": "단백질 이름, 유전자명 또는 UniProt accession을 입력하세요.",
        "search_button": "검색하기",
        "results": "검색 결과",
        "no_results": "검색 결과가 없습니다. 다른 검색어를 입력해 보세요.",
        "organism": "생물종",
        "gene": "유전자",
        "length": "서열 길이",
        "function": "기능 설명",
        "sequence": "아미노산 서열",
        "accession": "UniProt accession",
        "translate": "🇰🇷 한국어로 번역",
        "translate_en": "🌐 영어로 번역",
        "original": "원문 기능 설명",
        "translated": "번역 결과",
        "translation_error": "번역에 실패했어요. 잠시 후 다시 시도해 주세요.",
        "compare_title": "🧬 단백질 비교 분석",
        "protein_a": "첫 번째 단백질의 UniProt accession",
        "protein_b": "두 번째 단백질의 UniProt accession",
        "compare_button": "단백질 비교하기",
        "comparison": "기본 정보 비교",
        "similarity": "서열 일치율",
        "identity": "동일한 아미노산",
        "alignment": "서열 정렬 결과",
        "score": "정렬 점수",
        "length_diff": "서열 길이 차이",
        "interpretation": "결과 해석",
        "caution": "주의: 서열 일치율만으로 단백질의 기능, 구조 또는 약물 효과가 같다고 판단할 수 없습니다.",
        "explore_title": "🔬 생화학 탐구 가이드",
        "explore_desc": "단백질 서열 분석은 생명과학 및 신약 후보 탐색의 출발점 중 하나예요.",
        "topic1": "단백질 서열과 진화적 관계",
        "topic2": "아미노산 치환과 단백질 기능",
        "topic3": "표적 단백질과 신약 후보 연구",
        "topic1_desc": "서로 다른 생물의 단백질 서열을 비교해 보존된 영역을 탐구할 수 있어요.",
        "topic2_desc": "아미노산의 성질과 치환 위치가 단백질 구조 및 기능에 미치는 영향을 조사할 수 있어요.",
        "topic3_desc": "질병 관련 표적 단백질과 연구 문헌을 연결해 후보 물질 연구 과정을 알아볼 수 있어요.",
        "loading": "UniProt에서 단백질 정보를 가져오는 중...",
        "error": "정보를 불러오지 못했습니다.",
        "alignment_note": "정렬 결과는 앞부분 최대 1,200개 정렬 열까지 표시합니다.",
        "not_found": "해당 accession의 단백질을 찾지 못했어요.",
        "same_protein": "두 입력값이 같은 단백질을 가리키는지 확인해 주세요.",
    },
    "en": {
        "title": "BioTarget AI",
        "subtitle": "Protein Discovery and Comparison Platform",
        "language": "Language",
        "home": "Research Lab",
        "search": "Protein Search",
        "compare": "Protein Comparison",
        "explore": "Research Guide",
        "welcome": "Start your biomolecular research!",
        "welcome_desc": "Search protein information and explore biochemical features by comparing amino acid sequences.",
        "search_title": "🔎 Protein Search",
        "search_help": "Enter a protein name, gene name, or UniProt accession.",
        "search_button": "Search",
        "results": "Search Results",
        "no_results": "No results found. Try another query.",
        "organism": "Organism",
        "gene": "Gene",
        "length": "Sequence Length",
        "function": "Function",
        "sequence": "Amino Acid Sequence",
        "accession": "UniProt Accession",
        "translate": "🇰🇷 Translate to Korean",
        "translate_en": "🌐 Translate to English",
        "original": "Original Function",
        "translated": "Translation",
        "translation_error": "Translation failed. Please try again later.",
        "compare_title": "🧬 Protein Comparison",
        "protein_a": "First protein UniProt accession",
        "protein_b": "Second protein UniProt accession",
        "compare_button": "Compare Proteins",
        "comparison": "Basic Information",
        "similarity": "Sequence Identity",
        "identity": "Identical Amino Acids",
        "alignment": "Sequence Alignment",
        "score": "Alignment Score",
        "length_diff": "Sequence Length Difference",
        "interpretation": "Interpretation",
        "caution": "Caution: Sequence identity alone cannot establish identical protein function, structure, or drug effects.",
        "explore_title": "🔬 Biochemistry Research Guide",
        "explore_desc": "Protein sequence analysis is one starting point for life-science and drug discovery research.",
        "topic1": "Protein Sequences and Evolution",
        "topic2": "Amino Acid Substitutions and Function",
        "topic3": "Target Proteins and Drug Discovery",
        "topic1_desc": "Compare protein sequences from different organisms and investigate conserved regions.",
        "topic2_desc": "Explore how amino acid properties and substitution positions may affect protein structure and function.",
        "topic3_desc": "Connect disease-related target proteins with scientific literature to learn about candidate compound research.",
        "loading": "Fetching protein data from UniProt...",
        "error": "Could not retrieve information.",
        "alignment_note": "Only the first 1,200 alignment columns are displayed.",
        "not_found": "No protein found for that accession.",
        "same_protein": "Check whether both inputs refer to the same protein.",
    },
}


# -----------------------------
# 언어 설정
# -----------------------------
if "language" not in st.session_state:
    st.session_state.language = "ko"

def t(key):
    return TEXT[st.session_state.language][key]


# -----------------------------
# CSS: 하늘색 연구실 디자인
# -----------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #F4FAFF 0%, #FFFFFF 65%);
    }
    [data-testid="stSidebar"] {
        background: #E5F3FF;
        border-right: 1px solid #C7E3FA;
    }
    h1, h2, h3 {
        color: #164D7A;
    }
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #B5D9F5;
        background: #E4F3FF;
        color: #164D7A;
        font-weight: 600;
    }
    div.stButton > button:hover {
        border-color: #5CA8E8;
        background: #D3EAFF;
        color: #103C61;
    }
    [data-testid="stMetric"] {
        background: #F0F8FF;
        border: 1px solid #D2E9FA;
        padding: 12px;
        border-radius: 12px;
    }
    .lab-card {
        background: #FFFFFF;
        border: 1px solid #D7EAF9;
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 12px;
    }
    .small-note {
        color: #526D82;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# UniProt API
# -----------------------------
UNIPROT_BASE = "https://rest.uniprot.org/uniprotkb"

@st.cache_data(ttl=3600, show_spinner=False)
def search_proteins(query):
    url = f"{UNIPROT_BASE}/search"
    params = {
        "query": query,
        "format": "json",
        "size": 10,
    }
    response = requests.get(url, params=params, timeout=25)
    response.raise_for_status()
    data = response.json()
    return [
        extract_protein(entry)
        for entry in data.get("results", [])
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_protein(accession):
    url = f"{UNIPROT_BASE}/{accession}.json"
    response = requests.get(url, timeout=25)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return extract_protein(response.json())


def extract_protein(entry):
    accession = entry.get("primaryAccession", "")
    description = (
        entry.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "")
    )

    if not description:
        names = (
            entry.get("proteinDescription", {})
            .get("alternativeNames", [])
        )
        if names:
            description = (
                names[0].get("fullName", {}).get("value", "")
            )

    genes = entry.get("genes", [])
    gene_name = ""
    if genes:
        gene_name = (
            genes[0].get("geneName", {}).get("value", "")
        )

    organism = (
        entry.get("organism", {})
        .get("scientificName", "Unknown")
    )

    sequence_data = entry.get("sequence", {})
    sequence = sequence_data.get("value", "")
    sequence_length = sequence_data.get("length", len(sequence))

    function_text = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            texts = []
            for item in comment.get("texts", []):
                value = item.get("value", "")
                if value:
                    texts.append(value)
            if texts:
                function_text = " ".join(texts)
                break

    return {
        "accession": accession,
        "name": description or accession or "Unknown protein",
        "gene": gene_name or "—",
        "organism": organism,
        "length": sequence_length,
        "function": function_text or "No function annotation available.",
        "sequence": sequence,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}",
    }


# -----------------------------
# 수동 번역: 클릭할 때만 요청
# -----------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def translate_annotation(text, target_language):
    if not text or not text.strip():
        return ""

    # 긴 텍스트는 작은 덩어리로 나누어 번역 요청
    chunk_size = 3000
    chunks = [
        text[i:i + chunk_size]
        for i in range(0, len(text), chunk_size)
    ]

    translator = GoogleTranslator(
        source="auto",
        target=target_language,
    )

    if len(chunks) == 1:
        return translator.translate(chunks[0])

    translated_chunks = translator.translate_batch(chunks)
    return " ".join(
        chunk for chunk in translated_chunks if chunk
    )


def render_function_translation(protein, suffix=""):
    st.markdown(f"**{t('original')}**")
    st.write(protein["function"])

    target = (
        "ko"
        if st.session_state.language == "ko"
        else "en"
    )

    button_label = (
        t("translate")
        if target == "ko"
        else t("translate_en")
    )

    state_key = (
        f"translation_{protein['accession']}_{target}_{suffix}"
    )

    if st.button(
        button_label,
        key=f"translate_button_{protein['accession']}_{suffix}",
    ):
        try:
            with st.spinner("Translating..." if target == "en" else "번역 중..."):
                translated = translate_annotation(
                    protein["function"],
                    target,
                )
            st.session_state[state_key] = translated
        except Exception:
            st.warning(t("translation_error"))

    if state_key in st.session_state:
        st.markdown(f"**{t('translated')}**")
        st.write(st.session_state[state_key])


# -----------------------------
# 서열 정렬 및 일치율 계산
# -----------------------------
def calculate_sequence_identity(seq_a, seq_b):
    """
    Global pairwise alignment으로 두 서열을 정렬한다.
    일치율 = 정렬 열 중 동일한 아미노산이 차지하는 비율.
    갭(gap)도 전체 정렬 열에 포함한다.
    """
    seq_a = (seq_a or "").strip().upper()
    seq_b = (seq_b or "").strip().upper()

    if not seq_a or not seq_b:
        raise ValueError("One or both protein sequences are empty.")

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignment = aligner.align(seq_a, seq_b)[0]
    coordinates = alignment.coordinates

    aligned_a = []
    aligned_b = []

    for k in range(coordinates.shape[1] - 1):
        a_start = int(coordinates[0, k])
        a_end = int(coordinates[0, k + 1])
        b_start = int(coordinates[1, k])
        b_end = int(coordinates[1, k + 1])

        a_len = a_end - a_start
        b_len = b_end - b_start

        if a_len > 0 and b_len > 0:
            # 대각선 구간: 두 서열이 함께 진행
            aligned_a.append(seq_a[a_start:a_end])
            aligned_b.append(seq_b[b_start:b_end])
        elif a_len > 0:
            # 첫 번째 서열에만 잔기가 있음
            aligned_a.append(seq_a[a_start:a_end])
            aligned_b.append("-" * a_len)
        elif b_len > 0:
            # 두 번째 서열에만 잔기가 있음
            aligned_a.append("-" * b_len)
            aligned_b.append(seq_b[b_start:b_end])

    aligned_a = "".join(aligned_a)
    aligned_b = "".join(aligned_b)

    alignment_columns = len(aligned_a)
    identical = sum(
        aa == bb and aa != "-"
        for aa, bb in zip(aligned_a, aligned_b)
    )

    identity = (
        100 * identical / alignment_columns
        if alignment_columns
        else 0.0
    )

    return {
        "identity": identity,
        "identical": identical,
        "columns": alignment_columns,
        "score": float(alignment.score),
        "aligned_a": aligned_a,
        "aligned_b": aligned_b,
    }


def format_alignment(aligned_a, aligned_b, width=60, max_columns=1200):
    """정렬된 서열을 일정한 길이의 블록으로 보기 좋게 출력한다."""
    output = []
    limit = min(len(aligned_a), max_columns)

    for start in range(0, limit, width):
        a_part = aligned_a[start:start + width]
        b_part = aligned_b[start:start + width]

        marks = "".join(
            "|" if a == b and a != "-" else " "
            for a, b in zip(a_part, b_part)
        )

        output.append(
            f"A {start + 1:>5}: {a_part}\n"
            f"           {marks}\n"
            f"B {start + 1:>5}: {b_part}\n"
        )

    if len(aligned_a) > max_columns:
        output.append(
            f"... ({len(aligned_a) - max_columns} more alignment columns)"
        )

    return "\n".join(output)


# -----------------------------
# 사이드바
# -----------------------------
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption(t("subtitle"))

    language_label = st.selectbox(
        t("language"),
        ["한국어", "English"],
        index=0 if st.session_state.language == "ko" else 1,
    )
    st.session_state.language = (
        "ko" if language_label == "한국어" else "en"
    )

    st.divider()

    page = st.radio(
        "Menu",
        [
            t("home"),
            t("search"),
            t("compare"),
            t("explore"),
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Data source: UniProt")


# -----------------------------
# 헤더
# -----------------------------
st.title("🧬 " + t("title"))
st.caption(t("subtitle"))
st.divider()


# -----------------------------
# 홈
# -----------------------------
if page == t("home"):
    st.markdown(f"## {t('welcome')}")
    st.write(t("welcome_desc"))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="lab-card">
                <h3>🔎 {t('search')}</h3>
                <p>{t('search_help')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="lab-card">
                <h3>🧬 {t('compare')}</h3>
                <p>{t('similarity')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "이 앱은 교육 및 탐구용 도구입니다. "
        "계산 결과만으로 의학적 판단이나 약물의 효과·안전성을 결론 내릴 수 없습니다."
        if st.session_state.language == "ko"
        else
        "This app is for education and exploration. "
        "Its calculations cannot establish clinical conclusions or drug efficacy and safety."
    )


# -----------------------------
# 단백질 검색
# -----------------------------
elif page == t("search"):
    st.header(t("search_title"))
    query = st.text_input(
        t("search_help"),
        placeholder="예: insulin, TP53, P01308",
    )

    if st.button(t("search_button"), type="primary"):
        if not query.strip():
            st.warning(t("search_help"))
        else:
            try:
                with st.spinner(t("loading")):
                    results = search_proteins(query.strip())

                st.session_state.search_results = results

            except Exception as error:
                st.error(f"{t('error')} ({error})")

    results = st.session_state.get("search_results", [])

    if results:
        st.subheader(t("results"))
        st.caption(
            f"{len(results)} results"
            if st.session_state.language == "en"
            else f"검색 결과 {len(results)}개"
        )

        for index, protein in enumerate(results):
            label = (
                f"{protein['name']} — {protein['accession']}"
            )

            with st.expander(label):
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**{t('organism')}:** {protein['organism']}")
                    st.write(f"**{t('gene')}:** {protein['gene']}")
                    st.write(f"**{t('length')}:** {protein['length']} aa")
                    st.write(f"**{t('accession')}:** {protein['accession']}")

                with col2:
                    st.markdown(
                        f"[Open UniProt record]({protein['url']})"
                    )

                st.divider()
                render_function_translation(protein, suffix=f"search_{index}")

                with st.expander(t("sequence")):
                    st.code(protein["sequence"] or "No sequence available")

    elif "search_results" in st.session_state:
        st.info(t("no_results"))


# -----------------------------
# 단백질 비교
# -----------------------------
elif page == t("compare"):
    st.header(t("compare_title"))

    st.write(
        "UniProt accession 두 개를 입력하면 기본 정보와 아미노산 서열을 비교합니다."
        if st.session_state.language == "ko"
        else
        "Enter two UniProt accessions to compare basic information and amino acid sequences."
    )

    with st.form("protein_comparison_form"):
        col_a, col_b = st.columns(2)

        with col_a:
            accession_a = st.text_input(
                t("protein_a"),
                placeholder="예: P01308",
            )

        with col_b:
            accession_b = st.text_input(
                t("protein_b"),
                placeholder="예: P01315",
            )

        submitted = st.form_submit_button(
            t("compare_button"),
            type="primary",
        )

    if submitted:
        if not accession_a.strip() or not accession_b.strip():
            st.warning(
                "두 accession을 모두 입력해 주세요."
                if st.session_state.language == "ko"
                else "Please enter both accessions."
            )
        else:
            try:
                with st.spinner(t("loading")):
                    protein_a = fetch_protein(accession_a.strip())
                    protein_b = fetch_protein(accession_b.strip())

                if not protein_a or not protein_b:
                    st.error(t("not_found"))
                elif not protein_a["sequence"] or not protein_b["sequence"]:
                    st.error(
                        "한 단백질 이상의 서열 정보가 없습니다."
                        if st.session_state.language == "ko"
                        else "At least one protein has no available sequence."
                    )
                else:
                    with st.spinner(
                        "서열 정렬 및 유사도 계산 중..."
                        if st.session_state.language == "ko"
                        else "Aligning sequences and calculating identity..."
                    ):
                        comparison = calculate_sequence_identity(
                            protein_a["sequence"],
                            protein_b["sequence"],
                        )

                    st.session_state.comparison_data = {
                        "a": protein_a,
                        "b": protein_b,
                        "result": comparison,
                    }

            except Exception as error:
                st.error(f"{t('error')} ({error})")

    data = st.session_state.get("comparison_data")

    if data:
        protein_a = data["a"]
        protein_b = data["b"]
        result = data["result"]

        st.divider()
        st.subheader(t("comparison"))

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown(f"### A. {protein_a['name']}")
            st.write(f"**{t('accession')}:** {protein_a['accession']}")
            st.write(f"**{t('organism')}:** {protein_a['organism']}")
            st.write(f"**{t('gene')}:** {protein_a['gene']}")
            st.write(f"**{t('length')}:** {protein_a['length']} aa")
            st.markdown(f"[UniProt]({protein_a['url']})")

        with col_b:
            st.markdown(f"### B. {protein_b['name']}")
            st.write(f"**{t('accession')}:** {protein_b['accession']}")
            st.write(f"**{t('organism')}:** {protein_b['organism']}")
            st.write(f"**{t('gene')}:** {protein_b['gene']}")
            st.write(f"**{t('length')}:** {protein_b['length']} aa")
            st.markdown(f"[UniProt]({protein_b['url']})")

        st.divider()
        st.subheader(t("similarity"))

        metric1, metric2, metric3 = st.columns(3)

        metric1.metric(
            t("similarity"),
            f"{result['identity']:.2f}%",
        )
        metric2.metric(
            t("identity"),
            f"{result['identical']:,} / {result['columns']:,}",
        )
        metric3.metric(
            t("score"),
            f"{result['score']:.1f}",
        )

        length_difference = abs(
            int(protein_a["length"]) - int(protein_b["length"])
        )

        st.write(
            f"**{t('length_diff')}:** {length_difference} aa"
        )

        st.subheader(t("alignment"))
        st.caption(t("alignment_note"))

        formatted = format_alignment(
            result["aligned_a"],
            result["aligned_b"],
        )

        st.code(formatted, language="text")

        st.subheader(t("interpretation"))

        if result["identity"] >= 80:
            st.write(
                "정렬된 서열에서 높은 일치율이 관찰됩니다. "
                "보존된 구조나 기능이 있는지 추가 문헌과 단백질 구조 정보로 확인할 가치가 있습니다."
                if st.session_state.language == "ko"
                else
                "The aligned sequences show high identity. "
                "Further investigation of conserved structure or function using literature and structural data may be useful."
            )
        elif result["identity"] >= 40:
            st.write(
                "중간 수준의 서열 일치율입니다. "
                "정렬 영역, 보존된 아미노산, 단백질 도메인을 추가로 확인해 보세요."
                if st.session_state.language == "ko"
                else
                "The sequences show moderate identity. "
                "Inspect the aligned regions, conserved residues, and protein domains."
            )
        else:
            st.write(
                "서열 일치율이 비교적 낮습니다. "
                "서열 길이, 단백질 도메인, 정렬 방식에 따라 해석이 달라질 수 있습니다."
                if st.session_state.language == "ko"
                else
                "The sequence identity is relatively low. "
                "Interpretation may depend on sequence length, domains, and alignment settings."
            )

        st.warning(t("caution"))

        with st.expander(t("function")):
            st.markdown(f"#### A. {protein_a['name']}")
            render_function_translation(protein_a, suffix="compare_a")

            st.divider()

            st.markdown(f"#### B. {protein_b['name']}")
            render_function_translation(protein_b, suffix="compare_b")


# -----------------------------
# 탐구 가이드
# -----------------------------
elif page == t("explore"):
    st.header(t("explore_title"))
    st.write(t("explore_desc"))

    topics = [
        (t("topic1"), t("topic1_desc")),
        (t("topic2"), t("topic2_desc")),
        (t("topic3"), t("topic3_desc")),
    ]

    for title, description in topics:
        st.markdown(
            f"""
            <div class="lab-card">
                <h3>{title}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Further research")

    st.markdown(
        "- UniProt: https://www.uniprot.org/\n"
        "- NCBI BLAST: https://blast.ncbi.nlm.nih.gov/Blast.cgi\n"
        "- RCSB Protein Data Bank: https://www.rcsb.org/"
    )

    st.caption(
        "서열 유사도는 탐구의 출발점이며, 실제 단백질 기능과 약물 후보의 가능성은 별도의 근거로 평가해야 합니다."
        if st.session_state.language == "ko"
        else
        "Sequence identity is a starting point. Protein function and drug-candidate potential require separate evidence."
    )
