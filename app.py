import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 系統設定與金鑰讀取
# ==========================================
# 安全讀取 Secrets，避免系統找不到變數
API_KEY = st.secrets.get("api_key", "") 
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "")

# ==========================================
# 2. 核心功能：無敵防呆抓取資料法
# ==========================================
def get_data():
    # 防呆 1：自動清除 ID 前後不小心複製到的「隱形空白鍵」
    clean_id = SPREADSHEET_ID.strip()
    
    # 防呆 2：使用 gid=0 強制抓取「第一張分頁」，就算分頁名字打錯也能抓到
    url = f"https://docs.google.com/spreadsheets/d/{clean_id}/export?format=csv&gid=0"
    
    # 讀取資料，並設定 nrows=15 精準避開第 16 列的「總價」
    df = pd.read_csv(url, header=None, nrows=15).fillna(0)
    
    return df.values.tolist()

# ==========================================
# 3. 戰情室儀表板畫面繪製
# ==========================================
# 設定網頁標題與寬版顯示
st.set_page_config(page_title="千萬資產戰情室", layout="wide")
st.title("📊 我的專屬資產戰情室")

try:
    # 執行資料抓取
    data = get_data()
    
    if data:
        # 將資料轉為系統看得懂的表格，並命名欄位
        df_display = pd.DataFrame(data, columns=["資產項目", "金額"])
        
        # 防呆 3：強制將金額欄位轉為純數字，遇到文字或空白自動補 0
        df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
        
        # 計算總資產
        total_assets = df_display["金額"].sum()
        
        # 顯示最上方的大字報總額
        col1, col2 = st.columns(2)
        with col1:
            st.metric("目前資產總額", f"NT$ {total_assets:,.0f}")
        
        # 畫出華麗的資產配置圓餅圖
        fig = px.pie(df_display, values='金額', names='資產項目', title='資產配置比例')
        st.plotly_chart(fig, use_container_width=True)
        
        # 顯示下方的明細對帳單
        st.write("### 📝 資產明細清單")
        st.dataframe(df_display, use_container_width=True)
        
except Exception as e:
    # 如果還是有錯，會清楚顯示原因，不會讓系統直接當機
    st.error(f"戰情室連線暫時中斷，請確認網址 ID 是否正確。錯誤細節：{e}")

# 頁尾簽名檔
st.caption("數據自動對接更新 | 專為 Amy 隊長打造的理財決策系統")
