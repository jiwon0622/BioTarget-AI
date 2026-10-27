
import streamlit as st
import pandas as pd

# -------------------------
# 1. 페이지 기본 설정
# -------------------------
st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide"
)

# -------------------------
# 2. 화면 스타일
# -------------------------
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
        margin-bottom: 8px;
    }

    .hero p {
        color: #E4F2F8;
        font-size: 17px;
    }

    .info-card {
        background: white;
        border: 1px solid #DCE6EF;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 12px;
    }

    .small-note {
        color: #60758A;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# 3. 상단 소개
# -------------------------
st.markdown("""
<div class="hero">
    <h1>🧬 BioTarget AI</h1>
    <p>AI 기반 신약 연구 탐색 및 표적 단백질 비교 플랫폼</p>
    <p>단백질 정보를 비교하고, 서열 분석을 통해 생명과학적 의미를 탐구하세요.</p>
</div>
""", unsafe_allow_html=True)

st.info(
    "현재는 화면 제작 단계입니다. "
    "표시되는 단백질 데이터는 예시이며 실제 API 조회 결과가 아닙니다."
)

# -------------------------
# 4. 사이드바 메뉴
# -------------------------
menu = st.sidebar.radio(
    "메뉴",
    [
        "🏠 홈",
        "🔎 단백질 검색",
        "⚖️ 단백질 비교",
        "🧪 신약 연구 탐색"
    ]
)

# 예시 데이터: 실제 단백질 정보가 아님
demo_proteins = {
    "예시 단백질 A": {
        "gene": "GENE_A",
        "organism": "예시 생물종",
        "length": 320,
        "function": "기능 정보 예시"
    },
    "예시 단백질 B": {
        "gene": "GENE_B",
        "organism": "예시 생물종",
        "length": 275,
        "function": "기능 정보 예시"
    }
}

# -------------------------
# 5. 홈 화면
# -------------------------
if menu == "🏠 홈":
    st.header("프로젝트 소개")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🔎 검색</h3>
            <p>관심 있는 단백질의 정보를 찾아봅니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>⚖️ 비교</h3>
            <p>두 단백질의 특성과 서열을 비교합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🤖 AI 해석</h3>
            <p>분석 결과를 생화학적 관점에서 해석합니다.</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("개발 예정 기능")

    st.checkbox("UniProt 단백질 검색 API")
    st.checkbox("아미노산 서열 유사도 계산")
    st.checkbox("AI 비교 분석")
    st.checkbox("관련 화합물 및 논문 검색")

# -------------------------
# 6. 단백질 검색 화면
# -------------------------
elif menu == "🔎 단백질 검색":
    st.header("단백질 검색")

    query = st.text_input(
        "단백질 이름 또는 유전자명",
        placeholder="예: TP53, insulin"
    )

    st.caption(
        "현재 검색창은 UI 테스트용입니다. "
        "실제 검색 기능은 2단계에서 연결합니다."
    )

    if query:
        st.info(
            f"입력한 검색어: {query}\n\n"
            "다음 단계에서 UniProt 검색 결과가 표시됩니다."
        )

# -------------------------
# 7. 단백질 비교 화면
# -------------------------
elif menu == "⚖️ 단백질 비교":
    st.header("단백질 2개 비교")

    col1, col2 = st.columns(2)

    names = list(demo_proteins.keys())

    with col1:
        protein_a = st.selectbox(
            "단백질 A",
            names,
            index=0
        )

    with col2:
        protein_b = st.selectbox(
            "단백질 B",
            names,
            index=1
        )

    a = demo_proteins[protein_a]
    b = demo_proteins[protein_b]

    st.subheader("기본 정보 비교")

    comparison = pd.DataFrame({
        "항목": [
            "유전자명",
            "생물종",
            "서열 길이 (아미노산)",
            "기능"
        ],
        "단백질 A": [
            a["gene"],
            a["organism"],
            a["length"],
            a["function"]
        ],
        "단백질 B": [
            b["gene"],
            b["organism"],
            b["length"],
            b["function"]
        ]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("서열 분석 결과")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "서열 길이 차이",
            f"{abs(a['length'] - b['length'])} aa"
        )

    with c2:
        st.metric(
            "서열 동일성",
            "미계산"
        )

    st.caption(
        "서열 길이와 기능은 화면 구성을 위한 가상 예시입니다. "
        "실제 서열 동일성은 아직 계산하지 않습니다."
    )

    st.subheader("AI 비교 해석")

    st.markdown("""
    <div class="info-card">
        현재 AI 분석 기능은 연결되지 않았습니다.
        <br><br>
        다음 단계에서 실제 단백질 데이터와 서열 비교 결과를
        바탕으로 공통점과 차이점을 분석하도록 구현합니다.
    </div>
    """, unsafe_allow_html=True)

    st.button(
        "AI 비교 분석 실행",
        disabled=True
    )

# -------------------------
# 8. 신약 연구 탐색 화면
# -------------------------
elif menu == "🧪 신약 연구 탐색":
    st.header("신약 연구 탐색")

    keyword = st.text_input(
        "질병, 단백질 또는 화합물 검색",
        placeholder="예: 암, EGFR, aspirin"
    )

    st.caption(
        "다음 개발 단계에서 PubChem 및 논문 검색 API를 연결할 예정입니다."
    )

    if keyword:
        st.info(
            f"검색어: {keyword}\n\n"
            "현재는 검색 UI만 구현되어 있습니다."
        )

# -------------------------
# 9. 하단 안내
# -------------------------
st.divider()

st.caption(
    "BioTarget AI | 교육·연구 탐색용 프로토타입 | "
    "현재 데이터는 예시이며 실제 의약학적 판단에 사용할 수 없습니다."
)
