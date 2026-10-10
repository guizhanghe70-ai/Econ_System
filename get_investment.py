import akshare as ak
import pandas as pd

print("正在抓取城镇固定资产投资数据...")
# 这个接口目前相对稳定
investment_df = ak.macro_china_urban_investment()

print("\n✅ 抓取成功！预览如下：")
print(investment_df.head())

investment_df.to_csv("investment_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 investment_data.csv 中！")