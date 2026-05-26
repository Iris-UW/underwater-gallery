#!/usr/bin/env python3
"""
从照片元数据自动生成故事线分组。
模仿 Apple Photos Memories 的逻辑：
- 按日期聚类（连续拍摄日 → "旅程"）
- 按物种分类（同类生物 → "图鉴"）
- 按色彩主题（主色调 → "色韵"）
- 按相机（器材 → "视角"）
"""

import json, os
from datetime import datetime, timedelta
from collections import defaultdict

METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
STORIES_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "stories.json")
CURATION_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "curation.json")


def load_photos():
    with open(METADATA_JSON) as f:
        return json.load(f)["photos"]


def load_curation():
    """Load manual curation config. Returns list of curated story dicts."""
    if not os.path.exists(CURATION_JSON):
        return []
    with open(CURATION_JSON) as f:
        data = json.load(f)
    return data.get("curated_stories", [])


def photo_by_filename(photos, filename):
    """Find a photo dict by filename."""
    for p in photos:
        if p["filename"] == filename:
            return p
    return None


def find_thumbnail(p):
    base = os.path.splitext(p["filename"])[0]
    return f"images/thumbnails/{base}.webp"


def find_full(p):
    base = os.path.splitext(p["filename"])[0]
    return f"images/full/{base}.webp"


