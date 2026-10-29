
import streamlit as st
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from Bio.Align import PairwiseAligner

st.set_page_config(page_title="BioTarget AI", page_icon="🧬", layout="wide")

TEXT = {
    "ko": {
        "home": "연구실 홈", "search": "단백질 검색", "compare": "단백질 비교",
        "explore": "탐구 가이드", "language": "언어 선택",
        "subtitle": "단백질 탐색 및 비교 연구 플랫폼",
        "welcome": "바이오 연구를 시작해 보세요!",
        "search_title": "🔎 단백질 검색", "search_help": "단백질 이름 또는 유전자명을 입력하세요.",
        "search_button": "검색하기", "results": "검색 결과", "no_results": "검색 결과가 없습니다.",
        "organism": "생물종", "gene": "유전자", "length": "서열 길이",
        "function": "기능 설명", "sequence": "아미노산 서열", "accession": "UniProt 번호",
        "original": "원문 기능 설명", "translated": "번역 결과",
        "translate": "🇰🇷 한국어로 번역", "translate_en": "🌐 영어로 번역",
        "translation_error": "두 번역 서비스가 모두 실패했어요.",
        "compare_title": "🧬 단백질 비교 분석",
        "name_a": "첫 번째 단백질 검색", "name_b": "두 번째 단백질 검색",
        "search_a": "첫 번째 단백질 찾기", "search_b": "두 번째 단백질 찾기",
        "choose_a": "첫 번째 단백질 선택", "choose_b": "두 번째 단백질 선택",
        "compare_button": "선택한 단백질 비교하기",
        "need_search": "두 단백질을 각각 검색해 주세요.",
        "similarity": "서열 일치율", "identical": "동일한 아미노산",
        "score": "정렬 점수", "alignment": "서열 정렬 결과",
        "interpretation": "결과 해석",
        "caution": "서열 일치율만으로 단백질의 기능이나 약물 효과가 같다고 판단할 수 없습니다.",
        "loading": "데이터를 불러오는 중...",
        "error": "요청에 실패했습니다.",
        "not_found": "단백질 정보를 찾지 못했어요.",
        "papers": "📚 관련 연구 논문",
        "paper_hint": "단백질 관련 논문 검색",
        "paper_button": "논문 검색하기",
        "paper_none": "검색 결과가 없습니다. 다른 검색어를 시도해 보세요.",
        "paper_error": "논문 검색에 실패했어요.",
        "abstract": "초록",
        "no_abstract": "초록 정보가 없습니다.",
        "open_paper": "논문 페이지 열기",
        "paper_note": "논문 관련성과 연구의 신뢰도는 직접 확인해야 합니다.",
        "explore_title": "🔬 생화학 탐구 가이드",
    },
    "en": {
        "home": "Research Lab", "search": "Protein Search", "compare": "Protein Comparison",
        "explore": "Research Guide", "language": "Language",
        "subtitle": "Protein Discovery and Comparison Platform",
        "welcome": "Start your biomolecular research!",
        "search_title": "🔎 Protein Search", "search_help": "Enter a protein name or gene symbol.",
        "search_button": "Search", "results": "Search Results", "no_results": "No results found.",
        "organism": "Organism", "gene": "Gene", "length": "Sequence Length",
        "function": "Function", "sequence": "Amino Acid Sequence", "accession": "UniProt Accession",
        "original": "Original Function", "translated": "Translation",
        "translate": "🇰🇷 Translate to Korean", "translate_en": "🌐 Translate to English",
        "translation_error": "Both translation services failed.",
        "compare_title": "🧬 Protein Comparison",
        "name_a": "Search for the first protein", "name_b": "Search for the second protein",
        "search_a": "Find first protein", "search_b": "Find second protein",
        "choose_a": "Choose first protein", "choose_b": "Choose second protein",
        "compare_button": "Compare selected proteins",
        "need_search": "Search for both proteins first.",
        "similarity": "Sequence Identity", "identical": "Identical Amino Acids",
        "score": "Alignment Score", "alignment": "Sequence Alignment",
        "interpretation": "Interpretation",
        "caution": "Sequence identity alone cannot establish identical protein function or drug effects.",
        "loading": "Loading data...",
        "error": "Request failed.",
        "not_found": "Protein information not found.",
        "papers": "📚 Related Research Papers",
        "paper_hint": "Search papers related to this protein",
        "paper_button": "Search papers",
        "paper_none": "No results found. Try another search term.",
        "paper_error": "Paper search failed.",
        "abstract": "Abstract",
        "no_abstract": "No abstract available.",
        "open_paper": "Open paper page",
        "paper_note": "Check each paper's relevance and research quality yourself.",
        "explore_title": "🔬 Biochemistry Research Guide",
    },
}

