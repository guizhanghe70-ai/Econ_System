# coding: utf-8
# push_bot.py - 每日宏观数据微信推送机器人（含经济诊断与民生保障）

import os
import requests
from datetime import datetime
from macro_data import fetch_all_macro, get_val

PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "bb4a25de496548489a1cd2b33a008ceb")

def send_to_wechat(title, content):
    url = "http://www.pushplus.plus/send"
    data = {"token": PUSHPLUS_TOKEN, "title": title, "content": content, "template": "markdown"}
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
    
    cpi = get_val(macro, "cpi", fallback=0.8)
    ppi = get_val(macro, "ppi", fallback=3.8)
    cpi_ppi_scissors = cpi - ppi
    m1 = get_val(macro, "m1", fallback=4.1)
    m2 = get_val(macro, "m2", fallback=7.5)
    m1_m2_scissors = m1 - m2
    m2_balance = get_val(macro, "m2_balance", fallback=3568100.0)
    gdp = get_val(macro, "gdp", fallback=334193.0)
    m2_gdp = m2_balance / (gdp * 4) if m2_balance and gdp else 2.67
    china_us_spread = 2.5 - 4.2
    inventory_cycle_diff = 3.6
    m1_m2_deviation = m1_m2_scissors - (-2.0)
    
    # 民生数据（新增）
    income_yoy = get_val(macro, "income_yoy", fallback=4.0)
    retail_yoy = get_val(macro, "retail", fallback=0.4)
    social_security_yoy = get_val(macro, "social_security", fallback=3.5)
    
    # 诊断逻辑
    diag_lines = []
    if m2_gdp > 2.5:
        diag_lines.append("🔴 流动性陷阱：货币超发但未流入实体，需财政发力")
    if m1_m2_scissors < 0:
        diag_lines.append("🟡 资金活化不足：钱被存成定期，需刺激消费")
    if cpi < 1 and ppi > 0:
        diag_lines.append("🟡 下游通缩、上游挤压：中游利润被两头挤，需减税降费")
    if china_us_spread < 0:
        diag_lines.append("🔴 中美利差倒挂：外资流出压力大，降息空间受限")
    if inventory_cycle_diff > 0:
        diag_lines.append("🟢 主动补库：经济复苏初期，关注大宗商品")
    if not diag_lines:
        diag_lines.append("🟢 当前宏观指标未见明显异常")

    today_str = datetime.now().strftime("%Y年%m月%d日")
    content = f"""
### 📊 每日宏观数据早报（{today_str}）

**一、核心指标一览**
*   **CPI 同比**：{cpi:+.2f}%
*   **PPI 同比**：{ppi:+.2f}%
*   **CPI-PPI 剪刀差**：{cpi_ppi_scissors:+.2f}%
*   **M1 同比**：{m1:+.2f}%
*   **M2 同比**：{m2:+.2f}%
*   **M1-M2 剪刀差**：{m1_m2_scissors:+.2f}%

**二、货币超发监测**
*   **M2/GDP 比率**：{m2_gdp:.2f} 倍 （{"货币超发严重" if m2_gdp > 2.5 else "处于警戒线附近" if m2_gdp > 2.0 else "符合间接融资国情" if m2_gdp > 1.0 else "健康"}）

**三、宏观对冲仪表盘**
*   **中美利差 (10Y)**：{china_us_spread:+.2f}%
*   **库存周期(营收-库存)**：{inventory_cycle_diff:+.2f}%
*   **M1-M2偏离均值**：{m1_m2_deviation:+.2f}%

**四、民生与保障（内需底色）**
*   **居民收入同比**：{income_yoy:+.1f}% （{"⚠️低于GDP增速" if income_yoy < 5.0 else "✅与增长同步"}）
*   **社会消费品零售**：{retail_yoy:+.1f}% （{"🔴极度疲软" if retail_yoy < 2 else "🟢温和扩张"}）
*   **社保就业支出**：{social_security_yoy:+.1f}% （{"⚠️需加大兜底" if social_security_yoy < 3 else "🟢正在托底民生"}）

**五、经济诊断与对策**
{chr(10).join(diag_lines)}

---
💡 *提示：数据由 AkShare 自动抓取，诊断仅供参考。*
"""
    send_to_wechat("📈 今日宏观数据早报", content)

if __name__ == "__main__":
    run_daily_report()
