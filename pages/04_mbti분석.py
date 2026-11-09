import html
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="세계 MBTI 국가별 분석",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 세계 MBTI 국가별 비율 분석")
st.write("국가를 선택하면 MBTI 16개 유형의 비율을 높은 순서대로 보여줍니다.")

# app.py와 CSV 파일을 같은 GitHub 저장소 폴더에 업로드하세요.
CSV_PATH = Path(__file__).parent / "countriesMBTI_16types (6).csv"

@st.cache_data
def load_data(path):
    data = pd.read_csv(path)
    data.columns = data.columns.astype(str).str.strip()

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에서 'Country' 열을 찾을 수 없습니다.")

    data = data.dropna(subset=["Country"]).copy()
    data["Country"] = data["Country"].astype(str).str.strip()

    mbti_cols = [col for col in data.columns if col != "Country"]
    if not mbti_cols:
        raise ValueError("MBTI 유형 열을 찾을 수 없습니다.")

    for col in mbti_cols:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.drop_duplicates(subset=["Country"])
    data = data.sort_values("Country").reset_index(drop=True)
    return data, mbti_cols

try:
    df, mbti_types = load_data(CSV_PATH)
except FileNotFoundError:
    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "'app.py'와 'countriesMBTI_16types (6).csv'를 "
        "GitHub 저장소의 같은 폴더에 업로드했는지 확인하세요."
    )
    st.stop()
except (ValueError, pd.errors.ParserError) as exc:
    st.error(f"CSV 파일을 읽는 중 문제가 발생했습니다: {exc}")
    st.stop()

if df.empty:
    st.error("CSV 파일에 표시할 국가 데이터가 없습니다.")
    st.stop()

countries = df["Country"].tolist()
default_index = countries.index("South Korea") if "South Korea" in countries else 0
selected_country = st.selectbox(
    "국가 선택",
    options=countries,
    index=default_index,
)

country_row = df.loc[df["Country"] == selected_country].iloc[0]

chart_data = pd.DataFrame({
    "MBTI": mbti_types,
    "비율": [country_row[col] for col in mbti_types],
})
chart_data["비율"] = pd.to_numeric(chart_data["비율"], errors="coerce")
chart_data = chart_data.dropna(subset=["비율"])
chart_data = chart_data.sort_values("비율", ascending=False).reset_index(drop=True)

if chart_data.empty:
    st.warning("선택한 국가에는 표시할 MBTI 비율이 없습니다.")
    st.stop()

# CSV 값은 0~1 비율이라고 가정합니다. 화면에는 백분율로 표시합니다.
chart_data["퍼센트"] = chart_data["비율"] * 100
max_value = max(float(chart_data["퍼센트"].max()), 0.0001)

st.subheader(f"📊 {selected_country}의 MBTI 비율")
st.caption("1위는 노란색, 나머지는 진한 보라색에서 연한 보라색으로 표시됩니다.")

# 보라색은 2위에서 가장 진하고, 마지막 순위로 갈수록 밝아집니다.
purple_palette = [
    "#5B21B6", "#6D28D9", "#7C3AED", "#8B5CF6",
    "#9F7AEA", "#B09AF0", "#C4B5FD", "#D0C4FC",
    "#D9D0FD", "#E2DAFE", "#E8E1FE", "#EEE9FF",
    "#F1EDFF", "#F4F1FF", "#F7F5FF",
]

rows_html = []
for rank, row in chart_data.iterrows():
    mbti = html.escape(str(row["MBTI"]))
    pct = float(row["퍼센트"])
    width = max(0, min(100, pct / max_value * 100))
    color = "#FFD43B" if rank == 0 else purple_palette[min(rank - 1, len(purple_palette) - 1)]
    rank_label = "🥇 1위" if rank == 0 else f"{rank + 1}위"

    rows_html.append(f"""
    <div class="mbti-row">
      <div class="mbti-label">
        <span class="rank">{rank_label}</span>
        <span class="type">{mbti}</span>
        <span class="value">{pct:.2f}%</span>
      </div>
      <div class="bar-track">
        <div class="bar-fill" style="width:{width:.2f}%; background:{color};"></div>
      </div>
    </div>
    """)

chart_html = """
<style>
.mbti-chart { width: 100%; }
.mbti-row { margin: 0 0 15px 0; }
.mbti-label {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 6px; font-size: 15px;
}
.rank { width: 54px; color: #6B7280; font-size: 13px; }
.type { width: 55px; font-weight: 700; color: #222; }
.value { margin-left: auto; font-variant-numeric: tabular-nums; color: #333; }
.bar-track {
    width: 100%; height: 20px; border-radius: 7px;
    background: #F1F1F5; overflow: hidden;
}
.bar-fill { height: 100%; min-width: 2px; border-radius: 7px; }
</style>
<div class="mbti-chart">
""" + "\n".join(rows_html) + "\n</div>"

st.markdown(chart_html, unsafe_allow_html=True)

with st.expander("📋 비율 표 보기"):
    table = chart_data[["MBTI", "퍼센트"]].copy()
    table.columns = ["MBTI 유형", "비율(%)"]
    st.dataframe(
        table.style.format({"비율(%)": "{:.2f}%"}),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "참고: 그래프는 CSV에 기록된 값을 백분율로 환산해 표시합니다. "
    "이 데이터가 각 국가 전체 인구를 대표하는지 여부는 원본 출처를 확인하세요."
)
