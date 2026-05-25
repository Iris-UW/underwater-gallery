#!/usr/bin/env python3
"""
水下微距 AI 自动标签管线
对接视觉模型（Claude Vision / GPT-4V），对每张照片自动识别：
  - 物种（中文名 + 拉丁学名）
  - 生物分类（鱼/海兔/虾/螃蟹/其他）
  - 主色调（多色标签）
  - 行为状态
  - 构图类型

用法：
  python tag_pipeline.py              # 全量打标签
  python tag_pipeline.py --dry-run    # 预览待处理的照片
  python tag_pipeline.py --limit 5    # 只处理前5张测试
"""

import json
import os
import sys
import time
import base64
from datetime import datetime
from pathlib import Path


# ===================== 配置区 =====================
PHOTO_DIR = "/Volumes/IRIS/2026/已修图"
LOCAL_WEBP_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "images", "full")
METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
OUTPUT_JSON = METADATA_JSON  # 原地更新

# 图蓝本常见物种知识库（用于提示模型精细识别）
TULAMBEN_SPECIES_CONTEXT = """
印尼巴厘岛图蓝本（Tulamben, Bali）是世界级微距潜点。
该海域常见水下生物包括：

【海兔/裸鳃类 Nudibranchia】
- Chromodoris annae（安娜多彩海牛）
- Chromodoris elisabethina（伊丽莎白多彩海牛）
- Hypselodoris bullocki（紫海牛）
- Phyllidia varicosa（疣状叶海牛）
- Phyllidiella pustulosa（丘疹叶海牛）
- Jorunna funebris（黑斑鸠海牛）
- Nembrotha kubaryana（古巴纳海牛）
- Glossodoris cincta（环纹舌海牛）
- Flabellina 属（翅膀海牛）

【虾类 Caridea/Stenopodidea】
- 美人虾（Stenopus hispidus）
- 海葵虾（Periclimenes 属）
- 清洁虾（Lysmata amboinensis）
- 帝王虾（Periclimenes imperator）

【蟹类 Brachyura/Anomura】
- 箭蟹（Stenorhynchus 属）
- 瓷蟹（Neopetrolisthes 属）
- 软珊瑚蟹（Hoplophrys oatesi）
- 装饰蟹（Camposcia retusa）

【鱼类】
- 小丑鱼（Amphiprion 属）
- 虾虎鱼（Gobiidae）
- 䲟鱼（Blenniidae）
- 青蛙鱼（Antennariidae）
- 海马（Hippocampus 属）
- 鬼龙/海龙（Solenostomus 属）

【头足类】
- 火焰乌贼（Metasepia pfefferi）
- 拟态章鱼（Thaumoctopus mimicus）
- 蓝环章鱼（Hapalochlaena 属）
"""

SYSTEM_PROMPT = f"""你是一位海洋生物学专家，擅长识别水下微距摄影中的生物物种。

{TULAMBEN_SPECIES_CONTEXT}

请分析这张水下微距照片，以 JSON 格式返回以下字段：
{{
  "species_cn": "中文俗名（如：安娜多彩海牛）",
  "species_latin": "拉丁学名（如：Chromodoris annae）",
  "category": "鱼 / 海兔 / 海牛 / 虾 / 螃蟹 / 头足类 / 珊瑚 / 海葵 / 其他",
  "primary_colors": ["主色1", "主色2"],
  "behavior": "游动 / 静止 / 进食 / 产卵 / 拟态 / 防御 / 求偶 / 其他",
  "composition": "正面 / 侧面 / 俯视 / 特写 / 环境 / 其他",
  "confidence": 0.0-1.0之间的信心值,
  "notes": "简短补充说明"
}}

注意：
- 如果无法确定具体物种，填写大类 + 描述性特征（如"橙色海兔，疑似Chromodoris属"）
- 颜色使用中文描述，如"蓝紫""荧光橙""半透明白""墨黑""金黄"
- category 只能从给定选项中选择"""


def encode_image_base64(filepath):
    """将图片编码为 base64"""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def call_vision_api(image_path, api_provider="anthropic"):
    """
    调用视觉模型 API

    目前支持两种模式：
    1. api_provider="anthropic" — 需要设置 ANTHROPIC_API_KEY 环境变量
    2. api_provider="openai"    — 需要设置 OPENAI_API_KEY 环境变量
    3. api_provider="manual"    — 模拟返回，留空让用户手动填
    """
    if api_provider == "manual":
        # 模拟返回，供手动标注使用
        return {
            "species_cn": "",
            "species_latin": "",
            "category": "",
            "primary_colors": [],
            "behavior": "",
            "composition": "",
            "confidence": 0,
            "notes": "手动标注模式，请自行填写"
        }

    image_b64 = encode_image_base64(image_path)
    ext = os.path.splitext(image_path)[1].lower().replace(".", "")
    mime = f"image/{ext}" if ext in ("jpg", "jpeg", "png") else "image/jpeg"

    if api_provider == "anthropic":
        try:
            import anthropic
            client = anthropic.Anthropic()
            resp = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": mime, "data": image_b64}},
                        {"type": "text", "text": "请识别这张水下微距照片中的生物。"}
                    ]
                }]
            )
            # 提取 JSON
            text = resp.content[0].text
            # 尝试提取花括号内的 JSON
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"error": "无法解析模型响应", "raw": text}

        except ImportError:
            print("⚠️  未安装 anthropic 库，请运行: pip install anthropic")
            sys.exit(1)
        except Exception as e:
            return {"error": str(e)}

    elif api_provider in ("openai", "openrouter"):
        try:
            import openai
            if api_provider == "openrouter":
                client = openai.OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={
                        "HTTP-Referer": "https://iris-underwater.vercel.app",
                        "X-Title": "Iris Underwater Macro"
                    }
                )
                model = "openai/gpt-4o"
            else:
                client = openai.OpenAI()
                model = "gpt-4o"

            resp = client.chat.completions.create(
                model=model,
                messages=[{
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }, {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{image_b64}"}},
                        {"type": "text", "text": "请识别这张水下微距照片中的生物。"}
                    ]
                }],
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            return json.loads(resp.choices[0].message.content)
        except ImportError:
            print("⚠️  未安装 openai 库，请运行: pip install openai")
            sys.exit(1)
        except Exception as e:
            return {"error": str(e)}

    else:
        raise ValueError(f"不支持的 API 提供商: {api_provider}")


