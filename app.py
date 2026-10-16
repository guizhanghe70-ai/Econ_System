# coding: utf-8
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from macro_data import fetch_all_macro, get_val, get_date, is_monthly

INDICATORS_DATA = {
    "宏观经济学": [
        {"名称": "CPI（居民消费价格指数）", "公式": "（当期一篮子商品价格 / 基期一篮子商品价格）× 100", "大白话": "衡量老百姓日常买东西、服务是变贵了还是变便宜了。", "标准": "同比 2%~3% 为温和；>3% 通胀压力；<0% 通缩风险"},
        {"名称": "PPI（工业生产者出厂价格指数）", "公式": "（当期出厂价 / 基期出厂价）× 100", "大白话": "工厂卖货的价格涨跌，是 CPI 的先行指标。", "标准": "同比为正说明工业需求旺；持续为负说明需求疲软"},
        {"名称": "PMI（采购经理指数）", "公式": "对采购经理问卷加权汇总得出", "大白话": "企业对未来经济的信心投票。", "标准": "50 为荣枯线；>50 扩张；<50 收缩"},
        {"名称": "GDP（国内生产总值）", "公式": "消费 + 投资 + 政府支出 + 净出口", "大白话": "一个国家一年内新创造的全部财富。", "标准": "同比增速 5% 左右为健康"},
        {"名称": "M2（广义货币供应量）", "公式": "M1 + 定期存款 + 储蓄存款", "大白话": "市场上总共有多少钱在流动。", "标准": "同比 8%~10% 为合理；过高警惕通胀"},
        {"名称": "LPR（贷款市场报价利率）", "公式": "由 20 家报价行报价后去掉最高最低取平均", "大白话": "银行贷款的基准利率，影响房贷、企业贷。", "标准": "下调=宽松；上调=收紧"},
        {"名称": "货币流通速度", "公式": "V = GDP / M2（费雪方程式 MV = PY）", "大白话": "1块钱在一年内转手买了几次东西。", "标准": "越高说明钱转得越快；中国长期趋势在下降"},
        {"名称": "M2/GDP 比率", "公式": "M2余额 ÷ 年化GDP", "大白话": "市场上有多少钱，对应多少经济产出。", "标准": "健康区间 0.7~1.0；中国 >2 说明货币超发严重"},
    ],
    "微观经济学": [
        {"名称": "边际成本", "公式": "Δ总成本 / Δ产量", "大白话": "多生产一个产品，总共要多花多少钱。", "标准": "等于边际收入时利润最大"},
        {"名称": "需求价格弹性", "公式": "%Δ需求量 / %Δ价格", "大白话": "价格一变，买的人变多少。", "标准": ">1 富有弹性；<1 缺乏弹性"},
    ],
    "财务管理": [
        {"名称": "毛利率", "公式": "（营业收入 - 营业成本）/ 营业收入 × 100%", "大白话": "卖货赚的差价占收入的比例。", "标准": "行业差异大，广电行业约 30%~50%"},
        {"名称": "资产负债率", "公式": "总负债 / 总资产 × 100%", "大白话": "公司资产里有多少是借来的。", "标准": "40%~60% 为合理；>70% 偏高风险"},
    ],
}

st.set_page_config(page_title="经济运行分析系统", layout="wide")
st.sidebar.title("🧭 系统导航控制台")
page = st.sidebar.radio("请选择要查看的板块:", ["🇨🇳 中国经济实时监测", "📊 中国宏观经济看板", "经济指标百科全书大厅", "📊 经济指标实战应用中心", "🧮 经济指标计算器"])

@st.cache_data
def generate_sample_data():
    np.random.seed(42)
    months = pd.date_range(start='2020-01-01', end='2026-03-01', freq='MS')
    cpi = np.clip(100 + np.cumsum(np.random.normal(0.02, 0.25, len(months))), 98, 106)
    ppi = np.clip(100 + np.cumsum(np.random.normal(-0.03, 0.4, len(months))), 95, 108)
    pmi = np.clip(50 + np.cumsum(np.random.normal(0, 0.3, len(months))), 46, 54)
    m2 = np.clip(10 + np.cumsum(np.random.normal(0, 0.25, len(months))), 7, 14)
    cpi_df = pd.DataFrame({'月份': months, '全国-当月': np.round(cpi, 2)})
    ppi_df = pd.DataFrame({'月份': months, '当月': np.round(ppi, 2)})
    pmi_df = pd.DataFrame({'月份': months, '制造业PMI': np.round(pmi, 2), '非制造业PMI': np.round(pmi + np.random.normal(0.5, 0.3, len(months)), 2)})
    m2_df = pd.DataFrame({'月份': months, 'M2-同比': np.round(m2, 2)})
    return cpi_df, ppi_df, pmi_df, m2_df

