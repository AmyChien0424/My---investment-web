import streamlit as st
import pandas as pd
import plotly.express as px
import re

# ==========================================
# 1. 系統設定
# ==========================================
SPREADSHEET_ID = "1lVQm62yr_vy96TmeWYYF13ztS1mh1LoHjbRAeLYcKBc"
GID = "1762641193"
RETIREMENT_GOAL = 25000000  # 2,500 萬自由目標

# ==========================================
# 2. 核心功能：數據清洗與進階邏輯
# ==========================================
def get_processed_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    full_df = pd.read_csv(url).fillna(0)
    
    # 數字清理小工具
    def clean_num(val):
        if isinstance(val, str):
            res = re.sub(r'[^\d.-]', '', val)
            try: return float(res)
            except: return 0.0
        return float(val)

    if "金額" in full_df.columns:
        full_df["金額"] = full_df["金額"].apply(clean_num)
    
    first_col = full_df.columns[0]
    
    # 提取關鍵特定數據 (不參與圓餅圖加總)
    annual_dividend = full_df[full_df[first_col].astype(str).str.contains('年股利')]["金額"].sum()
    loan_amount = abs(full_df[full_df[first_col].astype(str).str.contains('質押借款')]["金額"].sum())
    pledged_market_value = full_df[full_df[first_col].astype(str).str.contains('質押成本計入')]["金額"].sum()
    
    # 排除非資產列 (過濾圓餅圖明細)
    display_df = full_df[~full_df[first_col].astype(str).str.contains('總|股利|Total|合計')]
    display_df = display_df[display_df[first_col] != 0]
    
    return display_df, annual_dividend, loan_amount, pledged_market_value

# ==========================================
# 3. 畫面呈現：自由航行儀表板
# ==========================================
st.set_page_config(page_title="Amy 的自由航行儀表板", layout="wide")
st.title("🚀 Amy 隊長：自由航行戰情室 II")

try:
    df, dividend, loan, market_value = get_processed_data()
    total_assets = df["金額"].sum()
    
    # --- 🎯 自由進度條 ---
    progress = min(total_assets / RETIREMENT_GOAL, 1.0)
    st.write(f"### 🏁 自由航行進度：{progress*100:.1f}%")
    st.progress(progress)
    
    # --- 📊 核心指標卡片 ---
    m1, m2, m3 = st.columns(3)
    m1.metric("目前總資產", f"NT$ {total_assets:,.0f}")
    m2.metric("每月被動加薪", f"NT$ {dividend/12:,.0f}", help="由年股利換算")
    
    # 計算質押維持率
    if loan > 0:
        ratio = (market_value / loan) * 100
        status = "✅ 安全" if ratio > 166 else "⚠️ 注意"
        m3.metric("質押維持率", f"{ratio:.0f}%", delta=status)
    else:
        m3.metric("質押維持率", "N/A (無借款)")

    # --- 📈 視覺化分析 ---
    st.write("---")
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        fig = px.pie(df, values='金額', names=df.columns[0], 
                     title='資產分佈比例', hole=0.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.write("### 📝 資產明細清單")
        st.dataframe(df.style.format({"金額": "{:,.0f}"}), height=400, use_container_width=True)

except Exception as e:
    st.error(f"系統升級中或連線異常：{e}")

st.caption("數據每小時同步 | 二期工程：自由加速計畫已啟動")
