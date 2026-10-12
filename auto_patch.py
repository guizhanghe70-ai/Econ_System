import os
import shutil

def patch_macro_data():
    path = "macro_data.py"
    if not os.path.exists(path):
        print(f"❌ 找不到 {path}，请确保脚本和它在同一个文件夹。")
        return False
    
    # 自动备份，防止改坏了
    shutil.copy(path, path + ".bak")
    
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    if "cpi_yoy" in code:
        print("⏩ macro_data.py 已经包含 CPI 同比，跳过。")
    else:
        target_ppi = "    # PPI\n"
        new_cpi = '''    # CPI 同比（用于剪刀差）
    try:
        df_cpi_yoy = safe_get("macro_china_cpi")
        if df_cpi_yoy is not None and len(df_cpi_yoy) > 0:
            yoy_col = None
            for col in df_cpi_yoy.columns:
                if "全国" in str(col) and "同比" in str(col):
                    yoy_col = col
                    break
            date_col = "月份" if "月份" in df_cpi_yoy.columns else df_cpi_yoy.columns[0]
            if yoy_col:
                latest = pick_latest(df_cpi_yoy, yoy_col, date_col)
                if latest is not None:
                    result["data"]["cpi_yoy"] = {
                        "value": to_float(latest[yoy_col]),
                        "date": str(latest[date_col]),
                    }
                    result["success"].append("CPI同比")
    except Exception:
        pass

'''
        if target_ppi in code:
            code = code.replace(target_ppi, new_cpi + target_ppi)
            print("✅ macro_data.py: CPI 同比补丁已自动插入。")
        else:
            print("⚠️ macro_data.py: 找不到 `    # PPI` 标记，请手动复制补丁。")

    if "shrzgm_stock_yoy" not in code:
        target_lpr = "    # LPR\n"
        new_shrzgm = '''    # 社融存量同比
    try:
        df_stock = safe_get("macro_china_shrzgm_stock")
        if df_stock is not None and len(df_stock) > 0:
            yoy_col = None
            for col in df_stock.columns:
                if "同比增长" in str(col) or "同比" in str(col):
                    yoy_col = col
                    break
            date_col = "月份" if "月份" in df_stock.columns else df_stock.columns[0]
            if yoy_col:
                latest = pick_latest(df_stock, yoy_col, date_col)
                if latest is not None:
                    result["data"]["shrzgm_stock_yoy"] = {
                        "value": to_float(latest[yoy_col]),
                        "date": str(latest[date_col]),
                    }
                    result["success"].append("社融存量同比")
    except Exception:
        pass

'''
        if target_lpr in code:
            code = code.replace(target_lpr, new_shrzgm + target_lpr)
            print("✅ macro_data.py: 社融存量同比补丁已自动插入。")
        else:
            print("⚠️ macro_data.py: 找不到 `    # LPR` 标记，请手动复制补丁。")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return True

def patch_app():
    path = "app.py"
    if not os.path.exists(path):
        print(f"❌ 找不到 {path}")
        return False
    
    shutil.copy(path, path + ".bak")
    
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    if "cpi_ppi_scissors" in code:
        print("⏩ app.py 已经包含 CPI-PPI 剪刀差，跳过。")
        return True

    target_app = '    st.markdown("### 📊 货币乘数'
    new_app = '''    # CPI-PPI 剪刀差
    cpi_yoy_val = get_val(macro, "cpi_yoy", fallback=None)
    ppi_val_for_diff = get_val(macro, "ppi", fallback=None)
    if cpi_yoy_val is not None and ppi_val_for_diff is not None:
        cpi_ppi_scissors = cpi_yoy_val - ppi_val_for_diff
        col_cp1, col_cp2 = st.columns(2)
        with col_cp1:
            st.metric("CPI 同比", f"{cpi_yoy_val:+.1f}%", f"PPI: {ppi_val_for_diff:+.1f}%")
        with col_cp2:
            st.metric("CPI-PPI 剪刀差", f"{cpi_ppi_scissors:+.1f}%", "正=消费强，负=生产强")
        if cpi_ppi_scissors > 0:
            st.info("🟢 剪刀差为正，说明消费端价格涨幅高于生产端，下游企业利润空间可能改善。")
        else:
            st.warning("🟡 剪刀差为负，说明生产端价格涨幅高于消费端，中下游企业成本压力较大。")
    else:
        st.info("📌 暂无 CPI 同比或 PPI 数据，无法计算剪刀差。")

    # 社融存量同比
    shrzgm_stock_yoy = get_val(macro, "shrzgm_stock_yoy", fallback=None)
    if shrzgm_stock_yoy is not None:
        st.metric("社融存量同比", f"{shrzgm_stock_yoy:+.1f}%", "反映金融对实体支持力度")
    else:
        st.metric("社融存量同比", "—", "数据暂缺")

'''
    if target_app in code:
        code = code.replace(target_app, new_app + target_app)
        print("✅ app.py: CPI-PPI 剪刀差、社融存量同比补丁已自动插入。")
    else:
        print("⚠️ app.py: 找不到 `    st.markdown(\"### 📊 货币乘数` 标记，请手动复制补丁。")

    with open(path, "w", encoding="utf-8") as f:
        f.write(code)
    return True

if __name__ == "__main__":
    print("开始一键打补丁...")
    m_ok = patch_macro_data()
    a_ok = patch_app()
    if m_ok and a_ok:
        print("🎉 补丁处理完毕！请重启 Streamlit。")
    else:
        print("❌ 部分补丁未能自动插入，请查看上方提示。")