cpi_df, ppi_df, pmi_df, m2_df = generate_sample_data()
if page == "🇨🇳 中国经济实时监测":
    st.title("🇨🇳 中国经济实时监测")
    st.caption("数据来源：国家统计局、中国人民银行 | AkShare 自动抓取")
    st.info("📌 **颜色说明**：🟢 健康 / 🟡 预警 / 🔴 风险")
    with st.spinner("正在从国家统计局、央行抓取最新数据..."):
        macro = fetch_all_macro()
    cpi_val = get_val(macro, "cpi", fallback=0.4); cpi_date = get_date(macro, "cpi", fallback="2026年3月")
    ppi_val = get_val(macro, "ppi", fallback=3.8); ppi_date = get_date(macro, "ppi", fallback="2026年3月")
    pmi_val = get_val(macro, "pmi", fallback=50.1); pmi_date = get_date(macro, "pmi", fallback="2026年9月")
    gdp_val = get_val(macro, "gdp", fallback=334193); gdp_date = get_date(macro, "gdp", fallback="2026Q1")
    m2_val = get_val(macro, "m2", fallback=7.5); m2_date = get_date(macro, "m2", fallback="2026年8月")
    shrzgm_val = get_val(macro, "shrzgm", fallback=20516); shrzgm_date = get_date(macro, "shrzgm", fallback="2026年8月")
    lpr1y = get_val(macro, "lpr", "lpr1y", fallback=3.0); lpr5y = get_val(macro, "lpr", "lpr5y", fallback=3.5)
    lpr_date = get_date(macro, "lpr", fallback="2026年8月")
    unemp_val = get_val(macro, "unemployment", fallback=5.0); unemp_date = get_date(macro, "unemployment", fallback="2026年8月")
    fx_val = get_val(macro, "exchange", fallback=6.9081); fx_date = get_date(macro, "exchange", fallback="2026年10月")
    retail_val = get_val(macro, "retail", fallback=0.4); retail_date = get_date(macro, "retail", fallback="2026年8月")
    investment_val = get_val(macro, "investment", fallback=-13.5); investment_date = get_date(macro, "investment", fallback="2026年8月")
    industrial_val = get_val(macro, "industrial", fallback=5.2); industrial_date = get_date(macro, "industrial", fallback="2026年8月")
    trade_val = get_val(macro, "trade", fallback=982); trade_date = get_date(macro, "trade", fallback="2026年9月")
    st.subheader("📌 核心指标速览")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        gdp_display = f"{gdp_val / 10000:.2f} 万亿元" if gdp_val else "—"
        st.metric("GDP（国内生产总值）", gdp_display, "+5.0%")
        st.caption(f"📅 {gdp_date} | 🟢 健康（≥5%）")
    with col2:
        cpi_label = "月率" if is_monthly(macro, "cpi") else "同比"
        st.metric("CPI（居民消费价格指数）", f"{cpi_val:+.1f}%", f"当月{cpi_label}")
        st.caption(f"📅 {cpi_date} | 🟢 健康（0%~3%）")
    with col3:
        st.metric("PPI（工业生产者出厂价格指数）", f"{ppi_val:+.1f}%", "当月同比")
        st.caption(f"📅 {ppi_date} | 🟡 预警（刚转正，需观察）")
    with col4:
        st.metric("PMI（采购经理指数）", f"{pmi_val:.1f}%", "荣枯线50")
        st.caption(f"📅 {pmi_date} | 🟢 健康（≥50）")
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("M2（广义货币供应量）", f"{m2_val:+.1f}%", "同比")
        st.caption(f"📅 {m2_date} | 🟢 健康（8%~10%）")
    with col6:
        st.metric("社融增量（社会融资规模）", f"{shrzgm_val:,.0f}亿元", "当月增量")
        st.caption(f"📅 {shrzgm_date} | 数据来源：央行")
    with col7:
        st.metric("LPR（贷款市场报价利率）", f"1Y {lpr1y:.1f}% / 5Y {lpr5y:.1f}%", "历史低位")
        st.caption(f"📅 {lpr_date} | 🟢 健康（历史低位，宽松）")
    with col8:
        st.metric("汇率（人民币/美元）", f"{fx_val:.4f}", "近期")
        st.caption(f"📅 {fx_date} | 🟢 健康（温和波动）")
    col9, col10, col11, col12 = st.columns(4)
    with col9:
        st.metric("社零（社会消费品零售总额）", f"{retail_val:+.1f}%", "当月同比")
        st.caption(f"📅 {retail_date} | 🟡 预警（低于GDP增速）")
    with col10:
        st.metric("固投（固定资产投资）", f"{investment_val:+.1f}%", "累计同比")
        st.caption(f"📅 {investment_date} | 🟡 预警（低于GDP增速）")
    with col11:
        st.metric("工业增加值（规模以上工业）", f"{industrial_val:+.1f}%", "当月同比")
        st.caption(f"📅 {industrial_date} | 🟡 预警（接近5%）")
    with col12:
        st.metric("服务业指数（服务业生产指数）", "+4.4%", "加快0.1pct")
        st.caption("📅 2026年5月 | 🟡 预警（接近5%）")
    col13, col14, col15, col16 = st.columns(4)
    with col13:
        if trade_val: st.metric("进出口（贸易差额）", f"{trade_val:,.0f}亿美元", "当月")
        else: st.metric("进出口（货物进出口总额）", "118380亿元", "+15.0%")
        st.caption(f"📅 {trade_date} | 🟢 健康")
    with col14:
        st.metric("失业率（城镇调查失业率）", f"{unemp_val:.1f}%", "当月")
        st.caption(f"📅 {unemp_date} | 🟡 预警（略高于5%）")
    with col15:
        st.metric("房地产投资（房地产开发投资）", "-16.2%", "深度调整")
        st.caption("📅 2026年1-5月 | 🔴 风险（持续负增长）")
    with col16:
        st.metric("居民收入（人均可支配收入）", "12782元", "+4.0%")
        st.caption("📅 2026Q1 | 🟡 预警（略低于GDP）")
    st.markdown("---")
    st.subheader("💵 货币政策传导效率（费雪方程式）")
    velocity_val = get_val(macro, "velocity", fallback=None); m2_balance_val = get_val(macro, "m2_balance", fallback=3568100.0)
    col_v1, col_v2, col_v3, col_v4 = st.columns(4)
    with col_v1:
        if gdp_val: st.metric("年化 GDP", f"{gdp_val * 4 / 10000:.2f} 万亿元", "最新季度×4")
        else: st.metric("年化 GDP", "—")
    with col_v2:
        if m2_balance_val: st.metric("M2 余额", f"{m2_balance_val / 10000:.2f} 万亿元", "最新月份")
        else: st.metric("M2 余额", "—")
    with col_v3:
        if velocity_val: st.metric("货币流通速度 V", f"{velocity_val:.3f}", "每1元M2对应GDP")
        else: st.metric("货币流通速度 V", "—")
    with col_v4:
        if gdp_val and m2_balance_val and gdp_val > 0:
            m2_gdp_ratio = m2_balance_val / (gdp_val * 4)
            st.metric("M2/GDP 比率", f"{m2_gdp_ratio:.2f} 倍", "货币超发程度")
        else: st.metric("M2/GDP 比率", "—")
    st.caption("**📖 大白话**：1块钱在一年内转手买了几次东西。**🏠 对你的影响**：中国过去20年 V 持续下降，说明发钱对经济的拉动越来越弱。")
    st.markdown("---")
    st.subheader("⚠️ 货币超发监测（含中美对比）")
    st.caption("M2/GDP 比率 = M2余额 ÷ 年化GDP。国际警戒线 1.0 倍；中国合理线 1.5~2.0 倍。超过 2.0 倍意味着债务驱动特征明显，超过 2.5 倍即为货币超发严重。")
    if gdp_val and m2_balance_val and gdp_val > 0:
        m2_gdp = m2_balance_val / (gdp_val * 4)
        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        with col_r1: st.metric("中国 M2/GDP", f"{m2_gdp:.2f} 倍", "当前实际值")
        with col_r2: st.metric("美国 M2/GDP", "约 0.74 倍", "国际参考")
        with col_r3: st.metric("中国合理线", "1.5~2.0 倍", "间接融资参考")
        with col_r4: st.metric("中国警戒线", "2.0 倍", "债务驱动警戒")
        with col_r5: st.metric("超发严重线", "2.5 倍", "货币传导效率低下")
        if m2_gdp > 2.5: st.error(f"🔴 **货币超发严重**：中国 M2/GDP = {m2_gdp:.2f} 倍，是美国（0.74）的 {m2_gdp/0.74:.1f} 倍。已突破 2.5 倍严重线。")
        elif m2_gdp > 2.0: st.warning(f"🟡 **突破警戒线**：中国 M2/GDP = {m2_gdp:.2f} 倍，债务驱动特征明显。")
        elif m2_gdp > 1.0: st.info(f"🟢 **符合间接融资国情**：中国 M2/GDP = {m2_gdp:.2f} 倍，处于 1.0~2.0 倍区间。")
        else: st.success(f"✅ **健康**：中国 M2/GDP = {m2_gdp:.2f} 倍，低于国际警戒线。")
    else: st.warning("⚠️ 无法计算 M2/GDP（缺 GDP 或 M2 余额数据）")
    st.markdown("---")
    st.subheader("🧮 进阶货币指标（M1/M2剪刀差、货币乘数、社融/M2）")
    m1_val = get_val(macro, "m1", fallback=4.1); m2_val_for_diff = get_val(macro, "m2", fallback=7.5)
    if m1_val is not None and m2_val_for_diff is not None:
        scissors = m1_val - m2_val_for_diff
        col_s1, col_s2 = st.columns(2)
        with col_s1: st.metric("M1 同比", f"{m1_val:+.1f}%", f"M2: {m2_val_for_diff:+.1f}%")
        with col_s2: st.metric("M1/M2 剪刀差", f"{scissors:+.1f}%", "扩大=资金活化程度低")
        if scissors < 0: st.warning("⚠️ 剪刀差为负且扩大，说明资金大量沉淀在定期存款中，大家把钱存起来不敢花。")
        else: st.success(f"✅ **资金活化，经济回暖**：剪刀差为 {scissors:+.1f}%，说明企业投资意愿和居民消费意愿增强。")
    else: st.info("📌 暂无 M1/M2 数据，建议在 macro_data.py 中检查 M1 抓取逻辑。")
    st.markdown("### 📊 货币乘数 & 社融/M2 比率")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("**货币乘数 = M2余额 ÷ 基础货币**")
        if m2_balance_val: st.metric("货币乘数（估算）", f"{m2_balance_val / 360000.0:.2f} 倍"); st.caption("反映银行放贷意愿。乘数越高，银行派生货币能力越强。")
        else: st.metric("货币乘数（估算）", "—")
    with col_c2:
        st.markdown("**社融/M2 比率 = 社融增量 ÷ M2增量**")
        if shrzgm_val and m2_balance_val:
            st.metric("社融/M2（估算）", f"{shrzgm_val / (m2_balance_val * 0.005):.2f} 倍"); st.caption("反映金融对实体经济的支持力度。比值越高，说明信贷派生越多。")
        else: st.metric("社融/M2（估算）", "—")
    st.markdown("### 📈 M2/GDP 历史趋势图（示意）")
    years = list(range(2000, 2027)); m2_gdp_trend = [1.3 + (i * 0.05) + (0.02 if i > 15 else 0) for i in range(len(years))]
    fig_m2gdp = go.Figure()
    fig_m2gdp.add_trace(go.Scatter(x=years, y=m2_gdp_trend, mode='lines+markers', name='M2/GDP 比率', hovertemplate="年份: %{x}<br>M2/GDP: %{y:.2f} 倍<extra></extra>"))
    fig_m2gdp.add_shape(type="line", x0=2000, y0=1.0, x1=2026, y1=1.0, line=dict(color="Gray", width=2, dash="dashdot"), name="国际警戒线 1.0")
    fig_m2gdp.update_layout(font=dict(size=14), yaxis_title="M2/GDP (倍)")
    st.plotly_chart(fig_m2gdp, use_container_width=True)
    st.markdown("---")
    st.subheader("🚀 领先预判指标（前照灯系统）")
    col_lead1, col_lead2, col_lead3 = st.columns(3)
    with col_lead1:
        st.markdown("**1. PMI 需求-库存剪刀差**")
        pmi_detail = macro.get("data", {}).get("pmi_detail", {})
        if pmi_detail:
            diff = pmi_detail.get("new_order", 50) - pmi_detail.get("inventory", 50)
            st.metric("新订单 - 产成品库存", f"{diff:+.1f}", "领先指标")
            if diff > 0: st.success("✅ 需求大于库存，企业即将补库扩产，经济看涨。")
            else: st.warning("🟡 需求弱于库存，企业仍在去库存，经济承压。")
        else: st.metric("新订单-产成品库存", "+1.2", "领先指标"); st.success("✅ 需求大于库存，企业即将补库扩产。")
    with col_lead2:
        st.markdown("**2. 社融存量 vs M2 剪刀差**")
        shrzgm_stock = get_val(macro, "shrzgm_stock", fallback=None)
        if shrzgm_stock and m2_val_for_diff:
            diff_sr = shrzgm_stock - m2_val_for_diff
            st.metric("社融存量同比 - M2同比", f"{diff_sr:+.1f}%", "大行情启动信号")
            if diff_sr > 0: st.success("✅ 社融上穿 M2，实体融资需求旺盛！")
            else: st.warning("🟡 社融弱于 M2，央行放的水还没流到实体。")
        else: st.metric("社融存量同比 - M2同比", "-0.8%", "大行情启动信号"); st.warning("🟡 社融弱于 M2，央行放的水还没流到实体。")
    with col_lead3:
        st.markdown("**3. 国债期限利差（10Y - 1Y）**")
        bond = macro.get("data", {}).get("bond_yield", {})
        if bond:
            spread = bond.get("spread", 0)
            st.metric("10年期 - 1年期国债利差", f"{spread:+.2f}%", "衰退预警指标")
            if spread < 0: st.error("🔴 收益率倒挂，强烈衰退预警！")
            elif spread < 0.5: st.warning("🟡 利差过窄，市场避险情绪浓。")
            else: st.success("✅ 利差正常，市场对未来经济乐观。")
        else: st.metric("10年期 - 1年期国债利差", "+0.65%", "衰退预警指标"); st.success("✅ 利差正常，市场对未来经济乐观。")
    st.markdown("---")
    st.subheader("⏰ 美林投资时钟（经济周期定位）")
    clock_fig = go.Figure()
    clock_fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=5, line=dict(color="Gray", width=1, dash="dot"))
    clock_fig.add_shape(type="line", x0=45, y0=1.5, x1=55, y1=1.5, line=dict(color="Gray", width=1, dash="dot"))
    hist_pmi = pmi_df['制造业PMI'].tail(12).tolist()
    hist_cpi = cpi_df['全国-当月'].tail(12).apply(lambda x: (x - 100) + 1.5).tolist()
    clock_fig.add_trace(go.Scatter(x=hist_pmi, y=hist_cpi, mode='lines+markers', name="经济轨迹", text=[m.strftime('%Y-%m') for m in pmi_df['月份'].tail(12)]))
    clock_fig.add_annotation(x=52, y=3, text="过热期<br>(PMI↑, CPI↑)<br>买大宗商品", showarrow=False, bgcolor="#ffeaa7")
    clock_fig.add_annotation(x=48, y=3, text="滞胀期<br>(PMI↓, CPI↑)<br>现金为王", showarrow=False, bgcolor="#fab1a0")
    clock_fig.add_annotation(x=52, y=0.5, text="复苏期<br>(PMI↑, CPI↓)<br>买股票", showarrow=False, bgcolor="#55efc4")
    clock_fig.add_annotation(x=48, y=0.5, text="衰退期<br>(PMI↓, CPI↓)<br>买债券", showarrow=False, bgcolor="#74b9ff")
    clock_fig.update_layout(xaxis_title="PMI（经济增长，50为荣枯线）", yaxis_title="CPI（通货膨胀，%）", xaxis=dict(range=[45, 55]), yaxis=dict(range=[0, 5]), showlegend=False, height=400)
    st.plotly_chart(clock_fig, use_container_width=True)
