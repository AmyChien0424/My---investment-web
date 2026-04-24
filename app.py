import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 從 Streamlit Secrets 讀取基本設定
# 雖然我們改用直讀法，但保留變數定義，確保您的 Secrets 依然發揮作用
API_KEY = st.secrets["api_key"]
SPREADSHEET_ID = st.secrets["spreadsheet_id"]

# 2. 核心功能：直接抓取 Google 試算表 CSV
def get_data():
    # 這是最強勢的讀取方式：繞過 API，直接把試算表當網頁抓取
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&sheet=Data"
    
    # 讀取資料並自動處理格式：
    # header=None 代表我們手動處理標題
    # nrows=15 代表我們只抓前 15 列，精準避開第 16 列的「總價」
    df = pd.read_csv(url, header=None, nrows=15).fillna(0)
    
    # 將資料轉換成清單格式，對接原本的儀表板邏輯
    return df.values.tolist()

# 3. 儀表板畫面呈現
st.set_page_config(page_title="千萬資產戰情室", layout="wide")
st.title("📊 我的專屬資產戰情室")

try:
    data = get_data()
    
    if data:
        # 將資料轉為表格物件，方便畫圖
        df_display = pd.DataFrame(data, columns=["資產項目", "金額"])
        # 確保金額欄位是數字格式
        df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
        
        # 計算總額
        total_assets = df_display["金額"].sum()
        
        # 顯示頂部數據
        col1, col2 = st.columns(2)
        with col1:
            st.metric("目前資產總額", f"NT$ {total_assets:,.0f}")
        
        # 畫出華麗的圓餅圖 (包含您的 0050、VOO、BRK.B 等)
        fig = px.pie(df_display, values='金額', names='資產項目', title='資產配置比例')
        st.plotly_chart(fig, use_container_width=True)
        
        # 顯示明細清單
        st.write("### 📝 資產明細清單")
        st.table(df_display)
        
except Exception as e:
    st.error(f"戰情室連線暫時中斷，請檢查試算表權限。錯誤代碼：{e}")

st.caption("數據每小時自動對接更新 | 專為 Amy 隊長打造的理財決策系統")金
