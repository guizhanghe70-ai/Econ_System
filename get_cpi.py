import akshare as ak
import pandas as pd

print("正在抓取全国、城市、农村 CPI 数据，请稍等...")

# 抓取最稳定的宏观汇总数据
df = ak.macro_china_cpi()

print("\n✅ 抓取成功！")
print(df.head())

# 保存数据
df.to_csv("cpi_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 cpi_data.csv 中！")