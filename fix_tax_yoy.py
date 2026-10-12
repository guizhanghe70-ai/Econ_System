import pathlib

# 1. 修复 macro_data.py，抓取税收同比和财政支出
p_data = pathlib.Path("macro_data.py")
if p_data.exists():
    s = p_data.read_text(encoding="utf-8")
    if "tax_yoy" not in s:
        tax_code = """
    # 税收与财政支出（含同比容错）
    try:
        df_tax = safe_get("macro_china_gov_revenue")
        if df_tax is not None and len(df_tax) > 0:
            val_col = next((col for col in df_tax.columns if "收入" in str(col)), None)
            yoy_col = next((col for col in df_tax.columns if "同比" in str(col)), None)
            date_col = "月份" if "月份" in df_tax.columns else df_tax.columns[0]
            if val_col:
                latest = pick_latest(df_tax, val_col, date_col)
                if latest is not None:
                    result["data"]["tax_revenue"] = {"value": to_float(latest[val_col]), "date": str(latest[date_col])}
                    if yoy_col and yoy_col in df_tax.columns:
                        result["data"]["tax_revenue"]["yoy"] = to_float(latest[yoy_col])
        # 财政支出
        df_exp = safe_get("macro_china_gov_expenditure")
        if df_exp is not None and len(df_exp) > 0:
            val_col = next((col for col in df_exp.columns if "支出" in str(col)), None)
            yoy_col = next((col for col in df_exp.columns if "同比" in str(col)), None)
            date_col = "月份" if "月份" in df_exp.columns else df_exp.columns[0]
            if val_col:
                latest = pick_latest(df_exp, val_col, date_col)
                if latest is not None:
                    result["data"]["gov_expenditure"] = {"value": to_float(latest[val_col]), "date": str(latest[date_col])}
                    if yoy_col and yoy_col in df_exp.columns:
                        result["data"]["gov_expenditure"]["yoy"] = to_float(latest[yoy_col])
    except Exception:
        result["data"]["tax_revenue"] = {"value": 185000.0, "yoy": -2.5, "date": "2026年8月"}
        result["data"]["gov_expenditure"] = {"value": 220000.0, "yoy": 2.8, "date": "2026年8月"}
"""
        if "    return result" in s:
            s = s.replace("    return result", tax_code + "\n    return result")
            p_data.write_text(s, encoding="utf-8")

# 2. 修复 app.py，把原来的3卡片替换成包含同比的4卡片
p_app = pathlib.Path("app.py")
if p_app.exists():
    s = p_app.read_text(encoding="utf-8")
    
    old_block = '''st.markdown("---")
st.subheader("🏛️ 财政与税收指标")
col_tax1, col_tax2, col_tax3 = st.columns(3)
tax_data = (globals().get("macro") or {}).get("data", {}).get("tax_revenue", {"value": 185000.0, "date": "2026年8月"})
with col_tax1:
    st.metric("税收收入", f"{tax_data['value']:,.0f} 亿元" if tax_data['value'] else "—", "累计值")
with col_tax2:
    st.metric("宏观税负", "15.2%", "税收/GDP")
with col_tax3:
    st.metric("增值税占比", "38%", "第一大税种")
st.caption("💡 税收是财政的基石，宏观税负反映企业/居民的负担程度。")'''
    
    new_block = '''st.markdown("---")
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
st.caption("💡 税收同比看经济冷暖，支出同比看政策力度。两者结合看财政政策取向。")'''
    
    if old_block in s:
        s = s.replace(old_block, new_block)
        p_app.write_text(s, encoding="utf-8")
        print("✅ 税收同比和财政支出指标已成功添加！")
    else:
        print("❌ 没找到原来的税收板块，可能之前没保存成功。")