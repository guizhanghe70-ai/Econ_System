import akshare as ak
import pandas as pd

print("正在抓取 M2（广义货币供应量）数据...")
m2_df = ak.macro_china_money_supply()

print("\n✅ M2 抓取成功！")
print(m2_df.head())

m2_df.to_csv("m2_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 m2_data.csv 中！")