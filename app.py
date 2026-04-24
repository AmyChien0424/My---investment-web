import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 系統設定：精準鎖定 ID 與分頁編號
# ==========================================
# 這是您剛才提供的完整 ID
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
# 這是您網址中指定的 gid 分頁編號
GID = "1762641193"

# ==========================================
# 2. 核心功能：無敵直讀抓取法
# ==========================================
def get_data():
    # 組合出最強勢的 CSV 導出網址
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    
    # 讀取資料：自動將第一列作為標題，抓取前 14 列內容
    df = pd.read_csv(url, nrows=14).fillna(0)
    return df

# ==========================================
# 3. 戰情室儀表板畫面呈現
# ==========================================
st.set_page_config(page_title="千萬資產戰情室", layout="wide")
st.title("📊 我的專屬資產戰情室")

try:
    df_display = get_data()
    
    if not df_display.empty:
        # 🛡️ 金額運算邏輯：自動辨識名為「金額」的欄位
        if "金額" in df_display.columns:
            df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
            total_assets = df_display["金額"].sum()
            
            # 顯示頂部總額數據
            col1, col2 = st.columns(2)
            with col1:
                st.metric("目前資產總額", f"NT$ {total_assets:,.0f}")
            
            # 畫出配置比例圓餅圖
            # 預設使用第一欄作為分類標籤
            label_col = df_display.columns[0]
            fig = px.pie(df_display, values='金額', names=label_col, title=f'資產配置比例 ({label_col})')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("提醒：試算表第一列標題需包含『金額』二字，系統才能計算總額。")

        # 顯示下方詳細資產清單 (會自動顯示所有新增欄位)
        st.write("### 📝 資產明細對帳單")
        st.dataframe(df_display, use_container_width=True)
        
except Exception as e:
    st.error(f"連線暫時中斷。請確認試算表共用權限是否已開啟。錯誤代碼：{e}")

st.caption("數據每小時自動同步 | 專為 Amy 隊長打造的理財決策系統")
