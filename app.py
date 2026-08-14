import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观双指标看板 (含PMI、预警与导出)")

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

except FileNotFoundError as e:
    st.error(f"❌ 找不到数据文件！请确保运行了 python get_cpi.py、get_ppi.py 和 get_pmi.py。\n错误：{e}")
    st.stop()

# ==================== 预警横幅功能 ====================
latest_cpi = cpi_df.iloc[-1]
cpi_val = latest_cpi['全国-当月']
if cpi_val > 103:
    st.error(f"🚨 **警报！** 当前全国 CPI 为 {cpi_val}，已突破 103 警戒线，存在高通胀压力！")
elif cpi_val < 99:
    st.warning(f"⚠️ **注意！** 当前全国 CPI 为 {cpi_val}，低于 99 警戒线，需警惕通缩风险。")
else:
    st.success(f"✅ 当前全国 CPI 为 {cpi_val}，处于 99~103 的正常平稳区间。")

st.sidebar.header("🔧 数据控制面板")

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

def get_status(val):
    if val > 103: return "⚠️ 存在通胀压力"
    elif val < 99: return "⚠️ 存在通缩风险"
    else: return "✅ 物价温和稳定"

# -------- 预测功能 --------
forecast_text = "⚠️ 当前数据不足无法预测。"
forecast_df = pd.DataFrame()
last_date = data['月份'].iloc[-1]

if col_name == '当月':
    ref_range = "（参考平稳区间：97.0 ~ 103.0）"
else:
    ref_range = "（参考平稳区间：99.0 ~ 103.0）"

if len(data) >= 24:
    try:
        model = ExponentialSmoothing(data[col_name], trend='add', seasonal='add', seasonal_periods=12).fit()
        forecast_values = model.forecast(3)
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='MS')
        forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': forecast_values})
        forecast_df['预测状态'] = forecast_df['预测值'].apply(get_status)
        forecast_text = f"💡 **{data_type} 模型预测**：预计下个月数值约为 **{forecast_values[0]:.2f}** {ref_range}。"
    except:
        forecast_text = "⚠️ 因数据波动降级为基础预估。"
        forecast_df = pd.DataFrame()
        
if forecast_df.empty and len(data) >= 12:
    try:
        last_6m_avg = data[col_name].iloc[-6:].mean()
        last_3m_avg = data[col_name].iloc[-3:].mean()
        val_next = last_3m_avg + 0.2 if last_3m_avg > last_6m_avg else last_3m_avg - 0.2 if last_3m_avg < last_6m_avg else last_3m_avg
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='MS')
        forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': [val_next, val_next+0.1, val_next+0.2]})
        forecast_df['预测状态'] = forecast_df['预测值'].apply(get_status)
        forecast_text = f"💡 **{data_type} 趋势预估**：基于最近趋势，预计下个月数值约为 **{val_next:.2f}** {ref_range}。"
    except:
        pass

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data[col_name], mode='lines+markers', name='实际数据',
    text=[get_status(v) for v in data[col_name]], hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['3个月移动均线'], mode='lines', name='3个月移动均线'))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['6个月移动均线'], mode='lines', name='6个月移动均线'))