if "language" not in st.session_state:
    st.session_state.language = "ko"

def t(key):
    return TEXT[st.session_state.language][key]

st.markdown("""
<style>
.stApp {background:linear-gradient(180deg,#F2F9FF 0%,#FFFFFF 70%);}
[data-testid="stSidebar"] {background:#E5F3FF;border-right:1px solid #C7E3FA;}
h1,h2,h3 {color:#164D7A;}
div.stButton>button {border-radius:10px;background:#E4F3FF;color:#164D7A;border:1px solid #B5D9F5;font-weight:600;}
div.stButton>button:hover {background:#D3EAFF;border-color:#5CA8E8;}
[data-testid="stMetric"] {background:#F0F8FF;border:1px solid #D2E9FA;padding:12px;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# UniProt
# ---------------------------------
UNIPROT = "https://rest.uniprot.org/uniprotkb"

def extract_protein(entry):
    accession = entry.get("primaryAccession", "")
    description = (
        entry.get("proteinDescription", {})
        .get("recommendedName", {})
        .get("fullName", {})
        .get("value", "")
    )

    if not description:
        alternatives = entry.get("proteinDescription", {}).get("alternativeNames", [])
        if alternatives:
            description = alternatives[0].get("fullName", {}).get("value", "")

    genes = entry.get("genes", [])
    gene = genes[0].get("geneName", {}).get("value", "") if genes else ""
    organism = entry.get("organism", {}).get("scientificName", "Unknown")
    seq_data = entry.get("sequence", {})
    sequence = seq_data.get("value", "")
    length = seq_data.get("length", len(sequence))

    function = ""
    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            values = [x.get("value", "") for x in comment.get("texts", []) if x.get("value")]
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
        f"{UNIPROT}/search",
        params={"query": query, "format": "json", "size": 10},
        timeout=25,
    )
    response.raise_for_status()
    return [extract_protein(x) for x in response.json().get("results", [])]

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_protein(accession):
    response = requests.get(f"{UNIPROT}/{accession}.json", timeout=25)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return extract_protein(response.json())


# ---------------------------------
# 논문 검색: Europe PMC
# ---------------------------------
@st.cache_data(ttl=3600, show_spinner=False)
def search_literature(term):
    term = (term or "").strip()
    if not term:
        return []

    # 단순 검색어로 요청. 필드 문법을 강제하지 않는다.
    response = requests.get(
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        params={
            "query": term,
            "format": "json",
            "pageSize": 5,
            "resultType": "core",
        },
        headers={"User-Agent": "BioTargetAI/1.0"},
        timeout=30,
    )

    if not response.ok:
        detail = response.text[:300].replace("\n", " ")
        raise RuntimeError(f"Europe PMC HTTP {response.status_code}: {detail}")

    data = response.json()
    items = data.get("resultList", {}).get("result", [])
    papers = []

    for item in items:
        pmcid = item.get("pmcid", "")
        doi = item.get("doi", "")
        pmid = item.get("pmid", "")

        if pmcid:
            url = f"https://europepmc.org/articles/{pmcid}"
        elif doi:
            url = f"https://doi.org/{doi}"
        elif pmid:
            url = f"https://europepmc.org/article/MED/{pmid}"
        else:
            url = "https://europepmc.org/"

        papers.append({
            "title": item.get("title", "Untitled paper"),
            "authors": item.get("authorString", "Authors unavailable"),
            "year": item.get("pubYear", "Year unavailable"),
            "journal": item.get("journalTitle", "Journal unavailable"),
            "abstract": item.get("abstractText", ""),
            "url": url,
        })

    return papers


def render_papers(protein, suffix=""):
    term = protein["gene"] or protein["name"]
    st.caption(f"{t('paper_hint')}: {term}")

    if st.button(
        f"{t('paper_button')} — {term}",
        key=f"paper_btn_{protein['accession']}_{suffix}",
    ):
        try:
            with st.spinner("논문 검색 중..." if st.session_state.language == "ko" else "Searching papers..."):
                papers = search_literature(term)
            st.session_state[f"papers_{protein['accession']}_{suffix}"] = papers
            st.session_state[f"paper_error_{protein['accession']}_{suffix}"] = ""
        except Exception as e:
            st.session_state[f"paper_error_{protein['accession']}_{suffix}"] = str(e)
            st.session_state[f"papers_{protein['accession']}_{suffix}"] = None

    key = f"papers_{protein['accession']}_{suffix}"
    error_key = f"paper_error_{protein['accession']}_{suffix}"

    if st.session_state.get(error_key):
        st.error(f"{t('paper_error')} Details: {st.session_state[error_key]}")

    papers = st.session_state.get(key)
    if papers is None:
        return
    if not papers:
        st.info(t("paper_none"))
        return

    for i, paper in enumerate(papers, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {paper['title']}**")
            st.caption(f"{paper['authors']} · {paper['year']} · {paper['journal']}")
            if paper["abstract"]:
                with st.expander(t("abstract")):
                    st.write(paper["abstract"])
            else:
                st.caption(t("no_abstract"))
            st.markdown(f"[{t('open_paper')}]({paper['url']})")

    st.caption(t("paper_note"))


# ---------------------------------
# 번역: Google 우선, MyMemory 대체
# ---------------------------------
def translate_with_fallback(text, target):
    if not text or not text.strip():
        return "", "empty"

    errors = []

    # 1차: Google 번역
    try:
        result = GoogleTranslator(source="auto", target=target).translate(text[:4500])
        if result:
            return result, "Google Translate"
    except Exception as e:
        errors.append(f"Google Translate: {type(e).__name__}: {e}")

    # 2차: MyMemory 번역. 단백질 주석은 대체로 영어 원문이다.
    try:
        source = "en"
        result = MyMemoryTranslator(source=source, target=target).translate(text[:4500])
        if result:
            return result, "MyMemory"
    except Exception as e:
        errors.append(f"MyMemory: {type(e).__name__}: {e}")

    raise RuntimeError(" | ".join(errors))


def render_translation(protein, suffix=""):
    st.markdown(f"**{t('original')}**")
    st.write(protein["function"])

    target = "ko" if st.session_state.language == "ko" else "en"
    label = t("translate") if target == "ko" else t("translate_en")
    key = f"translation_{protein['accession']}_{target}_{suffix}"
    error_key = key + "_error"

    if st.button(label, key=f"translate_btn_{protein['accession']}_{suffix}"):
        try:
            with st.spinner("번역 중..." if target == "ko" else "Translating..."):
                translated, provider = translate_with_fallback(protein["function"], target)
            st.session_state[key] = translated
            st.session_state[key + "_provider"] = provider
            st.session_state[error_key] = ""
        except Exception as e:
            st.session_state[error_key] = str(e)

    if st.session_state.get(error_key):
        st.warning(f"{t('translation_error')} Details: {st.session_state[error_key]}")
        st.caption(
            "번역 서비스의 요청 제한이나 일시적 장애일 수 있어요. 잠시 기다린 뒤 다시 시도해 주세요."
            if st.session_state.language == "ko"
            else "This may be caused by service limits or a temporary outage. Wait before retrying."
        )

    if st.session_state.get(key):
        st.markdown(f"**{t('translated')}**")
        provider = st.session_state.get(key + "_provider", "")
        st.caption(f"Translation provider: {provider}")
        st.write(st.session_state[key])


# ---------------------------------
# 서열 비교
# ---------------------------------
def compare_sequences(seq_a, seq_b):
    seq_a, seq_b = (seq_a or "").strip().upper(), (seq_b or "").strip().upper()
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

    aa, bb = "".join(out_a), "".join(out_b)
    columns = len(aa)
    identical = sum(x == y and x != "-" for x, y in zip(aa, bb))

    return {
        "a": aa, "b": bb, "columns": columns, "identical": identical,
        "identity": 100 * identical / columns if columns else 0,
        "score": float(alignment.score),
    }


def show_alignment(a, b, width=60, limit=1200):
    lines = []
    for start in range(0, min(len(a), limit), width):
        aa, bb = a[start:start + width], b[start:start + width]
        marks = "".join("|" if x == y and x != "-" else " " for x, y in zip(aa, bb))
        lines.append(f"A {start+1:>5}: {aa}\n           {marks}\nB {start+1:>5}: {bb}\n")
    if len(a) > limit:
        lines.append(f"... {len(a) - limit} more alignment columns")
    return "\n".join(lines)


def protein_label(p):
    return f"{p['name']} | {p['organism']} | {p['accession']}"


# ---------------------------------
# 사이드바 / 공통 헤더
# ---------------------------------
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption(t("subtitle"))
    lang = st.selectbox(
        t("language"), ["한국어", "English"],
        index=0 if st.session_state.language == "ko" else 1,
    )
    st.session_state.language = "ko" if lang == "한국어" else "en"
    page = st.radio(
        "Menu", [t("home"), t("search"), t("compare"), t("explore")],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Data: UniProt · Europe PMC")

st.title("🧬 BioTarget AI")
st.caption(t("subtitle"))
st.divider()


# ---------------------------------
# 홈
# ---------------------------------
if page == t("home"):
    st.header(t("welcome"))
    st.write(
        "단백질 검색, 서열 비교, 연구 논문 탐색을 한 곳에서 할 수 있어요."
        if st.session_state.language == "ko"
        else "Search proteins, compare sequences, and explore related research papers."
    )
    c1, c2, c3 = st.columns(3)
    c1.info("🔎 단백질 검색" if st.session_state.language == "ko" else "🔎 Protein search")
    c2.info("🧬 서열 비교" if st.session_state.language == "ko" else "🧬 Sequence comparison")
    c3.info("📚 논문 검색" if st.session_state.language == "ko" else "📚 Paper search")
    st.warning(t("caution"))


# ---------------------------------
# 단백질 검색
# ---------------------------------
elif page == t("search"):
    st.header(t("search_title"))
    query = st.text_input(t("search_help"), placeholder="예: TP53, insulin, hemoglobin")

    if st.button(t("search_button"), type="primary", key="single_search"):
        if query.strip():
            try:
                with st.spinner(t("loading")):
                    st.session_state.single_results = search_proteins(query.strip())
            except Exception as e:
                st.error(f"{t('error')} Details: {e}")
        else:
            st.warning(t("search_help"))

    results = st.session_state.get("single_results", [])
    if results:
        st.subheader(t("results"))
        for i, p in enumerate(results):
            with st.expander(protein_label(p)):
                st.write(f"**{t('organism')}:** {p['organism']}")
                st.write(f"**{t('gene')}:** {p['gene'] or '—'}")
                st.write(f"**{t('length')}:** {p['length']} aa")
                st.write(f"**{t('accession')}:** {p['accession']}")
                st.markdown(f"[UniProt]({p['url']})")

                render_translation(p, f"single_{i}")

                with st.expander(t("sequence")):
                    st.code(p["sequence"] or "Sequence not available.")

                st.divider()
                st.subheader(t("papers"))
                render_papers(p, f"single_{i}")

    elif "single_results" in st.session_state:
        st.info(t("no_results"))


# ---------------------------------
# 단백질 비교 + 논문
# ---------------------------------
elif page == t("compare"):
    st.header(t("compare_title"))
    col_a, col_b = st.columns(2)

    with col_a:
        query_a = st.text_input(t("name_a"), placeholder="예: TP53", key="query_a")
        if st.button(t("search_a"), key="search_a_btn"):
            if query_a.strip():
                try:
                    st.session_state.results_a = search_proteins(query_a.strip())
                except Exception as e:
                    st.error(f"{t('error')} Details: {e}")
            else:
                st.warning(t("need_search"))

    with col_b:
        query_b = st.text_input(t("name_b"), placeholder="예: BRCA1", key="query_b")
        if st.button(t("search_b"), key="search_b_btn"):
            if query_b.strip():
                try:
                    st.session_state.results_b = search_proteins(query_b.strip())
                except Exception as e:
                    st.error(f"{t('error')} Details: {e}")
            else:
                st.warning(t("need_search"))

    ra = st.session_state.get("results_a", [])
    rb = st.session_state.get("results_b", [])
    pa = pb = None

    if ra:
        idx_a = st.selectbox(
            t("choose_a"), range(len(ra)),
            format_func=lambda i: protein_label(ra[i]), key="choose_idx_a",
        )
        pa = ra[idx_a]

    if rb:
        idx_b = st.selectbox(
            t("choose_b"), range(len(rb)),
            format_func=lambda i: protein_label(rb[i]), key="choose_idx_b",
        )
        pb = rb[idx_b]

    if ra and rb and st.button(t("compare_button"), type="primary", key="compare_now"):
        if pa["accession"] == pb["accession"]:
            st.warning("같은 단백질을 선택했어요." if st.session_state.language == "ko" else "You selected the same protein twice.")
        else:
            try:
                full_a = fetch_protein(pa["accession"])
                full_b = fetch_protein(pb["accession"])
                if not full_a or not full_b:
                    st.error(t("not_found"))
                else:
                    result = compare_sequences(full_a["sequence"], full_b["sequence"])
                    st.session_state.comparison = {"a": full_a, "b": full_b, "result": result}
            except Exception as e:
                st.error(f"{t('error')} Details: {e}")
    elif not ra or not rb:
        st.info(t("need_search"))

    data = st.session_state.get("comparison")
    if data:
        a, b, result = data["a"], data["b"], data["result"]
        c1, c2 = st.columns(2)

        with c1:
            st.subheader("A. " + a["name"])
            st.write(f"{t('organism')}: {a['organism']}")
            st.write(f"{t('gene')}: {a['gene'] or '—'}")
            st.write(f"{t('length')}: {a['length']} aa")
            st.markdown(f"[UniProt]({a['url']})")

        with c2:
            st.subheader("B. " + b["name"])
            st.write(f"{t('organism')}: {b['organism']}")
            st.write(f"{t('gene')}: {b['gene'] or '—'}")
            st.write(f"{t('length')}: {b['length']} aa")
            st.markdown(f"[UniProt]({b['url']})")

        m1, m2, m3 = st.columns(3)
        m1.metric(t("similarity"), f"{result['identity']:.2f}%")
        m2.metric(t("identical"), f"{result['identical']} / {result['columns']}")
        m3.metric(t("score"), f"{result['score']:.1f}")

        st.subheader(t("alignment"))
        st.code(show_alignment(result["a"], result["b"]), language="text")
        st.warning(t("caution"))

        with st.expander(t("function")):
            st.markdown("#### A. " + a["name"])
            render_translation(a, "compare_a")
            st.divider()
            st.markdown("#### B. " + b["name"])
            render_translation(b, "compare_b")

        st.divider()
        st.header(t("papers"))
        left, right = st.columns(2)
        with left:
            st.subheader("A. " + a["name"])
            render_papers(a, "compare_a")
        with right:
            st.subheader("B. " + b["name"])
            render_papers(b, "compare_b")


# ---------------------------------
# 탐구 가이드
# ---------------------------------
elif page == t("explore"):
    st.header(t("explore_title"))
    st.markdown("""
    - **단백질 서열과 진화:** 생물 사이에서 보존된 아미노산 영역 찾기
    - **아미노산 치환:** 아미노산의 성질과 단백질 기능의 관계 조사
    - **질병 관련 단백질:** 연구 논문을 읽고 실험 근거와 한계 확인하기
    - **신약 표적 연구:** 표적 단백질과 후보 물질에 대한 연구 근거 비교하기

    데이터베이스:
    - [UniProt](https://www.uniprot.org/)
    - [Europe PMC](https://europepmc.org/)
    - [NCBI BLAST](https://blast.ncbi.nlm.nih.gov/Blast.cgi)
    - [RCSB Protein Data Bank](https://www.rcsb.org/)
    """)
