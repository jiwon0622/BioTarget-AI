
import streamlit as st
import pandas as pd
import requests

# =====================================
# 1. 페이지 설정
# =====================================
st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide"
)

API_URL = "https://rest.uniprot.org/uniprotkb/search"

# =====================================
# 2. 디자인
# =====================================
st.markdown("""
<style>
    .stApp {
        background-color: #F5F8FC;
    }

    h1, h2, h3 {
        color: #183B56;
    }

    .hero {
        background: linear-gradient(120deg, #173B57, #347C91);
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 22px;
    }

    .hero h1 {
        color: white;
    }

    .hero p {
        color: #E4F2F8;
        font-size: 16px;
    }

    .info-card {
        background: white;
        border: 1px solid #DCE6EF;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

# =====================================
# 3. UniProt 데이터 처리
# =====================================
def extract_protein(entry):
    """UniProt 응답에서 필요한 단백질 정보를 추출한다."""

    description = entry.get("proteinDescription", {})

    recommended = description.get("recommendedName", {})
    protein_name = (
        recommended.get("fullName", {}).get("value")
    )

    # 권장 이름이 없는 경우 대체 이름 확인
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
    gene_name = "정보 없음"

    if genes:
        gene_name = (
            genes[0].get("geneName", {}).get("value")
            or "정보 없음"
        )

    organism = entry.get("organism", {})
    sequence_data = entry.get("sequence", {})

    # 기능 주석 추출
    functions = []

    for comment in entry.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            for item in comment.get("texts", []):
                value = item.get("value")
                if value:
                    functions.append(value)

    function_text = (
        " ".join(functions)
        if functions
        else "등록된 기능 설명이 없습니다."
    )

    accession = entry.get("primaryAccession", "")

    return {
        "accession": accession,
        "name": protein_name or entry.get("uniProtkbId", accession),
        "gene": gene_name,
        "organism": organism.get("scientificName", "정보 없음"),
        "length": sequence_data.get("length", 0),
        "sequence": sequence_data.get("value", ""),
        "function": function_text,
        "url": f"https://www.uniprot.org/uniprotkb/{accession}"
    }


@st.cache_data(ttl=3600, show_spinner=False)
def search_proteins(query):
    """UniProt에서 검색어와 관련된 단백질을 조회한다."""

    params = {
        "query": query,
        "format": "json",
        "size": 10
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=20
    )

    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])

    proteins = []

    for entry in results:
        protein = extract_protein(entry)

        # 비교에 필요한 서열이 있는 항목만 선택지로 제공
        if protein["accession"] and protein["sequence"]:
            proteins.append(protein)

    return proteins


# =====================================
# 4. 상단 소개
# =====================================
st.markdown("""
<div class="hero">
    <h1>🧬 BioTarget AI</h1>
    <p>AI 기반 신약 연구 탐색 및 표적 단백질 비교 플랫폼</p>
    <p>실제 단백질 데이터로 생명과학적 특성을 탐구하세요.</p>
</div>
""", unsafe_allow_html=True)

st.success(
    "2단계: UniProt API 연결 완료 버전 — "
    "검색 결과는 실제 데이터베이스 응답에 따라 달라집니다."
)

# =====================================
# 5. 사이드바
# =====================================
menu = st.sidebar.radio(
    "메뉴",
    [
        "🏠 홈",
        "🔎 단백질 검색",
        "⚖️ 단백질 비교",
        "🧪 신약 연구 탐색"
    ]
)

st.sidebar.caption(
    "단백질 정보 출처: UniProt"
)

# =====================================
# 6. 검색 결과 상태 초기화
# =====================================
if "results_a" not in st.session_state:
    st.session_state.results_a = []

if "results_b" not in st.session_state:
    st.session_state.results_b = []

# =====================================
# 7. 홈 화면
# =====================================
if menu == "🏠 홈":
    st.header("프로젝트 소개")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🔎 검색</h3>
            <p>실제 단백질 데이터와 기능을 조회합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>⚖️ 비교</h3>
            <p>두 단백질의 기본 특성과 서열을 비교합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🤖 AI 해석</h3>
            <p>다음 단계에서 분석 결과 해석 기능을 연결합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("현재 구현된 기능")

    st.markdown("""
    - UniProt 단백질 검색 API
    - 단백질 A와 B 검색 및 선택
    - 단백질 이름, 유전자명, 생물종 조회
    - 아미노산 서열과 서열 길이 조회
    - 단백질 기능 설명 및 원본 데이터 링크
    """)

    st.subheader("검색 예시")

    st.code("TP53\nEGFR\ninsulin\nhemoglobin")

    st.caption(
        "검색어는 단백질명, 유전자명 등으로 입력할 수 있습니다. "
        "검색 결과는 UniProt의 실제 데이터에 따라 달라집니다."
    )

# =====================================
# 8. 단백질 검색 화면
# =====================================
elif menu == "🔎 단백질 검색":
    st.header("🔎 단백질 검색")

    query = st.text_input(
        "단백질 이름 또는 유전자명",
        placeholder="예: TP53, EGFR, insulin",
        key="single_query"
    )

    search_clicked = st.button(
        "UniProt에서 검색",
        type="primary",
        key="single_search"
    )

    if search_clicked:
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("실제 단백질 데이터를 검색하고 있습니다..."):
                    results = search_proteins(query.strip())

                st.session_state.single_results = results

                if not results:
                    st.info(
                        "검색 결과가 없습니다. "
                        "다른 단백질명이나 유전자명을 입력해 보세요."
                    )

            except requests.exceptions.Timeout:
                st.error("요청 시간이 초과되었습니다. 잠시 후 다시 시도해 주세요.")

            except requests.exceptions.RequestException:
                st.error(
                    "UniProt 서버에 연결하지 못했습니다. "
                    "인터넷 연결과 서버 상태를 확인해 주세요."
                )

            except (ValueError, KeyError, TypeError):
                st.error("응답 데이터를 처리하지 못했습니다. 다시 시도해 주세요.")

    results = st.session_state.get("single_results", [])

    if results:
        st.subheader(f"검색 결과: {len(results)}개")

        for protein in results:
            with st.expander(
                f"{protein['name']} | {protein['accession']}"
            ):
                st.write(f"**유전자명:** {protein['gene']}")
                st.write(f"**생물종:** {protein['organism']}")
                st.write(f"**서열 길이:** {protein['length']:,} aa")
                st.write(f"**기능:** {protein['function']}")

                st.markdown(
                    f"[UniProt 원본 데이터 보기]({protein['url']})"
                )

                with st.expander("아미노산 서열 보기"):
                    sequence = protein["sequence"]

                    # 긴 서열을 읽기 편하게 60개씩 줄바꿈
                    formatted = "\n".join(
                        sequence[i:i + 60]
                        for i in range(0, len(sequence), 60)
                    )

                    st.code(formatted, language="text")

# =====================================
# 9. 단백질 비교 화면
# =====================================
elif menu == "⚖️ 단백질 비교":
    st.header("⚖️ 단백질 2개 비교")

    st.write(
        "각 단백질을 검색한 후 검색 결과에서 비교할 항목을 선택하세요."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("단백질 A")

        query_a = st.text_input(
            "A 검색어",
            placeholder="예: TP53",
            key="query_a"
        )

        search_a = st.button(
            "A 검색",
            key="search_a",
            type="primary"
        )

    with col2:
        st.subheader("단백질 B")

        query_b = st.text_input(
            "B 검색어",
            placeholder="예: EGFR",
            key="query_b"
        )

        search_b = st.button(
            "B 검색",
            key="search_b",
            type="primary"
        )

    if search_a:
        if not query_a.strip():
            st.warning("단백질 A의 검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("단백질 A를 검색하고 있습니다..."):
                    st.session_state.results_a = search_proteins(
                        query_a.strip()
                    )

                if not st.session_state.results_a:
                    st.warning("단백질 A 검색 결과가 없습니다.")

            except requests.exceptions.RequestException:
                st.error("단백질 A 검색 중 네트워크 오류가 발생했습니다.")

            except (ValueError, KeyError, TypeError):
                st.error("단백질 A 응답을 처리하지 못했습니다.")

    if search_b:
        if not query_b.strip():
            st.warning("단백질 B의 검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("단백질 B를 검색하고 있습니다..."):
                    st.session_state.results_b = search_proteins(
                        query_b.strip()
                    )

                if not st.session_state.results_b:
                    st.warning("단백질 B 검색 결과가 없습니다.")

            except requests.exceptions.RequestException:
                st.error("단백질 B 검색 중 네트워크 오류가 발생했습니다.")

            except (ValueError, KeyError, TypeError):
                st.error("단백질 B 응답을 처리하지 못했습니다.")

    results_a = st.session_state.results_a
    results_b = st.session_state.results_b

    selected_a = None
    selected_b = None

    col1, col2 = st.columns(2)

    with col1:
        if results_a:
            labels_a = {
                p["accession"]:
                f'{p["name"]} | {p["accession"]} | {p["organism"]}'
                for p in results_a
            }

            accession_a = st.selectbox(
                "A 검색 결과에서 선택",
                options=list(labels_a.keys()),
                format_func=lambda x: labels_a[x],
                key="select_a"
            )

            selected_a = next(
                p for p in results_a
                if p["accession"] == accession_a
            )

    with col2:
        if results_b:
            labels_b = {
                p["accession"]:
                f'{p["name"]} | {p["accession"]} | {p["organism"]}'
                for p in results_b
            }

            accession_b = st.selectbox(
                "B 검색 결과에서 선택",
                options=list(labels_b.keys()),
                format_func=lambda x: labels_b[x],
                key="select_b"
            )

            selected_b = next(
                p for p in results_b
                if p["accession"] == accession_b
            )

    # 선택한 단백질의 기본 정보 비교
    if selected_a and selected_b:
        if selected_a["accession"] == selected_b["accession"]:
            st.warning(
                "같은 UniProt 항목이 선택되었습니다. "
                "서로 다른 항목을 선택해 주세요."
            )

        else:
            st.divider()
            st.subheader("기본 정보 비교")

            comparison = pd.DataFrame({
                "항목": [
                    "단백질명",
                    "UniProt ID",
                    "유전자명",
                    "생물종",
                    "서열 길이 (aa)",
                    "기능"
                ],
                "단백질 A": [
                    selected_a["name"],
                    selected_a["accession"],
                    selected_a["gene"],
                    selected_a["organism"],
                    selected_a["length"],
                    selected_a["function"]
                ],
                "단백질 B": [
                    selected_b["name"],
                    selected_b["accession"],
                    selected_b["gene"],
                    selected_b["organism"],
                    selected_b["length"],
                    selected_b["function"]
                ]
            })

            st.dataframe(
                comparison,
                use_container_width=True,
                hide_index=True
            )

            difference = abs(
                selected_a["length"] - selected_b["length"]
            )

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    "서열 길이 차이",
                    f"{difference:,} aa"
                )

            with c2:
                st.metric(
                    "서열 동일성",
                    "3단계에서 계산"
                )

            st.subheader("아미노산 서열")

            with st.expander("단백질 A 서열 보기"):
                st.code(
                    selected_a["sequence"],
                    language="text"
                )

            with st.expander("단백질 B 서열 보기"):
                st.code(
                    selected_b["sequence"],
                    language="text"
                )

            st.subheader("원본 데이터")

            st.markdown(
                f"- [단백질 A: UniProt]({selected_a['url']})"
            )

            st.markdown(
                f"- [단백질 B: UniProt]({selected_b['url']})"
            )

            st.info(
                "현재는 실제 기본 정보와 아미노산 서열을 비교합니다. "
                "서열 정렬과 유사도 계산은 다음 단계에서 구현합니다."
            )

# =====================================
# 10. 신약 연구 탐색 화면
# =====================================
elif menu == "🧪 신약 연구 탐색":
    st.header("🧪 신약 연구 탐색")

    st.info(
        "이 메뉴는 다음 단계에서 구현합니다. "
        "현재는 UniProt 단백질 검색 및 비교 기능을 테스트할 수 있습니다."
    )

    st.markdown("""
    향후 추가할 기능

    - 관련 화합물의 물성 정보
    - 관련 생의학 논문 검색
    - AI 기반 비교 결과 해석
    """)

# =====================================
# 11. 하단 안내
# =====================================
st.divider()

st.caption(
    "BioTarget AI | 교육용 생명과학 데이터 탐색 플랫폼"
)

st.caption(
    "단백질 데이터 출처: UniProt. "
    "서열 유사도와 약물 관련 해석은 별도의 검증이 필요합니다."
)
