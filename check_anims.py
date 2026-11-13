import unreal
import csv
import os
from collections import Counter


ASSET_ROOT = "/Game" # 资产路径
OUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.csv") # 表格生成路径
EXPECTED_FPS = 30.0 # 目标帧率
ALLOWED_PREFIXES = ("MM_", "Quinn_", "Manny_", "MF_") # 命名前缀审查

def check_problem(name, length, fps):
    problems = []
    if abs(fps - EXPECTED_FPS) > 0.01:
        problems.append(f"帧率不是{EXPECTED_FPS:g}")
    if not name.startswith(ALLOWED_PREFIXES):
        problems.append("命名前缀不符")
    return "；".join(problems)


paths = unreal.EditorAssetLibrary.list_assets(ASSET_ROOT, recursive=True, include_folder=False)

rows = []
for p in paths:
    data = unreal.EditorAssetLibrary.find_asset_data(p)
    if not data or str(data.asset_class_path.asset_name) != "AnimSequence":
        continue
    a = unreal.EditorAssetLibrary.load_asset(p)
    if not a:
        continue

    fps = 0.0
    try:
        fr = a.get_editor_property("target_frame_rate")
        fps = fr.numerator / fr.denominator
    except Exception:
        pass

    name = a.get_name()
    length = a.sequence_length
    rows.append([name, p, f"{length:.2f}", f"{fps:.1f}", check_problem(name, length, fps)])

os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
with open(OUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(["名称", "路径", "时长(s)", "帧率", "问题"])
    w.writerows(rows)

unreal.log(f"[AnimCheck] 共 {len(rows)} 个动画，已写入 {OUT_CSV}")
unreal.log(f"[AnimCheck] 有问题的：{sum(1 for r in rows if r[4])} 个")

# 统计每类问题出现多少次
counter = Counter()
for r in rows:
    if r[4]:
        for item in r[4].split("；"):
            counter[item] += 1

problem_rows = sum(1 for r in rows if r[4])

unreal.log("=" * 42)
unreal.log(f"扫描资产总数：{len(rows)}")
unreal.log(f"有问题资产数：{problem_rows}")
for k, v in counter.most_common():
    unreal.log(f"  - {k}：{v}")
unreal.log("=" * 42)