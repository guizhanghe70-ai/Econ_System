import akshare as ak
import pandas as pd

print("正在抓取中国 GDP 季度数据，请稍等...")
gdp_df = ak.macro_china_gdp()

print("\n✅ GDP 抓取成功！预览如下：")
print(gdp_df.head())

gdp_df.to_csv("gdp_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 gdp_data.csv 中！")