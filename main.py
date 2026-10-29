
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
        "welcome_desc": "단백질을 검색하고, 서열을 비교하고, 관련 연구 논문까지 탐색해 보세요.",
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
        "similarity": "서열 일치율", "identical": "동일한 아미노산",
        "score": "정렬 점수", "alignment": "서열 정렬 결과",
        "alignment_note": "정렬 결과는 최대 1,200개 열까지 표시합니다.",
        "interpretation": "결과 해석",
        "caution": "서열 일치율만으로 단백질의 기능, 구조 또는 약물 효과가 같다고 판단할 수 없습니다.",
        "loading": "UniProt에서 정보를 가져오는 중...",
        "error": "정보를 불러오지 못했습니다.",
        "not_found": "단백질 정보를 찾지 못했어요.",
        "explore_title": "🔬 생화학 탐구 가이드",
        "explore_desc": "서열 비교와 논문 조사를 함께 활용하면 단백질의 생물학적 역할을 더 깊게 탐구할 수 있어요.",
        "papers": "📚 관련 연구 논문",
        "paper_search": "관련 논문 검색",
        "paper_hint": "선택한 단백질의 이름 또는 유전자명을 이용해 논문을 검색합니다.",
        "paper_none": "관련 논문을 찾지 못했어요. 다른 검색어로 시도해 보세요.",
        "paper_error": "논문 검색에 실패했어요. 잠시 후 다시 시도해 주세요.",
        "abstract": "초록",
        "no_abstract": "초록 정보가 제공되지 않습니다.",
        "open_paper": "Europe PMC에서 논문 보기",
        "paper_note": "논문 검색 결과는 검색어와의 관련성을 바탕으로 표시되며, 논문의 결론이나 신뢰도를 자동 검증한 것은 아닙니다.",
        "single_papers": "이 단백질 관련 논문 찾기",
    },
    "en": {
        "home": "Research Lab", "search": "Protein Search", "compare": "Protein Comparison",
        "explore": "Research Guide", "language": "Language",
        "subtitle": "Protein Discovery and Comparison Platform",
        "welcome": "Start your biomolecular research!",
        "welcome_desc": "Search proteins, compare sequences, and explore related research papers.",
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
        "need_search": "Search for a protein in both search boxes first.",
        "similarity": "Sequence Identity", "identical": "Identical Amino Acids",
        "score": "Alignment Score", "alignment": "Sequence Alignment",
        "alignment_note": "Up to 1,200 alignment columns are displayed.",
        "interpretation": "Interpretation",
        "caution": "Sequence identity alone cannot establish identical function, structure, or drug effects.",
        "loading": "Fetching data from UniProt...",
        "error": "Could not retrieve information.",
        "not_found": "Protein information not found.",
        "explore_title": "🔬 Biochemistry Research Guide",
        "explore_desc": "Combining sequence comparison with literature research can deepen your understanding of protein biology.",
        "papers": "📚 Related Research Papers",
        "paper_search": "Search related papers",
        "paper_hint": "Search papers using the selected protein or gene name.",
        "paper_none": "No related papers found. Try another search term.",
        "paper_error": "Paper search failed. Please try again later.",
        "abstract": "Abstract",
        "no_abstract": "No abstract is available.",
        "open_paper": "View paper on Europe PMC",
        "paper_note": "Results are based on search-term relevance; the app does not automatically validate each paper's conclusions or reliability.",
        "single_papers": "Find papers about this protein",
    },
}


if "language" not in st.session_state:
    st.session_state.language = "ko"


def t(key):
    return TEXT[st.session_state.language][key]


