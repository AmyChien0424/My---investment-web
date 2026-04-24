import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 系統設定
# ==========================================
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
GID = "1762641193"

# ==========================================
# 2. 核心功能：精準過濾非資產列
# ==========================================
def get_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    
    # 讀取前 50 列
    df = pd.read_csv(url).fillna(0)
    
    if not df.empty:
        first_col = df.columns[0] # 抓取「金」那一欄
        
        # 🛡️ Amy 隊長的新格式過濾器：
        # 1. 排除包含「總」的列 (排除總價)
        # 2. 排除包含「股利」的列 (排除年股利)
        # 3. 排除空白列
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
        # 強制轉換金額為數字
        if "金額" in df_display.columns:
            df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
            
            # 自動計算總額 (明細加總)
            total_assets = df_display["金額"].sum()
            
            st.metric("目前資產總額 (系統自動核算)", f"NT$ {total_assets:,.0f}")
            
            # 圓餅圖
            label_col = df_display.columns[0]
            fig = px.pie(df_display, values='金額', names=label_col, 
                         title=f'資產配置比例分析 ({label_col})',
                         hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("請確保 Excel 第一列標題有『金額』。")

        st.write("### 📝 即時資產明細清單")
        st.dataframe(df_display, use_container_width=True)
        
except Exception as e:
    st.error(f"連線異常，請確認試算表設定。原因：{e}")

st.caption("數據每小時自動更新 | 專為 Amy 隊長打造的理財決策系統")
