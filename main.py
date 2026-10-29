import streamlit as st
import requests
import html
from deep_translator import MyMemoryTranslator, GoogleTranslator
from Bio.Align import PairwiseAligner

# =========================================================
# 페이지 설정
# =========================================================
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

.metric-card {
    background: #f0f8ff;
    border: 1px solid #d3e9fa;
    padding: 14px;
    border-radius: 14px;
    text-align: center;
}

div.stButton > button {
    background: linear-gradient(100deg, #258bd0, #36b4c8);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 10px 18px;
    font-weight: 700;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: linear-gradient(100deg, #176eae, #2198ae);
    color: white;
    border: none;
}

div[data-testid="stTextInput"] input {
    border-radius: 10px;
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
def safe_text(value, default="정보 없음"):
    """화면에 표시할 문자열을 안전하게 정리한다."""
    if value is None or str(value).strip() == "":
        return default
    return str(value)


def request_json(url, params=None, timeout=20):
    """API 요청 및 JSON 응답 처리."""
    response = requests.get(
        url,
        params=params,
        timeout=timeout,
        headers={"User-Agent": "BioTargetAI/1.0"}
    )
    response.raise_for_status()
    return response.json()


def get_protein_name(protein):
    """단백질의 대표 이름을 반환한다."""
    return (
        protein.get("protein_name")
        or protein.get("gene_names")
        or protein.get("accession")
        or "이름 없음"
    )


def get_protein_label(protein):
    """검색 결과 선택창에 표시할 단백질 정보."""
    name = get_protein_name(protein)
    gene = protein.get("gene_names", "")
    accession = protein.get("accession", "")
    organism = protein.get("organism", "")

    parts = [name]

    if gene and gene.lower() not in name.lower():
        parts.append(f"유전자: {gene}")

    if organism:
        parts.append(organism)

    if accession:
        parts.append(f"Accession: {accession}")

    return " | ".join(parts)


# =========================================================
# UniProt 단백질 검색
# =========================================================
def search_proteins(query, limit=10):
    """
    단백질 이름, 유전자명 또는 accession으로 UniProt 검색.
    결과에는 accession, 이름, 유전자, 생물종 등의 정보가 포함된다.
    """
    query = str(query).strip()

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

            protein_description = (
                item.get("proteinDescription", {})
                .get("recommendedName", {})
                .get("fullName", {})
                .get("value", "")
            )

            if not protein_description:
                submission_names = (
                    item.get("proteinDescription", {})
                    .get("submissionNames", [])
                )

                if submission_names:
                    protein_description = (
                        submission_names[0]
                        .get("fullName", {})
                        .get("value", "")
                    )

            gene_list = item.get("genes", [])
            gene_names = []

            for gene in gene_list:
                gene_name = (
                    gene.get("geneName", {}).get("value", "")
                )
                if gene_name:
                    gene_names.append(gene_name)

            organism = (
                item.get("organism", {}).get("scientificName", "")
            )

            sequence_info = item.get("sequence", {})
            length = sequence_info.get("length", None)

            results.append({
                "accession": accession,
                "protein_name": protein_description,
                "gene_names": ", ".join(gene_names),
                "organism": organism,
                "length": length,
                "url": (
                    f"https://www.uniprot.org/uniprotkb/{accession}"
                )
            })

        return results

    except Exception as e:
        st.error(f"UniProt 검색 중 오류가 발생했습니다: {e}")
        return []


def get_protein(accession):
    """UniProt accession으로 단백질 상세 정보와 서열을 조회한다."""
    accession = str(accession).strip()

    if not accession:
        return None

    try:
        data = request_json(
            f"{UNIPROT_URL}/uniprotkb/{accession}.json"
        )

        protein_description = (
            data.get("proteinDescription", {})
            .get("recommendedName", {})
            .get("fullName", {})
            .get("value", "")
        )

        if not protein_description:
            submission_names = (
                data.get("proteinDescription", {})
                .get("submissionNames", [])
            )
            if submission_names:
                protein_description = (
                    submission_names[0]
                    .get("fullName", {})
                    .get("value", "")
                )

        gene_list = data.get("genes", [])
        gene_names = []

        for gene in gene_list:
            gene_name = (
                gene.get("geneName", {}).get("value", "")
            )
            if gene_name:
                gene_names.append(gene_name)

        organism = (
            data.get("organism", {}).get("scientificName", "")
        )

        sequence_info = data.get("sequence", {})

        return {
            "accession": data.get("primaryAccession", accession),
            "protein_name": protein_description,
            "gene_names": ", ".join(gene_names),
            "organism": organism,
            "length": sequence_info.get("length"),
            "sequence": sequence_info.get("value", ""),
            "url": (
                f"https://www.uniprot.org/uniprotkb/{accession}"
            )
        }

    except Exception as e:
        st.error(
            f"단백질 상세 정보를 가져오지 못했습니다: {e}"
        )
        return None


# =========================================================
# 논문 검색
# =========================================================
def search_papers(query, limit=5):
    """Europe PMC에서 관련 논문을 검색한다."""
    query = str(query).strip()

    if not query:
        return []

    params = {
        "query": query,
        "format": "json",
        "pageSize": limit,
        "resultType": "core"
    }

    try:
        data = request_json(
            f"{EUROPE_PMC_URL}/search",
            params=params
        )

        results = []

        for paper in data.get("resultList", {}).get("result", []):
            title = paper.get("title", "제목 없음")
            authors = paper.get("authorString", "저자 정보 없음")
            year = paper.get("pubYear", "연도 미상")
            journal = paper.get("journalTitle", "학술지 정보 없음")
            abstract = paper.get("abstractText", "")
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

            results.append({
                "title": title,
                "authors": authors,
                "year": year,
                "journal": journal,
                "abstract": abstract,
                "url": url,
                "pmid": pmid,
                "doi": doi
            })

        return results

    except Exception as e:
        st.error(f"논문 검색 중 오류가 발생했습니다: {e}")
        return []


def paper_search_panel(default_query=""):
    """논문 검색 패널."""
    st.markdown("### 📚 관련 논문 검색")

    query = st.text_input(
        "단백질명, 유전자명 또는 연구 키워드",
        value=default_query,
        key="paper_query"
    )

    limit = st.selectbox(
        "검색할 논문 수",
        [5, 10, 15],
        index=0,
        key="paper_limit"
    )

    if st.button("논문 검색하기", key="paper_search_button"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("관련 논문을 검색하고 있습니다..."):
                st.session_state["paper_results"] = search_papers(
                    query, limit
                )
                st.session_state["paper_last_query"] = query

    papers = st.session_state.get("paper_results", [])

    if papers:
        st.markdown(
            f"**검색어:** {st.session_state.get('paper_last_query', '')}"
        )

        for index, paper in enumerate(papers, start=1):
            with st.container(border=True):
                st.markdown(f"**{index}. {paper['title']}**")
                st.caption(
                    f"{paper['year']} · {paper['journal']}"
                )
                st.write(f"저자: {paper['authors']}")

                if paper.get("abstract"):
                    with st.expander("초록 보기"):
                        st.write(paper["abstract"])

                st.markdown(f"[논문 원문 및 정보 보기]({paper['url']})")


# =========================================================
# 단백질 카드
# =========================================================
def protein_card(protein):
    """단백질 정보를 카드 형태로 표시한다."""
    accession = protein.get("accession", "")
    protein_url = (
        protein.get("url")
        or f"https://www.uniprot.org/uniprotkb/{accession}"
    )

    name = html.escape(
        safe_text(protein.get("protein_name", "이름 없음"))
    )
    gene = html.escape(
        safe_text(protein.get("gene_names", "정보 없음"))
    )
    organism = html.escape(
        safe_text(protein.get("organism", "정보 없음"))
    )
    accession_safe = html.escape(
        safe_text(accession)
    )
    length = protein.get("length")

    length_text = (
        f"{length:,}개 아미노산"
        if isinstance(length, int)
        else "정보 없음"
    )

    st.markdown(
        f"""
        <div class="section-card">
            <div class="protein-title">{name}</div>
            <p>🧬 <b>유전자명:</b> {gene}</p>
            <p>🌎 <b>생물종:</b> {organism}</p>
            <p>🔖 <b>Accession:</b> {accession_safe}</p>
            <p>📏 <b>서열 길이:</b> {length_text}</p>
            <a href="{html.escape(protein_url, quote=True)}"
               target="_blank">UniProt에서 자세히 보기 ↗</a>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 번역
# =========================================================
def translate_to_korean(text):
    """영문 텍스트를 한국어로 번역한다."""
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
        "잠시 후 다시 시도해 주세요. "
        + " / ".join(errors)
    )


def translation_panel():
    """영문 텍스트 번역 패널."""
    st.markdown("### 🌐 영문 → 한국어 번역")

    source_text = st.text_area(
        "번역할 영문 텍스트",
        height=150,
        placeholder="논문 초록이나 단백질 설명을 붙여 넣으세요.",
        key="translation_source"
    )

    if st.button("한국어로 번역하기", key="translate_button"):
        if not source_text.strip():
            st.warning("번역할 내용을 입력해 주세요.")
        else:
            with st.spinner("번역 중입니다..."):
                try:
                    translated = translate_to_korean(source_text)
                    st.session_state["translated_text"] = translated
                except Exception as e:
                    st.session_state["translated_text"] = ""
                    st.warning(str(e))

    translated_text = st.session_state.get("translated_text", "")

    if translated_text:
        st.markdown("#### 번역 결과")
        st.text_area(
            "한국어 번역",
            value=translated_text,
            height=200,
            key="translation_output"
        )


# =========================================================
# 단백질 이름으로 검색 결과 선택
# =========================================================
def find_protein_candidates(protein_name, limit=10):
    """
    사용자가 입력한 이름으로 UniProt를 검색한다.
    accession을 직접 입력하지 않아도 단백질 후보를 찾을 수 있다.
    """
    protein_name = protein_name.strip()

    if not protein_name:
        return []

    # 먼저 이름 그대로 검색한다.
    results = search_proteins(protein_name, limit=limit)

    if results:
        return results

    # 결과가 없으면 유전자명/단백질명 필드로 다시 검색한다.
    escaped_name = protein_name.replace('"', '\\"')
    field_query = (
        f'(gene:{escaped_name}) OR '
        f'(protein_name:"{escaped_name}")'
    )

    return search_proteins(field_query, limit=limit)


def candidate_label(protein):
    """비교 대상 후보를 선택할 때 표시할 문구."""
    name = get_protein_name(protein)
    gene = protein.get("gene_names", "")
    organism = protein.get("organism", "")
    accession = protein.get("accession", "")

    details = [name]

    if gene:
        details.append(f"유전자 {gene}")

    if organism:
        details.append(organism)

    if accession:
        details.append(f"UniProt {accession}")

    return " · ".join(details)


# =========================================================
# 단백질 비교
# =========================================================
def compare_sequences(sequence_a, sequence_b):
    """두 단백질 서열을 정렬하고 일치도를 계산한다."""
    sequence_a = "".join(sequence_a.split()).upper()
    sequence_b = "".join(sequence_b.split()).upper()

    if not sequence_a or not sequence_b:
        raise ValueError("비교할 단백질 서열이 비어 있습니다.")

    aligner = PairwiseAligner()
    aligner.mode = "global"
    aligner.match_score = 2
    aligner.mismatch_score = -1
    aligner.open_gap_score = -5
    aligner.extend_gap_score = -0.5

    alignment = aligner.align(sequence_a, sequence_b)[0]
    counts = alignment.counts()

    denominator = (
        counts.identities
        + counts.mismatches
        + counts.gaps
    )

    identity = (
        counts.identities / denominator * 100
        if denominator
        else 0.0
    )

    return alignment, identity, counts


def protein_comparison_panel():
    """
    단백질 비교 화면.
    사용자에게 accession 대신 단백질 이름을 입력받고,
    검색 결과에서 원하는 단백질을 선택하도록 한다.
    """
    st.markdown("## ⚖️ 단백질 비교")
    st.markdown(
        """
        <div class="info-box">
        비교할 단백질의 <b>이름 또는 유전자명</b>을 입력하세요.
        예: <code>TP53</code>, <code>insulin</code>,
        <code>hemoglobin subunit beta</code><br>
        UniProt accession 코드를 미리 알 필요가 없습니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("protein_comparison_search_form"):
        col1, col2 = st.columns(2)

        with col1:
            name_a = st.text_input(
                "첫 번째 단백질 이름",
                placeholder="예: insulin",
                key="comparison_name_a"
            )

        with col2:
            name_b = st.text_input(
                "두 번째 단백질 이름",
                placeholder="예: glucagon",
                key="comparison_name_b"
            )

        search_submitted = st.form_submit_button(
            "🔎 단백질 이름 검색하기",
            use_container_width=True
        )

    if search_submitted:
        if not name_a.strip() or not name_b.strip():
            st.warning("두 단백질의 이름을 모두 입력해 주세요.")
        else:
            with st.spinner("입력한 이름에 맞는 단백질을 찾고 있습니다..."):
                candidates_a = find_protein_candidates(name_a)
                candidates_b = find_protein_candidates(name_b)

            st.session_state["comparison_candidates_a"] = candidates_a
            st.session_state["comparison_candidates_b"] = candidates_b
            st.session_state["comparison_search_name_a"] = name_a.strip()
            st.session_state["comparison_search_name_b"] = name_b.strip()
            st.session_state["comparison_result"] = None

    candidates_a = st.session_state.get(
        "comparison_candidates_a", []
    )
    candidates_b = st.session_state.get(
        "comparison_candidates_b", []
    )

    if st.session_state.get("comparison_search_name_a") and (
        not candidates_a or not candidates_b
    ):
        missing = []

        if not candidates_a:
            missing.append(
                f"'{st.session_state['comparison_search_name_a']}'"
            )

        if not candidates_b:
            missing.append(
                f"'{st.session_state['comparison_search_name_b']}'"
            )

        if missing:
            st.warning(
                "다음 검색어에 해당하는 단백질을 찾지 못했습니다: "
                + ", ".join(missing)
                + ". 이름이나 유전자명을 바꿔 다시 검색해 주세요."
            )

    if candidates_a and candidates_b:
        st.markdown("### 검색 결과에서 비교할 단백질 선택")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown(
                f"**첫 번째 검색어:** "
                f"{st.session_state.get('comparison_search_name_a', '')}"
            )

            selected_a_index = st.selectbox(
                "첫 번째 단백질",
                options=list(range(len(candidates_a))),
                format_func=lambda i: candidate_label(candidates_a[i]),
                key="comparison_select_a"
            )

        with col2:
            st.markdown(
                f"**두 번째 검색어:** "
                f"{st.session_state.get('comparison_search_name_b', '')}"
            )

            selected_b_index = st.selectbox(
                "두 번째 단백질",
                options=list(range(len(candidates_b))),
                format_func=lambda i: candidate_label(candidates_b[i]),
                key="comparison_select_b"
            )

        protein_a = candidates_a[selected_a_index]
        protein_b = candidates_b[selected_b_index]

        if st.button(
            "🧬 두 단백질 비교하기",
            key="run_protein_comparison",
            use_container_width=True
        ):
            accession_a = protein_a.get("accession", "")
            accession_b = protein_b.get("accession", "")

            if accession_a == accession_b:
                st.warning(
                    "같은 단백질이 선택되었습니다. "
                    "서로 다른 단백질을 선택해 주세요."
                )
            else:
                with st.spinner("단백질 서열을 가져와 비교하고 있습니다..."):
                    detail_a = get_protein(accession_a)
                    detail_b = get_protein(accession_b)

                    if (
                        detail_a
                        and detail_b
                        and detail_a.get("sequence")
                        and detail_b.get("sequence")
                    ):
                        try:
                            alignment, identity, counts = compare_sequences(
                                detail_a["sequence"],
                                detail_b["sequence"]
                            )

                            st.session_state["comparison_result"] = {
                                "protein_a": detail_a,
                                "protein_b": detail_b,
                                "identity": identity,
                                "counts": {
                                    "identities": counts.identities,
                                    "mismatches": counts.mismatches,
                                    "gaps": counts.gaps
                                },
                                "alignment": str(alignment)
                            }

                        except Exception as e:
                            st.error(f"서열 비교 중 오류가 발생했습니다: {e}")
                            st.session_state["comparison_result"] = None
                    else:
                        st.error(
                            "선택한 단백질의 서열을 가져오지 못했습니다. "
                            "다른 검색 결과를 선택해 다시 시도해 주세요."
                        )
                        st.session_state["comparison_result"] = None

    comparison = st.session_state.get("comparison_result")

    if comparison:
        protein_a = comparison["protein_a"]
        protein_b = comparison["protein_b"]
        counts = comparison["counts"]

        st.markdown("---")
        st.markdown("### 📊 비교 결과")

        col1, col2 = st.columns(2)

        with col1:
            protein_card(protein_a)

        with col2:
            protein_card(protein_b)

        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric(
                "서열 일치도",
                f"{comparison['identity']:.2f}%"
            )

        with metric_col2:
            st.metric(
                "일치하는 위치",
                f"{counts['identities']:,}"
            )

        with metric_col3:
            st.metric(
                "불일치 및 갭",
                f"{counts['mismatches'] + counts['gaps']:,}"
            )

        st.markdown("#### 🧬 서열 정렬 결과")

        with st.expander("정렬된 서열 보기"):
            st.code(
                comparison["alignment"],
                language="text"
            )

        st.markdown(
            """
            <div class="info-box">
            <b>결과 해석:</b> 서열 일치도는 선택한 두 단백질의 아미노산
            서열을 정렬했을 때 일치하는 위치의 비율입니다.
            일치도가 높다고 해서 두 단백질의 기능이나 생물학적 효과가
            완전히 같다는 뜻은 아닙니다.
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 홈 화면
# =========================================================
def home_page():
    st.markdown(
        """
        <div class="hero">
            <h1>🧬 BioTarget AI</h1>
            <p>
                단백질 정보를 탐색하고, 아미노산 서열을 비교하며,
                관련 연구 논문을 찾아보는 생명과학 탐구 플랫폼입니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="section-card">
                <h3>🔎 단백질 검색</h3>
                <p>단백질 이름이나 유전자명으로 정보를 찾아보세요.</p>
                <p class="small-note">
                UniProt의 단백질 정보와 아미노산 서열을 활용합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            """
            <div class="section-card">
                <h3>⚖️ 단백질 비교</h3>
                <p>두 단백질의 서열을 정렬하고 일치도를 확인하세요.</p>
                <p class="small-note">
                accession 코드 대신 단백질 이름으로 검색할 수 있습니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <div class="section-card">
                <h3>🧪 신약 연구 탐색</h3>
                <p>단백질 표적과 관련 연구 논문을 탐색하세요.</p>
                <p class="small-note">
                교육 및 연구 주제 탐색을 위한 정보입니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("### 🌱 이렇게 활용해 보세요")

    st.markdown(
        """
        - **단백질 검색:** 관심 있는 단백질의 이름이나 유전자명을 검색합니다.
        - **단백질 비교:** 두 단백질의 아미노산 서열이 얼마나 유사한지 확인합니다.
        - **논문 검색:** 단백질 또는 연구 키워드와 관련된 논문을 찾아봅니다.
        - **번역:** 영어 논문 초록이나 단백질 설명을 한국어로 번역합니다.
        """
    )

    st.markdown(
        """
        <div class="info-box">
        💡 왼쪽 메뉴에서 원하는 기능을 선택해 시작하세요.
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 단백질 검색 화면
# =========================================================
def protein_search_page():
    st.markdown("## 🔎 단백질 검색")
    st.write(
        "단백질 이름, 유전자명 또는 UniProt accession을 입력하면 "
        "관련 정보를 검색할 수 있습니다."
    )

    query = st.text_input(
        "단백질 검색어",
        placeholder="예: insulin, TP53, hemoglobin",
        key="protein_search_query"
    )

    if st.button("단백질 검색", key="protein_search_button"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            with st.spinner("단백질 정보를 검색하고 있습니다..."):
                st.session_state["protein_search_results"] = (
                    search_proteins(query, limit=10)
                )
                st.session_state["protein_search_last_query"] = query

    results = st.session_state.get("protein_search_results", [])

    if results:
        st.markdown(
            f"### 검색 결과: {len(results)}개"
        )

        labels = [candidate_label(p) for p in results]

        selected_index = st.selectbox(
            "자세히 볼 단백질 선택",
            options=list(range(len(results))),
            format_func=lambda i: labels[i],
            key="protein_search_selected"
        )

        selected = results[selected_index]

        detail = get_protein(selected["accession"])

        if detail:
            protein_card(detail)

            sequence = detail.get("sequence", "")

            if sequence:
                st.markdown("### 🧬 아미노산 서열")

                st.caption(
                    f"서열 길이: {len(sequence):,}개 아미노산"
                )

                with st.expander("서열 보기"):
                    st.code(
                        "\n".join(
                            sequence[i:i + 60]
                            for i in range(0, len(sequence), 60)
                        ),
                        language="text"
                    )

            st.markdown("---")
            st.markdown("### 📚 이 단백질과 관련된 논문")

            papers = search_papers(
                detail.get("protein_name")
                or detail.get("gene_names")
                or detail.get("accession"),
                limit=5
            )

            if papers:
                for index, paper in enumerate(papers, start=1):
                    with st.container(border=True):
                        st.markdown(f"**{index}. {paper['title']}**")
                        st.caption(
                            f"{paper['year']} · {paper['journal']}"
                        )
                        st.write(f"저자: {paper['authors']}")

                        if paper.get("abstract"):
                            with st.expander("초록 보기"):
                                st.write(paper["abstract"])

                        st.markdown(
                            f"[논문 정보 보기]({paper['url']})"
                        )
            else:
                st.info("관련 논문을 찾지 못했습니다.")


# =========================================================
# 신약 연구 탐색 화면
# =========================================================
def drug_research_page():
    st.markdown("## 🧪 신약 연구 탐색")
    st.markdown(
        """
        <div class="info-box">
        단백질 표적과 관련된 연구 논문을 탐색하는 교육용 기능입니다.
        검색 결과만으로 실제 약물의 효능이나 안전성이 검증되는 것은 아닙니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    query = st.text_input(
        "관심 있는 단백질 또는 질환 키워드",
        placeholder="예: EGFR cancer, insulin resistance, TP53",
        key="drug_research_query"
    )

    if st.button("연구 자료 탐색", key="drug_research_button"):
        if not query.strip():
            st.warning("단백질명 또는 연구 키워드를 입력해 주세요.")
        else:
            with st.spinner("관련 단백질과 논문을 검색하고 있습니다..."):
                st.session_state["drug_protein_results"] = (
                    search_proteins(query, limit=5)
                )
                st.session_state["drug_paper_results"] = (
                    search_papers(query, limit=5)
                )
                st.session_state["drug_research_last_query"] = query

    protein_results = st.session_state.get(
        "drug_protein_results", []
    )
    paper_results = st.session_state.get(
        "drug_paper_results", []
    )

    if protein_results or paper_results:
        st.markdown("### 🧬 관련 단백질")

        if protein_results:
            for protein in protein_results:
                with st.container(border=True):
                    st.markdown(
                        f"**{safe_text(protein.get('protein_name'))}**"
                    )
                    st.write(
                        f"유전자명: {safe_text(protein.get('gene_names'))}"
                    )
                    st.write(
                        f"생물종: {safe_text(protein.get('organism'))}"
                    )
                    st.markdown(
                        f"[UniProt 정보 보기]({protein.get('url', '#')})"
                    )
        else:
            st.info("관련 단백질 정보를 찾지 못했습니다.")

        st.markdown("### 📚 관련 연구 논문")

        if paper_results:
            for index, paper in enumerate(paper_results, start=1):
                with st.container(border=True):
                    st.markdown(f"**{index}. {paper['title']}**")
                    st.caption(
                        f"{paper['year']} · {paper['journal']}"
                    )

                    if paper.get("abstract"):
                        with st.expander("초록 보기"):
                            st.write(paper["abstract"])

                    st.markdown(
                        f"[논문 정보 보기]({paper['url']})"
                    )
        else:
            st.info("관련 논문을 찾지 못했습니다.")


# =========================================================
# 사이드바 메뉴
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
    st.markdown(
        """
        <div class="small-note">
        데이터 출처<br>
        UniProt · Europe PMC
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 페이지 표시
# =========================================================
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
    st.write(
        "단백질명, 유전자명 또는 연구 키워드로 논문을 검색합니다."
    )
    paper_search_panel()

elif page == "🌐 영문 번역":
    st.markdown("## 🌐 영문 번역")
    translation_panel()


# =========================================================
# 하단 안내
# =========================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align:center; color:#7b9ab2; padding:10px;">
        BioTarget AI · 생명과학 연구 탐색을 위한 교육용 도구
    </div>
    """,
    unsafe_allow_html=True
)