st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#F2F9FF 0%,#FFFFFF 70%);
}
[data-testid="stSidebar"] {
    background:#E5F3FF;
    border-right:1px solid #C7E3FA;
}
h1,h2,h3 {color:#164D7A;}
div.stButton>button {
    border-radius:10px;
    background:#E4F3FF;
    color:#164D7A;
    border:1px solid #B5D9F5;
    font-weight:600;
}
div.stButton>button:hover {
    background:#D3EAFF;
    border-color:#5CA8E8;
}
[data-testid="stMetric"] {
    background:#F0F8FF;
    border:1px solid #D2E9FA;
    padding:12px;
    border-radius:12px;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# UniProt 단백질 데이터
# =====================================
UNIPROT_URL = "https://rest.uniprot.org/uniprotkb"


def extract_protein(entry):
    accession = entry.get("primaryAccession", "")

    description = (
        entry.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "")
    )

    if not description:
        alternatives = (
            entry.get("proteinDescription", {})
            .get("alternativeNames", [])
        )
        if alternatives:
            description = (
                alternatives[0].get("fullName", {}).get("value", "")
            )

    genes = entry.get("genes", [])
    gene = (
        genes[0].get("geneName", {}).get("value", "")
        if genes else ""
    )

    organism = (
        entry.get("organism", {}).get("scientificName", "Unknown")
    )

    sequence_info = entry.get("sequence", {})
    sequence = sequence_info.get("value", "")
    length = sequence_info.get("length", len(sequence))

    function = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            values = [
                item.get("value", "")
                for item in comment.get("texts", [])
                if item.get("value")
            ]
            if values:
                function = " ".join(values)
                break

    return {
        "accession": accession,
        "name": description or accession or "Unknown protein",
        "gene": gene or "",
        "organism": organism,
        "length": length,
        "function": function or "No function annotation available.",
        "sequence": sequence,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}",
    }


@st.cache_data(ttl=3600, show_spinner=False)
def search_proteins(query):
    response = requests.get(
        f"{UNIPROT_URL}/search",
        params={
            "query": query,
            "format": "json",
            "size": 10,
        },
        timeout=25,
    )
    response.raise_for_status()
    return [
        extract_protein(entry)
        for entry in response.json().get("results", [])
    ]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_protein(accession):
    response = requests.get(
        f"{UNIPROT_URL}/{accession}.json",
        timeout=25,
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return extract_protein(response.json())


# =====================================
# Europe PMC 논문 검색
# =====================================
@st.cache_data(ttl=3600, show_spinner=False)
def search_literature(search_term):
    """
    Europe PMC에서 검색어가 제목 또는 초록에 등장하는 논문을 찾는다.
    """
    if not search_term or not search_term.strip():
        return []

    # 검색 문법이 깨지지 않도록 특수 문자를 공백으로 치환
    safe_term = "".join(
        ch if ch.isalnum() or ch in "-_ " else " "
        for ch in search_term
    ).strip()

    if not safe_term:
        return []

    query = f'TITLE_ABS:"{safe_term}"'

    response = requests.get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        params={
            "query": query,
            "format": "json",
            "pageSize": 5,
            "resultType": "core",
            "sort": "RELEVANCE",
        },
        timeout=25,
    )
    response.raise_for_status()

    results = response.json().get("resultList", {}).get("result", [])

    papers = []
    for item in results:
        title = item.get("title", "Untitled paper")
        authors = item.get("authorString", "Author information unavailable")
        year = item.get("pubYear", "Year unavailable")
        journal = item.get("journalTitle", "Journal information unavailable")
        abstract = item.get("abstractText", "")
        doi = item.get("doi", "")
        pmid = item.get("pmid", "")
        pmcid = item.get("pmcid", "")

        if pmcid:
            url = f"https://europepmc.org/articles/{pmcid}"
        elif doi:
            url = f"https://doi.org/{doi}"
        elif pmid:
            url = f"https://europepmc.org/article/MED/{pmid}"
        else:
            url = "https://europepmc.org/"

        papers.append({
            "title": title,
            "authors": authors,
            "year": year,
            "journal": journal,
            "abstract": abstract,
            "doi": doi,
            "pmid": pmid,
            "url": url,
        })

    return papers


