import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import base64

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观双指标看板 (完全体)")

# ==================== 数据加载 ====================
try:
    cpi_df = pd.read_csv('cpi_data.csv')
    cpi_df['月份'] = cpi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    cpi_df['月份'] = pd.to_datetime(cpi_df['月份'])
    cpi_df = cpi_df.sort_values('月份', ascending=True)

    ppi_df = pd.read_csv('ppi_data.csv')
    ppi_df['月份'] = ppi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    ppi_df['月份'] = pd.to_datetime(ppi_df['月份'])
    ppi_df = ppi_df.sort_values('月份', ascending=True)

    pmi_df = pd.read_csv('pmi_data.csv')
    pmi_df['月份'] = pmi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    pmi_df['月份'] = pd.to_datetime(pmi_df['月份'])
    pmi_df = pmi_df.sort_values('月份', ascending=True)
    
    m2_df = pd.read_csv('m2_data.csv')
    m2_df['月份'] = m2_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    m2_df['月份'] = pd.to_datetime(m2_df['月份'])
    m2_df = m2_df.sort_values('月份', ascending=True)

except FileNotFoundError as e:
    st.error(f"❌ 找不到数据文件！请确保运行了 get_cpi.py、get_ppi.py、get_pmi.py 和 get_m2.py。\n错误：{e}")
    st.stop()

# ==================== 自定义预警阈值 (侧边栏) ====================
st.sidebar.header("🔧 预警面板")
cpi_warning_high = st.sidebar.number_input("CPI 通胀警戒线 (高于此值预警)", value=103.0, step=0.1)
cpi_warning_low = st.sidebar.number_input("CPI 通缩警戒线 (低于此值预警)", value=99.0, step=0.1)
pmi_line = st.sidebar.number_input("PMI 荣枯线 (高于扩张，低于收缩)", value=50.0, step=0.1)

# ==================== 预警横幅 ====================
latest_cpi = cpi_df.iloc[-1]
cpi_val = latest_cpi['全国-当月']
if cpi_val > cpi_warning_high:
    st.error(f"🚨 **警报！** 当前全国 CPI 为 {cpi_val}，已突破 {cpi_warning_high} 自定义警戒线，存在高通胀压力！")
elif cpi_val < cpi_warning_low:
    st.warning(f"⚠️ **注意！** 当前全国 CPI 为 {cpi_val}，低于 {cpi_warning_low} 自定义警戒线，需警惕通缩风险。")
else:
    st.success(f"✅ 当前全国 CPI 为 {cpi_val}，处于 {cpi_warning_low}~{cpi_warning_high} 自定义平稳区间。")

# ==================== 图表 1：主图及预测 ====================
st.subheader("📈 单指标趋势及移动均线分析")
metric_options = [col for col in cpi_df.columns if col != '月份']
selected_metric = st.sidebar.selectbox("📌 选择你想查看的指标：", metric_options, index=0)

if '当月' in selected_metric or '同比' in selected_metric or '环比' in selected_metric:
    data = ppi_df[['月份', '当月']].copy()
    col_name = '当月'
    data_type = "PPI（工业生产者出厂价格指数）"
else:
    data = cpi_df[['月份', selected_metric]].copy()
    col_name = selected_metric
    data_type = "CPI（居民消费价格指数）"

data['3个月移动均线'] = data[col_name].rolling(window=3).mean()
data['6个月移动均线'] = data[col_name].rolling(window=6).mean()

# 判断状态
def get_status(val, high, low):
    if val > high: return "⚠️ 存在通胀压力"
    elif val < low: return "⚠️ 存在通缩风险"
    else: return "✅ 物价温和稳定"

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data[col_name], mode='lines+markers', name='实际数据',
    text=[get_status(v, cpi_warning_high, cpi_warning_low) for v in data[col_name]], 
    hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['3个月移动均线'], mode='lines', name='3个月移动均线'))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['6个月移动均线'], mode='lines', name='6个月移动均线'))

# 预测逻辑
last_date = data['月份'].iloc[-1]
forecast_df = pd.DataFrame()
forecast_text = "⚠️ 数据不足以预测。"
if len(data) >= 6: # 已改为6个月即可触发
    try:
        model = ExponentialSmoothing(data[col_name], trend='add', seasonal=None).fit()
        forecast_values = model.forecast(3)
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='MS')
        forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': forecast_values})
        forecast_text = f"💡 **趋势预估**：预计下个月数值约为 **{forecast_values[0]:.2f}**。"
    except:
        pass

