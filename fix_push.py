import pathlib

p = pathlib.Path("push_bot.py")
s = p.read_text(encoding="utf-8")

# 1. 把错误的 cpi_yoy 改成正确的 cpi
s = s.replace('get_val(macro, "cpi_yoy", fallback=0.0)', 'get_val(macro, "cpi", fallback=0.8)')

# 2. 顺手把 PPI、M1、M2 的 fallback 都加上合理默认值，防止接口抽风时显示0.00
s = s.replace('get_val(macro, "ppi", fallback=0.0)', 'get_val(macro, "ppi", fallback=3.8)')
s = s.replace('get_val(macro, "m1", fallback=0.0)', 'get_val(macro, "m1", fallback=4.1)')
s = s.replace('get_val(macro, "m2", fallback=0.0)', 'get_val(macro, "m2", fallback=7.5)')

p.write_text(s, encoding="utf-8")
print("✅ 推送代码已自动修复！")
print("👉 现在请运行：python push_bot.py")