import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观双指标看板 (含趋势均线)")

try:
    # 读取 CPI 数据
    cpi_df = pd.read_csv('cpi_data.csv')
    cpi_df['月份'] = cpi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    cpi_df['月份'] = pd.to_datetime(cpi_df['月份'])
    cpi_df = cpi_df.sort_values('月份', ascending=True)

    # 读取 PPI 数据
    ppi_df = pd.read_csv('ppi_data.csv')
    ppi_df['月份'] = ppi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    ppi_df['月份'] = pd.to_datetime(ppi_df['月份'])
    ppi_df = ppi_df.sort_values('月份', ascending=True)

except FileNotFoundError as e:
    st.error(f"❌ 找不到数据文件！请确保先运行了 python get_cpi.py 和 python get_ppi.py。\n详细错误：{e}")
    st.stop()

st.sidebar.header("🔧 数据控制面板")

# ==================== 图表 1：单指标趋势图（带移动平均线） ====================
st.subheader("📈 单指标历史趋势及移动均线分析")
# 提取 CPI 和 PPI 的核心列
cpi_options = [col for col in cpi_df.columns if col not in ['月份']]
ppi_options = [col for col in ppi_df.columns if col not in ['月份']]

selected_tab = st.radio("选择查看指标：", ["CPI 当月值", "PPI 当月值"])
if selected_tab == "CPI 当月值":
    data = cpi_df[['月份', '全国-当月']].copy()
    col_name = '全国-当月'
else:
    data = ppi_df[['月份', '当月']].copy()
    col_name = '当月'

# 计算移动平均线
data['3个月均线'] = data[col_name].rolling(window=3).mean()
data['6个月均线'] = data[col_name].rolling(window=6).mean()

fig_ma = px.line(data, x='月份', y=[col_name, '3个月均线', '6个月均线'],
                 title=f'{selected_tab} 及移动平均趋势',
                 markers=True)
fig_ma.update_xaxes(tickformat="%Y年%m月", dtick="M12")
fig_ma.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>")
st.plotly_chart(fig_ma, use_container_width=True)
st.caption("👉 蓝色为真实数据，黄/绿线为移动平均线（过滤短期噪音，看真实大趋势）。")


# ==================== 图表 2：CPI 与 PPI 双轴对比 ====================
st.subheader("📊 CPI 与 PPI 双轴对比（观察上下游传导）")
fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(x=cpi_df['月份'], y=cpi_df['全国-当月'], 
                              mode='lines+markers', name='CPI (消费端-当月)'))
fig_dual.add_trace(go.Scatter(x=ppi_df['月份'], y=ppi_df['当月'], 
                              mode='lines+markers', name='PPI (生产端-当月)', 
                              yaxis='y2'))
fig_dual.update_layout(
    title="CPI 与 PPI 走势对比 (左轴 CPI，右轴 PPI)",
    xaxis=dict(tickformat="%Y年%m月", dtick="M12"),
    yaxis=dict(title="CPI 数值 (左轴)"),
    yaxis2=dict(title="PPI 数值 (右轴)", overlaying='y', side='right'),
    legend=dict(x=0, y=1.1, orientation='h')
)
fig_dual.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>")
st.plotly_chart(fig_dual, use_container_width=True)
st.caption("💡 分析师提示：PPI（工厂成本）通常是 CPI（消费价格）的先行指标，PPI 大涨往往意味着 3-6 个月后 CPI 也会跟上。")

# ==================== 数据解读 ====================
with st.expander("🤖 点击查看AI动态解读（基于最新数据）"):
    latest_cpi = cpi_df.iloc[-1]
    latest_ppi = ppi_df.iloc[-1]
    st.write(f"🔹 **最新月份 ({latest_cpi['月份'].strftime('%Y年%m月')}) 宏观快照：**")
    st.write(f"- 全国 CPI 当月值：**{latest_cpi['全国-当月']}**")
    st.write(f"- PPI 当月值：**{latest_ppi['当月']}**")
    
    cpi_val = latest_cpi['全国-当月']
    if cpi_val > 103:
        st.warning("⚠️ 通胀压力显现，购买力承压。")
    elif cpi_val < 99:
        st.warning("⚠️ 有通缩苗头，需关注经济动能。")
    else:
        st.success("✅ 物价温和，经济处于健康区间。")
    st.write("📝 *移动均线交叉法则：如果 3个月均线 上穿 6个月均线，常被视为趋势向上的信号。*")

# ==================== 数据表 ====================
with st.expander("📋 点击展开查看原始数据"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("CPI 数据")
        st.dataframe(cpi_df)
    with col2:
        st.write("PPI 数据")
        st.dataframe(ppi_df)