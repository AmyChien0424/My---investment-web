import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 系統設定與金鑰讀取
# ==========================================
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "").strip()

# ==========================================
# 2. 核心功能：動態欄位抓取法
# ==========================================
def get_data():
    # 使用 gid=0 抓取第一張分頁，不指定 A:B，改為抓取整張表
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
    
    # 讀取資料：
    # 我們不再設定 header=None，改為讓系統自動把第一列當作標題
    # nrows=14 代表抓取標題後下方的 14 列資料 (總共還是 15 列範圍)
    df = pd.read_csv(url, nrows=14).fillna(0)
    
    return df

# ==========================================
# 3. 戰情室儀表板畫面繪製
# ==========================================
st.set_page_config(page_title="千萬資產戰情室-動態版", layout="wide")
st.title("📊 我的專屬資產戰情室 (動態擴充版)")

try:
    df_display = get_data()
    
    if not df_display.empty:
        # 🛡️ 動態金額辨識：我們假設「金額」那一欄的名字就叫「金額」
        # 這樣不管您加了多少欄位，只要有一欄叫「金額」，系統就能算總額
        if "金額" in df_display.columns:
            df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
            total_assets = df_display["金額"].sum()
            
            # 顯示總額
            st.metric("目前資產總額", f"NT$ {total_assets:,.0f}")
            
            # 畫出圓餅圖 (預設使用第一欄作為名稱，金額欄作為數值)
            label_col = df_display.columns[0]
            fig = px.pie(df_display, values='金額', names=label_col, title=f'各項{label_col}配置比例')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("提醒：請確保試算表第一列有標題，且其中一格名稱為『金額』")

        # 顯示明細清單 (這裏會自動顯示您在 Excel 新增的所有欄位！)
        st.write("### 📝 資產明細清單 (自動適應多欄位)")
        st.dataframe(df_display, use_container_width=True)
        
except Exception as e:
    st.error(f"戰情室連線異常，請確認分頁名稱或 ID。細節：{e}")

st.caption("欄位動態同步中 | 專為 Amy 隊長打造的理財決策系統")
