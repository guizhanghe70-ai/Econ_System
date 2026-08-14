import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import os

# 解决图表中文字体显示为方块的问题
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  
matplotlib.rcParams['axes.unicode_minus'] = False 

# 读取文件
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, 'cpi_data.csv')

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print("❌ 找不到 cpi_data.csv 文件！请先运行 python get_cpi.py 生成数据！")
    exit()

# ⚠️ 这里就是修复报错的关键改动
df['月份'] = df['月份'].astype(str).str.replace('年', '-').str.replace('月份', '')
df['月份'] = pd.to_datetime(df['月份'])
df = df.sort_values('月份')

# 3. 开始画图
plt.figure(figsize=(12, 6))
plt.plot(df['月份'], df['全国-当月'], marker='o', linestyle='-', label='全国当月 CPI')

# 添加标题和标签
plt.title('中国 CPI 走势分析', fontsize=16)
plt.xlabel('时间', fontsize=12)
plt.ylabel('CPI 当月值', fontsize=12)
plt.grid(True)
plt.legend()

# 4. 保存为图片文件
save_path = os.path.join(current_dir, 'cpi_trend_chart.png')
plt.savefig(save_path)
print(f"✅ 成功！CPI 趋势图已生成，保存位置是：{save_path}")