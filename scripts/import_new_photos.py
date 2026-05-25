#!/usr/bin/env python3
"""
从硬盘导入新照片到画廊
- 从 /Volumes/IRIS/水摄已修图 读取 183 张新照片
- 提取 EXIF 元数据
- 追加到 data/photos_metadata.json（保留已有数据）
- 拷贝照片到项目 docs/images/ 目录
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# 路径配置
SOURCE_DIR = "/Volumes/IRIS/水摄已修图"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_JSON = os.path.join(PROJECT_ROOT, "data", "photos_metadata.json")
FULL_IMG_DIR = os.path.join(PROJECT_ROOT, "docs", "images", "full")
THUMB_IMG_DIR = os.path.join(PROJECT_ROOT, "docs", "images", "thumbnails")

KNOWN_LOCATION = {
    "country": "Indonesia",
    "region": "Bali",
    "site": "Tulamben",
    "site_cn": "图蓝本",
    "notes": "世界级微距潜点"
}

KEY_TAGS = [
    "Make", "Model", "DateTimeOriginal", "ISOSpeedRatings",
    "FNumber", "ExposureTime", "FocalLength", "FocalLengthIn35mmFilm",
    "LensModel", "Flash", "WhiteBalance", "MeteringMode",
    "ExposureProgram", "ExposureBiasValue", "ApertureValue",
    "ShutterSpeedValue", "ImageWidth", "ImageLength",
]


def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return str(val)


def extract_exif(filepath):
    """从单张照片提取 EXIF 数据"""
    img = Image.open(filepath)
    w, h = img.size
    filesize = os.path.getsize(filepath)

    meta = {
        "file_size_mb": round(filesize / (1024 * 1024), 2),
        "width": w,
        "height": h,
        "aspect_ratio": f"{w}:{h}",
    }

    exif_data = img._getexif()
    if not exif_data:
        return meta

    for tag_id, value in exif_data.items():
        tag_name = TAGS.get(tag_id, str(tag_id))

        if tag_name in KEY_TAGS:
            if tag_name == "FNumber":
                meta["f_number"] = safe_float(value)
            elif tag_name == "ExposureTime":
                meta["exposure_time"] = str(value)
            elif tag_name == "FocalLength":
                meta["focal_length"] = str(value)
            elif tag_name == "FocalLengthIn35mmFilm":
                meta["focal_length_35mm"] = str(value)
            elif tag_name == "ISOSpeedRatings":
                meta["iso"] = int(value) if isinstance(value, (int, float)) else str(value)
            elif tag_name == "Flash":
                flash_map = {0: "未触发", 1: "触发", 9: "触发(外闪)", 16: "关闭"}
                meta["flash"] = flash_map.get(int(value) if isinstance(value, (int, float)) else 0, str(value))
            elif tag_name == "DateTimeOriginal":
                meta["datetime_original"] = str(value)
                try:
                    dt = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                    meta["date"] = dt.strftime("%Y-%m-%d")
                    meta["time"] = dt.strftime("%H:%M:%S")
                except ValueError:
                    pass
            elif tag_name == "Make":
                meta["make"] = str(value)
            elif tag_name == "Model":
                meta["model"] = str(value)
            elif tag_name == "LensModel":
                meta["lensmodel"] = str(value)
            else:
                meta[tag_name.lower()] = str(value)

    # 生成相机+镜头描述
    make = meta.get("make", "")
    model = meta.get("model", "")
    lens = meta.get("lensmodel", "")
    meta["camera"] = f"{make} {model}".strip()
    meta["lens"] = lens

    return meta


def main():
    os.makedirs(FULL_IMG_DIR, exist_ok=True)
    os.makedirs(THUMB_IMG_DIR, exist_ok=True)

    # 读取现有 metadata
    with open(METADATA_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    existing_filenames = {p["filename"] for p in data["photos"]}

    # 扫描硬盘新照片
    source_files = sorted([
        f for f in os.listdir(SOURCE_DIR)
        if not f.startswith("._") and f.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))
    ])

    new_photos = []
    copied = 0
    errors = []

    for fname in source_files:
        if fname in existing_filenames:
            print(f"  ⏭ 跳过(已存在): {fname}")
            continue

        src_path = os.path.join(SOURCE_DIR, fname)
        dst_fname = fname  # 保持原始文件名
        dst_path = os.path.join(FULL_IMG_DIR, dst_fname)

        try:
            # 拷贝照片
            shutil.copy2(src_path, dst_path)

            # 提取EXIF
            meta = extract_exif(dst_path)

            # 补充地点信息
            if "date" not in meta:
                meta["date"] = "2026-02"

            photo_entry = {
                "filename": dst_fname,
                "file_size_mb": meta.get("file_size_mb", 0),
                "width": meta.get("width", 0),
                "height": meta.get("height", 0),
                "aspect_ratio": meta.get("aspect_ratio", ""),
                "date": meta.get("date", "2026-02"),
                "time": meta.get("time", ""),
                "datetime_original": meta.get("datetime_original", ""),
                "make": meta.get("make", ""),
                "model": meta.get("model", ""),
                "camera": meta.get("camera", ""),
                "lens": meta.get("lens", ""),
                "f_number": meta.get("f_number", ""),
                "exposure_time": meta.get("exposure_time", ""),
                "focal_length": meta.get("focal_length", ""),
                "focal_length_35mm": meta.get("focal_length_35mm", ""),
                "iso": meta.get("iso", ""),
                "flash": meta.get("flash", ""),
                "location": KNOWN_LOCATION,
                "ai_tags": {},        # 待AI打标签
                "poetic_title": {},    # 待生成诗意标题
            }

            new_photos.append(photo_entry)
            copied += 1
            if copied <= 5 or copied % 20 == 0:
                print(f"  ✅ [{copied}] {fname}")

        except Exception as e:
            errors.append(f"{fname}: {e}")
            print(f"  ❌ 错误: {fname} - {e}")

    # 追加到 metadata
    data["photos"].extend(new_photos)
    data["total_photos"] = len(data["photos"])
    data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 保存
    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"📸 导入完成!")
    print(f"  原有: {len(existing_filenames)} 张")
    print(f"  新增: {copied} 张")
    print(f"  错误: {len(errors)} 张")
    print(f"  总计: {len(data['photos'])} 张")
    if errors:
        print(f"\n⚠️ 错误详情:")
        for e in errors:
            print(f"  - {e}")


if __name__ == "__main__":
    main()