def render_papers(protein, suffix=""):
    st.markdown(f"**{t('paper_hint')}**")

    # Gene symbol is often more useful for literature searches.
    term = protein["gene"] if protein["gene"] else protein["name"]

    if st.button(
        f"{t('single_papers')}: {term}",
        key=f"paper_button_{protein['accession']}_{suffix}",
    ):
        try:
            with st.spinner("논문 검색 중..." if st.session_state.language == "ko" else "Searching papers..."):
                papers = search_literature(term)
            st.session_state[f"papers_{protein['accession']}_{suffix}"] = papers
        except Exception:
            st.error(t("paper_error"))

    state_key = f"papers_{protein['accession']}_{suffix}"
    papers = st.session_state.get(state_key)

    if papers is not None:
        if not papers:
            st.info(t("paper_none"))
        else:
            for index, paper in enumerate(papers, start=1):
                with st.container(border=True):
                    st.markdown(f"**{index}. {paper['title']}**")
                    st.caption(
                        f"{paper['authors']} · {paper['year']} · {paper['journal']}"
                    )

                    if paper["abstract"]:
                        with st.expander(t("abstract")):
                            st.write(paper["abstract"])
                    else:
                        st.caption(t("no_abstract"))

                    st.markdown(
                        f"[{t('open_paper')}]({paper['url']})"
                    )

            st.caption(t("paper_note"))


# =====================================
# 번역 기능
# =====================================
@st.cache_data(ttl=86400, show_spinner=False)
def translate_annotation(text, target):
    if not text or not text.strip():
        return ""

    chunks = [
        text[i:i + 3000]
        for i in range(0, len(text), 3000)
    ]

    translator = GoogleTranslator(source="auto", target=target)

    if len(chunks) == 1:
        return translator.translate(chunks[0])

    return " ".join(
        part for part in translator.translate_batch(chunks) if part
    )


def render_translation(protein, suffix=""):
    st.markdown(f"**{t('original')}**")
    st.write(protein["function"])

    target = "ko" if st.session_state.language == "ko" else "en"
    label = t("translate") if target == "ko" else t("translate_en")
    state_key = f"translation_{protein['accession']}_{target}_{suffix}"

    if st.button(
        label,
        key=f"translate_btn_{protein['accession']}_{suffix}",
    ):
        try:
            with st.spinner("번역 중..." if target == "ko" else "Translating..."):
                st.session_state[state_key] = translate_annotation(
                    protein["function"], target
                )
        except Exception:
            st.warning(t("translation_error"))

    if state_key in st.session_state:
        st.markdown(f"**{t('translated')}**")
        st.write(st.session_state[state_key])


# =====================================
# 서열 정렬 및 일치율
# =====================================
def compare_sequences(seq_a, seq_b):
    seq_a = (seq_a or "").strip().upper()
    seq_b = (seq_b or "").strip().upper()

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

    aligned_a = "".join(out_a)
    aligned_b = "".join(out_b)
    columns = len(aligned_a)

    identical = sum(
        a == b and a != "-"
        for a, b in zip(aligned_a, aligned_b)
    )

    return {
        "aligned_a": aligned_a,
        "aligned_b": aligned_b,
        "columns": columns,
        "identical": identical,
        "identity": 100 * identical / columns if columns else 0,
        "score": float(alignment.score),
    }


def show_alignment(a, b, width=60, limit=1200):
    lines = []

    for start in range(0, min(len(a), limit), width):
        aa = a[start:start + width]
        bb = b[start:start + width]
        marks = "".join(
            "|" if x == y and x != "-" else " "
            for x, y in zip(aa, bb)
        )

        lines.append(
            f"A {start + 1:>5}: {aa}\n"
            f"           {marks}\n"
            f"B {start + 1:>5}: {bb}\n"
        )

    if len(a) > limit:
        lines.append(f"... {len(a) - limit} more alignment columns")

    return "\n".join(lines)


def protein_label(protein):
    return (
        f"{protein['name']} | {protein['organism']} "
        f"| {protein['accession']}"
    )


