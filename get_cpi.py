import akshare as ak
import pandas as pd

print("正在抓取 CPI 数据，请稍等...")

# 抓取数据
cpi_df = ak.macro_china_cpi()

# 查看前5行
print("\n✅ 抓取成功！前 5 行数据如下：")
print(cpi_df.head())

# 保存到当前文件夹，命名为 cpi_data.csv
cpi_df.to_csv("cpi_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已经保存在你文件夹里的 cpi_data.csv 中！")