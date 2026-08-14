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
st.title("📊 中国宏观双指标看板 (含企业与政策建议)")

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
    st.error(f"❌ 找不到数据文件！请确保运行了相关抓取脚本。\n错误：{e}")
    st.stop()

st.sidebar.header("🔧 预警面板")
cpi_warning_high = st.sidebar.number_input("CPI 通胀警戒线", value=103.0, step=0.1)
cpi_warning_low = st.sidebar.number_input("CPI 通缩警戒线", value=99.0, step=0.1)
pmi_line = st.sidebar.number_input("PMI 荣枯线", value=50.0, step=0.1)

latest_cpi = cpi_df.iloc[-1]
cpi_val = latest_cpi['全国-当月']
if cpi_val > cpi_warning_high:
    st.error(f"🚨 **警报！** 当前 CPI 为 {cpi_val}，突破 {cpi_warning_high} 警戒线！")
elif cpi_val < cpi_warning_low:
    st.warning(f"⚠️ **注意！** 当前 CPI 为 {cpi_val}，低于 {cpi_warning_low} 警戒线！")
else:
    st.success(f"✅ 当前 CPI 为 {cpi_val}，平稳区间。")

# ==================== 核心：预测及AI影响建议 ====================
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

# 🟢【核心升级】：为企业直接提供决策建议
def get_forecast_description(name, val):
    # 前缀数据展示
    desc = f"**📊 指标分析**：{name} 预计下月预测值为 **{val:.2f}**。\n\n"
    
    if "CPI" in name: # 居民消费价格
        if val > 103:
            desc += "**📈 宏观判断**：进入较高通胀压力区间，消费端物价上涨较快。\n"
            desc += "**⚡ 核心影响**：消费者购买力被稀释，日常消费成本上升，储蓄贬值。\n"
            desc += "**🎯 政策建议**：国家层面应**适度收紧货币政策**，防范经济过热，控制通胀预期。\n"
            desc += "**🏢 企业对策**：可**适当提前锁定原材料成本**，但需警惕终端消费者购买力下降影响销量，避免盲目高价囤货。"
        elif val < 99:
            desc += "**📉 宏观判断**：进入通缩风险区间，消费需求整体疲软。\n"
            desc += "**⚡ 核心影响**：企业利润承压，居民倾向于储蓄而非消费，经济内生增长动力不足。\n"
            desc += "**🎯 政策建议**：国家应**降准降息，加大民生与基建领域的投资力度**，刺激总需求。\n"
            desc += "**🏢 企业对策**：企业应**主动降价去库存，以价换量**；暂停非必要的扩产投资，储备现金流以度过需求低迷期。"
        else:
            desc += "**✅ 宏观判断**：处于健康温和通胀区间，物价平稳。\n"
            desc += "**⚡ 核心影响**：物价温和，有助于企业正常经营和居民稳步消费。\n"
            desc += "**🎯 政策建议**：国家应**保持货币政策稳健**，维持当前投资节奏，灵活适度调节。\n"
            desc += "**🏢 企业对策**：企业应**维持正常生产与供销节奏**，可根据市场实际需求进行小规模扩张，避免冒进。"
            
    elif "PPI" in name: # 工业生产者出厂价
        if val > 103:
            desc += "**📈 宏观判断**：工业品出厂价格偏高，上游原材料成本压力大。\n"
            desc += "**⚡ 核心影响**：下游制造业利润空间被严重挤压，中小企业生存压力增大。\n"
            desc += "**🎯 政策建议**：国家应**保供稳价**，适当投放战略物资储备，防止上游价格过度上涨。\n"
            desc += "**🏢 企业对策**：中下游企业应**积极寻找替代原材料**，或与上游签订长单锁定价格，同时通过提高产品附加值来转嫁成本。"
        elif val < 97:
            desc += "**📉 宏观判断**：工业品出厂价格偏低，工厂订单需求偏冷。\n"
            desc += "**⚡ 核心影响**：工业产能利用率下降，企业开工率不足，工业通缩迹象明显。\n"
            desc += "**🎯 政策建议**：国家应**通过新基建、制造业扶持项目加大固定资产投资**，拉动工业品需求。\n"
            desc += "**🏢 企业对策**：企业应**谨慎接单，避免产能过剩**；利用同行的减产潮优化自身产能结构，静待市场供需重新平衡。"
        else:
            desc += "**✅ 宏观判断**：工业品价格处于正常波动区间。\n"
            desc += "**⚡ 核心影响**：上下游价格传导平稳，企业成本可控。\n"
            desc += "**🎯 政策建议**：保持现有产业扶持政策，**投资按既定规划执行**。\n"
            desc += "**🏢 企业对策**：企业可**按现有的采购和销售计划稳定经营**，保持正常的原材料库存周转。"
            
    elif "M2" in name: # 广义货币
        if val > 15:
            desc += "**🚀 宏观判断**：市场流动性非常宽松，货币供应量偏大。\n"
            desc += "**⚡ 核心影响**：容易催生资本市场泡沫，推高资产价格（如核心城市房价、大宗商品）。\n"
            desc += "**🎯 政策建议**：国家应**防范资产泡沫，控制宏观杠杆率**，货币政策应转向“收紧流动性”。\n"
            desc += "**🏢 企业对策**：有融资需求的企业**应抓紧时机利用低成本资金**进行技术升级或扩张；但需警惕资金最终流向股市/楼市，避免借钱炒高风险资产。"
        elif val < 8:
            desc += "**💧 宏观判断**：市场流动性偏紧缩，资金供给不足。\n"
            desc += "**⚡ 核心影响**：企业融资成本上升，实体经济可能面临“缺血”和融资难的问题。\n"
            desc += "**🎯 政策建议**：国家应**降准降息，加大信贷投放，扩大基础设施投资规模**，释放流动性。\n"
            desc += "**🏢 企业对策**：企业应**控制有息负债，加速应收账款周转**，确保手上有充裕现金流，避免在资金收紧时盲目借入高息贷款。"
        else:
            desc += "**✅ 宏观判断**：市场流动性处于合理充裕区间。\n"
            desc += "**⚡ 核心影响**：宏观资金面平稳，企业信贷条件适中。\n"
            desc += "**🎯 政策建议**：国家应**实行精准滴灌**，继续支持中小微企业。\n"
            desc += "**🏢 企业对策**：可**适度进行债务扩张**，利用当前利率水平合理安排长短期融资比例，维持稳健的财务杠杆。"
            
    elif "PMI" in name: # 采购经理指数
        if val > 50:
            desc += "**✅ 宏观判断**：处于荣枯线之上，制造业呈扩张态势，景气度转好。\n"
            desc += "**⚡ 核心影响**：订单增长，企业产能利用率提升，就业市场稳固。\n"
            desc += "**🎯 政策建议**：国家应**依靠市场自发动力**，政府可适度减少直接干预，**投资重点向科技创新倾斜**。\n"
            desc += "**🏢 企业对策**：企业应**加大采购和备产力度，适当增加招工**，积极抢占市场份额；但需警惕扩张过快带来的现金流压力。"
        else:
            desc += "**⚠️ 宏观判断**：跌破荣枯线，处于收缩区间，制造业景气度下行。\n"
            desc += "**⚡ 核心影响**：制造业订单减少，行业普遍承压，可能引发局部裁员。\n"
            desc += "**🎯 政策建议**：国家应**加大逆周期调节力度**，**加快发行专项债，启动一批重大基建工程项目**。\n"
            desc += "**🏢 企业对策**：企业应**主动削减非核心开支，清理积压库存**；暂停重资产投资计划，以“保现金、保生存”为第一要务，等待市场回暖。"
    return desc

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