# =====================================
# Sidebar
# =====================================
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption(t("subtitle"))

    language = st.selectbox(
        t("language"),
        ["한국어", "English"],
        index=0 if st.session_state.language == "ko" else 1,
    )
    st.session_state.language = (
        "ko" if language == "한국어" else "en"
    )

    page = st.radio(
        "Menu",
        [t("home"), t("search"), t("compare"), t("explore")],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Data: UniProt · Europe PMC")


st.title("🧬 BioTarget AI")
st.caption(t("subtitle"))
st.divider()


# =====================================
# 홈
# =====================================
if page == t("home"):
    st.header(t("welcome"))
    st.write(t("welcome_desc"))

    c1, c2, c3 = st.columns(3)
    c1.info("🔎 단백질 검색" if st.session_state.language == "ko" else "🔎 Protein search")
    c2.info("🧬 서열 비교" if st.session_state.language == "ko" else "🧬 Sequence comparison")
    c3.info("📚 논문 탐색" if st.session_state.language == "ko" else "📚 Literature search")

    st.warning(
        "이 앱은 교육·탐구용 도구입니다. 검색 결과와 서열 비교만으로 의학적 판단이나 약물의 효과·안전성을 결론 내릴 수 없습니다."
        if st.session_state.language == "ko"
        else "This app is for education and exploration. Search results and sequence comparisons cannot establish clinical conclusions or drug efficacy and safety."
    )


# =====================================
# 단백질 검색
# =====================================
elif page == t("search"):
    st.header(t("search_title"))

    query = st.text_input(
        t("search_help"),
        placeholder="예: insulin, TP53, hemoglobin",
    )

    if st.button(t("search_button"), type="primary", key="single_search"):
        if query.strip():
            try:
                with st.spinner(t("loading")):
                    st.session_state.single_results = search_proteins(query.strip())
            except Exception as error:
                st.error(f"{t('error')} ({error})")
        else:
            st.warning(t("search_help"))

    results = st.session_state.get("single_results", [])

    if results:
        st.subheader(t("results"))

        for index, protein in enumerate(results):
            with st.expander(protein_label(protein)):
                left, right = st.columns(2)

                with left:
                    st.write(f"**{t('organism')}:** {protein['organism']}")
                    st.write(f"**{t('gene')}:** {protein['gene'] or '—'}")
                    st.write(f"**{t('length')}:** {protein['length']} aa")
                    st.write(f"**{t('accession')}:** {protein['accession']}")

                with right:
                    st.markdown(f"[UniProt]({protein['url']})")

                render_translation(protein, f"single_{index}")

                with st.expander(t("sequence")):
                    st.code(protein["sequence"] or "Sequence not available.")

                st.divider()
                st.markdown(f"### {t('papers')}")
                render_papers(protein, f"single_{index}")

    elif "single_results" in st.session_state:
        st.info(t("no_results"))


# =====================================
# 단백질 비교
# =====================================
elif page == t("compare"):
    st.header(t("compare_title"))

    st.write(
        "두 단백질을 이름으로 검색하고 각각 선택한 뒤 비교하세요."
        if st.session_state.language == "ko"
        else "Search for two proteins by name, select each one, and compare them."
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
                except Exception as error:
                    st.error(f"{t('error')} ({error})")
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
                except Exception as error:
                    st.error(f"{t('error')} ({error})")
            else:
                st.warning(t("need_search"))

    results_a = st.session_state.get("compare_results_a", [])
    results_b = st.session_state.get("compare_results_b", [])

    selected_a = None
    selected_b = None

    if results_a:
        st.markdown(f"### {t('choose_a')}")
        selected_index_a = st.selectbox(
            t("choose_a"),
            range(len(results_a)),
            format_func=lambda i: protein_label(results_a[i]),
            key="selected_protein_a",
            label_visibility="collapsed",
        )
        selected_a = results_a[selected_index_a]

    if results_b:
        st.markdown(f"### {t('choose_b')}")
        selected_index_b = st.selectbox(
            t("choose_b"),
            range(len(results_b)),
            format_func=lambda i: protein_label(results_b[i]),
            key="selected_protein_b",
            label_visibility="collapsed",
        )
        selected_b = results_b[selected_index_b]

    if results_a and results_b:
        if st.button(t("compare_button"), type="primary", key="run_comparison"):
            if selected_a["accession"] == selected_b["accession"]:
                st.warning(
                    "같은 단백질을 선택했어요. 서로 다른 단백질을 골라 주세요."
                    if st.session_state.language == "ko"
                    else "You selected the same protein twice. Choose two different proteins."
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
                            "서열 정렬 중..." if st.session_state.language == "ko"
                            else "Aligning sequences..."
                        ):
                            result = compare_sequences(
                                full_a["sequence"],
                                full_b["sequence"],
                            )

                        st.session_state.latest_comparison = {
                            "a": full_a,
                            "b": full_b,
                            "result": result,
                        }
                except Exception as error:
                    st.error(f"{t('error')} ({error})")
    else:
        st.info(t("need_search"))

    data = st.session_state.get("latest_comparison")

    if data:
        a = data["a"]
        b = data["b"]
        result = data["result"]

        st.divider()
        left, right = st.columns(2)

        with left:
            st.subheader("A. " + a["name"])
            st.write(f"**{t('organism')}:** {a['organism']}")
            st.write(f"**{t('gene')}:** {a['gene'] or '—'}")
            st.write(f"**{t('length')}:** {a['length']} aa")
            st.markdown(f"[UniProt]({a['url']})")

        with right:
            st.subheader("B. " + b["name"])
            st.write(f"**{t('organism')}:** {b['organism']}")
            st.write(f"**{t('gene')}:** {b['gene'] or '—'}")
            st.write(f"**{t('length')}:** {b['length']} aa")
            st.markdown(f"[UniProt]({b['url']})")

        st.divider()
        st.subheader(t("similarity"))

        m1, m2, m3 = st.columns(3)
        m1.metric(t("similarity"), f"{result['identity']:.2f}%")
        m2.metric(
            t("identical"),
            f"{result['identical']:,} / {result['columns']:,}",
        )
        m3.metric(t("score"), f"{result['score']:.1f}")

        st.subheader(t("alignment"))
        st.caption(t("alignment_note"))
        st.code(
            show_alignment(result["aligned_a"], result["aligned_b"]),
            language="text",
        )

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

        st.divider()
        st.header(t("papers"))
        st.write(
            "각 단백질에 대한 논문을 따로 검색할 수 있어요."
            if st.session_state.language == "ko"
            else "Search for papers about each protein separately."
        )

        paper_a, paper_b = st.columns(2)

        with paper_a:
            st.subheader("A. " + a["name"])
            render_papers(a, "comparison_a")

        with paper_b:
            st.subheader("B. " + b["name"])
            render_papers(b, "comparison_b")


# =====================================
# 탐구 가이드
# =====================================
elif page == t("explore"):
    st.header(t("explore_title"))
    st.write(t("explore_desc"))

    st.markdown("""
    ### 탐구 주제 예시

    - **단백질 서열과 진화:** 서로 다른 생물에서 보존된 아미노산 영역 찾기
    - **아미노산 치환:** 아미노산의 성질과 단백질 기능의 관계 조사
    - **질병 관련 단백질:** 질병과 관련된 단백질의 기능 및 연구 논문 조사
    - **신약 표적 연구:** 논문에서 제안한 표적과 실험 근거 비교

    ### 연구 데이터베이스

    - [UniProt — 단백질 정보](https://www.uniprot.org/)
    - [Europe PMC — 생명과학 논문](https://europepmc.org/)
    - [NCBI BLAST — 서열 유사성 검색](https://blast.ncbi.nlm.nih.gov/Blast.cgi)
    - [RCSB PDB — 단백질 구조](https://www.rcsb.org/)
    """)

    st.info(
        "논문 초록은 연구 내용을 빠르게 파악하는 데 도움이 되지만, 결론을 평가할 때는 연구 방법과 결과, 한계도 함께 살펴보세요."
        if st.session_state.language == "ko"
        else "Abstracts help you quickly understand a study, but assess methods, results, and limitations before drawing conclusions."
    )
