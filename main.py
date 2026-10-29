
import streamlit as st
import requests
import html
from deep_translator import MyMemoryTranslator, GoogleTranslator
from Bio.Align import PairwiseAligner

st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

UNIPROT_URL = "https://rest.uniprot.org"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"


# =========================================================
# 디자인
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Nanum Gothic', sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #f1f9ff 0%, #f8fbff 55%, #edf7ff 100%);
    color: #183b5b;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #dff1ff 0%, #eaf6ff 100%);
    border-right: 1px solid #c9e4fa;
}
h1, h2, h3 {
    color: #174a78 !important;
    font-weight: 800 !important;
}
.hero {
    background: linear-gradient(125deg, #d8efff, #e5f8ff 55%, #d7f4f0);
    padding: 30px;
    border-radius: 22px;
    border: 1px solid #c6e5f7;
    margin-bottom: 24px;
    box-shadow: 0 5px 18px rgba(51, 116, 161, 0.08);
}
.hero h1 {
    font-size: 35px;
    margin-bottom: 12px;
}
.hero p {
    font-size: 16px;
    line-height: 1.8;
    color: #365b78;
}
.section-card {
    background: #ffffff;
    padding: 22px;
    border: 1px solid #d9eaf7;
    border-radius: 18px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(47, 101, 143, 0.06);
}
.info-box {
    background: #e9f6ff;
    border-left: 5px solid #56a8e8;
    padding: 14px 18px;
    border-radius: 10px;
    margin: 12px 0;
    line-height: 1.7;
}
.small-note {
    color: #66839b;
    font-size: 13px;
}
.protein-title {
    font-size: 21px;
    color: #174a78;
    font-weight: 800;
}
div.stButton > button {
    background: linear-gradient(100deg, #258bd0, #36b4c8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 700;
}
div.stButton > button:hover {
    background: linear-gradient(100deg, #176eae, #2198ae);
    color: white;
    border: none;
}
hr {
    border-color: #d9eaf7;
}
footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 공통 함수
# =========================================================
def request_json(url, params=None, timeout=25):
    response = requests.get(
        url,
        params=params,
        timeout=timeout,
        headers={"User-Agent": "BioTargetAI/1.0"}
    )
    response.raise_for_status()
    return response.json()


def safe_text(value, default="정보 없음"):
    if value is None or not str(value).strip():
        return default
    return str(value)


def get_protein_name(protein):
    return (
        protein.get("protein_name")
        or protein.get("gene_names")
        or protein.get("accession")
        or "이름 없음"
    )


def candidate_label(protein):
    parts = [get_protein_name(protein)]

    if protein.get("gene_names"):
        parts.append(f"유전자: {protein['gene_names']}")

    if protein.get("organism"):
        parts.append(protein["organism"])

    if protein.get("accession"):
        parts.append(f"Accession: {protein['accession']}")

    return " | ".join(parts)


def extract_protein_function(data):
    """UniProt 주석에서 단백질의 FUNCTION 설명을 추출한다."""
    functions = []

    for comment in data.get("comments", []):
        if comment.get("commentType") != "FUNCTION":
            continue

        for entry in comment.get("texts", []):
            value = entry.get("value", "").strip()
            if value and value not in functions:
                functions.append(value)

    return "\n\n".join(functions)


# =========================================================
# 단백질 검색
# =========================================================
def search_proteins(query, limit=10):
    query = query.strip()
    if not query:
        return []

    params = {
        "query": query,
        "format": "json",
        "size": limit,
        "fields": (
            "accession,id,protein_name,gene_names,"
            "organism_name,length"
        )
    }

    try:
        data = request_json(
            f"{UNIPROT_URL}/uniprotkb/search",
            params=params
        )

        results = []

        for item in data.get("results", []):
            accession = item.get("primaryAccession", "")

            description = (
                item.get("proteinDescription", {})
                .get("recommendedName", {})
                .get("fullName", {})
                .get("value", "")
            )

            if not description:
                submissions = item.get(
                    "proteinDescription", {}
                ).get("submissionNames", [])

                if submissions:
                    description = submissions[0].get(
                        "fullName", {}
                    ).get("value", "")

            genes = []
            for gene in item.get("genes", []):
                name = gene.get("geneName", {}).get("value", "")
                if name:
                    genes.append(name)

            results.append({
                "accession": accession,
                "protein_name": description,
                "gene_names": ", ".join(genes),
                "organism": item.get(
                    "organism", {}
                ).get("scientificName", ""),
                "length": item.get("sequence", {}).get("length"),
                "url": f"https://www.uniprot.org/uniprotkb/{accession}"
            })

        return results

    except Exception as e:
        st.error(f"단백질 검색 오류: {e}")
        return []


def find_protein_candidates(name, limit=10):
    name = name.strip()
    if not name:
        return []

    results = search_proteins(name, limit)

    if results:
        return results

    # 이름 검색 결과가 없을 때 유전자명으로 다시 검색
    safe_name = name.replace('"', '\\"')
    return search_proteins(
        f'(gene:{safe_name}) OR (protein_name:"{safe_name}")',
        limit
    )


def get_protein(accession):
    """단백질 상세 정보, 아미노산 서열 및 기능 설명 조회."""
    try:
        data = request_json(
            f"{UNIPROT_URL}/uniprotkb/{accession}.json"
        )

        description = (
            data.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", "")
        )

        if not description:
            submissions = data.get(
                "proteinDescription", {}
            ).get("submissionNames", [])

            if submissions:
                description = submissions[0].get(
                    "fullName", {}
                ).get("value", "")

        genes = []
        for gene in data.get("genes", []):
            name = gene.get("geneName", {}).get("value", "")
            if name:
                genes.append(name)

        sequence_info = data.get("sequence", {})
        primary_accession = data.get(
            "primaryAccession", accession
        )

        return {
            "accession": primary_accession,
            "protein_name": description,
            "gene_names": ", ".join(genes),
            "organism": data.get(
                "organism", {}
            ).get("scientificName", ""),
            "length": sequence_info.get("length"),
            "sequence": sequence_info.get("value", ""),
            "function": extract_protein_function(data),
            "url": (
                f"https://www.uniprot.org/uniprotkb/"
                f"{primary_accession}"
            )
        }

    except Exception as e:
        st.error(f"단백질 상세 정보 조회 오류: {e}")
        return None


# =========================================================
# 번역 함수
# =========================================================
def translate_to_korean(text):
    text = str(text).strip()

    if not text:
        return ""

    errors = []

    try:
        return MyMemoryTranslator(
            source="en-GB",
            target="ko-KR"
        ).translate(text)
    except Exception as e:
        errors.append(str(e))

    try:
        return GoogleTranslator(
            source="auto",
            target="ko"
        ).translate(text)
    except Exception as e:
        errors.append(str(e))

    raise RuntimeError(
        "번역 서비스에 연결하지 못했습니다. "
        "잠시 후 다시 시도해 주세요."
    )


def render_function_translation(protein, suffix):
    """
    단백질 기능 원문을 보여주고,
    버튼을 누르면 해당 설명을 한국어로 번역한다.
    """
    function_text = protein.get("function", "").strip()
    accession = protein.get("accession", "protein")
    state_key = f"function_translation_{suffix}_{accession}"

    st.markdown("#### 🧪 단백질 기능")

    if not function_text:
        st.info(
            "UniProt에서 제공하는 기능 설명이 없습니다. "
            "다른 단백질 항목을 확인해 보세요."
        )
        return

    st.write(function_text)

    if st.button(
        "🌐 단백질 기능 한국어로 번역",
        key=f"translate_function_button_{suffix}_{accession}"
    ):
        with st.spinner("단백질 기능을 번역하고 있습니다..."):
            try:
                st.session_state[state_key] = translate_to_korean(
                    function_text
                )
                st.session_state[f"{state_key}_error"] = ""
            except Exception as e:
                st.session_state[state_key] = ""
                st.session_state[f"{state_key}_error"] = str(e)

    translation_error = st.session_state.get(
        f"{state_key}_error", ""
    )
    translated = st.session_state.get(state_key, "")

    if translation_error:
        st.warning(translation_error)

    if translated:
        st.markdown("**🇰🇷 한국어 번역**")
        st.markdown(
            f"""
            <div class="info-box">
                {html.escape(translated).replace(chr(10), '<br>')}
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 단백질 정보 카드
# =========================================================
def protein_card(protein, show_function=True, suffix="card"):
    accession = protein.get("accession", "")
    protein_url = protein.get(
        "url",
        f"https://www.uniprot.org/uniprotkb/{accession}"
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="protein-title">
                {html.escape(safe_text(protein.get('protein_name')))}
            </div>
            <p><b>유전자명:</b>
                {html.escape(safe_text(protein.get('gene_names')))}</p>
            <p><b>생물종:</b>
                {html.escape(safe_text(protein.get('organism')))}</p>
            <p><b>Accession:</b>
                {html.escape(safe_text(accession))}</p>
            <p><b>서열 길이:</b>
                {protein.get('length') or '정보 없음'}개 아미노산</p>
            <a href="{html.escape(protein_url, quote=True)}"
               target="_blank">UniProt에서 자세히 보기 ↗</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    if show_function:
        render_function_translation(protein, suffix)


# =========================================================
# 논문 검색
# =========================================================
def search_papers(query, limit=5):
    if not query.strip():
        return []

    try:
        data = request_json(
            f"{EUROPE_PMC_URL}/search",
            params={
                "query": query,
                "format": "json",
                "pageSize": limit,
                "resultType": "core"
            }
        )

        papers = []

        for paper in data.get("resultList", {}).get("result", []):
            pmid = paper.get("pmid", "")
            pmcid = paper.get("pmcid", "")
            doi = paper.get("doi", "")

            if pmcid:
                url = f"https://europepmc.org/articles/{pmcid}"
            elif pmid:
                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            elif doi:
                url = f"https://doi.org/{doi}"
            else:
                url = "https://europepmc.org/"

            papers.append({
                "title": paper.get("title", "제목 없음"),
                "authors": paper.get("authorString", "저자 정보 없음"),
                "year": paper.get("pubYear", "연도 미상"),
                "journal": paper.get("journalTitle", "학술지 정보 없음"),
                "abstract": paper.get("abstractText", ""),
                "url": url
            })

        return papers

    except Exception as e:
        st.error(f"논문 검색 오류: {e}")
        return []


def display_papers(papers):
    if not papers:
        st.info("관련 논문을 찾지 못했습니다.")
        return

    for i, paper in enumerate(papers, 1):
        with st.container(border=True):
            st.markdown(f"**{i}. {paper['title']}**")
            st.caption(f"{paper['year']} · {paper['journal']}")
            st.write(f"저자: {paper['authors']}")

            if paper.get("abstract"):
                with st.expander("초록 보기"):
                    st.write(paper["abstract"])

            st.markdown(f"[논문 정보 보기]({paper['url']})")


def paper_search_panel():
    st.markdown("### 📚 관련 논문 검색")

    query = st.text_input(
        "단백질명, 유전자명 또는 연구 키워드",
        key="paper_query"
    )

    limit = st.selectbox(
        "검색할 논문 수",
        [5, 10, 15],
        key="paper_limit"
    )

    if st.button("논문 검색하기", key="paper_search_button"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("논문 검색 중..."):
                st.session_state["paper_results"] = search_papers(
                    query, limit
                )

    display_papers(st.session_state.get("paper_results", []))


# =========================================================
# 단백질 서열 비교
# =========================================================
def compare_sequences(sequence_a, sequence_b):
    sequence_a = "".join(sequence_a.split()).upper()
    sequence_b = "".join(sequence_b.split()).upper()

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignment = aligner.align(sequence_a, sequence_b)[0]
    counts = alignment.counts()

    total = counts.identities + counts.mismatches + counts.gaps
    identity = counts.identities / total * 100 if total else 0

    return alignment, identity, counts


def protein_comparison_panel():
    st.markdown("## ⚖️ 단백질 비교")

    st.markdown("""
    <div class="info-box">
    비교할 단백질의 이름이나 유전자명을 입력하세요.
    예: <b>TP53</b>, <b>insulin</b>,
    <b>hemoglobin subunit beta</b><br>
    Accession 코드를 미리 알 필요가 없습니다.
    </div>
    """, unsafe_allow_html=True)

    with st.form("comparison_form"):
        col1, col2 = st.columns(2)

        with col1:
            name_a = st.text_input(
                "첫 번째 단백질 이름",
                placeholder="예: insulin"
            )

        with col2:
            name_b = st.text_input(
                "두 번째 단백질 이름",
                placeholder="예: glucagon"
            )

        submitted = st.form_submit_button(
            "🔎 단백질 이름 검색하기",
            use_container_width=True
        )

    if submitted:
        if not name_a.strip() or not name_b.strip():
            st.warning("두 단백질 이름을 모두 입력해 주세요.")
        else:
            with st.spinner("단백질을 검색하고 있습니다..."):
                results_a = find_protein_candidates(name_a)
                results_b = find_protein_candidates(name_b)

            st.session_state["comparison_candidates_a"] = results_a
            st.session_state["comparison_candidates_b"] = results_b
            st.session_state["comparison_result"] = None

    results_a = st.session_state.get("comparison_candidates_a", [])
    results_b = st.session_state.get("comparison_candidates_b", [])

    if not results_a or not results_b:
        if "comparison_candidates_a" in st.session_state:
            st.warning(
                "검색 결과가 부족합니다. 단백질 이름이나 유전자명을 "
                "다르게 입력해 보세요."
            )
        return

    col1, col2 = st.columns(2)

    with col1:
        index_a = st.selectbox(
            "첫 번째 단백질 선택",
            range(len(results_a)),
            format_func=lambda i: candidate_label(results_a[i]),
            key="comparison_select_a"
        )

    with col2:
        index_b = st.selectbox(
            "두 번째 단백질 선택",
            range(len(results_b)),
            format_func=lambda i: candidate_label(results_b[i]),
            key="comparison_select_b"
        )

    if st.button(
        "🧬 두 단백질 비교하기",
        use_container_width=True,
        key="run_comparison"
    ):
        accession_a = results_a[index_a]["accession"]
        accession_b = results_b[index_b]["accession"]

        if accession_a == accession_b:
            st.warning("서로 다른 단백질을 선택해 주세요.")
        else:
            with st.spinner("단백질 서열과 기능을 불러오는 중..."):
                protein_a = get_protein(accession_a)
                protein_b = get_protein(accession_b)

                if (
                    protein_a and protein_b
                    and protein_a.get("sequence")
                    and protein_b.get("sequence")
                ):
                    try:
                        alignment, identity, counts = compare_sequences(
                            protein_a["sequence"],
                            protein_b["sequence"]
                        )

                        st.session_state["comparison_result"] = {
                            "a": protein_a,
                            "b": protein_b,
                            "identity": identity,
                            "identities": counts.identities,
                            "mismatches": counts.mismatches,
                            "gaps": counts.gaps,
                            "alignment": str(alignment)
                        }
                    except Exception as e:
                        st.error(f"서열 비교 오류: {e}")
                else:
                    st.error("단백질 서열을 가져오지 못했습니다.")

    result = st.session_state.get("comparison_result")

    if result:
        st.markdown("---")
        st.markdown("### 📊 비교 결과")

        col1, col2 = st.columns(2)

        with col1:
            protein_card(result["a"], suffix="compare_a")

        with col2:
            protein_card(result["b"], suffix="compare_b")

        c1, c2, c3 = st.columns(3)
        c1.metric("서열 일치도", f"{result['identity']:.2f}%")
        c2.metric("일치하는 위치", f"{result['identities']:,}")
        c3.metric(
            "불일치 및 갭",
            f"{result['mismatches'] + result['gaps']:,}"
        )

        with st.expander("🧬 정렬된 아미노산 서열 보기"):
            st.code(result["alignment"], language="text")

        st.markdown("""
        <div class="info-box">
        서열 일치도는 아미노산 서열의 유사성을 보여주는 지표입니다.
        일치도가 높더라도 단백질의 기능이나 생물학적 효과가
        반드시 같다는 뜻은 아닙니다.
        </div>
        """, unsafe_allow_html=True)


# =========================================================
# 단백질 검색 페이지
# =========================================================
def protein_search_page():
    st.markdown("## 🔎 단백질 검색")
    query = st.text_input(
        "단백질 이름 또는 유전자명",
        placeholder="예: insulin, TP53, hemoglobin",
        key="protein_search_query"
    )

    if st.button("단백질 검색", key="protein_search_button"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("단백질 검색 중..."):
                st.session_state["protein_search_results"] = (
                    search_proteins(query)
                )

    results = st.session_state.get("protein_search_results", [])

    if results:
        selected_index = st.selectbox(
            "자세히 볼 단백질 선택",
            range(len(results)),
            format_func=lambda i: candidate_label(results[i]),
            key="protein_search_selected"
        )

        selected = results[selected_index]

        with st.spinner("단백질 상세 정보 불러오는 중..."):
            detail = get_protein(selected["accession"])

        if detail:
            protein_card(detail, suffix="protein_search")

            if detail.get("sequence"):
                with st.expander("🧬 아미노산 서열 보기"):
                    sequence = detail["sequence"]
                    st.code(
                        "\n".join(
                            sequence[i:i + 60]
                            for i in range(0, len(sequence), 60)
                        ),
                        language="text"
                    )

            st.markdown("---")
            st.markdown("### 📚 관련 논문")

            papers = search_papers(
                detail.get("protein_name")
                or detail.get("gene_names")
                or detail.get("accession"),
                5
            )
            display_papers(papers)


# =========================================================
# 신약 연구 탐색
# =========================================================
def drug_research_page():
    st.markdown("## 🧪 신약 연구 탐색")

    st.markdown("""
    <div class="info-box">
    단백질 표적 및 관련 논문을 탐색하는 교육용 기능입니다.
    검색 결과만으로 약물의 효능이나 안전성이 검증되는 것은 아닙니다.
    </div>
    """, unsafe_allow_html=True)

    query = st.text_input(
        "단백질 또는 질환 키워드",
        placeholder="예: EGFR cancer, TP53, insulin resistance",
        key="drug_research_query"
    )

    if st.button("연구 자료 탐색", key="drug_research_button"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("연구 자료 검색 중..."):
                st.session_state["drug_proteins"] = search_proteins(
                    query, 5
                )
                st.session_state["drug_papers"] = search_papers(
                    query, 5
                )

    proteins = st.session_state.get("drug_proteins", [])
    papers = st.session_state.get("drug_papers", [])

    if proteins or papers:
        st.markdown("### 🧬 관련 단백질")

        for i, protein in enumerate(proteins):
            with st.container(border=True):
                st.markdown(f"**{get_protein_name(protein)}**")
                st.write(
                    f"유전자명: {safe_text(protein.get('gene_names'))}"
                )
                st.write(
                    f"생물종: {safe_text(protein.get('organism'))}"
                )
                st.markdown(
                    f"[UniProt 정보 보기]({protein.get('url', '#')})"
                )

                if st.button(
                    "기능 설명 보기",
                    key=f"drug_function_{i}_{protein.get('accession')}"
                ):
                    with st.spinner("기능 정보를 불러오는 중..."):
                        detail = get_protein(protein["accession"])
                        if detail:
                            st.session_state[
                                f"drug_detail_{protein['accession']}"
                            ] = detail

                detail = st.session_state.get(
                    f"drug_detail_{protein['accession']}"
                )
                if detail:
                    render_function_translation(
                        detail, f"drug_{protein['accession']}"
                    )

        st.markdown("### 📚 관련 연구 논문")
        display_papers(papers)


# =========================================================
# 홈
# =========================================================
def home_page():
    st.markdown("""
    <div class="hero">
        <h1>🧬 BioTarget AI</h1>
        <p>
        단백질 정보를 탐색하고, 아미노산 서열을 비교하며,
        관련 연구 논문을 찾아보는 생명과학 탐구 플랫폼입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="section-card">
            <h3>🔎 단백질 검색</h3>
            <p>단백질 이름과 유전자명으로 정보를 탐색하세요.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="section-card">
            <h3>⚖️ 단백질 비교</h3>
            <p>두 단백질의 아미노산 서열과 일치도를 비교하세요.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="section-card">
            <h3>🧪 신약 연구 탐색</h3>
            <p>관심 있는 단백질 표적과 관련 논문을 찾아보세요.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🌱 활용 방법")
    st.write("- 단백질 검색: 이름이나 유전자명으로 검색")
    st.write("- 단백질 기능: 기능 설명 확인 및 한국어 번역")
    st.write("- 단백질 비교: 두 단백질의 서열 일치도 확인")
    st.write("- 논문 검색: 관련 연구 논문 탐색")
    st.write("- 영문 번역: 논문 초록이나 설명을 한국어로 번역")

    st.markdown("""
    <div class="info-box">
    💡 왼쪽 메뉴에서 원하는 기능을 선택해 시작하세요.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 일반 텍스트 번역 페이지
# =========================================================
def translation_page():
    st.markdown("## 🌐 영문 → 한국어 번역")

    text = st.text_area(
        "번역할 영문 텍스트",
        height=180,
        placeholder="논문 초록이나 단백질 설명을 붙여 넣으세요.",
        key="general_translation_input"
    )

    if st.button("한국어로 번역하기", key="general_translate_button"):
        if not text.strip():
            st.warning("번역할 내용을 입력해 주세요.")
        else:
            with st.spinner("번역 중..."):
                try:
                    st.session_state["general_translation_result"] = (
                        translate_to_korean(text)
                    )
                    st.session_state["general_translation_error"] = ""
                except Exception as e:
                    st.session_state["general_translation_result"] = ""
                    st.session_state["general_translation_error"] = str(e)

    error = st.session_state.get("general_translation_error", "")
    result = st.session_state.get("general_translation_result", "")

    if error:
        st.warning(error)

    if result:
        st.markdown("### 🇰🇷 번역 결과")
        st.text_area(
            "한국어 번역",
            value=result,
            height=220,
            key="general_translation_output"
        )


# =========================================================
# 사이드바 및 메뉴
# =========================================================
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption("단백질 · 생명과학 연구 탐색")
    st.markdown("---")

    page = st.radio(
        "메뉴",
        [
            "🏠 홈",
            "🔎 단백질 검색",
            "⚖️ 단백질 비교",
            "🧪 신약 연구 탐색",
            "📚 논문 검색",
            "🌐 영문 번역"
        ],
        key="main_navigation"
    )

    st.markdown("---")
    st.markdown("""
    <div class="small-note">
    데이터 출처<br>
    UniProt · Europe PMC
    </div>
    """, unsafe_allow_html=True)


if page == "🏠 홈":
    home_page()

elif page == "🔎 단백질 검색":
    protein_search_page()

elif page == "⚖️ 단백질 비교":
    protein_comparison_panel()

elif page == "🧪 신약 연구 탐색":
    drug_research_page()

elif page == "📚 논문 검색":
    st.markdown("## 📚 논문 검색")
    paper_search_panel()

elif page == "🌐 영문 번역":
    translation_page()


st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#7b9ab2; padding:10px;">
BioTarget AI · 생명과학 연구 탐색을 위한 교육용 도구
</div>
""", unsafe_allow_html=True)
