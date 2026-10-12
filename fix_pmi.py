import pathlib

p = pathlib.Path("app.py")
s = p.read_text(encoding="utf-8")

# 检查是不是真的丢了那几个辅助函数
if "def get_pmi_status" not in s:
    lines = s.splitlines()
    injected = False
    for i, line in enumerate(lines):
        if 'pmi_line = st.sidebar.number_input' in line:
            # 把三个辅助函数补在 PMI 定义之后
            lines.insert(i+1, '    def get_cpi_status(val): return "⚠️ 通胀" if val > 103 else ("⚠️ 通缩" if val < 99 else "✅ 稳定")')
            lines.insert(i+2, '    def get_m2_status(val): return "🔵 宽松" if val > 15 else ("🔴 紧缩" if val < 8 else "🟢 平稳")')
            lines.insert(i+3, '    def get_pmi_status(val): return "✅ 扩张" if val > pmi_line else "⚠️ 收缩"')
            injected = True
            break
    if injected:
        s = "\n".join(lines)
        p.write_text(s, encoding="utf-8")
        print("✅ 修复成功！缺失的函数已经补回去了。")
    else:
        print("❌ 找不到定位点，可能文件被改乱了，请告诉我。")
else:
    print("✅ 代码里已经有了，无需修复。")