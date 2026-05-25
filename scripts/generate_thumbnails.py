#!/usr/bin/env python3
"""
生成 Web 优化图片：缩略图(400px) + 展示图(1200px) WebP 格式
"""

import os
import json
from PIL import Image

PHOTO_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "images", "full")
METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
WEB_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "images")
THUMB_DIR = os.path.join(WEB_IMG_DIR, "thumbnails")
FULL_DIR = os.path.join(WEB_IMG_DIR, "full")

THUMB_SIZE = (400, 400)    # 缩略图最大边长
FULL_SIZE = (1400, 1400)   # 展示图最大边长
QUALITY = 82               # WebP 质量


def generate_images():
    os.makedirs(THUMB_DIR, exist_ok=True)
    os.makedirs(FULL_DIR, exist_ok=True)

    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    total = len(data["photos"])
    generated = 0
    errors = 0

    for i, photo in enumerate(data["photos"]):
        fname = photo["filename"]
        fpath = os.path.join(PHOTO_DIR, fname)

        if not os.path.exists(fpath):
            print(f"⚠️  [{i+1}/{total}] 跳过（源文件不存在）: {fname}")
            errors += 1
            continue

        base = os.path.splitext(fname)[0]

        try:
            img = Image.open(fpath)
            # 保留 EXIF 方向
            try:
                from PIL.ImageOps import exif_transpose
                img = exif_transpose(img)
            except Exception:
                pass

            # 转为 RGB（WebP 不支持 CMYK）
            if img.mode in ("RGBA", "LA", "P"):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 缩略图
            thumb = img.copy()
            thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
            thumb_path = os.path.join(THUMB_DIR, f"{base}.webp")
            thumb.save(thumb_path, "WEBP", quality=QUALITY)

            # 展示图
            full = img.copy()
            full.thumbnail(FULL_SIZE, Image.LANCZOS)
            full_path = os.path.join(FULL_DIR, f"{base}.webp")
            full.save(full_path, "WEBP", quality=QUALITY)

            # 更新元数据中的图片路径
            photo["web_paths"] = {
                "thumbnail": f"images/thumbnails/{base}.webp",
                "full": f"images/full/{base}.webp",
            }

            generated += 1
            size_kb = round(os.path.getsize(thumb_path) / 1024, 1)
            print(f"  [{i+1}/{total}] {base} — 缩略图 {size_kb}KB ✅")

        except Exception as e:
            print(f"❌ [{i+1}/{total}] {fname}: {e}")
            errors += 1

    # 更新 metadata
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    total_thumb = sum(
        os.path.getsize(os.path.join(THUMB_DIR, f))
        for f in os.listdir(THUMB_DIR) if f.endswith(".webp")
    )
    total_full = sum(
        os.path.getsize(os.path.join(FULL_DIR, f))
        for f in os.listdir(FULL_DIR) if f.endswith(".webp")
    )

    print(f"\n✅ 完成：{generated} 张成功，{errors} 张失败")
    print(f"📦 缩略图总计：{round(total_thumb / (1024*1024), 2)} MB")
    print(f"📦 展示图总计：{round(total_full / (1024*1024), 2)} MB")


if __name__ == "__main__":
    generate_images()
