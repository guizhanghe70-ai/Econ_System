import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import base64

try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观经济双指标看板 (全指标完全体)")

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
    
    # 新增 GDP 和 LPR
    gdp_df = pd.read_csv('gdp_data.csv')
    lpr_df = pd.read_csv('lpr_data.csv')
    lpr_df['日期'] = pd.to_datetime(lpr_df['日期'])
    lpr_df = lpr_df.sort_values('日期', ascending=True)

except FileNotFoundError as e:
    st.error(f"❌ 找不到数据文件！请确保运行了所有抓取脚本。\n错误：{e}")
    st.stop()

# ==================== 预警面板 ====================
st.sidebar.header("🔧 预警面板")
cpi_warning_high = st.sidebar.number_input("CPI 通胀警戒线", value=103.0, step=0.1)
cpi_warning_low = st.sidebar.number_input("CPI 通缩警戒线", value=99.0, step=0.1)
pmi_line = st.sidebar.number_input("PMI 荣枯线", value=50.0, step=0.1)
m2_warning_high = st.sidebar.number_input("M2 宽松警戒线 (高于此值)", value=15.0, step=0.5)
m2_warning_low = st.sidebar.number_input("M2 紧缩警戒线 (低于此值)", value=8.0, step=0.5)

latest_cpi = cpi_df.iloc[-1]
cpi_val = latest_cpi['全国-当月']
if cpi_val > cpi_warning_high:
    st.error(f"🚨 **警报！** 当前 CPI 为 {cpi_val}，突破 {cpi_warning_high} 警戒线！")
elif cpi_val < cpi_warning_low:
    st.warning(f"⚠️ **注意！** 当前 CPI 为 {cpi_val}，低于 {cpi_warning_low} 警戒线！")
else:
    st.success(f"✅ 当前 CPI 为 {cpi_val}，平稳区间。")

# ==================== 核心预测 ====================
def safe_forecast(series, steps=3):
    if len(series) < 3: return None, "数据不足"
    forecast_vals = None
    method_used = "基础趋势推算"
    if HAS_STATSMODELS:
        try:
            clean_series = series.dropna()
            if len(clean_series) > 4:
                model = ExponentialSmoothing(clean_series, trend='add', seasonal=None, initialization_method='estimated').fit()
                preds = model.forecast(steps).tolist()
                forecast_vals = preds
                method_used = "AI统计模型"
        except:
            forecast_vals = None
    if forecast_vals is None:
        try:
            diffs = series.diff().tail(3).dropna()
            recent_diff = diffs.mean() if len(diffs) > 0 else 0
            last_val = series.iloc[-1]
            forecast_vals = [last_val + recent_diff * (i+1) for i in range(steps)]
            method_used = "基础趋势推算"
        except:
            return None, "预测失败"
    return forecast_vals, method_used

def get_status(val, high, low):
    if val > high: return "⚠️ 存在通胀压力"
    elif val < low: return "⚠️ 存在通缩风险"
    else: return "✅ 物价温和稳定"

# ==================== 图表 1：主图及预测 ====================
st.subheader("📈 单指标趋势及移动均线分析")
metric_options = [col for col in cpi_df.columns if col != '月份']
selected_metric = st.sidebar.selectbox("📌 选择你想查看的指标：", metric_options, index=0)

if '当月' in selected_metric or '同比' in selected_metric or '环比' in selected_metric:
    data = ppi_df[['月份', '当月']].copy()
    col_name = '当月'
    data_type = "PPI"
else:
    data = cpi_df[['月份', selected_metric]].copy()
    col_name = selected_metric
    data_type = "CPI"

data['3个月移动均线'] = data[col_name].rolling(window=3).mean()
data['6个月移动均线'] = data[col_name].rolling(window=6).mean()

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data[col_name], mode='lines+markers', name='实际数据',
    text=[get_status(v, cpi_warning_high, cpi_warning_low) for v in data[col_name]], 
    hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['3个月移动均线'], mode='lines', name='3个月移动均线'))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['6个月移动均线'], mode='lines', name='6个月移动均线'))

