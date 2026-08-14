import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观经济 CPI 数据看板")

try:
    df = pd.read_csv('cpi_data.csv')
    # 处理日期
    df['月份'] = df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    df['月份'] = pd.to_datetime(df['月份'])
except FileNotFoundError:
    st.error("❌ 找不到数据文件！请先运行 python get_cpi.py 生成数据。")
    st.stop()

# 剔除月份列，获取可选指标
metric_options = [col for col in df.columns if col != '月份']

st.sidebar.header("🔧 数据控制面板")

# ==================== 图表 1：带移动平均线的趋势图 ====================
selected_metric = st.sidebar.selectbox("📌 选择你想查看的指标：", metric_options, index=0)
st.subheader(f"📈 {selected_metric} 历史走势")

# 把数据提取出来用于分析
plot_data = df[['月份', selected_metric]].copy()
# 计算 3 个月和 6 个月的移动平均线
plot_data['3个月移动均线'] = plot_data[selected_metric].rolling(window=3).mean()
plot_data['6个月移动均线'] = plot_data[selected_metric].rolling(window=6).mean()

# 使用 Plotly 画图
fig = px.line(plot_data, x='月份', y=[selected_metric, '3个月移动均线', '6个月移动均线'],
              title=f'{selected_metric} 及其移动平均趋势',
              markers=True)

# 强制 X轴显示中文时间格式
fig.update_xaxes(tickformat="%Y年%m月", dtick="M12")

# 优化图例显示格式
fig.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>")

st.plotly_chart(fig, use_container_width=True)


# ==================== 图表 2：多指标对比 ====================
st.subheader("🔁 多指标对比分析")
compare_metrics = st.multiselect("按住 Ctrl 或 Shift 键多选对比：", metric_options, default=['全国-当月', '城市-当月'])

if compare_metrics:
    compare_df = df[['月份'] + compare_metrics].melt(id_vars=['月份'], var_name='指标', value_name='数值')
    fig_compare = px.line(compare_df, x='月份', y='数值', color='指标', title='主要经济指标对比')
    fig_compare.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    fig_compare.update_traces(hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>")
    st.plotly_chart(fig_compare, use_container_width=True)


# ==================== 智能文字解读（教你如何看数据） ====================
with st.expander("🤖 点击查看AI动态解读（基于最新数据）"):
    latest_data = df.iloc[-1]
    st.write(f"🔹 **最新月份 ({latest_data['月份'].strftime('%Y年%m月')}) 数据解读：**")
    if '全国-当月' in df.columns:
        cpi_val = latest_data['全国-当月']
        st.write(f"- 全国居民消费价格指数当月值为 **{cpi_val}**。")
        if cpi_val > 103:
            st.warning("⚠️ 该数值较高，说明当前有较为明显的通货膨胀压力。")
        elif cpi_val < 99:
            st.warning("⚠️ 该数值偏低，说明当前经济存在通缩风险。")
        else:
            st.success("✅ 该数值处于 99~103 的温和区间，物价稳定，经济处于健康状态。")
        
    st.write("📝 *（提示：移动平均线如果开始抬头，说明经济可能进入上升周期；如果掉头向下，说明增长动能减弱。）*")


# 展示原始数据
with st.expander("📋 点击展开查看原始数据表格"):
    st.dataframe(df)

st.sidebar.success("✅ 看板已上线，增加移动平均趋势分析！")