import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观经济 CPI & PPI 双指标看板")

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
    st.error(f"❌ 找不到数据文件！请确保你先运行了 python get_cpi.py 和 python get_ppi.py。\n详细错误：{e}")
    st.stop()

st.sidebar.header("🔧 数据分析面板")

# ==================== 图表 1：CPI 与 PPI 双轴对比（专业分析核心） ====================
st.subheader("📈 CPI（消费者物价） vs PPI（工业出厂价） 对比分析")

# 使用 Plotly Graph Objects 绘制双Y轴图表
fig_dual = go.Figure()

# 添加 CPI 左轴
fig_dual.add_trace(go.Scatter(x=cpi_df['月份'], y=cpi_df['全国-当月'], 
                              mode='lines+markers', name='CPI (全国-当月)'))

# 添加 PPI 右轴
fig_dual.add_trace(go.Scatter(x=ppi_df['月份'], y=ppi_df['当月'], 
                              mode='lines+markers', name='PPI (当月)', 
                              yaxis='y2'))

# 设置双Y轴布局
fig_dual.update_layout(
    title="CPI (左轴) 与 PPI (右轴) 历史走势对比",
    xaxis=dict(tickformat="%Y年%m月", dtick="M12"),
    yaxis=dict(title="CPI 数值 (左轴)"),
    yaxis2=dict(title="PPI 数值 (右轴)", overlaying='y', side='right'),
    legend=dict(x=0, y=1.1, orientation='h')
)
fig_dual.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>")

st.plotly_chart(fig_dual, use_container_width=True)

st.markdown("> 💡 **分析师提示**：PPI（工厂端价格）通常是 CPI（消费端价格）的先行指标。如果蓝线（PPI）明显抬头，往往意味着几个月后红线（CPI）也会跟着上涨，这是观察通胀压力的重要信号！")

# ==================== 图表 2：CPI 同比与环比分析 ====================
st.subheader("📉 CPI 同比与环比变化趋势")
cpi_metrics = [col for col in cpi_df.columns if '同比' in col or '环比' in col]
if cpi_metrics:
    default_cpi = [c for c in cpi_metrics if '同比' in c][:1]
    selected_yoy_metric = st.selectbox("查看 CPI 的变化率指标：", cpi_metrics, index=0)
    
    fig_yoy = px.line(cpi_df, x='月份', y=selected_yoy_metric, 
                      title=f'{selected_yoy_metric} 走势',
                      markers=True)
    fig_yoy.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    fig_yoy.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}%<extra></extra>")
    st.plotly_chart(fig_yoy, use_container_width=True)
else:
    st.info("⚠️ 当前 CPI 数据中未检测到同比或环比列，无法绘制变化率图表。")


# ==================== 智能文字解读 ====================
with st.expander("🤖 点击查看AI动态解读（基于最新数据）"):
    latest_cpi = cpi_df.iloc[-1]
    latest_ppi = ppi_df.iloc[-1]
    st.write(f"🔹 **最新月份 ({latest_cpi['月份'].strftime('%Y年%m月')}) 宏观数据快照：**")
    st.write(f"- 全国 CPI 当月值：**{latest_cpi['全国-当月']}**")
    st.write(f"- PPI 当月值：**{latest_ppi['当月']}**")
    
    cpi_val = latest_cpi['全国-当月']
    if cpi_val > 103:
        st.warning("⚠️ CPI 较高，存在通胀压力，需关注购买力变化。")
    elif cpi_val < 99:
        st.warning("⚠️ CPI 偏低，存在通缩风险，需关注经济增长动能。")
    else:
        st.success("✅ CPI 处于 99~103 的温和区间，物价总体平稳。")
        
    st.write("📝 *（提示：如果 PPI 走高而 CPI 尚未跟上，说明成本在向终端传导中，未来消费端可能面临涨价。）*")

# ==================== 展示原始数据 ====================
with st.expander("📋 点击展开查看原始数据表格"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("CPI 数据")
        st.dataframe(cpi_df)
    with col2:
        st.write("PPI 数据")
        st.dataframe(ppi_df)

st.sidebar.success("✅ 双指标看板升级完成！")