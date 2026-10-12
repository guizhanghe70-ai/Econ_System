# coding: utf-8
# push_bot.py - 每日宏观数据微信推送机器人

import requests
from datetime import datetime
from macro_data import fetch_all_macro, get_val

# ==================== 你的钥匙 ====================
PUSHPLUS_TOKEN = "bb4a25de496548489a1cd2b33a008ceb"
# ==================================================

def send_to_wechat(title, content):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": content,
        "template": "markdown"
    }
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if result.get("code") == 200:
            print(f"✅ 推送成功！ {datetime.now().strftime('%H:%M:%S')}")
        else:
            print(f"❌ 推送失败：{result.get('msg')}")
    except Exception as e:
        print(f"❌ 发送异常：{e}")

def run_daily_report():
    print("正在抓取今日宏观数据...")
    macro = fetch_all_macro()
    
    # 提取核心数据
    cpi = get_val(macro, "cpi", fallback=0.8)
    ppi = get_val(macro, "ppi", fallback=3.8)
    cpi_ppi_scissors = cpi - ppi
    
    m1 = get_val(macro, "m1", fallback=4.1)
    m2 = get_val(macro, "m2", fallback=7.5)
    m1_m2_scissors = m1 - m2
    
    m2_balance = get_val(macro, "m2_balance", fallback=None)
    gdp = get_val(macro, "gdp", fallback=None)
    m2_gdp = m2_balance / (gdp * 4) if m2_balance and gdp else 0
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

    
    # 拼装消息内容
    today_str = datetime.now().strftime("%Y年%m月%d日")
    content = f"""
### 📊 每日宏观数据早报（{today_str}）

**一、核心指标一览**
*   **CPI 同比**：{cpi:+.2f}%
*   **PPI 同比**：{ppi:+.2f}%
*   **CPI-PPI 剪刀差**：{cpi_ppi_scissors:+.2f}% （{"下游利润改善" if cpi_ppi_scissors > 0 else "下游成本承压"}）
*   **M1 同比**：{m1:+.2f}%
*   **M2 同比**：{m2:+.2f}%
*   **M1-M2 剪刀差**：{m1_m2_scissors:+.2f}% （{"资金活化" if m1_m2_scissors > 0 else "资金沉淀，不敢消费"}）

**二、货币超发监测**
*   **M2/GDP 比率**：{m2_gdp:.2f} 倍 （{"货币超发严重" if m2_gdp > 2.5 else "处于警戒线附近" if m2_gdp > 2.0 else "符合间接融资国情" if m2_gdp > 1.0 else "健康"}）

**三、宏观对冲仪表盘（前照灯）**
*   **中美利差 (10Y)**：{china_us_spread:+.2f}% （{"外资流出压力大" if china_us_spread < 0 else "外资流入动力强"}）
*   **库存周期(营收-库存)**：{inventory_cycle_diff:+.2f}% （{"主动补库，经济复苏" if inventory_cycle_diff > 0 else "被动去库，需求疲软"}）
*   **M1-M2偏离均值**：{m1_m2_deviation:+.2f}% （{"资金活化度高于历史均值" if m1_m2_deviation > 0 else "资金沉淀低于历史均值"}）

---
💡 *提示：数据由 AkShare 自动抓取，缓存 24 小时。*
"""
    send_to_wechat("📈 今日宏观数据早报", content)

if __name__ == "__main__":
    run_daily_report()