def build_stories(photos):
    stories = []

    # ===== 0. 手动策展故事（优先，排在前面）=====
    curated = load_curation()
    curated_ids = set()
    for cs in curated:
        cid = cs.get("id", "")
        curated_ids.add(cid)
        # Resolve photo objects from filenames
        photo_fnames = cs.get("photo_filenames", [])
        story_photos = [photo_by_filename(photos, fn) for fn in photo_fnames]
        story_photos = [p for p in story_photos if p is not None]

        if len(story_photos) < 2:
            print(f"  ⚠️  Curated story '{cid}' has <2 valid photos, skipping")
            continue

        cover_fn = cs.get("cover_filename", "")
        cover = photo_by_filename(photos, cover_fn) if cover_fn else story_photos[0]
        if not cover:
            cover = story_photos[0]

        stories.append({
            "id": cid,
            "type": cs.get("type", "curated"),
            "priority": cs.get("priority", 99),
            "title_en": cs.get("title_en", ""),
            "title_zh": cs.get("title_zh", ""),
            "title_ja": cs.get("title_ja", ""),
            "subtitle_en": cs.get("subtitle_en", ""),
            "subtitle_zh": cs.get("subtitle_zh", ""),
            "subtitle_ja": cs.get("subtitle_ja", ""),
            "narrative_en": cs.get("narrative_en", ""),
            "narrative_zh": cs.get("narrative_zh", ""),
            "narrative_ja": cs.get("narrative_ja", ""),
            "cover": find_full(cover),
            "cover_thumb": find_thumbnail(cover),
            "photo_count": len(story_photos),
            "photos": [{
                "filename": p["filename"],
                "full": find_full(p),
                "thumb": find_thumbnail(p),
                "date": p.get("date", ""),
                "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                "species": (p.get("ai_tags") or {}).get("species_cn", ""),
                "category": (p.get("ai_tags") or {}).get("category", ""),
                "colors": (p.get("ai_tags") or {}).get("primary_colors", []),
            } for p in story_photos]
        })
        print(f"  ✅ Curated: {cid} ({len(story_photos)} photos)")

    # 从第一张照片提取地点信息
    first_photo = photos[0] if photos else {}
    loc = first_photo.get("location", {})
    site_en = loc.get("site", "Tulamben")
    site_cn = loc.get("site_cn", "图蓝本")
    site_ja = loc.get("site_ja", "トゥランベン")

    # ===== 1. 时间线故事：按拍摄日分组 =====
    days = defaultdict(list)
    for p in photos:
        date = p.get("date", "")
        if date:
            days[date].append(p)
    
    sorted_days = sorted(days.keys())
    
    # 找出连续日期段
    date_ranges = []
    if sorted_days:
        start = sorted_days[0]
        end = sorted_days[0]
        for d in sorted_days[1:]:
            try:
                prev = datetime.strptime(end, "%Y-%m-%d")
                curr = datetime.strptime(d, "%Y-%m-%d")
                if (curr - prev).days <= 1:
                    end = d
                else:
                    date_ranges.append((start, end))
                    start = d
                    end = d
            except:
                date_ranges.append((start, end))
                start = d
                end = d
        date_ranges.append((start, end))

    # Helper: date range to month description
    def month_desc(start, end):
        """Convert date range to poetic month description like '4月', '4~5月'"""
        sm, sy = int(start[5:7]), start[:4]
        em, ey = int(end[5:7]), end[:4]
        if sy != ey:
            en_months = [datetime(2000, sm, 1).strftime('%B')]
            en_months.append(f"{datetime(2000, em, 1).strftime('%B')} {ey}")
            cn_months = f"{sy}年{sm}月~{ey}年{em}月"
        elif sm == em:
            en_months = [datetime(2000, sm, 1).strftime('%B')]
            cn_months = f"{sm}月"
        else:
            en_months = [f"{datetime(2000, sm, 1).strftime('%B')}-{datetime(2000, em, 1).strftime('%B')}"]
            cn_months = f"{sm}~{em}月"
        en_month = ' '.join(en_months)
        # Japanese month names
        ja_names = {1:'1月',2:'2月',3:'3月',4:'4月',5:'5月',6:'6月',
                    7:'7月',8:'8月',9:'9月',10:'10月',11:'11月',12:'12月'}
        ja_month = ja_names[sm] if sm == em else f"{ja_names[sm]}〜{ja_names[em]}"
        return en_month, cn_months, ja_month

    # Track same-month journeys to differentiate (only add seq if dupes exist)
    month_order = {}  # key -> list of (start, end) in order
    for start, end in date_ranges:
        sm = int(start[5:7])
        em = int(end[5:7])
        key = (sm, em)
        if key not in month_order:
            month_order[key] = []
        month_order[key].append((start, end))
    
    # Build journey titles with proper sequencing
    journey_titles = []
    month_seq = {}  # key -> current occurrence counter
    for start, end in date_ranges:
        sm = int(start[5:7])
        em = int(end[5:7])
        key = (sm, em)
        duplicates = len(month_order[key])
        month_seq[key] = month_seq.get(key, 0) + 1
        seq_num = month_seq[key]
        
        en_m, cn_m, ja_m = month_desc(start, end)
        
        if duplicates > 1 and seq_num > 1:
            seq_en = [" II"," III"," IV"," V"][seq_num-2] if seq_num <= 5 else f" #{seq_num}"
            seq_zh = ["其二","其三","其四","其五"][seq_num-2] if seq_num <= 5 else f"·{seq_num}"
            seq_ja = ["其の二","其の三","其の四","其の五"][seq_num-2] if seq_num <= 5 else f" #{seq_num}"
        else:
            seq_en = seq_zh = seq_ja = ""
        journey_titles.append((en_m, cn_m, ja_m, seq_en, seq_zh, seq_ja))

    # 为每个连续日期段创建一个故事
    for idx, (start, end) in enumerate(date_ranges):
        story_photos = []
        for d in sorted_days:
            if start <= d <= end:
                story_photos.extend(days[d])
        # 按日期排序
        story_photos.sort(key=lambda p: p.get("date", ""))
        
        if len(story_photos) >= 3:  # 至少3张才叫故事
            cover = story_photos[0]
            day_count = len(set(p.get("date", "") for p in story_photos))
            en_m, cn_m, ja_m, seq_en, seq_zh, seq_ja = journey_titles[idx]
            stories.append({
                "id": f"journey-{idx+1}",
                "type": "journey",
                "title_en": f"{site_en}: {en_m} Journey{seq_en}",
                "title_zh": f"{site_cn}·{cn_m}之旅{seq_zh}",
                "title_ja": f"{site_ja}·{ja_m}の旅{seq_ja}",
                "subtitle_en": f"{day_count} days, {len(story_photos)} moments",
                "subtitle_zh": f"{day_count}天，{len(story_photos)}个瞬间",
                "subtitle_ja": f"{day_count}日間、{len(story_photos)}の瞬間",
                "cover": find_full(cover),
                "cover_thumb": find_thumbnail(cover),
                "photo_count": len(story_photos),
                "photos": [{
                    "filename": p["filename"],
                    "full": find_full(p),
                    "thumb": find_thumbnail(p),
                    "date": p.get("date", ""),
                    "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                    "species": (p.get("ai_tags") or {}).get("species_cn", ""),
                    "category": (p.get("ai_tags") or {}).get("category", ""),
                    "colors": (p.get("ai_tags") or {}).get("primary_colors", []),
                } for p in story_photos]
            })

    # ===== 2. 物种图鉴 =====
    categories = defaultdict(list)
    for p in photos:
        cat = (p.get("ai_tags") or {}).get("category", "其他")
        categories[cat].append(p)

    category_config = {
        "海兔": {"icon": "🐌", "title_en": "The Nudibranch Ballet", "title_zh": "海兔图鉴", "title_ja": "ウミウシ図鑑",
                 "desc_en": "A kaleidoscope of sea slugs, each a tiny masterpiece of evolution",
                 "desc_zh": "万花筒般的海蛞蝓，每一只都是进化的微缩杰作",
                 "desc_ja": "万華鏡のようなウミウシたち、それぞれが進化の小さな傑作"},
        "鱼": {"icon": "🐠", "title_en": "Fish Portraits", "title_zh": "鱼类肖像", "title_ja": "魚のポートレート",
               "desc_en": "From clownfish to frogfish, the characters of the reef",
               "desc_zh": "从小丑鱼到青蛙鱼，珊瑚礁的角色们",
               "desc_ja": "クマノミからカエルアンコウまで、サンゴ礁の住人たち"},
        "虾": {"icon": "🦐", "title_en": "Shrimp Encounters", "title_zh": "虾遇", "title_ja": "エビとの出会い",
               "desc_en": "Tiny emperors and dancers of the deep",
               "desc_zh": "深蓝中的小小帝王与舞者",
               "desc_ja": "深海の小さな皇帝と踊り子たち"},
        "螃蟹": {"icon": "🦀", "title_en": "Crab Chronicles", "title_zh": "蟹行记", "title_ja": "カニの記録",
                 "desc_en": "Armored wanderers of coral castles",
                 "desc_zh": "珊瑚城堡中的盔甲漫游者",
                 "desc_ja": "サンゴの城を歩く鎧の旅人"},
        "头足类": {"icon": "🐙", "title_en": "Cephalopod Whispers", "title_zh": "头足密语", "title_ja": "頭足類のささやき",
                   "desc_en": "Masters of disguise in the blue",
                   "desc_zh": "蔚蓝中的伪装大师",
                   "desc_ja": "青の中の変装の達人"},
        "珊瑚": {"icon": "🪸", "title_en": "Coral Gardens", "title_zh": "珊瑚花园", "title_ja": "サンゴの庭",
                 "desc_en": "The living architecture of the ocean",
                 "desc_zh": "海洋的活体建筑",
                 "desc_ja": "海の生きた建築"},
        "其他": {"icon": "🔍", "title_en": "Mysteries of the Deep", "title_zh": "深海之谜", "title_ja": "深海の謎",
                 "desc_en": "Unidentified wonders beneath the surface",
                 "desc_zh": "水面之下的未解奇观",
                 "desc_ja": "水面下の未確認の驚異"},
    }

    for cat, cat_photos in sorted(categories.items(), key=lambda x: -len(x[1])):
        if len(cat_photos) < 2:
            continue
        cfg = category_config.get(cat, category_config["其他"])
        cat_photos.sort(key=lambda p: p.get("date", ""))
        cover = cat_photos[len(cat_photos)//2]  # 取中间那张做封面
        stories.append({
            "id": f"category-{cat}",
            "type": "category",
            "icon": cfg["icon"],
            "title_en": cfg["title_en"],
            "title_zh": cfg["title_zh"],
            "title_ja": cfg["title_ja"],
            "subtitle_en": cfg["desc_en"],
            "subtitle_zh": cfg["desc_zh"],
            "subtitle_ja": cfg["desc_ja"],
            "cover": find_full(cover),
            "cover_thumb": find_thumbnail(cover),
            "photo_count": len(cat_photos),
            "photos": [{
                "filename": p["filename"],
                "full": find_full(p),
                "thumb": find_thumbnail(p),
                "date": p.get("date", ""),
                "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                "species": (p.get("ai_tags") or {}).get("species_cn", ""),
                "category": cat,
                "colors": (p.get("ai_tags") or {}).get("primary_colors", []),
            } for p in cat_photos]
        })

    # ===== 3. 色彩故事 =====
    color_map = {
        "蓝色": {"en": "Blue", "zh": "蓝", "ja": "青"},
        "蓝": {"en": "Blue", "zh": "蓝", "ja": "青"},
        "橙色": {"en": "Orange", "zh": "橙", "ja": "オレンジ"},
        "橙": {"en": "Orange", "zh": "橙", "ja": "オレンジ"},
        "紫色": {"en": "Purple", "zh": "紫", "ja": "紫"},
        "紫": {"en": "Purple", "zh": "紫", "ja": "紫"},
        "红色": {"en": "Red", "zh": "红", "ja": "赤"},
        "红": {"en": "Red", "zh": "红", "ja": "赤"},
        "黄色": {"en": "Yellow", "zh": "黄", "ja": "黄色"},
        "黄": {"en": "Yellow", "zh": "黄", "ja": "黄色"},
        "黑色": {"en": "Black", "zh": "黑", "ja": "黒"},
        "黑": {"en": "Black", "zh": "黑", "ja": "黒"},
        "白色": {"en": "White", "zh": "白", "ja": "白"},
        "白": {"en": "White", "zh": "白", "ja": "白"},
        "绿色": {"en": "Green", "zh": "绿", "ja": "緑"},
        "绿": {"en": "Green", "zh": "绿", "ja": "緑"},
        "粉色": {"en": "Pink", "zh": "粉", "ja": "ピンク"},
        "粉": {"en": "Pink", "zh": "粉", "ja": "ピンク"},
    }

    color_groups = defaultdict(list)
    for p in photos:
        colors = (p.get("ai_tags") or {}).get("primary_colors", [])
        for c in colors:
            mapped = color_map.get(c, {})
            if mapped:
                color_groups[mapped["en"]].append((p, c))
    
    for color_name, color_photos in sorted(color_groups.items(), key=lambda x: -len(x[1])):
        if len(color_photos) < 2:
            continue
        photos_only = [cp[0] for cp in color_photos]
        photos_only.sort(key=lambda p: p.get("date", ""))
        cover = photos_only[0]
        stories.append({
            "id": f"color-{color_name.lower()}",
            "type": "color",
            "color_name": color_name,
            "title_en": f"{color_name} Symphony",
            "title_zh": f"{color_name}色韵律",
            "title_ja": f"{color_name}の調べ",
            "subtitle_en": f"{len(color_photos)} moments bathed in {color_name.lower()}",
            "subtitle_zh": f"{len(color_photos)}个{color_name}色瞬间",
            "subtitle_ja": f"{color_name}に染まる{len(color_photos)}の瞬間",
            "cover": find_full(cover),
            "cover_thumb": find_thumbnail(cover),
            "photo_count": len(color_photos),
            "photos": [{
                "filename": p["filename"],
                "full": find_full(p),
                "thumb": find_thumbnail(p),
                "date": p.get("date", ""),
                "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                "species": (p.get("ai_tags") or {}).get("species_cn", ""),
                "category": (p.get("ai_tags") or {}).get("category", ""),
                "colors": (p.get("ai_tags") or {}).get("primary_colors", []),
            } for p in photos_only]
        })

    # ===== 4. 相机视角 =====
    olympus = [p for p in photos if "OLYMPUS" in str(p.get("camera_info", {}).get("camera", ""))]
    sony = [p for p in photos if "SONY" in str(p.get("camera_info", {}).get("camera", "")).upper() or "ILCE" in str(p.get("camera_info", {}).get("camera", ""))]
    
    if olympus and sony:
        stories.append({
            "id": "camera-dual",
            "type": "camera",
            "title_en": "Two Cameras, One Ocean",
            "title_zh": "两台相机，一片海",
            "title_ja": "二つのカメラ、一つの海",
            "subtitle_en": f"Olympus E-M1 II ({len(olympus)} shots) × Sony A7R IV ({len(sony)} shots)",
            "subtitle_zh": f"奥林巴斯 E-M1 II（{len(olympus)}张）× 索尼 A7R IV（{len(sony)}张）",
            "subtitle_ja": f"オリンパス E-M1 II（{len(olympus)}枚）× ソニー A7R IV（{len(sony)}枚）",
            "cover": find_full(olympus[0]),
            "cover_thumb": find_thumbnail(olympus[0]),
            "photo_count": len(olympus) + len(sony),
            "sections": [
                {
                    "label_en": "Olympus",
                    "label_zh": "奥林巴斯",
                    "label_ja": "オリンパス",
                    "photos": [{
                        "filename": p["filename"],
                        "full": find_full(p),
                        "thumb": find_thumbnail(p),
                        "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                    } for p in olympus]
                },
                {
                    "label_en": "Sony",
                    "label_zh": "索尼",
                    "label_ja": "ソニー",
                    "photos": [{
                        "filename": p["filename"],
                        "full": find_full(p),
                        "thumb": find_thumbnail(p),
                        "title": (p.get("ai_tags") or {}).get("poetic_title", ""),
                    } for p in sony]
                }
            ]
        })

    # ===== 5. 按 priority 排序 =====
    stories.sort(key=lambda s: s.get("priority", 99))

    return stories


def main():
    photos = load_photos()
    stories = build_stories(photos)

    with open(STORIES_JSON, "w") as f:
        json.dump({"stories": stories, "generated_at": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

    print(f"📖 生成了 {len(stories)} 个故事线（含手动策展）：")
    for s in stories:
        print(f"  [{s['type']}] {s.get('title_zh', s.get('title_en',''))} ({s['photo_count']}张)")

    # 也输出一个纯JS版本方便嵌入HTML
    js_path = os.path.join(os.path.dirname(__file__), "..", "docs", "stories-data.js")
    with open(js_path, "w") as f:
        f.write(f"// Auto-generated stories data\nconst STORIES = {json.dumps(stories, ensure_ascii=False, indent=2)};\n")
    print(f"📄 JS数据已写入 {js_path}")


if __name__ == "__main__":
    main()