# 预测执行
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
    
    forecast_text = f"💡 **{data_type} {pred_method}**:\n\n{get_forecast_description(data_type, forecast_vals[0])}"

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
        if val > 15: return "🔵 货币偏宽松"
        elif val < 8: return "🔴 货币偏紧缩"
        else: return "🟢 货币平稳"

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
    
    if m2_vals is not None:
        st.info(f"💡 **M2 {m2_method}**:\n\n{get_forecast_description('M2', m2_vals[0])}")


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

if pmi_vals is not None:
    st.info(f"💡 **PMI {pmi_method}**:\n\n{get_forecast_description('PMI', pmi_vals[0])}")


# ==================== 导出与数据表 ====================
st.subheader("📥 数据导出")
col1, col2 = st.columns(2)
with col1:
    st.download_button("📥 下载 CPI 数据 (CSV)", cpi_df.to_csv(index=False).encode('utf-8-sig'), "cpi_data.csv", "text/csv")
with col2:
    st.download_button("📥 下载 PMI 数据 (CSV)", pmi_df.to_csv(index=False).encode('utf-8-sig'), "pmi_data.csv", "text/csv")

with st.expander("📋 原始数据表"):
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.write("CPI"); st.dataframe(cpi_df)
    with col2: st.write("PPI"); st.dataframe(ppi_df)
    with col3: st.write("PMI"); st.dataframe(pmi_df)
    with col4: st.write("M2"); st.dataframe(m2_df)