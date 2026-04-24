import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 系統設定：精準鎖定您的資料源
# ==========================================
# 門牌號碼：您的試算表 ID
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
# 分頁編號：對應您的「Data」分頁
GID = "1762641193"

# ==========================================
# 2. 核心功能：動態讀取與自動過濾
# ==========================================
def get_data():
    # 組合 CSV 導出網址
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    
    # 讀取資料：抓取前 50 列，確保涵蓋所有明細
    df = pd.read_csv(url).fillna(0)
    
    # 防呆過濾：排除掉「資產項目」中包含「總」字或空白的列（避免重複計算總額）
    # 這樣系統就不會把您的第 16 列「總價」也算進資產明細裡
    if not df.empty:
        first_col = df.columns[0]
        df = df[~df[first_col].astype(str).str.contains('總|Total|total|合計')]
        df = df[df[first_col] != 0] # 排除空行
        
    return df

# ==========================================
# 3. 戰情室儀表板畫面呈現
# ==========================================
st.set_page_config(page_title="千萬資產戰情室", layout="wide")
st.title("📊 我的專屬資產戰情室")

try:
    df_display = get_data()
    
    if not df_display.empty:
        # 🛡️ 金額運算：強制轉換「金額」欄位為數字
        if "金額" in df_display.columns:
            df_display["金額"] = pd.to_numeric(df_display["金額"], errors='coerce').fillna(0)
            
            # 計算真正的總資產
            total_assets = df_display["金額"].sum()
            
            # 顯示大字報
            st.metric("目前資產總額 (自動加總)", f"NT$ {total_assets:,.0f}")
            
            # 畫出圓餅圖
            label_col = df_display.columns[0]
            fig = px.pie(df_display, values='金額', names=label_col, 
                         title=f'資產配置比例分析 ({label_col})',
                         hole=0.3) # 加上中間圓孔，看起來更現代
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("請檢查試算表第一列標題是否有『金額』二字。")

        # 顯示下方明細表格
        st.write("### 📝 即時資產明細清單")
        st.dataframe(df_display, use_container_width=True)
        
except Exception as e:
    st.error(f"系統暫時無法連線到試算表，請確認權限設定。錯誤原因：{e}")

st.caption("數據每小時自動更新 | 專為 Amy 隊長打造的理財決策系統")