# 🟢【核心修复】：给预测线加上正确的状态参数
if not forecast_df.empty:
    # 使用 lambda 完美把侧边栏的阈值传进去
    forecast_df['预测状态'] = forecast_df['预测值'].apply(lambda x: get_status(x, cpi_warning_high, cpi_warning_low))
    fig_ma.add_trace(go.Scatter(x=forecast_df['月份'], y=forecast_df['预测值'], mode='lines+markers', name='未来3个月预测趋势',
        line=dict(dash='dash', color='red'), marker=dict(color='red'), 
        text=forecast_df['预测状态'],
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<br><b>📌 预测情况: %{text}</b><extra>预测</extra>"))

fig_ma.update_xaxes(tickformat="%Y年%m月", dtick="M12")
fig_ma.update_layout(margin=dict(b=80))
st.plotly_chart(fig_ma, use_container_width=True)
if forecast_text: st.info(forecast_text)

# ==================== M2 数据展示栏 ====================
st.subheader("💰 资金面指标: M2 (广义货币) 同比增长率")
m2_cols = [col for col in m2_df.columns if '同比' in col][:1]
if m2_cols:
    selected_m2 = m2_cols[0]
    fig_m2 = px.line(m2_df, x='月份', y=selected_m2, title=f"M2 同比增长走势")
    fig_m2.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    st.plotly_chart(fig_m2, use_container_width=True)
    st.caption("💡 M2 增速是经济货币供应的宽口径指标，M2 大涨往往预示着未来几个月 CPI 会跟随上涨。")

# ==================== PMI 景气度 (使用了自定义荣枯线) ====================
st.subheader("🏭 PMI（采购经理指数）景气度监测")
pmi_options = [col for col in pmi_df.columns if col != '月份']
selected_pmi = st.selectbox("选择 PMI 分类指标：", pmi_options)

pmi_data = pmi_df[['月份', selected_pmi]].copy()
fig_pmi = go.Figure()
fig_pmi.add_trace(go.Scatter(
    x=pmi_data['月份'], y=pmi_data[selected_pmi],
    mode='lines+markers', name=selected_pmi,
    hovertemplate="月份: %{x|%Y年%m月}<br>PMI数值: %{y:.2f}<extra></extra>"))
fig_pmi.add_hline(y=pmi_line, line_dash="dash", line_color="red", annotation_text=f"自定义荣枯线 {pmi_line}")
fig_pmi.update_xaxes(tickformat="%Y年%m月", dtick="M12")
st.plotly_chart(fig_pmi, use_container_width=True)

# ==================== 一键导出简报功能 ====================
st.subheader("📥 数据导出与简报")
col1, col2, col3 = st.columns(3)
with col1:
    csv_cpi = cpi_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载 CPI 数据 (CSV)", csv_cpi, "cpi_data.csv", "text/csv")
with col2:
    csv_pmi = pmi_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载 PMI 数据 (CSV)", csv_pmi, "pmi_data.csv", "text/csv")
with col3:
    html_report = f"""
    <h2>经济运行简报 ({latest_cpi['月份'].strftime('%Y年%m月')})</h2>
    <p><b>最新 CPI：</b>{latest_cpi['全国-当月']}</p>
    <p><b>最新 PMI：</b>{pmi_df.iloc[-1][selected_pmi]}</p>
    <p><b>经济分析：</b>当前宏观数据整体处于分析区间。</p>
    """
    b64 = base64.b64encode(html_report.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="economic_report.html">📄 下载简报 (HTML)</a>'
    st.markdown(href, unsafe_allow_html=True)

# ==================== 数据表 ====================
with st.expander("📋 点击展开查看所有原始数据表格"):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.write("CPI 数据"); st.dataframe(cpi_df)
    with col2: st.write("PPI 数据"); st.dataframe(ppi_df)
    with col3: st.write("PMI 数据"); st.dataframe(pmi_df)
    with col4: st.write("M2 数据"); st.dataframe(m2_df)