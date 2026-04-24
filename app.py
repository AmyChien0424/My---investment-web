import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ==========================================
# 1. 系統設定
# ==========================================
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
GID = "1762641193"

# ==========================================
# 2. 核心功能：強制清理並讀取數字
# ==========================================
def get_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    
    # 讀取資料
    df = pd.read_csv(url).fillna(0)
    
    if not df.empty:
        # 🛡️ Amy 隊長專屬：強制數字清理邏輯
        def clean_number(value):
            if isinstance(value, str):
                # 移除所有非數字、非小數點、非負號的字元 (例如逗號、NT$)
                clean_val = re.sub(r'[^\d.-]', '', value)
                try:
                    return float(clean_val)
                except:
                    return 0.0
            return float(value)

        # 針對「金額」欄位執行深度清理
        if "金額" in df.columns:
            df["金額"] = df["金額"].apply(clean_number)
            
        # 排除非資產列 (總價、股利、空行)
        first_col = df.columns[0]
        df = df[~df[first_col].astype(str).str.contains('總|股利|Total|total|合計')]
        df = df[df[first_col] != 0]
        
    return df

# ==========================================
# 3. 畫面呈現
# ==========================================
st.set_page_config(page_title="千萬資產戰情室", layout="wide")
st.title("📊 我的專屬資產戰情室")

try:
    df_display = get_data()
    
    if not df_display.empty:
        # 計算總額
        total_assets = df_display["金額"].sum()
        
        st.metric("目前資產總額 (系統深度核算)", f"NT$ {total_assets:,.0f}")
        
        # 圓餅圖
        label_col = df_display.columns[0]
        fig = px.pie(df_display, values='金額', names=label_col, 
                     title=f'資產配置比例分析 ({label_col})',
                     hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

        st.write("### 📝 即時資產明細清單")
        # 格式化表格中的數字顯示，方便閱讀
        st.dataframe(df_display.style.format({"金額": "{:,.0f}"}), use_container_width=True)
        
except Exception as e:
    st.error(f"連線異常，請確認試算表格式。原因：{e}")

st.caption("數據深度同步中 | 專為 Amy 隊長打造的理財決策系統")