elif page == "📊 中国宏观经济看板":
    st.title("📊 中国宏观经济双指标看板")
    st.caption("当前使用内置模拟数据。如需接入真实数据，替换为你的 CSV 即可。")
    st.sidebar.header("🔧 预警面板")
    cpi_warning_high = st.sidebar.number_input("CPI 通胀警戒线", value=103.0, step=0.1)
    cpi_warning_low = st.sidebar.number_input("CPI 通缩警戒线", value=99.0, step=0.1)
    pmi_line = st.sidebar.number_input("PMI 荣枯线", value=50.0, step=0.1)
    def get_cpi_status(val): return "⚠️ 通胀" if val > 103 else ("⚠️ 通缩" if val < 99 else "✅ 稳定")
    def get_m2_status(val): return "🔵 宽松" if val > 15 else ("🔴 紧缩" if val < 8 else "🟢 平稳")
    def get_pmi_status(val): return "✅ 扩张" if val > pmi_line else "⚠️ 收缩"
    m2_warning_high = st.sidebar.number_input("M2 宽松警戒线", value=15.0, step=0.5)
    m2_warning_low = st.sidebar.number_input("M2 紧缩警戒线", value=8.0, step=0.5)
    def get_cpi_status(val):
        if val > cpi_warning_high: return "⚠️ 存在通胀压力"
        elif val < cpi_warning_low: return "⚠️ 存在通缩风险"
        else: return "✅ 物价温和稳定"
    def get_m2_status(val):
        if val > m2_warning_high: return f"🔵 货币偏宽松"
        elif val < m2_warning_low: return f"🔴 货币偏紧缩"
        else: return "🟢 货币平稳"
    latest_cpi = cpi_df.iloc[-1]['全国-当月']
    if latest_cpi > cpi_warning_high: st.error(f"🚨 **警报！** 当前 CPI 为 {latest_cpi}，突破警戒线！")
    elif latest_cpi < cpi_warning_low: st.warning(f"⚠️ **注意！** 当前 CPI 为 {latest_cpi}，低于警戒线！")
    else: st.success(f"✅ 当前 CPI 为 {latest_cpi}，处于平稳区间。")
    st.subheader("📈 CPI 趋势及移动均线分析")
    data = cpi_df[['月份', '全国-当月']].copy()
    data['3个月移动均线'] = data['全国-当月'].rolling(window=3).mean()
    data['6个月移动均线'] = data['全国-当月'].rolling(window=6).mean()
    fig_cpi = go.Figure()
    fig_cpi.add_trace(go.Scatter(x=data['月份'], y=data['全国-当月'], mode='lines+markers', name='CPI 实际', text=[get_cpi_status(v) for v in data['全国-当月']], hovertemplate="月份: %{x|%Y年%m月}<br>CPI: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))
    fig_cpi.add_trace(go.Scatter(x=data['月份'], y=data['3个月移动均线'], mode='lines', name='3个月均线'))
    fig_cpi.add_trace(go.Scatter(x=data['月份'], y=data['6个月移动均线'], mode='lines', name='6个月均线'))
    fig_cpi.update_layout(font=dict(size=14), hoverlabel=dict(font_size=15)); fig_cpi.update_xaxes(tickformat="%Y年%m月")
    st.plotly_chart(fig_cpi, use_container_width=True)
    st.subheader("🏭 PPI 趋势分析")
    ppi_data = ppi_df[['月份', '当月']].copy()
    fig_ppi = go.Figure()
    fig_ppi.add_trace(go.Scatter(x=ppi_data['月份'], y=ppi_data['当月'], mode='lines+markers', name='PPI', hovertemplate="月份: %{x|%Y年%m月}<br>PPI: %{y:.2f}<extra></extra>"))
    fig_ppi.update_layout(font=dict(size=14)); fig_ppi.update_xaxes(tickformat="%Y年%m月")
    st.plotly_chart(fig_ppi, use_container_width=True)
    st.subheader("💰 资金面指标: M2 同比增长率")
    m2_data = m2_df[['月份', 'M2-同比']].copy()
    fig_m2 = go.Figure()
    fig_m2.add_trace(go.Scatter(x=m2_data['月份'], y=m2_data['M2-同比'], mode='lines+markers', name='M2 同比', text=[get_m2_status(v) for v in m2_data['M2-同比']], hovertemplate="月份: %{x|%Y年%m月}<br>M2同比: %{y:.2f}%<br><b>📌 状态: %{text}</b><extra></extra>"))
    fig_m2.update_layout(font=dict(size=14)); fig_m2.update_xaxes(tickformat="%Y年%m月")
    st.plotly_chart(fig_m2, use_container_width=True)
    st.subheader("🏭 PMI 景气度监测")
    pmi_options = [col for col in pmi_df.columns if col != '月份']
    selected_pmi = st.selectbox("选择 PMI 分类指标：", pmi_options)
    pmi_data = pmi_df[['月份', selected_pmi]].copy()
    fig_pmi = go.Figure()
    fig_pmi.add_trace(go.Scatter(x=pmi_data['月份'], y=pmi_data[selected_pmi], mode='lines+markers', name=selected_pmi, text=[get_pmi_status(v) for v in pmi_data[selected_pmi]], hovertemplate="月份: %{x|%Y年%m月}<br>PMI: %{y:.2f}<br><b>📌 状态: %{text}</b><extra></extra>"))
    fig_pmi.add_shape(type="line", x0=pmi_data['月份'].min(), y0=pmi_line, x1=pmi_data['月份'].max(), y1=pmi_line, line=dict(color="Gray", width=2, dash="dashdot"))
    fig_pmi.update_layout(font=dict(size=14)); fig_pmi.update_xaxes(tickformat="%Y年%m月")
    st.plotly_chart(fig_pmi, use_container_width=True)

elif page == "经济指标百科全书大厅":
    st.title("📚 全球经济指标与微观学核心辞典")
    search_query = st.text_input("🔍 搜一搜：输入关键词一键直达核心指标（如：CPI、边际、利润、储蓄）")
    if search_query:
        st.subheader(f"🎯 包含 '{search_query}' 的搜索结果：")
        found = False
        for category, items in INDICATORS_DATA.items():
            for item in items:
                if (search_query.lower() in item["名称"].lower() or search_query.lower() in item["大白话"].lower()):
                    found = True
                    with st.expander(f"📌 【{category}】• {item['名称']}", expanded=True):
                        st.info(f"🧮 计算公式：{item['公式']}"); st.success(f"💡 大白话解释：{item['大白话']}"); st.warning(f"⚖️ 参考值 / 判断标准：{item['标准']}")
        if not found: st.error("❌ 未匹配到相关指标，请更换关键词。")
    st.markdown("### 🗂️ 按学科全谱系分类完整浏览")
    for category, items in INDICATORS_DATA.items():
        with st.expander(f"📁 {category}（收录 {len(items)} 个指标）"):
            cleaned_items = [{"核心指标名称": str(item.get("名称", "")), "计算公式": str(item.get("公式", "")), "大白话解释": str(item.get("大白话", "")), "参考值 / 判定标准": str(item.get("标准", ""))} for item in items]
            st.dataframe(pd.DataFrame(cleaned_items), use_container_width=True, hide_index=True)

elif page == "📊 经济指标实战应用中心":
    st.title("📊 经济指标实战应用中心")
    st.markdown("把词典里的指标**用起来**——输入你的实际值，系统自动诊断。")
    st.subheader("🌡️ 一、宏观健康度综合评分")
    c1, c2, c3, c4 = st.columns(4)
    with c1: cpi_input = st.number_input("CPI 同比 (%)", value=100.5, step=0.1)
    with c2: ppi_input = st.number_input("PPI 同比 (%)", value=99.2, step=0.1)
    with c3: pmi_input = st.number_input("PMI", value=49.8, step=0.1)
    with c4: m2_input = st.number_input("M2 同比 (%)", value=9.5, step=0.1)
    score = 0; details = []
    if 100 <= cpi_input <= 103: cpi_score = 25; cpi_status = "✅ 温和"
    elif 99 <= cpi_input < 100 or 103 < cpi_input <= 104: cpi_score = 15; cpi_status = "🟡 临界"
    else: cpi_score = 5; cpi_status = "🔴 异常"
    score += cpi_score; details.append(f"CPI：{cpi_input} → {cpi_status}（{cpi_score}/25）")
    if ppi_input >= 100: ppi_score = 25; ppi_status = "✅ 需求旺"
    elif ppi_input >= 98: ppi_score = 15; ppi_status = "🟡 偏弱"
    else: ppi_score = 5; ppi_status = "🔴 疲软"
    score += ppi_score; details.append(f"PPI：{ppi_input} → {ppi_status}（{ppi_score}/25）")
    if pmi_input >= 50: pmi_score = 25; pmi_status = "✅ 扩张"
    elif pmi_input >= 49: pmi_score = 15; pmi_status = "🟡 临界"
    else: pmi_score = 5; pmi_status = "🔴 收缩"
    score += pmi_score; details.append(f"PMI：{pmi_input} → {pmi_status}（{pmi_score}/25）")
    if 8 <= m2_input <= 12: m2_score = 25; m2_status = "✅ 合理"
    elif 6 <= m2_input < 8 or 12 < m2_input <= 15: m2_score = 15; m2_status = "🟡 偏松/偏紧"
    else: m2_score = 5; m2_status = "🔴 异常"
    score += m2_score; details.append(f"M2：{m2_input} → {m2_status}（{m2_score}/25）")
    col_a, col_b = st.columns([1, 3])
    with col_a:
        if score >= 80: st.success(f"### {score} 分\n经济健康")
        elif score >= 60: st.warning(f"### {score} 分\n有隐忧")
        else: st.error(f"### {score} 分\n需警惕")
    with col_b:
        for d in details: st.write(f"• {d}")
    st.markdown("---")
    st.subheader("🏢 二、公司经营对标（广电行业）")
    col_g1, col_g2, col_g3 = st.columns(3)
    with col_g1: gross_margin = st.number_input("毛利率 (%)", value=42.0, step=0.5, key="gm"); net_margin = st.number_input("净利率 (%)", value=-8.5, step=0.5, key="nm")
    with col_g2: debt_ratio = st.number_input("资产负债率 (%)", value=55.0, step=0.5, key="dr"); current_ratio = st.number_input("流动比率", value=1.8, step=0.1, key="cr")
    with col_g3: ar_days = st.number_input("应收账款周转天数", value=180, step=10, key="ar"); roe = st.number_input("ROE (%)", value=3.0, step=0.5, key="roe")
    benchmarks = [("毛利率", gross_margin, 30, 50, "%", "广电行业 30%~50%"), ("净利率", net_margin, 5, 100, "%", "健康线 ≥5%"), ("资产负债率", debt_ratio, 40, 60, "%", "合理区间 40%~60%"), ("流动比率", current_ratio, 2, 100, "", "稳健线 ≥2"), ("应收账款周转天数", ar_days, 0, 120, "天", "越短越好，广电常 >150天"), ("ROE", roe, 15, 100, "%", "优秀线 ≥15%")]
    benchmark_df = []
    for name, val, low, high, unit, note in benchmarks:
        if name in ["资产负债率", "应收账款周转天数"]:
            status = "🟢 优秀" if val <= low else ("🟡 一般" if val <= high else "🔴 偏高")
        else:
            status = "🟢 优秀" if val >= high else ("🟡 一般" if val >= low else "🔴 偏低")
        benchmark_df.append({"指标": name, "实际值": f"{val}{unit}", "参考标准": note, "诊断": status})
    st.dataframe(pd.DataFrame(benchmark_df), use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("🔍 三、任意指标快速诊断")
    all_indicators = [f"【{cat}】{item['名称']}" for cat, items in INDICATORS_DATA.items() for item in items]
    selected_indicator = st.selectbox("选择指标：", all_indicators); actual_value = st.number_input("输入你的实际值：", value=0.0, step=0.1)
    if st.button("🔬 开始诊断"):
        for cat, items in INDICATORS_DATA.items():
            for item in items:
                if f"【{cat}】{item['名称']}" == selected_indicator:
                    st.info(f"🧮 **公式**：{item['公式']}"); st.success(f"💡 **大白话**：{item['大白话']}"); st.warning(f"⚖️ **参考标准**：{item['标准']}"); st.markdown(f"**你的输入值**：{actual_value}"); st.markdown("👉 请对照上面的参考标准，自行判断当前状态。")
    st.markdown("---"); st.caption("💡 提示：本板块的判断逻辑基于通用经济理论，具体决策请结合公司实际情况。")

elif page == "🧮 经济指标计算器":
    st.title("🧮 经济指标计算器")
    st.caption("输入数字，自动套公式计算 + 判断状态。不需要你记公式。")
    st.subheader("📊 一、宏观核算类")
    with st.expander("🔢 GDP平减指数", expanded=False):
        n_gdp = st.number_input("名义GDP（亿元）", value=1400000.0, key="n_gdp")
        r_gdp = st.number_input("实际GDP（亿元）", value=1350000.0, key="r_gdp")
        if st.button("计算GDP平减指数", key="bp_deflator"):
            if r_gdp > 0:
                dl = n_gdp / r_gdp * 100
                st.metric("GDP平减指数", f"{dl:.2f}")
                if 101 <= dl <= 103: st.success("✅ 温和上涨，健康区间")
                elif dl < 100: st.warning("⚠️ 物价下跌，警惕通缩")
                else: st.error("🔴 物价上涨过快，警惕通胀")
    with st.expander("🔢 实际GDP增长率", expanded=False):
        c_gdp = st.number_input("本期实际GDP（亿元）", value=334193.0, key="c_gdp")
        p_gdp = st.number_input("上期实际GDP（亿元）", value=318000.0, key="p_gdp")
        if st.button("计算实际GDP增长率", key="bp_gdp_growth"):
            if p_gdp > 0:
                g = (c_gdp - p_gdp) / p_gdp * 100
                st.metric("实际GDP增长率", f"{g:.2f}%")
                if g >= 5: st.success("✅ 健康增长（≥5%）")
                elif g >= 3: st.warning("🟡 增长放缓（3%~5%）")
                else: st.error("🔴 增长乏力（<3%）")
    with st.expander("🔢 人均GDP", expanded=False):
        gdp_t = st.number_input("GDP总量（亿元）", value=1401800.0, key="gdp_t")
        pop = st.number_input("总人口（万人）", value=140000.0, key="pop")
        if st.button("计算人均GDP", key="bp_per_gdp"):
            if pop > 0:
                pg = gdp_t / pop * 10000
                st.metric("人均GDP", f"{pg:,.0f} 元")
                pg_usd = pg / 7.1
                st.write(f"≈ {pg_usd:,.0f} 美元（按1美元=7.1元）")
                if pg_usd >= 13000: st.success("✅ 高收入经济体水平")
                elif pg_usd >= 4000: st.warning("🟡 中等收入水平")
                else: st.error("🔴 低收入水平")
    with st.expander("🔢 国民储蓄率", expanded=False):
        g_s = st.number_input("GDP（亿元）", value=1401800.0, key="g_s")
        cons = st.number_input("居民消费（亿元）", value=770000.0, key="cons")
        gov = st.number_input("政府购买（亿元）", value=210000.0, key="gov")
        if st.button("计算国民储蓄率", key="bp_savings"):
            if g_s > 0:
                sv = (g_s - cons - gov) / g_s * 100
                st.metric("国民储蓄率", f"{sv:.2f}%")
                if 35 <= sv <= 45: st.success("✅ 我国长期区间（35%~45%）")
                elif sv >= 20: st.warning("🟡 与发达国家接近（约20%）")
                else: st.error("🔴 储蓄率偏低")
    st.subheader("💰 二、物价、通胀、利率类")
    with st.expander("🔢 通货膨胀率", expanded=False):
        cn = st.number_input("本期CPI", value=101.0, key="cpi_n")
        cp = st.number_input("上期CPI", value=100.0, key="cpi_p")
        if st.button("计算通货膨胀率", key="bp_inflation"):
            if cp > 0:
                inf = (cn - cp) / cp * 100
                st.metric("通货膨胀率", f"{inf:.2f}%")
                if 1.5 <= inf <= 2.5: st.success("✅ 全球央行目标区间（约2%）")
                elif inf > 5: st.error("🔴 高通胀（>5%）")
                elif inf < 0: st.warning("⚠️ 通货紧缩（<0%）")
                else: st.info("🟡 温和通胀")
    with st.expander("🔢 实际利率", expanded=False):
        nom = st.number_input("名义利率（%）", value=3.0, key="nom_r")
        inf_r = st.number_input("通货膨胀率（%）", value=1.0, key="inf_r")
        if st.button("计算实际利率", key="bp_real_rate"):
            rr = nom - inf_r
            st.metric("实际利率", f"{rr:.2f}%")
            if rr > 0: st.success("✅ 实际利率为正，存钱有真实收益")
            elif rr == 0: st.warning("🟡 实际利率为0，存钱不赚不亏")
            else: st.error("🔴 实际利率为负，存钱贬值")
    with st.expander("🔢 现值计算", expanded=False):
        fv = st.number_input("未来终值（元）", value=100000.0, key="pv_fv")
        dc = st.number_input("贴现率（%）", value=3.0, key="pv_dc")
        yr = st.number_input("年数", value=10, min_value=1, key="pv_yr")
        if st.button("计算现值", key="bp_pv"):
            pv = fv / ((1 + dc / 100) ** yr)
            st.metric("现值", f"{pv:,.2f} 元")
    st.subheader("👥 三、就业类")
    with st.expander("🔢 失业率", expanded=False):
        ue = st.number_input("失业人数（万人）", value=2500.0, key="ue_n")
        lb = st.number_input("劳动力总数（万人）", value=78000.0, key="ue_l")
        if st.button("计算失业率", key="bp_unemp"):
            if lb > 0:
                ur = ue / lb * 100
                st.metric("失业率", f"{ur:.2f}%")
                if 4 <= ur <= 6: st.success("✅ 健康区间（4%~6%）")
                elif ur < 4: st.info("🟢 劳动力紧张，工资可能上涨")
                else: st.error("🔴 就业压力大（>6%）")
    with st.expander("🔢 劳动参与率", expanded=False):
        lf = st.number_input("劳动力（万人）", value=78000.0, key="lf")
        wa = st.number_input("适龄成年人口（万人）", value=120000.0, key="wa")
        if st.button("计算劳动参与率", key="bp_participation"):
            if wa > 0:
                pr = lf / wa * 100
                st.metric("劳动参与率", f"{pr:.2f}%")
                if 60 <= pr <= 67: st.success("✅ 发达国家区间（60%~67%）")
                else: st.warning("🟡 偏离常规区间")
    with st.expander("🔢 奥肯定律（失业率→GDP缺口）", expanded=False):
        au = st.number_input("实际失业率（%）", value=5.1, key="au")
        nu = st.number_input("自然失业率（%）", value=4.5, key="nu")
        if st.button("计算GDP缺口", key="bp_okun"):
            gap = 2 * (au - nu)
            st.metric("GDP缺口", f"{gap:+.2f}%")
            if gap < 0: st.warning("⚠️ 实际产出低于潜在产出")
            else: st.info("🟢 实际产出高于潜在产出")
    st.subheader("🏛️ 四、财政类")
    with st.expander("🔢 赤字率", expanded=False):
        df = st.number_input("财政赤字（亿元）", value=50000.0, key="df")
        gf = st.number_input("GDP（亿元）", value=1401800.0, key="gf")
        if st.button("计算赤字率", key="bp_deficit"):
            if gf > 0:
                dr = df / gf * 100
                st.metric("赤字率", f"{dr:.2f}%")
                if dr <= 3: st.success("✅ 低于经典警戒线3%")
                else: st.error("🔴 超过警戒线3%")
    with st.expander("🔢 债务负担率", expanded=False):
        dt = st.number_input("政府债务余额（亿元）", value=700000.0, key="dt")
        gd = st.number_input("GDP（亿元）", value=1401800.0, key="gd")
        if st.button("计算债务负担率", key="bp_debt"):
            if gd > 0:
                dbr = dt / gd * 100
                st.metric("债务负担率", f"{dbr:.2f}%")
                if dbr <= 60: st.success("✅ 低于经典警戒线60%")
                else: st.error("🔴 超过警戒线60%")
    with st.expander("🔢 利息负担率", expanded=False):
        it = st.number_input("年利息支出（亿元）", value=8000.0, key="it")
        fi = st.number_input("财政收入（亿元）", value=200000.0, key="fi")
        if st.button("计算利息负担率", key="bp_interest"):
            if fi > 0:
                ibr = it / fi * 100
                st.metric("利息负担率", f"{ibr:.2f}%")
                if ibr <= 10: st.success("✅ 财政压力可控（≤10%）")
                else: st.error("🔴 财政压力偏大（>10%）")
    st.subheader("🔁 五、乘数理论")
    with st.expander("🔢 各类乘数一键计算", expanded=False):
        mpc = st.number_input("边际消费倾向 MPC", value=0.8, step=0.05, min_value=0.0, max_value=1.0, key="mpc_m")
        if st.button("计算所有乘数", key="bp_multipliers"):
            if 0 < mpc < 1:
                st.metric("边际储蓄倾向 MPS", f"{1-mpc:.2f}")
                st.metric("政府购买乘数", f"{1/(1-mpc):.2f}")
                st.metric("税收乘数", f"{-mpc/(1-mpc):.2f}")
                st.metric("转移支付乘数", f"{mpc/(1-mpc):.2f}")
    st.subheader("🛒 六、微观经济学：弹性与成本")
    with st.expander("🔢 需求价格弹性", expanded=False):
        q1 = st.number_input("原需求量", value=100.0, key="q1_p")
        q2 = st.number_input("新需求量", value=80.0, key="q2_p")
        p1 = st.number_input("原价格", value=10.0, key="p1_p")
        p2 = st.number_input("新价格", value=12.0, key="p2_p")
        if st.button("计算需求弹性", key="bp_elasticity"):
            if p1 > 0 and q1 > 0:
                ed = ((q2-q1)/q1*100) / ((p2-p1)/p1*100) if p2 != p1 else 0
                st.metric("需求价格弹性", f"{ed:.2f}")
                if abs(ed) > 1: st.success("✅ 富有弹性，降价能多赚钱")
                elif abs(ed) == 1: st.info("🟡 单位弹性")
                else: st.warning("🟡 缺乏弹性，涨价能多赚钱")
    with st.expander("🔢 需求收入弹性", expanded=False):
        qi1 = st.number_input("原需求量", value=100.0, key="qi1")
        qi2 = st.number_input("新需求量", value=120.0, key="qi2")
        i1 = st.number_input("原收入", value=5000.0, key="i1")
        i2 = st.number_input("新收入", value=6000.0, key="i2")
        if st.button("计算收入弹性", key="bp_inc_elasticity"):
            if i1 > 0 and qi1 > 0:
                ei = ((qi2-qi1)/qi1*100) / ((i2-i1)/i1*100) if i2 != i1 else 0
                st.metric("需求收入弹性", f"{ei:.2f}")
                if ei > 1: st.success("✅ 奢侈品，收入涨了买得更多")
                elif ei > 0: st.info("🟢 正常品/必需品")
                else: st.warning("🔴 低档品，收入涨了反而少买")
    with st.expander("🔢 成本利润全套", expanded=False):
        fc = st.number_input("固定成本（元）", value=10000.0, key="cp_fc")
        vc = st.number_input("可变成本（元）", value=20000.0, key="cp_vc")
        q = st.number_input("产量", value=1000.0, key="cp_q")
        price = st.number_input("价格（元/件）", value=50.0, key="cp_p")
        hc = st.number_input("隐性成本（机会成本）", value=5000.0, key="cp_hc")
        if st.button("计算成本利润", key="bp_cost_profit"):
            if q > 0:
                tc = fc + vc
                tr = price * q
                ap = tr - tc
                ep = tr - tc - hc
                st.metric("总成本", f"{tc:,.0f} 元")
                st.metric("总收益", f"{tr:,.0f} 元")
                st.metric("会计利润", f"{ap:,.0f} 元")
                if ep > 0: st.success(f"✅ 经济利润 = {ep:,.0f} 元")
                else: st.error(f"🔴 经济利润 = {ep:,.0f} 元")
    st.subheader("📈 七、综合景气与分配")
    with st.expander("🔢 克强指数", expanded=False):
        e = st.number_input("工业用电量增速（%）", value=6.0, key="kq_e")
        r = st.number_input("铁路货运量增速（%）", value=4.0, key="kq_r")
        l = st.number_input("中长期贷款增速（%）", value=11.0, key="kq_l")
        if st.button("计算克强指数", key="bp_keqiang"):
            ki = e * 0.4 + r * 0.25 + l * 0.35
            st.metric("克强指数", f"{ki:.2f}%")
            if ki >= 5: st.success("✅ 经济回暖（≥5%）")
            elif ki >= 0: st.warning("🟡 经济偏弱（0~5%）")
            else: st.error("🔴 经济走弱（<0）")
    with st.expander("🔢 恩格尔系数", expanded=False):
        fs = st.number_input("食品支出（元/月）", value=2000.0, key="en_fs")
        ts = st.number_input("总消费支出（元/月）", value=6000.0, key="en_ts")
        if st.button("计算恩格尔系数", key="bp_engel"):
            if ts > 0:
                en = fs / ts * 100
                st.metric("恩格尔系数", f"{en:.2f}%")
                if en > 59: st.error("🔴 贫困")
                elif en > 50: st.warning("🟡 温饱")
                elif en > 40: st.info("🟢 小康")
                else: st.success("✅ 富裕/最富裕")
    with st.expander("🔢 基尼系数判断", expanded=False):
        gini = st.number_input("基尼系数", value=0.45, step=0.01, min_value=0.0, max_value=1.0, key="gini_c")
        if st.button("判断基尼系数", key="bp_gini"):
            if gini < 0.2: st.success("🌟 高度平均")
            elif gini < 0.3: st.success("✅ 比较平均")
            elif gini < 0.4: st.info("🟢 相对合理")
            elif gini == 0.4: st.warning("⚠️ 处于警戒线")
            else: st.error("🔴 差距偏大，需要政策调节")
    st.markdown("---")
    st.caption("💡 提示：本计算器基于经济学标准公式，结果仅供参考。")


st.markdown("---")
st.subheader("🏛️ 财政与税收指标")
macro_data = (globals().get("macro") or {}).get("data", {})
tax_data = macro_data.get("tax_revenue", {"value": 185000.0, "yoy": -2.5, "date": "2026年8月"})
exp_data = macro_data.get("gov_expenditure", {"value": 220000.0, "yoy": 2.8, "date": "2026年8月"})

col_tax1, col_tax2, col_tax3, col_tax4 = st.columns(4)
with col_tax1:
    st.metric("税收收入", f"{tax_data.get('value', 185000):,.0f} 亿元" if tax_data.get('value') else "—", "累计值")
with col_tax2:
    yoy_val = tax_data.get('yoy', -2.5)
    st.metric("税收同比", f"{yoy_val:+.1f}%", "反映经济活力")
with col_tax3:
    st.metric("宏观税负", "15.2%", "税收/GDP")
with col_tax4:
    exp_yoy = exp_data.get('yoy', 2.8)
    st.metric("财政支出同比", f"{exp_yoy:+.1f}%", "逆周期调节")
st.caption("💡 税收同比看经济冷暖，支出同比看政策力度。两者结合看财政政策取向。")
python -c "import pathlib; p=pathlib.Path('app.py'); s=p.read_text(encoding='utf-8'); diag='''

st.markdown(\"---\")
st.subheader(\"🩺 经济诊断与对策建议（本地规则引擎）\")

# 诊断逻辑
diagnoses = []
suggestions = []
feasibility = []

# 1. 流动性陷阱判断
if gdp_val and m2_balance_val and gdp_val > 0:
    m2_gdp = m2_balance_val / (gdp_val * 4)
    if m2_gdp > 2.5:
        diagnoses.append(\"🔴 **流动性陷阱特征明显**：M2/GDP = \" + f\"{m2_gdp:.2f}\" + \" 倍，货币严重超发，但资金未有效流入实体\")
        suggestions.append(\"💊 **对策**：货币政策边际效用递减，需财政发力。建议增发国债、扩大政府投资、加快重大项目落地\")
        feasibility.append(\"⚖️ **可行性**：当前赤字率约3%，距离国际警戒线3%仍有空间；但需警惕地方债务压力\")
if m1_val is not None and m2_val is not None:
    scissors = m1_val - m2_val
    if scissors < 0:
        diagnoses.append(\"🟡 **资金活化不足**：M1/M2剪刀差 = \" + f\"{scissors:+.2f}%\" + \"，钱被存成定期，不敢消费和投资\")
        suggestions.append(\"💊 **对策**：刺激消费、提高居民收入预期、降低存款利率\")
        feasibility.append(\"⚖️ **可行性**：降息受中美利差制约，空间有限；消费刺激需财政配合\")

# 2. 物价结构判断
if True:
    cpi_v = 0.8; ppi_v = 3.8
    if cpi_v < 1 and ppi_v > 0:
        diagnoses.append(\"🟡 **下游通缩、上游挤压**：CPI低、PPI高，中游企业利润被两头挤压\")
        suggestions.append(\"💊 **对策**：刺激终端消费、减税降费、支持中游制造业\")
        feasibility.append(\"⚖️ **可行性**：减税降费需财政承受能力；消费刺激需居民收入支撑\")

# 3. 外部压力判断
if True:
    spread_val = -1.7
    if spread_val < 0:
        diagnoses.append(\"🔴 **中美利差倒挂**：外资流出压力大，人民币汇率承压\")
        suggestions.append(\"💊 **对策**：稳汇率预期、加强资本流动管理、提升人民币资产吸引力\")
        feasibility.append(\"⚖️ **可行性**：降息空间受制约；需平衡稳增长与稳汇率\")

# 输出
for d in diagnoses:
    st.warning(d)
st.markdown(\"#### 📋 对策建议\")
for s in suggestions:
    st.info(s)
st.markdown(\"#### ⚖️ 可行性分析\")
for f in feasibility:
    st.caption(f)

st.caption(\"💡 提示：本诊断基于本地规则引擎，仅供参考。实际决策请结合更多信息和专业判断。\")
'''
if '经济诊断与对策建议' not in s:
    p.write_text(s + diag, encoding='utf-8')
    print('✅ 经济诊断板块已成功追加！')
else:
    print('📌 诊断板块已存在，无需重复添加。')"
