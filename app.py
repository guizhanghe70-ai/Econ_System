import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观经济 CPI 数据看板")

try:
    df = pd.read_csv('cpi_data.csv')
    # 处理中文日期格式（修复之前的日期报错）
    df['月份'] = df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    df['月份'] = pd.to_datetime(df['月份'])
except FileNotFoundError:
    st.error("❌ 找不到数据文件！请先运行 python get_cpi.py 生成数据。")
    st.stop()

# 剔除“月份”列，剩下的都是可以选择的指标
metric_options = [col for col in df.columns if col != '月份']

st.sidebar.header("🔧 数据控制面板")

# =================== 图表 1：单指标走势 ===================
selected_metric = st.sidebar.selectbox("📌 选择你想查看的指标：", metric_options, index=0)
st.subheader(f"📈 {selected_metric} 走势图")

fig = px.line(df, x='月份', y=selected_metric, 
              title=f'{selected_metric} 历史走势',
              markers=True)

# 强制 X轴和悬浮提示显示中文时间格式
fig.update_xaxes(
    tickformat="%Y年%m月",   # X轴时间格式改为：2026年08月
    dtick="M12"              # 控制刻度密度，防止年份挤成一团
)
fig.update_traces(
    hovertemplate=f"月份: %{{x|%Y年%m月}}<br>{selected_metric}: %{{y:.2f}}<extra></extra>"
)
st.plotly_chart(fig, use_container_width=True)


# =================== 图表 2：多指标对比 ===================
st.subheader("🔁 多指标对比分析")
compare_metrics = st.multiselect("按住 Ctrl 或 Shift 键多选对比：", metric_options, default=['全国-当月', '城市-当月'])

if compare_metrics:
    # 把数据转换成 Plotly 可以对比的长格式
    compare_df = df[['月份'] + compare_metrics].melt(id_vars=['月份'], var_name='指标', value_name='数值')
    
    fig_compare = px.line(compare_df, x='月份', y='数值', color='指标',
                          title='主要经济指标对比')
    
    # 同样为对比图设定中文时间格式
    fig_compare.update_xaxes(
        tickformat="%Y年%m月",
        dtick="M12"
    )
    fig_compare.update_traces(
        hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<extra>%{fullData.name}</extra>"
    )
    st.plotly_chart(fig_compare, use_container_width=True)


# =================== 展示原始数据 ===================
with st.expander("📋 点击展开查看原始数据表格"):
    st.dataframe(df)

st.sidebar.success("✅ 看板已上线，鼠标悬停即可查看详细数字！")