import pathlib

p = pathlib.Path("app.py")
s = p.read_text(encoding="utf-8")

# 找到计算器板块的位置，把它及之后的内容全部替换为完整的计算器代码
if 'elif page == "🧮 经济指标计算器":' in s:
    s = s.split('elif page == "🧮 经济指标计算器":')[0]

full_calc_code = '''elif page == "🧮 经济指标计算器":
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
'''

p.write_text(s + full_calc_code, encoding="utf-8")
print("✅ 计算器全部恢复！")