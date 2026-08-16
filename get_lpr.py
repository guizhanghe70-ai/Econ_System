import akshare as ak
import pandas as pd

print("正在抓取 LPR（贷款市场报价利率）数据...")
lpr_df = ak.macro_china_lpr()

print("\n✅ LPR 抓取成功！预览如下：")
print(lpr_df.head())

lpr_df.to_csv("lpr_data.csv", index=False, encoding='utf-8-sig')
print("\n📁 数据已保存到 lpr_data.csv 中！")