if not forecast_df.empty:
    fig_ma.add_trace(go.Scatter(x=forecast_df['月份'], y=forecast_df['预测值'], mode='lines+markers', name='未来3个月预测趋势',
        line=dict(dash='dash', color='red'), marker=dict(color='red'), text=forecast_df['预测状态'],
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<br><b>📌 预测情况: %{text}</b><extra>预测</extra>"))
fig_ma.update_xaxes(tickformat="%Y年%m月", dtick="M12")
fig_ma.add_annotation(xref="paper", yref="paper", x=0.5, y=-0.15,
    text=f"🔵 {data_type} 实际 | 🔷 3个月均线 | 🔴 6个月均线 | {ref_range}",
    showarrow=False, font=dict(size=12))
fig_ma.update_layout(margin=dict(b=80))
st.plotly_chart(fig_ma, use_container_width=True)
if forecast_text: st.info(forecast_text)

# ==================== 环比/同比柱状图 ====================
st.subheader("📊 指标同比与环比增长分析")
comp_cols = [c for c in data.columns if '同比' in c or '环比' in c]
if comp_cols:
    selected_trend = st.selectbox("查看具体的增长幅度(柱状图)：", comp_cols)
    fig_bar = px.bar(data, x='月份', y=selected_trend, title=f'{selected_trend} 变化幅度')
    fig_bar.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    st.plotly_chart(fig_bar, use_container_width=True)

# ==================== 🌟 新增：PMI 预警与预测模块（大幅升级） ====================
st.subheader("🏭 PMI（采购经理指数）景气度监测")
pmi_options = [col for col in pmi_df.columns if col != '月份']
selected_pmi = st.selectbox("选择 PMI 分类指标：", pmi_options)

pmi_data = pmi_df[['月份', selected_pmi]].copy()
pmi_data['3个月移动均线'] = pmi_data[selected_pmi].rolling(window=3).mean()

def get_pmi_status(val):
    if val > 50: return "✅ 经济处于扩张区间"
    else: return "⚠️ 经济处于收缩区间"

# ========== PMI 预测逻辑 ==========
pmi_forecast_text = ""
pmi_forecast_df = pd.DataFrame()
if len(pmi_data) >= 12:
    try:
        # PMI 月度波动极大，更适合只追踪趋势
        model = ExponentialSmoothing(pmi_data[selected_pmi], trend='add', seasonal=None).fit()
        pmi_forecast_vals = model.forecast(3)
        last_date = pmi_data['月份'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='MS')
        pmi_forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': pmi_forecast_vals})
        pmi_forecast_df['预测状态'] = pmi_forecast_df['预测值'].apply(get_pmi_status)
        pmi_forecast_text = f"💡 **PMI 趋势预测**：基于最近走势，预计下个月 PMI 约为 **{pmi_forecast_vals[0]:.2f}**。"
    except:
        pmi_forecast_text = "⚠️ PMI 数据波动较大，无法进行准确趋势预测。"

# ========== 画图 ==========
fig_pmi = go.Figure()
fig_pmi.add_trace(go.Scatter(
    x=pmi_data['月份'], y=pmi_data[selected_pmi],
    mode='lines+markers', name=selected_pmi,
    text=[get_pmi_status(v) for v in pmi_data[selected_pmi]],
    hovertemplate="月份: %{x|%Y年%m月}<br>PMI数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"
))
# 预测线
if not pmi_forecast_df.empty:
    fig_pmi.add_trace(go.Scatter(
        x=pmi_forecast_df['月份'], y=pmi_forecast_df['预测值'],
        mode='lines+markers', name='未来3个月PMI预测趋势',
        line=dict(dash='dash', color='orange'),
        marker=dict(color='orange'),
        text=pmi_forecast_df['预测状态'],
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra>预测</extra>"
    ))

# 加上 50 荣枯线
fig_pmi.add_hline(y=50, line_dash="dash", line_color="red", annotation_text="荣枯线 50")
fig_pmi.update_xaxes(tickformat="%Y年%m月", dtick="M12")
st.plotly_chart(fig_pmi, use_container_width=True)

# ========== PMI 预警与解读提示 ==========
latest_pmi_val = pmi_df.iloc[-1][selected_pmi]
if latest_pmi_val > 50:
    st.success(f"✅ **当前状态**：{selected_pmi} 最新值为 **{latest_pmi_val}**。位于 50 荣枯线之上，表明制造业正处于 **扩张区间**，工业景气度良好。")
else:
    st.warning(f"⚠️ **重要预警**：{selected_pmi} 最新值为 **{latest_pmi_val}**。已跌破 50 荣枯线，表明制造业已进入 **收缩区间**，需警惕订单减少、工业景气度下滑的风险。")

if pmi_forecast_text:
    st.info(pmi_forecast_text)

# ==================== 一键导出 CSV ====================
st.subheader("📥 数据导出与分析")
col1, col2 = st.columns(2)
with col1:
    csv_cpi = cpi_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载 CPI 数据 (CSV)", csv_cpi, "cpi_data.csv", "text/csv")
with col2:
    csv_pmi = pmi_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下载 PMI 数据 (CSV)", csv_pmi, "pmi_data.csv", "text/csv")

# ==================== AI 解读 ====================
with st.expander("🤖 点击查看AI动态解读（基于最新数据）"):
    pmi_col_name = pmi_df.columns[1]  # 自动识别 PMI 列名
    pmi_val = pmi_df.iloc[-1][pmi_col_name] 

    st.write(f"🔹 **最新月份 ({latest_cpi['月份'].strftime('%Y年%m月')}) 宏观快照：**")
    st.write(f"- 全国 CPI：**{latest_cpi['全国-当月']}** （参考：99.0 ~ 103.0）")
    st.write(f"- {pmi_col_name}：**{pmi_val}** （>50 为扩张，<50 为收缩）")

# ==================== 数据表 ====================
with st.expander("📋 点击展开查看所有原始数据表格"):
    col1, col2, col3 = st.columns(3)
    with col1: st.write("CPI 数据"); st.dataframe(cpi_df)
    with col2: st.write("PPI 数据"); st.dataframe(ppi_df)
    with col3: st.write("PMI 数据"); st.dataframe(pmi_df)