def process_photos(limit=None, dry_run=False, api="manual"):
    """主处理流程"""
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    photos = data["photos"]

    # 筛选需要打标签的照片（ai_tags 为空的）
    to_process = [
        p for p in photos
        if not p.get("ai_tags", {}).get("species_cn")
    ]

    if limit:
        to_process = to_process[:limit]

    print(f"📸 共 {len(photos)} 张照片，{len(to_process)} 张待打标签\n")

    if dry_run:
        for p in to_process:
            print(f"  [{p.get('date', '?')}] {p['filename']} — {p['file_size_mb']}MB")
        return

    for i, p in enumerate(to_process):
        # 优先本地 WebP 展示图（避免外置硬盘 IO 问题）
        base = os.path.splitext(p["filename"])[0]
        webp_path = os.path.join(LOCAL_WEBP_DIR, base + ".webp")
        raw_path = os.path.join(PHOTO_DIR, p["filename"])

        if os.path.exists(webp_path):
            fpath = webp_path
        elif os.path.exists(raw_path):
            fpath = raw_path
        else:
            print(f"⚠️  跳过（文件不存在）: {p['filename']}")
            continue

        print(f"[{i+1}/{len(to_process)}] {p['filename']} ...", end=" ")

        try:
            tags = call_vision_api(fpath, api_provider=api)
            p["ai_tags"] = tags
            species = tags.get("species_cn", "?")
            cat = tags.get("category", "?")
            conf = tags.get("confidence", 0)
            print(f"✅ {species} ({cat}) 信心:{conf}")
        except Exception as e:
            print(f"❌ {e}")
            p["ai_tags"] = {"error": str(e)}

        # 防止 API 限流
        if api != "manual":
            time.sleep(1)

    # 保存更新
    data["photos"] = photos
    data["last_tagged_at"] = datetime.now().isoformat()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 标签已保存到 {OUTPUT_JSON}")


# ===================== 手动标注辅助 =====================

def manual_tag_editor():
    """交互式手动标注工具"""
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    CATEGORIES = ["鱼", "海兔", "海牛", "虾", "螃蟹", "头足类", "珊瑚", "海葵", "其他"]
    COLORS = ["蓝紫", "荧光橙", "半透明白", "墨黑", "金黄", "粉红", "翠绿", "棕褐",
              "银灰", "乳白", "鲜红", "深蓝", "明黄", "靛青", "橙红", "黑白"]

    for p in data["photos"]:
        if p.get("ai_tags", {}).get("species_cn"):
            continue
        print(f"\n--- {p['filename']} ({p.get('date', '?')}) ---")
        print(f"相机：{p.get('camera_info', {}).get('camera', '?')}")
        print(f"参数：f/{p.get('f_number', '?')}, {p.get('exposure_time', '?')}s, ISO{p.get('iso', '?')}")

        cat = input(f"  分类 [{', '.join(CATEGORIES)}]: ").strip()
        species = input("  物种中文名: ").strip()
        latin = input("  拉丁学名: ").strip()
        colors_raw = input(f"  颜色（逗号分隔，可选: {', '.join(COLORS[:6])}...）: ").strip()
        behavior = input("  行为 [游动/静止/进食/产卵/拟态/其他]: ").strip()

        p["ai_tags"] = {
            "species_cn": species,
            "species_latin": latin,
            "category": cat,
            "primary_colors": [c.strip() for c in colors_raw.split(",") if c.strip()],
            "behavior": behavior,
            "composition": "",
            "confidence": 1.0,
            "notes": "手动标注"
        }

    data["last_tagged_at"] = datetime.now().isoformat()
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ 手动标注已保存")


# ===================== CLI 入口 =====================

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="水下微距 AI 标签管线")
    parser.add_argument("--dry-run", action="store_true", help="预览待处理照片，不实际打标签")
    parser.add_argument("--limit", type=int, help="只处理前 N 张")
    parser.add_argument("--api", choices=["manual", "anthropic", "openai", "openrouter"], default="manual",
                       help="API 提供商（默认 manual 留空模式）")
    parser.add_argument("--manual", action="store_true", help="交互式手动标注")
    args = parser.parse_args()

    if args.manual:
        manual_tag_editor()
    else:
        process_photos(limit=args.limit, dry_run=args.dry_run, api=args.api)
