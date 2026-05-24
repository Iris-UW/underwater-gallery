#!/usr/bin/env python3
"""
水下微距照片元数据批量提取工具
从 EXIF 提取拍摄参数、时间、设备信息，输出结构化 JSON
"""

import os
import json
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


PHOTO_DIR = "/Volumes/IRIS/2026/已修图"
OUTPUT_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
KNOWN_LOCATION = {
    "country": "Indonesia",
    "region": "Bali",
    "site": "Tulamben",
    "site_cn": "图蓝本",
    "notes": "世界级微距潜点，自由号沉船 + 垃圾潜水"
}

# 关注的关键 EXIF 标签
KEY_TAGS = [
    "Make", "Model", "DateTimeOriginal", "ISOSpeedRatings",
    "FNumber", "ExposureTime", "FocalLength", "FocalLengthIn35mmFilm",
    "LensModel", "Flash", "WhiteBalance", "MeteringMode",
    "ExposureProgram", "ExposureBiasValue", "ApertureValue",
    "ShutterSpeedValue", "ImageWidth", "ImageLength",
]


def parse_gps(gps_info):
    """解析 GPS 信息（如果有的话）"""
    if not gps_info:
        return None
    gps = {}
    for key, value in gps_info.items():
        tag = GPSTAGS.get(key, str(key))
        gps[tag] = str(value)
    return gps


def safe_float(val):
    """安全转换为浮点数"""
    try:
        return float(val)
    except (TypeError, ValueError):
        return str(val)


def extract_exif(filepath):
    """从单张照片提取所有关键 EXIF 数据"""
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

        if tag_name == "GPSInfo":
            gps = parse_gps(value)
            if gps:
                meta["gps"] = gps
        elif tag_name in KEY_TAGS:
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
                # Flash: 0=未触发, 1=触发, 9=触发+返回光检测, 16=关闭
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
            else:
                meta[tag_name.lower()] = str(value)

    return meta


def format_camera(meta):
    """生成相机+镜头的可读描述"""
    make = meta.get("make", "")
    model = meta.get("model", "")
    lens = meta.get("lensmodel", "")
    camera = f"{make} {model}".strip()
    return {"camera": camera, "lens": lens}


def main():
    photos = []

    for fname in sorted(os.listdir(PHOTO_DIR)):
        if fname.startswith(".") or fname == "无水印":
            continue
        if not fname.lower().endswith((".jpg", ".jpeg")):
            continue

        fpath = os.path.join(PHOTO_DIR, fname)
        try:
            meta = extract_exif(fpath)
        except Exception as e:
            meta = {"error": str(e)}

        # 从文件名提取日期（当 EXIF 日期缺失时备用）
        if "date" not in meta:
            basename = os.path.splitext(fname)[0]
            parts = basename.split("-")
            if len(parts) >= 1 and len(parts[0]) == 8:
                try:
                    dt = datetime.strptime(parts[0], "%Y%m%d")
                    meta["date"] = dt.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        # 添加文件名和路径
        meta["filename"] = fname
        meta["camera_info"] = format_camera(meta)
        meta["location"] = KNOWN_LOCATION

        # 留空 AI 标签字段，后续由标签管线填充
        meta["ai_tags"] = {
            "species_cn": "",
            "species_latin": "",
            "category": "",         # 鱼 / 海兔 / 虾 / 螃蟹 / 其他
            "primary_colors": [],   # ["蓝紫", "橙黄"]
            "behavior": "",         # 产卵, 进食, 拟态, 游动, 静止
            "composition": "",      # 正面, 侧面, 俯视, 微距特写
            "confidence": 0,
        }

        photos.append(meta)

    # 按日期排序
    photos.sort(key=lambda p: p.get("date", "9999-99-99"))

    # 统计摘要
    summary = {
        "total_photos": len(photos),
        "location": KNOWN_LOCATION,
        "date_range": {
            "from": photos[0].get("date") if photos else None,
            "to": photos[-1].get("date") if photos else None,
        },
        "days": len(set(p.get("date") for p in photos if p.get("date"))),
        "cameras": list(set(p.get("camera_info", {}).get("camera", "") for p in photos)),
        "total_size_mb": round(sum(p.get("file_size_mb", 0) for p in photos), 2),
        "file_formats": list(set(os.path.splitext(p["filename"])[1] for p in photos)),
    }

    output = {
        "generated_at": datetime.now().isoformat(),
        "summary": summary,
        "photos": photos,
    }

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ 提取完成：{len(photos)} 张照片")
    print(f"📁 元数据已保存：{OUTPUT_JSON}")
    print(f"\n📊 统计：")
    print(f"  拍摄日期：{summary['date_range']['from']} ～ {summary['date_range']['to']}")
    print(f"  拍摄天数：{summary['days']} 天")
    print(f"  使用相机：{', '.join(summary['cameras'])}")
    print(f"  总文件大小：{summary['total_size_mb']} MB")


if __name__ == "__main__":
    main()
