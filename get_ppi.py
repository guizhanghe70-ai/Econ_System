import akshare as ak
import pandas as pd

print("正在抓取 PPI（工业生产者出厂价格指数）数据...")
ppi_df = ak.macro_china_ppi()

print("\n✅ 抓取成功！PPI 数据预览如下：")
print(ppi_df.head())

# 保存为单独的 ppi_data.csv
ppi_df.to_csv("ppi_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 PPI 数据已单独保存为 ppi_data.csv！")