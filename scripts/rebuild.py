#!/usr/bin/env python3
"""
水下微距画廊 — 统一构建管线
==========================

将所有数据源（原图 → 元数据 → AI标签 → 图片 → JS）串联为一条命令。

完整流程（9步）：
  python rebuild.py              # 全量构建
  python rebuild.py --quick      # 快速模式（跳过AI，仅更新JS+图片）
  python rebuild.py --dry-run    # 预览会做什么，不实际执行
  python rebuild.py --step 3     # 只执行第3步（generate thumbnails）

当你添加新照片时：
  1. 将新 JPG 文件放入 /Volumes/IRIS/2026/已修图/
  2. 运行 python rebuild.py --new-only
  3. 或运行 python rebuild.py 全量重建

步骤说明：
  [1] extract_metadata    — 从原图EXIF提取拍摄参数 → data/photos_metadata.json
  [2] tag_pipeline        — AI视觉模型识别物种/色彩/行为 → 更新metadata
  [3] poetic_titles       — AI生成诗意标题 → 更新metadata
  [4] generate_thumbnails — 生成缩略图+展示图(WebP) → web/images/
  [5] data_to_js          — metadata → web/gallery-data.js (首页画廊数据)
  [6] build_stories       — metadata → web/stories-data.js (故事线)
  [7] build_photo_kb      — metadata → web/photo_kb.js (AI对话知识库)
"""

import os
import sys
import subprocess
import json
import argparse
from datetime import datetime

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPTS_DIR)
METADATA_JSON = os.path.join(PROJECT_DIR, "data", "photos_metadata.json")

STEPS = {
    1: {"name": "extract_metadata", "script": "extract_metadata.py",
        "desc": "从原图EXIF提取拍摄参数"},
    2: {"name": "tag_pipeline", "script": "tag_pipeline.py",
        "desc": "AI视觉模型识别物种/色彩/行为"},
    3: {"name": "poetic_titles", "script": "poetic_titles.py",
        "desc": "AI生成诗意标题"},
    4: {"name": "generate_thumbnails", "script": "generate_thumbnails.py",
        "desc": "生成缩略图+展示图(WebP)"},
    5: {"name": "data_to_js", "script": "data_to_js.py",
        "desc": "生成web/gallery-data.js"},
    6: {"name": "build_stories", "script": "build_stories.py",
        "desc": "生成web/stories-data.js"},
    7: {"name": "build_photo_kb", "script": "build_photo_kb.py",
        "desc": "生成web/photo_kb.js"},
}


def run_step(step_id, script_name, extra_args=None):
    """运行单个构建步骤"""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    if not os.path.exists(script_path):
        print(f"  ⚠️  脚本不存在: {script_path}")
        return False

    cmd = [sys.executable, script_path]
    if extra_args:
        cmd.extend(extra_args)

    print(f"\n{'='*60}")
    print(f"🔧 [{step_id}] {STEPS[step_id]['desc']}")
    print(f"📄 {script_name}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(cmd, cwd=SCRIPTS_DIR, capture_output=False)
        if result.returncode != 0:
            print(f"  ❌ 步骤 {step_id} 失败 (exit code {result.returncode})")
            return False
        return True
    except Exception as e:
        print(f"  ❌ 步骤 {step_id} 异常: {e}")
        return False


def load_metadata():
    """加载当前元数据"""
    if os.path.exists(METADATA_JSON):
        with open(METADATA_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"photos": [], "summary": {}}


def main():
    parser = argparse.ArgumentParser(
        description="水下微距画廊 — 统一构建管线",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python rebuild.py              # 全量构建
  python rebuild.py --quick      # 快速模式（跳过AI步骤）
  python rebuild.py --step 5     # 只运行第5步
  python rebuild.py --dry-run    # 预览
        """
    )
    parser.add_argument("--quick", action="store_true",
                       help="快速模式：跳过AI步骤(2,3)，仅更新图片和JS")
    parser.add_argument("--step", type=int, choices=range(1, 8),
                       help="只运行指定步骤")
    parser.add_argument("--dry-run", action="store_true",
                       help="预览模式，不实际执行")
    parser.add_argument("--skip-ai", action="store_true",
                       help="跳过AI相关步骤(2,3)")
    args = parser.parse_args()

    # 确定要执行的步骤
    if args.step:
        steps_to_run = [args.step]
    elif args.quick or args.skip_ai:
        steps_to_run = [1, 4, 5, 6, 7]  # 跳过AI步骤
    else:
        steps_to_run = list(range(1, 8))

    # 加载现有元数据用于预览
    data = load_metadata()
    photo_count = len(data.get("photos", []))

    print("🌊 水下微距画廊 — 构建管线")
    print(f"📸 当前照片数：{photo_count}")
    print(f"📋 将执行步骤：{steps_to_run}")
    print(f"⚡ 模式：{'快速(跳过AI)' if args.quick or args.skip_ai else '完整'}")
    print(f"🔍 预览：{'是' if args.dry_run else '否'}")
    print()

    if args.dry_run:
        for sid in steps_to_run:
            step = STEPS[sid]
            print(f"  [{sid}] {step['desc']} → {step['script']}")
        print(f"\n💡 去掉 --dry-run 即可实际执行")
        return

    start_time = datetime.now()
    failed = []

    for sid in steps_to_run:
        success = run_step(sid, STEPS[sid]["script"])
        if not success:
            failed.append(sid)
            if sid <= 2:  # 元数据或标签失败，后续步骤无意义
                print(f"\n⚠️  步骤 {sid} 失败，终止后续步骤")
                break

    elapsed = (datetime.now() - start_time).total_seconds()

    # 汇总
    print(f"\n{'='*60}")
    print(f"🏁 构建完成 ({elapsed:.1f}s)")
    if failed:
        print(f"❌ 失败的步骤：{failed}")
    else:
        print("✅ 所有步骤成功！")
        # 重新统计
        data = load_metadata()
        new_count = len(data.get("photos", []))
        print(f"📸 当前照片总数：{new_count}")
        print(f"\n📁 输出文件：")
        print(f"   web/gallery-data.js  — 首页画廊数据")
        print(f"   web/stories-data.js  — 故事线")
        print(f"   web/photo_kb.js      — AI对话知识库")
        print(f"   web/images/          — 缩略图+展示图")


if __name__ == "__main__":
    main()
