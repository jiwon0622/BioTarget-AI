
import streamlit as st
import requests
from deep_translator import GoogleTranslator
from Bio.Align import PairwiseAligner

st.set_page_config(page_title="BioTarget AI", page_icon="🧬", layout="wide")

TEXT = {
    "ko": {
        "home": "연구실 홈", "search": "단백질 검색", "compare": "단백질 비교",
        "explore": "탐구 가이드", "language": "언어 선택",
        "subtitle": "단백질 탐색 및 비교 연구 플랫폼",
        "welcome": "바이오 연구를 시작해 보세요!",
        "welcome_desc": "단백질을 검색하고 아미노산 서열을 비교해 생화학적 특징을 탐구해 보세요.",
        "search_title": "🔎 단백질 검색", "search_help": "단백질 이름, 유전자명 또는 accession을 입력하세요.",
        "search_button": "검색하기", "results": "검색 결과", "no_results": "검색 결과가 없습니다.",
        "organism": "생물종", "gene": "유전자", "length": "서열 길이",
        "function": "기능 설명", "sequence": "아미노산 서열", "accession": "UniProt 번호",
        "original": "원문 기능 설명", "translated": "번역 결과",
        "translate": "🇰🇷 한국어로 번역", "translate_en": "🌐 영어로 번역",
        "translation_error": "번역에 실패했어요. 잠시 후 다시 시도해 주세요.",
        "compare_title": "🧬 단백질 비교 분석",
        "name_a": "첫 번째 단백질 검색", "name_b": "두 번째 단백질 검색",
        "search_a": "첫 번째 단백질 찾기", "search_b": "두 번째 단백질 찾기",
        "choose_a": "첫 번째 단백질 선택", "choose_b": "두 번째 단백질 선택",
        "compare_button": "선택한 단백질 비교하기",
        "need_search": "두 검색창에 단백질 이름을 입력한 뒤 검색 버튼을 눌러 주세요.",
        "choose_result": "검색 결과에서 비교할 단백질을 선택하세요.",
        "similarity": "서열 일치율", "identical": "동일한 아미노산",
        "score": "정렬 점수", "alignment": "서열 정렬 결과",
        "alignment_note": "정렬 결과는 최대 1,200개 열까지 표시합니다.",
        "interpretation": "결과 해석",
        "caution": "서열 일치율만으로 단백질의 기능, 구조 또는 약물 효과가 같다고 판단할 수 없습니다.",
        "loading": "UniProt에서 정보를 가져오는 중...",
        "error": "정보를 불러오지 못했습니다.",
        "not_found": "단백질 정보를 찾지 못했어요.",
        "explore_title": "🔬 생화학 탐구 가이드",
        "explore_desc": "서열 비교는 단백질의 특징과 생물학적 관계를 탐구하는 출발점입니다.",
    },
    "en": {
        "home": "Research Lab", "search": "Protein Search", "compare": "Protein Comparison",
        "explore": "Research Guide", "language": "Language",
        "subtitle": "Protein Discovery and Comparison Platform",
        "welcome": "Start your biomolecular research!",
        "welcome_desc": "Search proteins and compare amino acid sequences to explore biochemical features.",
        "search_title": "🔎 Protein Search", "search_help": "Enter a protein name, gene name, or accession.",
        "search_button": "Search", "results": "Search Results", "no_results": "No results found.",
        "organism": "Organism", "gene": "Gene", "length": "Sequence Length",
        "function": "Function", "sequence": "Amino Acid Sequence", "accession": "UniProt Accession",
        "original": "Original Function", "translated": "Translation",
        "translate": "🇰🇷 Translate to Korean", "translate_en": "🌐 Translate to English",
        "translation_error": "Translation failed. Please try again later.",
        "compare_title": "🧬 Protein Comparison",
        "name_a": "Search for the first protein", "name_b": "Search for the second protein",
        "search_a": "Find first protein", "search_b": "Find second protein",
        "choose_a": "Choose first protein", "choose_b": "Choose second protein",
        "compare_button": "Compare selected proteins",
        "need_search": "Enter a protein name in each search box and search.",
        "choose_result": "Select a protein from each search result.",
        "similarity": "Sequence Identity", "identical": "Identical Amino Acids",
        "score": "Alignment Score", "alignment": "Sequence Alignment",
        "alignment_note": "Up to 1,200 alignment columns are displayed.",
        "interpretation": "Interpretation",
        "caution": "Sequence identity alone cannot establish identical function, structure, or drug effects.",
        "loading": "Fetching data from UniProt...",
        "error": "Could not retrieve information.",
        "not_found": "Protein information not found.",
        "explore_title": "🔬 Biochemistry Research Guide",
        "explore_desc": "Sequence comparison is a starting point for exploring protein properties and biological relationships.",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "ko"

def t(key):
    return TEXT[st.session_state.language][key]

st.markdown("""
<style>
.stApp {background: linear-gradient(180deg,#F2F9FF 0%,#FFFFFF 70%);}
[data-testid="stSidebar"] {background:#E5F3FF;border-right:1px solid #C7E3FA;}
h1,h2,h3 {color:#164D7A;}
div.stButton>button {border-radius:10px;background:#E4F3FF;color:#164D7A;border:1px solid #B5D9F5;font-weight:600;}
div.stButton>button:hover {background:#D3EAFF;border-color:#5CA8E8;}
[data-testid="stMetric"] {background:#F0F8FF;border:1px solid #D2E9FA;padding:12px;border-radius:12px;}
</style>
""", unsafe_allow_html=True)


# -------------------------
# UniProt 데이터 가져오기
# -------------------------
BASE_URL = "https://rest.uniprot.org/uniprotkb"

def extract_protein(entry):
    accession = entry.get("primaryAccession", "")
    description = (
        entry.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "")
    )

    if not description:
        alternative = entry.get("proteinDescription", {}).get("alternativeNames", [])
        if alternative:
            description = alternative[0].get("fullName", {}).get("value", "")

    genes = entry.get("genes", [])
    gene = genes[0].get("geneName", {}).get("value", "") if genes else ""
    organism = entry.get("organism", {}).get("scientificName", "Unknown")
    sequence_info = entry.get("sequence", {})
    sequence = sequence_info.get("value", "")
    length = sequence_info.get("length", len(sequence))

    function = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            texts = [x.get("value", "") for x in comment.get("texts", []) if x.get("value")]
            if texts:
                function = " ".join(texts)
                break

    return {
        "accession": accession,
        "name": description or accession or "Unknown protein",
        "gene": gene or "—",
        "organism": organism,
        "length": length,
        "function": function or "No function annotation available.",
        "sequence": sequence,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def search_proteins(query):
    response = requests.get(
        f"{BASE_URL}/search",
        params={"query": query, "format": "json", "size": 10},
        timeout=25,
    )
    response.raise_for_status()
    return [extract_protein(x) for x in response.json().get("results", [])]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_protein(accession):
    response = requests.get(f"{BASE_URL}/{accession}.json", timeout=25)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return extract_protein(response.json())


@st.cache_data(ttl=86400, show_spinner=False)
def translate_annotation(text, target):
    if not text or not text.strip():
        return ""
    chunks = [text[i:i + 3000] for i in range(0, len(text), 3000)]
    translator = GoogleTranslator(source="auto", target=target)
    if len(chunks) == 1:
        return translator.translate(chunks[0])
    return " ".join(translator.translate_batch(chunks))


def render_translation(protein, suffix=""):
    st.markdown(f"**{t('original')}**")
    st.write(protein["function"])

    target = "ko" if st.session_state.language == "ko" else "en"
    label = t("translate") if target == "ko" else t("translate_en")
    state_key = f"translation_{protein['accession']}_{target}_{suffix}"

    if st.button(label, key=f"translate_btn_{protein['accession']}_{suffix}"):
        try:
            with st.spinner("번역 중..." if target == "ko" else "Translating..."):
                st.session_state[state_key] = translate_annotation(protein["function"], target)
        except Exception:
            st.warning(t("translation_error"))

    if state_key in st.session_state:
        st.markdown(f"**{t('translated')}**")
        st.write(st.session_state[state_key])


# -------------------------
# 서열 정렬
# -------------------------
def compare_sequences(seq_a, seq_b):
    seq_a, seq_b = seq_a.strip().upper(), seq_b.strip().upper()
    if not seq_a or not seq_b:
        raise ValueError("Protein sequence is empty.")

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignment = aligner.align(seq_a, seq_b)[0]
    coords = alignment.coordinates
    out_a, out_b = [], []

    for i in range(coords.shape[1] - 1):
        a0, a1 = int(coords[0, i]), int(coords[0, i + 1])
        b0, b1 = int(coords[1, i]), int(coords[1, i + 1])
        da, db = a1 - a0, b1 - b0

        if da > 0 and db > 0:
            out_a.append(seq_a[a0:a1])
            out_b.append(seq_b[b0:b1])
        elif da > 0:
            out_a.append(seq_a[a0:a1])
            out_b.append("-" * da)
        elif db > 0:
            out_a.append("-" * db)
            out_b.append(seq_b[b0:b1])

    aligned_a, aligned_b = "".join(out_a), "".join(out_b)
    columns = len(aligned_a)
    identical = sum(a == b and a != "-" for a, b in zip(aligned_a, aligned_b))
    identity = 100 * identical / columns if columns else 0

    return {
        "aligned_a": aligned_a,
        "aligned_b": aligned_b,
        "columns": columns,
        "identical": identical,
        "identity": identity,
        "score": float(alignment.score),
    }


def show_alignment(a, b, width=60, limit=1200):
    lines = []
    for start in range(0, min(len(a), limit), width):
        aa, bb = a[start:start + width], b[start:start + width]
        marks = "".join("|" if x == y and x != "-" else " " for x, y in zip(aa, bb))
        lines.append(f"A {start + 1:>5}: {aa}\n           {marks}\nB {start + 1:>5}: {bb}\n")
    if len(a) > limit:
        lines.append(f"... {len(a) - limit} more alignment columns")
    return "\n".join(lines)


def protein_label(protein):
    return f"{protein['name']} | {protein['organism']} | {protein['accession']}"


# -------------------------
# Sidebar
# -------------------------
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption(t("subtitle"))
    language = st.selectbox(
        t("language"), ["한국어", "English"],
        index=0 if st.session_state.language == "ko" else 1,
    )
    st.session_state.language = "ko" if language == "한국어" else "en"

    page = st.radio(
        "Menu", [t("home"), t("search"), t("compare"), t("explore")],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Data source: UniProt")

st.title("🧬 BioTarget AI")
st.caption(t("subtitle"))
st.divider()


# -------------------------
# Home
# -------------------------
if page == t("home"):
    st.header(t("welcome"))
    st.write(t("welcome_desc"))
    st.info(
        "이 앱은 교육·탐구용 도구입니다. 결과만으로 의학적 판단이나 약물의 효과·안전성을 결론 내릴 수 없습니다."
        if st.session_state.language == "ko"
        else "This app is for education and exploration, not for clinical decisions or establishing drug efficacy or safety."
    )


# -------------------------
# Protein search
# -------------------------
elif page == t("search"):
    st.header(t("search_title"))
    query = st.text_input(t("search_help"), placeholder="예: insulin, TP53, hemoglobin")

    if st.button(t("search_button"), type="primary", key="single_search"):
        if query.strip():
            try:
                with st.spinner(t("loading")):
                    st.session_state.single_results = search_proteins(query.strip())
            except Exception as e:
                st.error(f"{t('error')} ({e})")
        else:
            st.warning(t("search_help"))

    results = st.session_state.get("single_results", [])
    if results:
        st.subheader(t("results"))
        for i, protein in enumerate(results):
            with st.expander(protein_label(protein)):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**{t('organism')}:** {protein['organism']}")
                    st.write(f"**{t('gene')}:** {protein['gene']}")
                    st.write(f"**{t('length')}:** {protein['length']} aa")
                    st.write(f"**{t('accession')}:** {protein['accession']}")
                with c2:
                    st.markdown(f"[UniProt]({protein['url']})")
                render_translation(protein, f"single_{i}")
                with st.expander(t("sequence")):
                    st.code(protein["sequence"] or "Sequence not available.")
    elif "single_results" in st.session_state:
        st.info(t("no_results"))


# -------------------------
# Compare: search by name, then select
# -------------------------
elif page == t("compare"):
    st.header(t("compare_title"))
    st.write(
        "이름으로 두 단백질을 각각 검색한 뒤, 검색 결과에서 원하는 항목을 선택하세요."
        if st.session_state.language == "ko"
        else "Search for each protein by name, then select the desired results."
    )

    col_a, col_b = st.columns(2)

    with col_a:
        query_a = st.text_input(
            t("name_a"), placeholder="예: insulin", key="compare_query_a"
        )
        if st.button(t("search_a"), key="search_protein_a"):
            if query_a.strip():
                try:
                    with st.spinner(t("loading")):
                        st.session_state.compare_results_a = search_proteins(query_a.strip())
                except Exception as e:
                    st.error(f"{t('error')} ({e})")
            else:
                st.warning(t("need_search"))

    with col_b:
        query_b = st.text_input(
            t("name_b"), placeholder="예: IGF-1", key="compare_query_b"
        )
        if st.button(t("search_b"), key="search_protein_b"):
            if query_b.strip():
                try:
                    with st.spinner(t("loading")):
                        st.session_state.compare_results_b = search_proteins(query_b.strip())
                except Exception as e:
                    st.error(f"{t('error')} ({e})")
            else:
                st.warning(t("need_search"))

    results_a = st.session_state.get("compare_results_a", [])
    results_b = st.session_state.get("compare_results_b", [])

    selected_a = None
    selected_b = None

    if results_a:
        st.markdown(f"### {t('choose_a')}")
        labels_a = [protein_label(p) for p in results_a]
        index_a = st.selectbox(
            t("choose_a"), range(len(results_a)),
            format_func=lambda i: labels_a[i],
            key="selected_protein_a",
            label_visibility="collapsed",
        )
        selected_a = results_a[index_a]

    if results_b:
        st.markdown(f"### {t('choose_b')}")
        labels_b = [protein_label(p) for p in results_b]
        index_b = st.selectbox(
            t("choose_b"), range(len(results_b)),
            format_func=lambda i: labels_b[i],
            key="selected_protein_b",
            label_visibility="collapsed",
        )
        selected_b = results_b[index_b]

    if results_a and results_b:
        if st.button(t("compare_button"), type="primary", key="run_comparison"):
            if selected_a["accession"] == selected_b["accession"]:
                st.warning(
                    "같은 단백질을 선택했어요. 서로 다른 단백질을 골라 주세요."
                    if st.session_state.language == "ko"
                    else "You selected the same protein twice. Please choose two different proteins."
                )
            else:
                try:
                    with st.spinner(t("loading")):
                        full_a = fetch_protein(selected_a["accession"])
                        full_b = fetch_protein(selected_b["accession"])

                    if not full_a or not full_b:
                        st.error(t("not_found"))
                    elif not full_a["sequence"] or not full_b["sequence"]:
                        st.error(
                            "서열 정보가 없는 단백질입니다."
                            if st.session_state.language == "ko"
                            else "A protein sequence is unavailable."
                        )
                    else:
                        with st.spinner(
                            "서열을 정렬하고 있어요..." if st.session_state.language == "ko"
                            else "Aligning sequences..."
                        ):
                            result = compare_sequences(
                                full_a["sequence"], full_b["sequence"]
                            )
                        st.session_state.latest_comparison = {
                            "a": full_a, "b": full_b, "result": result
                        }
                except Exception as e:
                    st.error(f"{t('error')} ({e})")
    else:
        st.info(t("need_search"))

    data = st.session_state.get("latest_comparison")
    if data:
        a, b, result = data["a"], data["b"], data["result"]
        st.divider()
        ca, cb = st.columns(2)

        with ca:
            st.subheader("A. " + a["name"])
            st.write(f"**{t('organism')}:** {a['organism']}")
            st.write(f"**{t('gene')}:** {a['gene']}")
            st.write(f"**{t('length')}:** {a['length']} aa")
            st.markdown(f"[UniProt]({a['url']})")

        with cb:
            st.subheader("B. " + b["name"])
            st.write(f"**{t('organism')}:** {b['organism']}")
            st.write(f"**{t('gene')}:** {b['gene']}")
            st.write(f"**{t('length')}:** {b['length']} aa")
            st.markdown(f"[UniProt]({b['url']})")

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric(t("similarity"), f"{result['identity']:.2f}%")
        m2.metric(t("identical"), f"{result['identical']:,} / {result['columns']:,}")
        m3.metric(t("score"), f"{result['score']:.1f}")

        st.subheader(t("alignment"))
        st.caption(t("alignment_note"))
        st.code(show_alignment(result["aligned_a"], result["aligned_b"]), language="text")

        st.subheader(t("interpretation"))
        if result["identity"] >= 80:
            st.write(
                "높은 서열 일치율이 관찰됩니다. 보존된 구조나 기능이 있는지 추가로 확인해 보세요."
                if st.session_state.language == "ko"
                else "High sequence identity is observed. Further investigate conserved structure or function."
            )
        elif result["identity"] >= 40:
            st.write(
                "중간 수준의 일치율입니다. 보존된 영역과 단백질 도메인을 살펴보세요."
                if st.session_state.language == "ko"
                else "Moderate identity is observed. Examine conserved regions and protein domains."
            )
        else:
            st.write(
                "일치율이 비교적 낮습니다. 서열 길이와 정렬 영역을 함께 고려해 보세요."
                if st.session_state.language == "ko"
                else "Identity is relatively low. Consider sequence length and aligned regions."
            )
        st.warning(t("caution"))

        with st.expander(t("function")):
            st.markdown("#### A. " + a["name"])
            render_translation(a, "comparison_a")
            st.divider()
            st.markdown("#### B. " + b["name"])
            render_translation(b, "comparison_b")


# -------------------------
# Research guide
# -------------------------
elif page == t("explore"):
    st.header(t("explore_title"))
    st.write(t("explore_desc"))
    st.markdown("""
    - **단백질 서열과 진화:** 서로 다른 생물에서 보존된 서열 찾기
    - **아미노산 치환:** 아미노산 성질과 단백질 기능의 관계 탐구
    - **표적 단백질 연구:** 논문과 단백질 데이터베이스를 활용해 질병 관련 단백질 조사

    참고 사이트:
    - [UniProt](https://www.uniprot.org/)
    - [NCBI BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi)
    - [RCSB Protein Data Bank](https://www.rcsb.org/)
    """)
    st.caption(
        "서열 유사도는 탐구의 출발점이며, 단백질 기능이나 약물 효과를 단독으로 입증하지 않습니다."
        if st.session_state.language == "ko"
        else "Sequence similarity is a starting point and does not independently prove protein function or drug effects."
    )
