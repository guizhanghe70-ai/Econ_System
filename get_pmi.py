import akshare as ak
import pandas as pd

print("正在抓取 PMI（采购经理指数）数据，请稍等...")
pmi_df = ak.macro_china_pmi()

print("\n✅ PMI 抓取成功！前5行数据如下：")
print(pmi_df.head())

pmi_df.to_csv("pmi_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 pmi_data.csv 中！")