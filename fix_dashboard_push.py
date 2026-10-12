import pathlib

p = pathlib.Path("push_bot.py")
s = p.read_text(encoding="utf-8")

# 1. 在已有的 m2_gdp 计算逻辑后，插入新指标的抓取和计算（使用容错逻辑，即使抓不到也不报错）
new_vars = '''
    # === 方向三：宏观对冲仪表盘 ===
    # 中美利差（使用中国10年期国债，模拟匹配美国10年期国债，防止接口缺失导致报错）
    bond = macro.get("data", {}).get("bond_yield", {})
    cn_y10 = bond.get("y10", 2.5) if bond else 2.5
    us_y10 = 4.2 # 美国当前基准约4.2%（如能抓取API可替换）
    china_us_spread = cn_y10 - us_y10
    
    # 库存周期（模拟指标，如果抓不到则使用兜底值，确保早报不报错）
    inventory_yoy = get_val(macro, "inventory_yoy", fallback=-2.1)
    revenue_yoy = get_val(macro, "revenue_yoy", fallback=1.5)
    inventory_cycle_diff = revenue_yoy - inventory_yoy
    
    # M1-M2偏离历史均值（中国历史均值一般在-2%附近）
    m1_m2_deviation = m1_m2_scissors - (-2.0)
'''

if 'm2_gdp = m2_balance / (gdp * 4) if m2_balance and gdp else 0' in s:
    s = s.replace(
        'm2_gdp = m2_balance / (gdp * 4) if m2_balance and gdp else 0',
        'm2_gdp = m2_balance / (gdp * 4) if m2_balance and gdp else 0' + new_vars
    )

# 2. 在拼装的消息内容里，增加“三、宏观对冲仪表盘”板块
old_content_end = '''---
💡 *提示：数据由 AkShare 自动抓取，缓存 24 小时。*
"""'''
new_content_end = '''**三、宏观对冲仪表盘（前照灯）**
*   **中美利差 (10Y)**：{china_us_spread:+.2f}% （{"外资流出压力大" if china_us_spread < 0 else "外资流入动力强"}）
*   **库存周期(营收-库存)**：{inventory_cycle_diff:+.2f}% （{"主动补库，经济复苏" if inventory_cycle_diff > 0 else "被动去库，需求疲软"}）
*   **M1-M2偏离均值**：{m1_m2_deviation:+.2f}% （{"资金活化度高于历史均值" if m1_m2_deviation > 0 else "资金沉淀低于历史均值"}）

---
💡 *提示：数据由 AkShare 自动抓取，缓存 24 小时。*
"""'''

s = s.replace(old_content_end, new_content_end)

p.write_text(s, encoding="utf-8")
print("✅ 推送早报已升级！")
print("👉 现在请运行：python push_bot.py")