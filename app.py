import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from statsmodels.tsa.holtwinters import ExponentialSmoothing

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.title("📊 中国宏观双指标看板（含趋势预测）")

try:
    cpi_df = pd.read_csv('cpi_data.csv')
    cpi_df['月份'] = cpi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    cpi_df['月份'] = pd.to_datetime(cpi_df['月份'])
    cpi_df = cpi_df.sort_values('月份', ascending=True)

    ppi_df = pd.read_csv('ppi_data.csv')
    ppi_df['月份'] = ppi_df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
    ppi_df['月份'] = pd.to_datetime(ppi_df['月份'])
    ppi_df = ppi_df.sort_values('月份', ascending=True)

except FileNotFoundError as e:
    st.error(f"❌ 找不到数据文件！请确保先运行了 python get_cpi.py 和 python get_ppi.py。\n详细错误：{e}")
    st.stop()

st.sidebar.header("🔧 数据控制面板")

# ==================== 图表 1：带移动平均线和预测的趋势图 ====================
st.subheader("📈 单指标趋势及移动均线分析")
metric_options = [col for col in cpi_df.columns if col != '月份']
selected_metric = st.sidebar.selectbox("📌 选择你想查看的指标：", metric_options, index=0)

if '当月' in selected_metric or '同比' in selected_metric or '环比' in selected_metric:
    data = ppi_df[['月份', '当月']].copy()
    col_name = '当月'
else:
    data = cpi_df[['月份', selected_metric]].copy()
    col_name = selected_metric

data['3个月移动均线'] = data[col_name].rolling(window=3).mean()
data['6个月移动均线'] = data[col_name].rolling(window=6).mean()

def get_status(val):
    if val > 103: return "⚠️ 存在通胀压力"
    elif val < 99: return "⚠️ 存在通缩风险"
    else: return "✅ 物价温和稳定"

# ----- 预测功能开始 -----
forecast_text = ""
forecast_df = pd.DataFrame()
if len(data) >= 12: # 数据够长才做预测
    try:
        # 使用 Holt-Winters 进行预测（模型参数自动匹配）
        model = ExponentialSmoothing(data[col_name], trend='add', seasonal=None).fit()
        # 预测未来 3 个月
        forecast_steps = 3
        forecast_values = model.forecast(forecast_steps)
        
        # 构建预测的数据框
        last_date = data['月份'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1), periods=forecast_steps, freq='MS')
        forecast_df = pd.DataFrame({'月份': forecast_dates, '预测值': forecast_values})
        forecast_text = f"💡 **模型预测**：根据过去数据推算，未来 3 个月的指标趋势平缓，预计下个月数值为 **{forecast_values[0]:.2f}**。"
    except Exception as e:
        forecast_text = "⚠️ 当前数据波动过大或样本不足，无法进行精确预测。"
# ----- 预测功能结束 -----

fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(
    x=data['月份'], y=data[col_name],
    mode='lines+markers', name=selected_metric,
    text=[get_status(v) for v in data[col_name]],
    hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"
))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['3个月移动均线'], mode='lines', name='3个月移动均线'))
fig_ma.add_trace(go.Scatter(x=data['月份'], y=data['6个月移动均线'], mode='lines', name='6个月移动均线'))

# 画预测线（如果没有预测数据，则不画）
if not forecast_df.empty:
    fig_ma.add_trace(go.Scatter(
        x=forecast_df['月份'], y=forecast_df['预测值'],
        mode='lines+markers', name='未来3个月预测趋势',
        line=dict(dash='dash', color='red'), # 使用红色虚线突出显示预测
        marker=dict(color='red'),
        hovertemplate="预测月份: %{x|%Y年%m月}<br>预测数值: %{y:.2f}<extra>预测</extra>"
    ))

fig_ma.update_xaxes(tickformat="%Y年%m月", dtick="M12")
st.plotly_chart(fig_ma, use_container_width=True)

# 在图表下方展示预测结果
if forecast_text:
    st.info(forecast_text)


# ==================== 图表 2：CPI & PPI 双轴对比 ====================
st.subheader("🔁 CPI（消费端） vs PPI（生产端） 对比分析")
def get_ppi_status(val):
    if val > 103: return "工厂生产成本偏高"
    elif val < 97: return "工业生产需求偏冷"
    else: return "工业生产价格平稳"

fig_dual = go.Figure()
fig_dual.add_trace(go.Scatter(
    x=cpi_df['月份'], y=cpi_df['全国-当月'], 
    mode='lines+markers', name='CPI (全国-当月)',
    text=[get_status(v) for v in cpi_df['全国-当月']],
    hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 CPI状态: %{text}</b><extra>CPI</extra>"
))
fig_dual.add_trace(go.Scatter(
    x=ppi_df['月份'], y=ppi_df['当月'], 
    mode='lines+markers', name='PPI (当月)', yaxis='y2',
    text=[get_ppi_status(v) for v in ppi_df['当月']],
    hovertemplate="月份: %{x|%Y年%m月}<br>数值: %{y:.2f}<br><b>📌 PPI状态: %{text}</b><extra>PPI</extra>"
))
fig_dual.update_layout(
    title="CPI (左轴) 与 PPI (右轴) 历史走势对比",
    xaxis=dict(tickformat="%Y年%m月", dtick="M12"),
    yaxis=dict(title="CPI 数值 (左轴)"),
    yaxis2=dict(title="PPI 数值 (右轴)", overlaying='y', side='right'),
    legend=dict(x=0, y=1.1, orientation='h')
)
st.plotly_chart(fig_dual, use_container_width=True)

# ==================== AI解读 ====================
with st.expander("🤖 点击查看AI动态解读（基于最新数据）"):
    latest_cpi = cpi_df.iloc[-1]
    latest_ppi = ppi_df.iloc[-1]
    st.write(f"🔹 **最新月份 ({latest_cpi['月份'].strftime('%Y年%m月')}) 宏观数据快照：**")
    st.write(f"- 全国 CPI 当月值：**{latest_cpi['全国-当月']}** （参考平稳区间：99.0 ~ 103.0）")
    st.write(f"- PPI 当月值：**{latest_ppi['当月']}** （参考平稳区间：97.0 ~ 103.0）")
    
    cpi_val = latest_cpi['全国-当月']
    if cpi_val > 103:
        st.warning("⚠️ CPI 较高（大于103），存在通胀压力。")
    elif cpi_val < 99:
        st.warning("⚠️ CPI 偏低（小于99），存在通缩风险。")
    else:
        st.success(f"✅ CPI 为 {cpi_val}，处于温和区间，物价平稳。")

# ==================== 数据表 ====================
with st.expander("📋 点击展开查看原始数据表格"):
    col1, col2 = st.columns(2)
    with col1:
        st.write("CPI 数据")
        st.dataframe(cpi_df)
    with col2:
        st.write("PPI 数据")
        st.dataframe(ppi_df)