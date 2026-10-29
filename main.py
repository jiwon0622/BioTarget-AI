
import streamlit as st
import requests
from deep_translator import GoogleTranslator, MyMemoryTranslator
from Bio.Align import PairwiseAligner

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="BioTarget AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

UNIPROT_URL = "https://rest.uniprot.org"
EUROPE_PMC_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

HEADERS = {
    "User-Agent": "BioTargetAI/1.0 educational research app"
}

# =========================================================
# 기존 디자인 복구: 하늘색 연구실 테마
# =========================================================
st.markdown("""
<style>
.stApp {
    background: #F5F8FC;
    color: #243B53;
}

[data-testid="stHeader"] {
    background: rgba(245, 248, 252, 0.9);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #E7F2FC 0%, #F3F8FD 100%);
    border-right: 1px solid #D6E5F3;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #183B56;
}

h1, h2, h3 {
    color: #183B56;
    letter-spacing: -0.4px;
}

p, label, li {
    color: #344E64;
}

.hero {
    background: linear-gradient(120deg, #173B57 0%, #347C91 100%);
    padding: 34px 36px;
    border-radius: 22px;
    color: white;
    margin-bottom: 25px;
    box-shadow: 0 8px 24px rgba(23, 59, 87, 0.12);
}

.hero h1 {
    color: white;
    font-size: 34px;
    margin-bottom: 10px;
}

.hero p {
    color: #EAF7FF;
    font-size: 16px;
    line-height: 1.8;
    margin-bottom: 0;
}

.section-card {
    background: white;
    border: 1px solid #DCE8F3;
    border-radius: 17px;
    padding: 21px;
    margin-bottom: 15px;
    box-shadow: 0 3px 12px rgba(34, 76, 112, 0.045);
}

.card-title {
    color: #204D70;
    font-size: 19px;
    font-weight: 700;
    margin-bottom: 8px;
}

.card-description {
    color: #60788C;
    font-size: 14px;
    line-height: 1.75;
}

.small-label {
    color: #5285A6;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
}

.info-box {
    background: #EAF5FF;
    border-left: 4px solid #6BAED6;
    padding: 14px 17px;
    border-radius: 9px;
    margin: 12px 0;
    color: #244D6B;
}

div.stButton > button {
    background: linear-gradient(120deg, #DCEEFF 0%, #C8E4FA 100%);
    color: #183B56;
    border: 1px solid #B9D8F0;
    border-radius: 10px;
    font-weight: 650;
    min-height: 42px;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    background: #B8DDF7;
    border-color: #81BCE4;
    color: #123650;
}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div,
div[data-testid="stTextArea"] textarea {
    background: white;
    border-radius: 9px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #DCE8F3;
    padding: 15px;
    border-radius: 13px;
}

[data-testid="stExpander"] {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid #DCE8F3;
    border-radius: 12px;
}

hr {
    border-color: #DCE8F3;
}

.footer {
    text-align: center;
    color: #7890A3;
    font-size: 12px;
    padding: 25px 0 10px 0;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 데이터 요청 함수
# =========================================================
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
        timeout=25
    )
    response.raise_for_status()

    results = []

    for item in response.json().get("results", []):
        description = item.get("proteinDescription", {})

        name = description.get(
            "recommendedName", {}
        ).get("fullName", {}).get("value", "")

        if not name:
            submissions = description.get("submissionNames", [])
            if submissions:
                name = submissions[0].get(
                    "fullName", {}
                ).get("value", "")

        genes = item.get("genes", [])
        gene = (
            genes[0].get("geneName", {}).get("value", "")
            if genes else ""
        )

        function = ""
        for comment in item.get("comments", []):
            if comment.get("commentType") == "FUNCTION":
                texts = comment.get("texts", [])
                if texts:
                    function = texts[0].get("value", "")
                    break

        results.append({
            "accession": item.get("primaryAccession", ""),
            "name": name or "이름 정보 없음",
            "gene": gene or "정보 없음",
            "organism": item.get("organism", {}).get(
                "scientificName", "정보 없음"
            ),
            "function": function or "기능 설명 없음",
            "length": item.get("sequence", {}).get("length", 0)
        })

    return results


@st.cache_data(ttl=1800, show_spinner=False)
def get_protein(accession):
    response = requests.get(
        f"{UNIPROT_URL}/uniprotkb/{accession}.json",
        headers=HEADERS,
        timeout=25
    )
    response.raise_for_status()

    item = response.json()
    description = item.get("proteinDescription", {})

    name = description.get(
        "recommendedName", {}
    ).get("fullName", {}).get("value", "")

    if not name:
        submissions = description.get("submissionNames", [])
        if submissions:
            name = submissions[0].get(
                "fullName", {}
            ).get("value", "")

    genes = item.get("genes", [])
    gene = (
        genes[0].get("geneName", {}).get("value", "")
        if genes else ""
    )

    function = ""
    for comment in item.get("comments", []):
        if comment.get("commentType") == "FUNCTION":
            texts = comment.get("texts", [])
            if texts:
                function = texts[0].get("value", "")
                break

    sequence = item.get("sequence", {}).get("value", "")

    return {
        "accession": item.get("primaryAccession", accession),
        "name": name or "이름 정보 없음",
        "gene": gene or "정보 없음",
        "organism": item.get("organism", {}).get(
            "scientificName", "정보 없음"
        ),
        "function": function or "기능 설명 없음",
        "sequence": sequence,
        "length": len(sequence),
        "url": f"https://www.uniprot.org/uniprotkb/{accession}"
    }


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

    papers = []

    for item in response.json().get(
        "resultList", {}
    ).get("result", []):
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
            "title": item.get("title", "제목 정보 없음"),
            "authors": item.get("authorString", "저자 정보 없음"),
            "journal": item.get("journalTitle", "학술지 정보 없음"),
            "year": item.get("pubYear", ""),
            "abstract": item.get("abstractText", ""),
            "url": url
        })

    return papers


# =========================================================
# 번역 함수: 언어 코드 수정 + 대체 서비스
# =========================================================
def translate_to_korean(text):
    if not text or not text.strip():
        return {
            "success": False,
            "text": "",
            "provider": "",
            "error": "번역할 문장이 없습니다."
        }

    text = text.strip()[:4000]
    errors = []

    # MyMemory는 지원 언어 코드 en-GB, ko-KR 사용
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
        errors.append(
            f"MyMemory: {type(exc).__name__}: {exc}"
        )

    # Google은 MyMemory가 실패한 경우에만 요청
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
        errors.append(
            f"Google Translate: {type(exc).__name__}: {exc}"
        )

    return {
        "success": False,
        "text": "",
        "provider": "",
        "error": "\n\n".join(errors)
    }


# =========================================================
# 번역 버튼: 클릭했을 때만 번역 실행
# =========================================================
def translation_panel(text, key):
    if not text or text == "기능 설명 없음":
        st.info("번역할 원문이 없습니다.")
        return

    result_key = f"translation_result_{key}"

    if st.button("🌐 한국어 번역", key=f"translate_button_{key}"):
        with st.spinner("문장을 한국어로 번역하고 있습니다..."):
            result = translate_to_korean(text)

        st.session_state[result_key] = result

    result = st.session_state.get(result_key)

    if result:
        if result["success"]:
            st.markdown("**🇰🇷 한국어 번역**")
            st.write(result["text"])
            st.caption(f"번역 서비스: {result['provider']}")
        else:
            st.warning(
                "자동 번역 서비스가 응답하지 않았어요. "
                "잠시 후 다시 시도하거나 영어 원문을 확인해 주세요."
            )
            with st.expander("번역 오류 자세히 보기"):
                st.code(result["error"])


# =========================================================
# 공통 단백질 결과 표시
# =========================================================
def protein_card(protein, key):
    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    st.markdown(f"### {protein['name']}")
    st.caption(f"UniProt accession: {protein['accession']}")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**유전자:** {protein['gene']}")
        st.write(f"**생물종:** {protein['organism']}")

    with col2:
        st.write(f"**아미노산 길이:** {protein['length']}")
        st.markdown(
            f"[UniProt에서 자세히 보기]({protein['url']})"
        )

    st.markdown("**기능 설명 원문**")
    st.write(protein["function"])

    translation_panel(protein["function"], key)

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# 공통 논문 검색 UI
# =========================================================
def paper_search_panel(default_query="", key="papers"):
    st.markdown("### 📚 관련 논문 탐색")
    st.caption("단백질 이름, 유전자 이름 또는 생명과학 주제로 검색하세요.")

    query = st.text_input(
        "논문 검색어",
        value=default_query,
        key=f"paper_query_{key}",
        placeholder="예: TP53 cancer, insulin signaling"
    )

    if st.button("논문 검색", key=f"paper_button_{key}"):
        if not query.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("Europe PMC에서 논문을 찾고 있어요..."):
                    papers = search_papers(query.strip())

                st.session_state[f"paper_results_{key}"] = papers

            except Exception as exc:
                st.error("논문 검색 중 오류가 발생했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    papers = st.session_state.get(f"paper_results_{key}", [])

    if papers:
        st.success(f"논문 {len(papers)}편을 찾았습니다.")

        for i, paper in enumerate(papers):
            with st.expander(
                f"{paper['title']} ({paper['year'] or '연도 미상'})"
            ):
                st.write(f"**저자:** {paper['authors']}")
                st.write(f"**학술지:** {paper['journal']}")
                st.markdown(f"[논문 정보 열기]({paper['url']})")

                if paper["abstract"]:
                    st.markdown("**초록 원문**")
                    st.write(paper["abstract"])
                    translation_panel(
                        paper["abstract"],
                        f"{key}_abstract_{i}"
                    )
                else:
                    st.info("이 논문에는 초록이 제공되지 않습니다.")


# =========================================================
# 사이드바
# =========================================================
with st.sidebar:
    st.markdown("## 🧬 BioTarget AI")
    st.caption("AI-assisted protein research")
    st.markdown("---")

    page = st.radio(
        "메뉴",
        [
            "🏠 홈",
            "🔎 단백질 검색",
            "⚖️ 단백질 비교",
            "🧪 신약 연구 탐색"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**데이터베이스**")
    st.markdown("- [UniProt](https://www.uniprot.org/)")
    st.markdown("- [Europe PMC](https://europepmc.org/)")
    st.markdown("---")
    st.caption("교육 및 연구 탐색용 도구입니다.")


# =========================================================
# 홈
# =========================================================
if page == "🏠 홈":
    st.markdown("""
    <div class="hero">
        <div class="small-label" style="color:#BDE8F8;">
            BIOCHEMISTRY · PROTEIN RESEARCH
        </div>
        <h1>BioTarget AI</h1>
        <p>
            단백질 정보를 탐색하고, 아미노산 서열을 비교하고,
            관련 생명과학 논문을 찾아보세요.<br>
            생화학 연구를 시작하는 학생을 위한 탐색 도구입니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 연구 도구")
    st.write("원하는 기능을 선택해 탐구를 시작하세요.")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:30px;">🔎</div>
            <div class="card-title">단백질 검색</div>
            <div class="card-description">
                단백질 이름과 유전자 정보를 검색하고
                단백질의 생물학적 기능을 확인합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("단백질 검색하기", key="home_search"):
            st.session_state["navigate_to"] = "🔎 단백질 검색"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:30px;">⚖️</div>
            <div class="card-title">단백질 비교</div>
            <div class="card-description">
                두 단백질의 아미노산 서열을 정렬하고
                서열 일치율을 비교합니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("단백질 비교하기", key="home_compare"):
            st.session_state["navigate_to"] = "⚖️ 단백질 비교"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="section-card">
            <div style="font-size:30px;">🧪</div>
            <div class="card-title">신약 연구 탐색</div>
            <div class="card-description">
                관심 있는 단백질 표적과 관련 논문을 검색해
                신약 연구의 기초 정보를 살펴봅니다.
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("연구 탐색하기", key="home_research"):
            st.session_state["navigate_to"] = "🧪 신약 연구 탐색"
            st.rerun()

    st.markdown("---")
    st.markdown("## 연구 흐름")

    flow1, flow2, flow3 = st.columns(3)

    with flow1:
        st.markdown("**01 · 표적 탐색**")
        st.write("관심 있는 단백질과 유전자 정보를 확인합니다.")

    with flow2:
        st.markdown("**02 · 서열 분석**")
        st.write("단백질 서열의 유사성을 비교합니다.")

    with flow3:
        st.markdown("**03 · 논문 조사**")
        st.write("관련 연구의 초록과 연구 결과를 살펴봅니다.")

    st.markdown("""
    <div class="info-box">
        <b>참고:</b> 단백질 정보와 서열 유사성만으로
        특정 물질의 약효나 안전성을 확정할 수는 없습니다.
        실제 약물 개발에는 추가적인 실험과 검증이 필요합니다.
    </div>
    """, unsafe_allow_html=True)


# 홈에서 메뉴 이동
if "navigate_to" in st.session_state:
    destination = st.session_state.pop("navigate_to")
    if page == "🏠 홈":
        st.info(
            f"왼쪽 메뉴에서 **{destination}** 을 선택해 주세요."
        )


# =========================================================
# 단백질 검색
# =========================================================
elif page == "🔎 단백질 검색":
    st.markdown("## 🔎 단백질 검색")
    st.write(
        "단백질 이름, 유전자 이름 또는 기능 키워드로 UniProt을 검색합니다."
    )

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    keyword = st.text_input(
        "단백질 또는 유전자 키워드",
        placeholder="예: insulin, TP53, hemoglobin",
        key="protein_search_keyword"
    )

    limit = st.selectbox(
        "검색 결과 개수",
        [5, 10, 20],
        index=1,
        key="protein_search_limit"
    )

    if st.button("🔍 검색 시작", key="protein_search_submit"):
        if not keyword.strip():
            st.warning("검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("UniProt 데이터베이스 검색 중..."):
                    results = search_proteins(keyword.strip(), limit)
                st.session_state["protein_search_results"] = results

            except Exception as exc:
                st.error("단백질 검색에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)

    results = st.session_state.get("protein_search_results", [])

    if results:
        st.markdown(f"### 검색 결과 · {len(results)}개")

        labels = [
            f"{p['name']} | {p['accession']} | {p['organism']}"
            for p in results
        ]

        selected_label = st.selectbox(
            "자세히 볼 단백질 선택",
            labels,
            key="selected_protein_label"
        )

        selected_index = labels.index(selected_label)
        protein_card(
            results[selected_index],
            f"search_protein_{results[selected_index]['accession']}"
        )

        st.markdown("---")
        paper_search_panel(
            default_query=results[selected_index]["gene"],
            key="protein_related"
        )


# =========================================================
# 단백질 비교
# =========================================================
elif page == "⚖️ 단백질 비교":
    st.markdown("## ⚖️ 단백질 서열 비교")
    st.write(
        "UniProt accession을 입력해 두 단백질의 아미노산 서열을 비교합니다."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 단백질 A")
        accession_a = st.text_input(
            "Accession A",
            placeholder="예: P01308",
            key="compare_accession_a"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown("### 단백질 B")
        accession_b = st.text_input(
            "Accession B",
            placeholder="예: P68871",
            key="compare_accession_b"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.button("서열 비교 시작", key="compare_submit"):
        if not accession_a.strip() or not accession_b.strip():
            st.warning("두 accession을 모두 입력해 주세요.")
        else:
            try:
                with st.spinner("단백질 정보와 서열을 가져오는 중..."):
                    protein_a = get_protein(accession_a.strip())
                    protein_b = get_protein(accession_b.strip())

                seq_a = protein_a["sequence"]
                seq_b = protein_b["sequence"]

                if not seq_a or not seq_b:
                    st.error("하나 이상의 서열을 찾을 수 없습니다.")
                else:
                    aligner = PairwiseAligner()
                    aligner.mode = "global"
                    aligner.match_score = 2
                    aligner.mismatch_score = -1
                    aligner.open_gap_score = -2
                    aligner.extend_gap_score = -0.5

                    alignment = aligner.align(seq_a, seq_b)[0]
                    aligned_a, aligned_b = alignment.aligned

                    identical = 0
                    aligned_length = 0

                    for (start_a, end_a), (start_b, end_b) in zip(
                        aligned_a, aligned_b
                    ):
                        segment_length = min(
                            end_a - start_a,
                            end_b - start_b
                        )
                        for offset in range(segment_length):
                            aligned_length += 1
                            if (
                                seq_a[start_a + offset]
                                == seq_b[start_b + offset]
                            ):
                                identical += 1

                    identity = (
                        identical / aligned_length * 100
                        if aligned_length else 0
                    )

                    st.session_state["comparison_result"] = {
                        "a": protein_a,
                        "b": protein_b,
                        "identity": identity,
                        "score": alignment.score
                    }

            except Exception as exc:
                st.error("서열 비교에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    comparison = st.session_state.get("comparison_result")

    if comparison:
        a = comparison["a"]
        b = comparison["b"]

        st.markdown("### 비교 결과")

        left, right = st.columns(2)

        with left:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"#### {a['name']}")
            st.write(f"**Accession:** {a['accession']}")
            st.write(f"**유전자:** {a['gene']}")
            st.write(f"**생물종:** {a['organism']}")
            st.write(f"**서열 길이:** {a['length']} aa")
            st.markdown(f"[UniProt 상세 정보]({a['url']})")
            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown(f"#### {b['name']}")
            st.write(f"**Accession:** {b['accession']}")
            st.write(f"**유전자:** {b['gene']}")
            st.write(f"**생물종:** {b['organism']}")
            st.write(f"**서열 길이:** {b['length']} aa")
            st.markdown(f"[UniProt 상세 정보]({b['url']})")
            st.markdown("</div>", unsafe_allow_html=True)

        metric1, metric2 = st.columns(2)

        with metric1:
            st.metric(
                "정렬 구간 서열 일치율",
                f"{comparison['identity']:.2f}%"
            )

        with metric2:
            st.metric("정렬 점수", f"{comparison['score']:.1f}")

        with st.expander("아미노산 서열 확인"):
            st.markdown("**단백질 A**")
            st.code(a["sequence"])
            st.markdown("**단백질 B**")
            st.code(b["sequence"])

        st.markdown("""
        <div class="info-box">
            서열 일치율은 두 단백질의 정렬된 구간을 비교한 값입니다.
            이것만으로 두 단백질의 기능이 같거나 약물 표적으로 적합하다고
            결론 내릴 수는 없습니다.
        </div>
        """, unsafe_allow_html=True)

        paper_query = f'"{a["name"]}" OR "{b["name"]}"'
        paper_search_panel(
            default_query=paper_query,
            key="comparison_papers"
        )


# =========================================================
# 신약 연구 탐색
# =========================================================
elif page == "🧪 신약 연구 탐색":
    st.markdown("## 🧪 신약 연구 탐색")
    st.write(
        "관심 있는 단백질 표적과 관련 논문을 찾아 연구 배경을 조사합니다."
    )

    st.markdown("""
    <div class="hero">
        <div class="small-label" style="color:#BDE8F8;">
            TARGET DISCOVERY
        </div>
        <h1>어떤 단백질을 연구할까요?</h1>
        <p>
            단백질의 생물학적 기능을 확인하고 관련 논문을 탐색해
            연구 가설을 세우는 데 활용할 수 있습니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

    target = st.text_input(
        "관심 있는 표적 단백질 또는 유전자",
        placeholder="예: EGFR, TP53, insulin receptor",
        key="research_target"
    )

    if st.button("표적 정보 탐색", key="research_target_submit"):
        if not target.strip():
            st.warning("단백질 또는 유전자 이름을 입력해 주세요.")
        else:
            try:
                with st.spinner("관련 단백질 정보를 검색 중..."):
                    results = search_proteins(target.strip(), 5)

                st.session_state["research_target_results"] = results
                st.session_state["research_target_query"] = target.strip()

            except Exception as exc:
                st.error("표적 검색에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    target_results = st.session_state.get(
        "research_target_results", []
    )

    if target_results:
        st.markdown("### 관련 단백질")

        for i, protein in enumerate(target_results):
            with st.expander(
                f"{protein['name']} · {protein['accession']}"
            ):
                st.write(f"**유전자:** {protein['gene']}")
                st.write(f"**생물종:** {protein['organism']}")
                st.write(f"**기능 설명:** {protein['function']}")
                st.markdown(
                    f"[UniProt 상세 정보](https://www.uniprot.org/uniprotkb/{protein['accession']})"
                )

                translation_panel(
                    protein["function"],
                    f"research_target_{protein['accession']}"
                )

    st.markdown("---")
    st.markdown("### 관련 연구 논문")

    research_query = st.text_input(
        "논문 검색어",
        value=st.session_state.get("research_target_query", ""),
        placeholder="예: EGFR inhibitor cancer",
        key="research_paper_query"
    )

    if st.button("관련 논문 찾기", key="research_paper_submit"):
        if not research_query.strip():
            st.warning("논문 검색어를 입력해 주세요.")
        else:
            try:
                with st.spinner("관련 논문을 검색 중..."):
                    papers = search_papers(research_query.strip())

                st.session_state["research_papers"] = papers

            except Exception as exc:
                st.error("논문 검색에 실패했습니다.")
                st.code(f"{type(exc).__name__}: {exc}")

    research_papers = st.session_state.get("research_papers", [])

    if research_papers:
        st.success(f"관련 논문 {len(research_papers)}편")

        for i, paper in enumerate(research_papers):
            with st.expander(
                f"{paper['title']} ({paper['year'] or '연도 미상'})"
            ):
                st.write(f"**저자:** {paper['authors']}")
                st.write(f"**학술지:** {paper['journal']}")
                st.markdown(f"[논문 정보 열기]({paper['url']})")

                if paper["abstract"]:
                    st.markdown("**초록 원문**")
                    st.write(paper["abstract"])
                    translation_panel(
                        paper["abstract"],
                        f"research_paper_abstract_{i}"
                    )
                else:
                    st.info("초록이 제공되지 않는 논문입니다.")

    st.markdown("""
    <div class="info-box">
        <b>연구 해석 시 주의:</b> 논문에서 보고된 표적 단백질의 역할이나
        실험 결과는 연구 조건에 따라 달라질 수 있습니다.
        표적 후보를 찾는 것과 실제 약물의 효과 및 안전성을 입증하는 것은
        서로 다른 단계입니다.
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# 푸터
# =========================================================
st.markdown("""
<div class="footer">
    BioTarget AI · Educational Protein Research Explorer<br>
    Data sources: UniProt and Europe PMC
</div>
""", unsafe_allow_html=True)
