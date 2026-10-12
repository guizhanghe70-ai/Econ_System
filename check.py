# coding: utf-8
import akshare as ak

def show(title, func):
    print("=" * 60)
    print(f"【{title}】")
    print("=" * 60)
    try:
        df = func()
        print(f"共 {len(df)} 行")
        print(f"列名（共{len(df.columns)}列）：")
        for i, c in enumerate(df.columns):
            print(f"   [{i}] {c}")
        print()
        print("前 3 行数据：")
        print(df.head(3).to_string())
        print()
    except Exception as e:
        print(f"❌ 出错: {e}")
        print()

show("社融（社会融资规模）", lambda: ak.macro_china_shrzgm())
show("失业率（城镇调查失业率）", lambda: ak.macro_china_urban_unemployment())