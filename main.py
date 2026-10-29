
import time
import requests
import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from Bio.Align import PairwiseAligner

st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide"
)

# -------------------------
# 디자인
# -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f2f9ff 0%, #ffffff 100%);
}
h1, h2, h3 {
    color: #174a75;
}
div.stButton > button {
    background-color: #dceeff;
    color: #174a75;
    border: 1px solid #b6d9f5;
    border-radius: 10px;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #c5e3ff;
    color: #10395b;
    border-color: #86bff0;
}
[data-testid="stMetric"] {
    background-color: #edf7ff;
    border: 1px solid #d3eaff;
    padding: 12px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧬 BioTarget AI")
st.caption("단백질 정보 · 서열 비교 · 관련 논문 탐색")

# -------------------------
# API 설정
# -------------------------
UNIPROT_URL = "https://rest.uniprot.org"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

HEADERS = {
    "User-Agent": "BioTargetAI/1.0 educational research app"
}


# -------------------------
# UniProt 단백질 검색
# -------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_proteins(keyword, limit=10):
    response = requests.get(
        f"{UNIPROT_URL}/uniprotkb/search",
        params={
            "query": keyword,
            "format": "json",
            "size": limit,
            "fields": (
                "accession,protein_name,gene_names,"
                "organism_name,length,cc_function"
            )
        },
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()
    results = []

    for item in response.json().get("results", []):
        protein_desc = item.get("proteinDescription", {})
        recommended = protein_desc.get(
            "recommendedName", {}
        ).get("fullName", {}).get("value", "")

        if not recommended:
            names = protein_desc.get("submissionNames", [])
            if names:
                recommended = names[0].get(
                    "fullName", {}
                ).get("value", "")

        genes = item.get("genes", [])
        gene_name = ""
        if genes:
            gene_name = genes[0].get(
                "geneName", {}
            ).get("value", "")

        organism = item.get("organism", {}).get(
            "scientificName", "Unknown"
        )

        function_text = ""
        comments = item.get("comments", [])
        for comment in comments:
            if comment.get("commentType") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function_text = texts[0].get(
                        "value", ""
                    )
                    break

        results.append({
            "accession": item.get("primaryAccession", ""),
            "name": recommended or "이름 정보 없음",
            "gene": gene_name or "정보 없음",
            "organism": organism,
            "length": item.get("sequence", {}).get(
                "length", 0
            ),
            "function": function_text or "기능 설명 없음"
        })

    return results


@st.cache_data(ttl=1800, show_spinner=False)
def get_protein_by_accession(accession):
    response = requests.get(
        f"{UNIPROT_URL}/uniprotkb/{accession}.json",
        headers=HEADERS,
        timeout=20
    )
    response.raise_for_status()
    item = response.json()

    protein_desc = item.get("proteinDescription", {})
    name = protein_desc.get(
        "recommendedName", {}
    ).get("fullName", {}).get("value", "")

    if not name:
        submissions = protein_desc.get("submissionNames", [])
        if submissions:
            name = submissions[0].get(
                "fullName", {}
            ).get("value", "")

    genes = item.get("genes", [])
    gene_name = ""
    if genes:
        gene_name = genes[0].get(
            "geneName", {}
        ).get("value", "")

    comments = item.get("comments", [])
    function_text = ""
    for comment in comments:
        if comment.get("commentType") == "FUNCTION":
            texts = comment.get("texts", [])
            if texts:
                function_text = texts[0].get("value", "")
                break

    sequence = item.get("sequence", {}).get("value", "")

    return {
        "accession": item.get("primaryAccession", accession),
        "name": name or "이름 정보 없음",
        "gene": gene_name or "정보 없음",
        "organism": item.get("organism", {}).get(
            "scientificName", "Unknown"
        ),
        "length": len(sequence),
        "function": function_text or "기능 설명 없음",
        "sequence": sequence,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}"
    }


# -------------------------
# 번역
# -------------------------
@st.cache_data(ttl=86400, show_spinner=False)
def translate_to_korean(text):
    """
    번역 성공 결과를 하루 동안 캐싱한다.
    MyMemory를 먼저 사용하고 실패할 때 Google을 한 번 시도한다.
    """
    if not text or not text.strip():
        return {
            "success": False,
            "text": "",
            "provider": "",
            "error": "번역할 문장이 없습니다."
        }

    text = text.strip()

    # 너무 긴 문장은 번역 서비스의 제한에 걸릴 수 있으므로 제한
    text = text[:4000]

    errors = []

    # 1. MyMemory: 언어 코드를 en-GB / ko-KR로 지정
    try:
        translator = MyMemoryTranslator(
            source="en-GB",
            target="ko-KR"
        )
        result = translator.translate(text)

        if result and result.strip():
            return {
                "success": True,
                "text": result.strip(),
                "provider": "MyMemory",
                "error": ""
            }

        errors.append("MyMemory: 번역 결과가 비어 있습니다.")

    except Exception as exc:
        errors.append(f"MyMemory: {type(exc).__name__}: {exc}")

    # 2. Google: 요청 제한에 걸릴 수 있으므로 한 번만 시도
    try:
        translator = GoogleTranslator(
            source="auto",
            target="ko"
        )
        result = translator.translate(text)

        if result and result.strip():
            return {
                "success": True,
                "text": result.strip(),
                "provider": "Google Translate",
                "error": ""
            }

        errors.append("Google Translate: 번역 결과가 비어 있습니다.")

    except Exception as exc:
        errors.append(f"Google Translate: {type(exc).__name__}: {exc}")

    return {
        "success": False,
        "text": "",
        "provider": "",
        "error": "\n\n".join(errors)
    }


# -------------------------
# Europe PMC 논문 검색
# -------------------------
@st.cache_data(ttl=1800, show_spinner=False)
def search_papers(keyword, limit=8):
    response = requests.get(
        f"{EUROPE_PMC_URL}/search",
        params={
            "query": keyword,
            "format": "json",
            "pageSize": limit,
            "resultType": "core"
        },
        headers=HEADERS,
        timeout=25
    )
    response.raise_for_status()

    data = response.json()
    papers = []

    for item in data.get("resultList", {}).get("result", []):
        title = item.get("title", "제목 없음")
        authors = item.get("authorString", "저자 정보 없음")
        journal = item.get("journalTitle", "학술지 정보 없음")
        year = item.get("pubYear", "")
        abstract = item.get("abstractText", "")
        pmid = item.get("pmid", "")
        pmcid = item.get("pmcid", "")
        doi = item.get("doi", "")

        if pmcid:
            url = f"https://europepmc.org/articles/{pmcid}"
        elif pmid:
            url = f"https://europepmc.org/article/MED/{pmid}"
        elif doi:
            url = f"https://doi.org/{doi}"
        else:
            url = "https://europepmc.org/"

        papers.append({
            "title": title,
            "authors": authors,
            "journal": journal,
            "year": year,
            "abstract": abstract,
            "url": url
        })

    return papers


# -------------------------
# 사이드바
# -------------------------
with st.sidebar:
    st.header("🔬 메뉴")
    page = st.radio(
        "기능 선택",
        [
            "단백질 검색",
            "단백질 서열 비교",
            "논문 검색"
        ]
    )

    st.markdown("---")
    st.caption("데이터 출처: UniProt · Europe PMC")
    st.caption("교육 및 탐색용 도구이며 임상적 판단을 대신하지 않습니다.")


# -------------------------
# 논문 검색 UI
# -------------------------
def show_paper_search(default_query=""):
    st.subheader("📚 관련 논문 검색")
    st.caption("영어 검색어 또는 단백질 이름을 입력하세요.")

    query = st.text_input(
        "논문 검색어",
        value=default_query,
        key=f"paper_query_{page}"
    )

    if st.button("논문 찾기", key=f"paper_search_button_{page}"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("Europe PMC에서 논문을 찾는 중..."):
                    papers = search_papers(query.strip())

                if not papers:
                    st.info("검색 결과가 없습니다. 다른 검색어로 시도해 보세요.")
                else:
                    st.success(f"논문 {len(papers)}편을 찾았습니다.")

                    for index, paper in enumerate(papers):
                        with st.expander(
                            f"{paper['title']} ({paper['year'] or '연도 미상'})"
                        ):
                            st.write(
                                f"**저자:** {paper['authors']}"
                            )
                            st.write(
                                f"**학술지:** {paper['journal']}"
                            )

                            st.markdown(
                                f"[논문 원문 또는 상세 정보 열기]({paper['url']})"
                            )

                            if paper["abstract"]:
                                st.markdown("**초록 (Abstract)**")
                                st.write(paper["abstract"])

                                translation_key = (
                                    f"abstract_translation_{page}_{index}"
                                )

                                if st.button(
                                    "초록 한국어 번역",
                                    key=translation_key
                                ):
                                    with st.spinner("번역 중..."):
                                        translated = translate_to_korean(
                                            paper["abstract"]
                                        )

                                    st.session_state[
                                        f"translated_{translation_key}"
                                    ] = translated

                                saved = st.session_state.get(
                                    f"translated_{translation_key}"
                                )

                                if saved:
                                    if saved["success"]:
                                        st.markdown("**한국어 번역**")
                                        st.write(saved["text"])
                                        st.caption(
                                            f"번역 서비스: {saved['provider']}"
                                        )
                                    else:
                                        st.warning(
                                            "번역에 실패했습니다. 원문 초록은 위에서 확인할 수 있습니다."
                                        )
                                        with st.expander("번역 오류 자세히 보기"):
                                            st.code(saved["error"])

                            else:
                                st.info("제공된 초록이 없는 논문입니다.")

            except requests.RequestException as exc:
                st.error("논문 검색 중 통신 오류가 발생했습니다.")
                st.code(str(exc))
            except Exception as exc:
                st.error("논문 검색 중 오류가 발생했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")


# -------------------------
# 페이지 1: 단백질 검색
# -------------------------
if page == "단백질 검색":
    st.header("🧬 단백질 검색")
    st.write(
        "단백질 이름, 유전자 이름 또는 관련 키워드로 UniProt 정보를 검색합니다."
    )

    keyword = st.text_input(
        "검색어 입력",
        placeholder="예: insulin, TP53, hemoglobin",
        key="protein_keyword"
    )

    if st.button("단백질 검색", key="protein_search_button"):
        if not keyword.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("UniProt 데이터베이스 검색 중..."):
                    results = search_proteins(keyword.strip())

                st.session_state["protein_results"] = results

                if not results:
                    st.info("검색 결과가 없습니다. 다른 검색어를 입력해 보세요.")

            except Exception as exc:
                st.error("단백질 검색에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    results = st.session_state.get("protein_results", [])

    if results:
        st.success(f"검색 결과: {len(results)}개")

        for index, protein in enumerate(results):
            with st.expander(
                f"{protein['name']} — {protein['accession']}"
            ):
                st.write(f"**유전자:** {protein['gene']}")
                st.write(f"**생물종:** {protein['organism']}")
                st.write(f"**아미노산 길이:** {protein['length']}")
                st.markdown(
                    f"[UniProt 상세 정보](https://www.uniprot.org/uniprotkb/{protein['accession']})"
                )

                st.markdown("**기능 설명 (영어 원문)**")
                st.write(protein["function"])

                if protein["function"] != "기능 설명 없음":
                    translation_key = f"protein_translation_{index}"

                    if st.button(
                        "기능 설명 한국어 번역",
                        key=translation_key
                    ):
                        with st.spinner("번역 중..."):
                            translated = translate_to_korean(
                                protein["function"]
                            )

                        st.session_state[
                            f"translated_{translation_key}"
                        ] = translated

                    saved = st.session_state.get(
                        f"translated_{translation_key}"
                    )

                    if saved:
                        if saved["success"]:
                            st.markdown("**한국어 번역**")
                            st.write(saved["text"])
                            st.caption(
                                f"번역 서비스: {saved['provider']}"
                            )
                        else:
                            st.warning(
                                "자동 번역에 실패했습니다. 영어 원문은 그대로 확인할 수 있습니다."
                            )
                            with st.expander("번역 오류 자세히 보기"):
                                st.code(saved["error"])


# -------------------------
# 페이지 2: 단백질 서열 비교
# -------------------------
elif page == "단백질 서열 비교":
    st.header("🧪 단백질 서열 비교")
    st.write(
        "UniProt accession을 입력해 두 단백질의 아미노산 서열을 비교합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        accession1 = st.text_input(
            "첫 번째 단백질 accession",
            placeholder="예: P01308",
            key="accession1"
        )

    with col2:
        accession2 = st.text_input(
            "두 번째 단백질 accession",
            placeholder="예: P68871",
            key="accession2"
        )

    if st.button("서열 비교하기"):
        if not accession1.strip() or not accession2.strip():
            st.warning("두 accession을 모두 입력해 주세요.")
        else:
            try:
                with st.spinner("단백질 정보를 가져오는 중..."):
                    protein1 = get_protein_by_accession(
                        accession1.strip()
                    )
                    protein2 = get_protein_by_accession(
                        accession2.strip()
                    )

                seq1 = protein1["sequence"]
                seq2 = protein2["sequence"]

                if not seq1 or not seq2:
                    st.error("하나 이상의 단백질 서열을 찾을 수 없습니다.")
                else:
                    aligner = PairwiseAligner()
                    aligner.mode = "global"
                    aligner.match_score = 2
                    aligner.mismatch_score = -1
                    aligner.open_gap_score = -2
                    aligner.extend_gap_score = -0.5

                    alignment = aligner.align(seq1, seq2)[0]
                    aligned1, aligned2 = alignment.aligned

                    # 정렬된 구간을 이용해 일치 잔기 수를 계산
                    identical = 0
                    aligned_positions = 0

                    for (start1, end1), (start2, end2) in zip(
                        aligned1, aligned2
                    ):
                        length = min(
                            end1 - start1,
                            end2 - start2
                        )
                        for offset in range(length):
                            aligned_positions += 1
                            if (
                                seq1[start1 + offset]
                                == seq2[start2 + offset]
                            ):
                                identical += 1

                    identity = (
                        identical / aligned_positions * 100
                        if aligned_positions
                        else 0
                    )

                    st.session_state["comparison"] = {
                        "protein1": protein1,
                        "protein2": protein2,
                        "identity": identity,
                        "score": alignment.score
                    }

            except Exception as exc:
                st.error("단백질 서열 비교에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    comparison = st.session_state.get("comparison")

    if comparison:
        p1 = comparison["protein1"]
        p2 = comparison["protein2"]

        left, right = st.columns(2)

        with left:
            st.subheader("첫 번째 단백질")
            st.write(f"**이름:** {p1['name']}")
            st.write(f"**Accession:** {p1['accession']}")
            st.write(f"**생물종:** {p1['organism']}")
            st.write(f"**서열 길이:** {p1['length']}")

        with right:
            st.subheader("두 번째 단백질")
            st.write(f"**이름:** {p2['name']}")
            st.write(f"**Accession:** {p2['accession']}")
            st.write(f"**생물종:** {p2['organism']}")
            st.write(f"**서열 길이:** {p2['length']}")

        st.metric(
            "정렬된 구간의 서열 일치율",
            f"{comparison['identity']:.2f}%"
        )
        st.metric(
            "정렬 점수",
            f"{comparison['score']:.1f}"
        )

        st.caption(
            "서열 일치율은 정렬된 구간에서 계산한 값입니다. "
            "단백질의 기능적 유사성이나 약물 효과를 직접 입증하는 지표는 아닙니다."
        )

        st.markdown("### 관련 논문")
        default_query = f'"{p1["name"]}" OR "{p2["name"]}"'
        show_paper_search(default_query)


# -------------------------
# 페이지 3: 논문 검색
# -------------------------
elif page == "논문 검색":
    st.header("📚 생명과학 논문 검색")
    st.write(
        "Europe PMC를 이용해 단백질, 유전자, 질병 및 생화학 관련 논문을 찾아보세요."
    )
    show_paper_search()
