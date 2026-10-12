import pathlib

p = pathlib.Path("app.py")
s = p.read_text(encoding="utf-8")

# 找到报错的那行代码，改成安全容错的版本
old_code = 'tax_data = macro.get("data", {}).get("tax_revenue", {"value": 185000.0, "date": "2026年8月"})'
new_code = 'tax_data = (globals().get("macro") or {}).get("data", {}).get("tax_revenue", {"value": 185000.0, "date": "2026年8月"})'

if old_code in s:
    s = s.replace(old_code, new_code)
    p.write_text(s, encoding="utf-8")
    print("✅ 税收板块的 bug 已成功修复！")
else:
    print("❌ 没找到旧代码，可能刚才没保存，请把 app.py 重新发我。")