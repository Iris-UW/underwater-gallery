#!/usr/bin/env python3
"""
水下微距照片诗意标题生成器
用AI视觉模型为每张照片生成故事化、留白式的标题。

不同于物种标签（"安娜多彩海牛"），诗意标题更像是：
  - "钴蓝蛞蝓的独舞"
  - "橙色迷雾中的信使"
  - "深渊壁纸上的裂缝"
  - 或者干脆空着 —— 留给观者想象

用法：
  python poetic_titles.py --api openrouter    # OpenRouter
  python poetic_titles.py --api openai        # OpenAI直连
  python poetic_titles.py --keep-empty        # 全部留空（极简风格）
  python poetic_titles.py --dry-run           # 预览
"""

import json, os, sys, time, base64, argparse
from datetime import datetime

LOCAL_WEBP_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "images", "full")
METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")

# ===== 提示词：引导AI生成诗意标题 =====
POETIC_PROMPT = """你是一位诗人兼水下摄影师。请为这张水下微距照片生成一个诗意的、留白的标题。

规则：
1. 不要使用生物学名称（不要出现"Chromodoris""海兔""帝王虾"等分类词汇）
2. 标题应该像一首短诗的标题，或者像当代艺术展品的名字
3. 可以基于画面中的颜色、形态、光影、情绪来命名
4. 风格参考："蓝色迷宫里的旅人""橙色火焰的独白""珊瑚暗处的一瞥""无名的庆典"
5. 字数控制在2-8个汉字为佳
6. 如果你觉得画面本身已经足够有力量，可以返回空字符串""，意为"无题"——让观者自行想象
7. 偶尔可以用英文短词，如"Solitude""Drift""Bloom"

返回JSON格式：
{
  "poetic_title": "标题",
  "reason": "简短说明为什么取这个名字（内部使用）"
}"""


def encode_image_base64(filepath):
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_image_path(filename):
    """优先本地WebP，回退到外置硬盘原图"""
    base = os.path.splitext(filename)[0]
    webp = os.path.join(LOCAL_WEBP_DIR, base + ".webp")
    if os.path.exists(webp):
        return webp, "image/webp"
    raw = os.path.join("/Volumes/IRIS/2026/已修图", filename)
    if os.path.exists(raw):
        ext = filename.rsplit(".", 1)[1].lower()
        return raw, f"image/{ext}"
    return None, None


def call_api(image_path, mime, api_provider="openrouter"):
    """调用视觉模型生成诗意标题"""
    img_b64 = encode_image_base64(image_path)

    if api_provider == "openrouter":
        import openai
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://iris-underwater.vercel.app",
                "X-Title": "Iris UW Poetic"
            }
        )
        model = "qwen/qwen2.5-vl-72b-instruct"
    elif api_provider == "openai":
        import openai
        client = openai.OpenAI()
        model = "gpt-4o"
    else:
        raise ValueError(f"不支持的API: {api_provider}")

    resp = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": POETIC_PROMPT},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{img_b64}"}}
            ]
        }],
        max_tokens=200,
    )
    text = resp.choices[0].message.content.strip()
    # Qwen 可能用 markdown 包裹 JSON
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def process_all(api="openrouter", keep_empty=False, limit=None):
    """主处理流程"""
    with open(METADATA_JSON, "r") as f:
        data = json.load(f)

    photos = data["photos"]
    to_process = [
        p for p in photos
        if "poetic_title" not in (p.get("ai_tags") or {})
    ]
    if limit:
        to_process = to_process[:limit]

    print(f"📸 {len(photos)} 张，{len(to_process)} 张待生成诗意标题\n")

    for i, p in enumerate(to_process):
        fpath, mime = get_image_path(p["filename"])
        if not fpath:
            print(f"⚠️  跳过: {p['filename']}")
            continue

        print(f"[{i+1}/{len(to_process)}] {p['filename']} ...", end=" ")

        try:
            result = call_api(fpath, mime, api_provider=api)
            title = result.get("poetic_title", "")
            reason = result.get("reason", "")

            tags = p.get("ai_tags", {})
            tags["poetic_title"] = title
            tags["poetic_reason"] = reason
            p["ai_tags"] = tags

            display = title if title else "「无题」"
            print(f"✨ {display}")

        except Exception as e:
            print(f"❌ {e}")
            tags = p.get("ai_tags", {})
            tags["poetic_title"] = ""
            tags["poetic_error"] = str(e)
            p["ai_tags"] = tags

        if api != "manual":
            time.sleep(1.5)  # 限流间隔

    data["photos"] = photos
    data["poetic_titles_generated_at"] = datetime.now().isoformat()
    with open(METADATA_JSON, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    titled = sum(1 for p in photos if (p.get("ai_tags") or {}).get("poetic_title"))
    untitled = sum(1 for p in photos if (p.get("ai_tags") or {}).get("poetic_title") == "")
    print(f"\n✅ 已生成 {titled} 个诗意标题，{untitled} 张留白（无题）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="水下微距诗意标题生成器")
    parser.add_argument("--api", choices=["openai", "openrouter"], default="openrouter")
    parser.add_argument("--dry-run", action="store_true", help="预览")
    parser.add_argument("--limit", type=int, help="限制数量")
    args = parser.parse_args()

    if args.dry_run:
        with open(METADATA_JSON) as f:
            data = json.load(f)
        photos = data["photos"]
        missing = sum(1 for p in photos if "poetic_title" not in (p.get("ai_tags") or {}))
        print(f"📸 共 {len(photos)} 张，{missing} 张待生成诗意标题")
    else:
        process_all(api=args.api, limit=args.limit)
