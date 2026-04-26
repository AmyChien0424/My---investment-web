import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ==========================================
# 1. 系統設定
# ==========================================
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
GID = "1762641193"

# --- 🎯 隊長的自由目標設定 (可自行修改) ---
RETIREMENT_GOAL = 25000000  # 設定目標為 2,500 萬

# ==========================================
# 2. 核心功能：清理並讀取數據
# ==========================================
def get_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url).fillna(0)
    if not df.empty:
        def clean_number(value):
            if isinstance(value, str):
                clean_val = re.sub(r'[^\d.-]', '', value)
                try: return float(clean_val)
                except: return 0.0
            return float(value)
        if "金額" in df.columns:
            df["金額"] = df["金額"].apply(clean_number)
        first_col = df.columns[0]
        df = df[~df[first_col].astype(str).str.contains('總|股利|Total|total|合計')]
        df = df[df[first_col] != 0]
    return df

# ==========================================
# 3. 畫面呈現
# ==========================================
st.set_page_config(page_title="Amy的自由戰情室", layout="wide")
st.title("🚀 Amy 隊長：自由航行戰情室")

try:
    df_display = get_data()
    if not df_display.empty:
        total_assets = df_display["金額"].sum()
        progress = min(total_assets / RETIREMENT_GOAL, 1.0) # 計算進度比率
        
        # --- 🌟 退休進度條區塊 ---
        st.write(f"### 🎯 自由目標達成率：{progress*100:.1f}%")
        st.progress(progress)
        
        if progress >= 1.0:
            st.balloons()
            st.success("恭喜Amy！您已達到自由門檻，隨時可以開除老闆！")
        else:
            remaining = RETIREMENT_GOAL - total_assets
            st.info(f"距離 2,500 萬自由目標，還差 NT$ {remaining:,.0f}。加油，複利正在為您工作！")

        # 頂部數據卡片
        col1, col2 = st.columns(2)
        col1.metric("目前資產總額", f"NT$ {total_assets:,.0f}")
        col2.metric("目標金額", f"NT$ {RETIREMENT_GOAL:,.0f}")
        
        # 圓餅圖
        fig = px.pie(df_display, values='金額', names=df_display.columns[0], 
                     title='資產配置比例', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.write("### 📝 即時資產明細")
        st.dataframe(df_display.style.format({"金額": "{:,.0f}"}), use_container_width=True)
        
except Exception as e:
    st.error(f"連線異常：{e}")

st.caption("數據同步中 | 投資不是為了賺錢，是為了選擇的自由")