last_date = data['月份'].iloc[-1]
forecast_vals, pred_method = safe_forecast(data[col_name])
forecast_text = ""
if forecast_vals is not None:
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=3, freq='MS')
    forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': forecast_vals})
    forecast_df['预测状态'] = forecast_df['预测值'].apply(lambda x: get_status(x, cpi_warning_high, cpi_warning_low))
    
    fig_ma.add_trace(go.Scatter(x=forecast_df['月份'], y=forecast_df['预测值'], mode='lines+markers', name='未来3个月预测趋势',
        line=dict(dash='dash', color='red'), marker=dict(color='red'), text=forecast_df['预测状态'],
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<br><b>📌 预测情况: %{text}</b><extra>预测</extra>"))
    forecast_text = f"💡 **{data_type} {pred_method}**：预计下月数值约为 **{forecast_vals[0]:.2f}**。"

fig_ma.update_layout(font=dict(size=14), hoverlabel=dict(font_size=15))
fig_ma.update_xaxes(tickformat="%Y年%m月", dtick="M12")
st.plotly_chart(fig_ma, use_container_width=True)
if forecast_text: st.info(forecast_text)


# ==================== M2 图表 ====================
st.subheader("💰 资金面指标: M2 (广义货币) 同比增长率")
m2_cols = [col for col in m2_df.columns if '同比' in col]
if m2_cols:
    selected_m2 = m2_cols[0]
    
    def get_m2_status(val):
        if val > m2_warning_high: return f"🔵 货币偏宽松 (突破 {m2_warning_high}%)"
        elif val < m2_warning_low: return f"🔴 货币偏紧缩 (跌破 {m2_warning_low}%)"
        else: return "🟢 货币平稳 (合理区间)"

    fig_m2 = go.Figure()
    fig_m2.add_trace(go.Scatter(x=m2_df['月份'], y=m2_df[selected_m2], mode='lines+markers', name=selected_m2,
        text=[get_m2_status(v) for v in m2_df[selected_m2]],
        hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}%<br><b>📌 状态: %{text}</b><extra></extra>"))

    m2_vals, m2_method = safe_forecast(m2_df[selected_m2])
    if m2_vals is not None:
        m2_last = m2_df['月份'].iloc[-1]
        m2_dates = pd.date_range(start=m2_last + pd.DateOffset(months=1), periods=3, freq='MS')
        m2_f_df = pd.DataFrame({'月份': m2_dates, '预测值': m2_vals})
        m2_f_df['预测状态'] = m2_f_df['预测值'].apply(get_m2_status)
        fig_m2.add_trace(go.Scatter(x=m2_f_df['月份'], y=m2_f_df['预测值'], mode='lines+markers', 
            name='未来3个月预测趋势', line=dict(dash='dash', color='orange'), marker=dict(color='orange'),
            text=m2_f_df['预测状态'],
            hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}%<br><b>📌 预测情况: %{text}</b><extra>预测</extra>"))
            
    fig_m2.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    fig_m2.update_layout(font=dict(size=14), hoverlabel=dict(font_size=15))
    st.plotly_chart(fig_m2, use_container_width=True)
    if m2_vals is not None: st.info(f"💡 **M2 {m2_method}**：预计下月同比增长约为 **{m2_vals[0]:.2f}%**。")


# ==================== PMI 图表 ====================
st.subheader("🏭 PMI（采购经理指数）景气度监测")
pmi_options = [col for col in pmi_df.columns if col != '月份']
selected_pmi = st.selectbox("选择 PMI 分类指标：", pmi_options)

pmi_data = pmi_df[['月份', selected_pmi]].copy()

def get_pmi_status(val):
    return "✅ 扩张" if val > pmi_line else "⚠️ 收缩"

fig_pmi = go.Figure()
fig_pmi.add_trace(go.Scatter(
    x=pmi_data['月份'], y=pmi_data[selected_pmi],
    mode='lines+markers', name=selected_pmi,
    text=[get_pmi_status(v) for v in pmi_data[selected_pmi]],
    hovertemplate="月份: %{x|%Y年%m月}<br>PMI: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))

pmi_vals, pmi_method = safe_forecast(pmi_data[selected_pmi])
if pmi_vals is not None:
    pmi_last = pmi_data['月份'].iloc[-1]
    pmi_dates = pd.date_range(start=pmi_last + pd.DateOffset(months=1), periods=3, freq='MS')
    pmi_f_df = pd.DataFrame({'月份': pmi_dates, '预测值': pmi_vals})
    pmi_f_df['预测状态'] = pmi_f_df['预测值'].apply(get_pmi_status)
    fig_pmi.add_trace(go.Scatter(
        x=pmi_f_df['月份'], y=pmi_f_df['预测值'], mode='lines+markers', 
        name='未来3个月预测趋势', line=dict(dash='dash', color='orange'), marker=dict(color='orange'),
        text=pmi_f_df['预测状态'],
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<br><b>📌 预测情况: %{text}</b><extra>预测</extra>"))

fig_pmi.add_hline(y=pmi_line, line_dash="dash", line_color="red", annotation_text=f"荣枯线 {pmi_line}")
fig_pmi.update_xaxes(tickformat="%Y年%m月", dtick="M12")
fig_pmi.update_layout(font=dict(size=14), hoverlabel=dict(font_size=15))
st.plotly_chart(fig_pmi, use_container_width=True)
if pmi_vals is not None: st.info(f"💡 **PMI {pmi_method}**：预计下月 PMI 约为 **{pmi_vals[0]:.2f}**。")


# ==================== 新增 GDP 图表 ====================
st.subheader("🏛️ GDP (国内生产总值) 季度增速监测")
try:
    gdp_df['季度'] = gdp_df['季度'].astype(str).str.replace('年', '年').str.replace('季度', '季度')
    fig_gdp = px.bar(gdp_df.tail(12), x='季度', y='国内生产总值-同比增长', 
                     title='最近 12 个季度 GDP 同比增速 (%)',
                     text='国内生产总值-同比增长')
    fig_gdp.update_xaxes(tickangle=45)
    fig_gdp.update_layout(font=dict(size=14))
    st.plotly_chart(fig_gdp, use_container_width=True)
    latest_gdp = gdp_df.iloc[-1]
    st.info(f"📌 **最新 GDP 数据**：最新季度 GDP 同比增长 **{latest_gdp['国内生产总值-同比增长']}%**。")
except:
    st.warning("⚠️ GDP 数据格式读取异常，请检查 gdp_data.csv。")


# ==================== 新增 LPR 图表 ====================
st.subheader("🏦 LPR (贷款市场报价利率) 走势监测")
try:
    fig_lpr = go.Figure()
    fig_lpr.add_trace(go.Scatter(x=lpr_df['日期'], y=lpr_df['1年期'], mode='lines+markers', name='1年期 LPR (企业贷款基准)'))
    fig_lpr.add_trace(go.Scatter(x=lpr_df['日期'], y=lpr_df['5年期'], mode='lines+markers', name='5年期以上 LPR (房贷基准)'))
    fig_lpr.update_xaxes(tickformat="%Y年%m月", dtick="M12")
    fig_lpr.update_layout(font=dict(size=14), hoverlabel=dict(font_size=15))
    st.plotly_chart(fig_lpr, use_container_width=True)
    latest_lpr = lpr_df.iloc[-1]
    st.info(f"📌 **最新 LPR**：1年期 **{latest_lpr['1年期']}%**，5年期以上 **{latest_lpr['5年期']}%**。")
except:
    st.warning("⚠️ LPR 数据读取异常，请检查 lpr_data.csv。")


# ==================== 导出功能 ====================
st.subheader("📥 数据导出")
col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 下载 CPI 数据 (CSV)", cpi_df.to_csv(index=False).encode('utf-8-sig'), "cpi_data.csv", "text/csv")
with col2:
    st.download_button("📥 下载 PMI 数据 (CSV)", pmi_df.to_csv(index=False).encode('utf-8-sig'), "pmi_data.csv", "text/csv")