#!/usr/bin/env python3
"""
为未翻译的诗意标题生成 EN/JA 翻译（基于规则 + 词典映射）
因为直接调用 OpenAI API 被地区限制，这里用模式匹配完成基础翻译。
"""

import json, os, re

METADATA = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
I18N_JS = os.path.join(os.path.dirname(__file__), "..", "docs", "gallery-i18n.js")

# ---- 词汇映射表 ----
COLOR_MAP = {
    "红": ("Red", "赤"), "橙": ("Orange", "オレンジ"), "黄": ("Yellow", "黄"),
    "绿": ("Green", "緑"), "青": ("Cyan", "青"), "蓝": ("Blue", "青"),
    "紫": ("Purple", "紫"), "黑": ("Black", "黒"), "白": ("White", "白"),
    "金": ("Golden", "金色"), "银": ("Silver", "銀"), "粉": ("Pink", "ピンク"),
    "灰": ("Gray", "灰"), "暗": ("Dark", "暗"), "焕彩": ("Radiant", "光彩"),
    "幽": ("Ethereal", "幽玄"), "深": ("Deep", "深"),
    "橙红": ("Orange-Red", "橙赤"), "红白": ("Red & White", "紅白"),
}

NATURE_MAP = {
    "花": ("Bloom", "花"), "梦": ("Dream", "夢"), "影": ("Shadow", "影"),
    "光": ("Light", "光"), "夜": ("Night", "夜"), "星": ("Star", "星"),
    "月": ("Moon", "月"), "海": ("Sea", "海"), "火": ("Flame", "炎"),
    "风": ("Wind", "風"), "水": ("Water", "水"), "羽": ("Feather", "羽"),
    "翼": ("Wing", "翼"), "眼": ("Eye", "瞳"), "眸": ("Gaze", "眸"),
    "舞": ("Dance", "舞"), "舞者": ("Dancer", "踊り子"),
    "晨曦": ("Dawn", "夜明け"), "晨光": ("Morning Light", "朝光"),
    "夜色": ("Nightfall", "夜色"), "夜幕": ("Nightfall", "夜幕"),
    "深渊": ("Abyss", "深淵"), "深海": ("Deep Sea", "深海"),
    "珊瑚": ("Coral", "珊瑚"), "花园": ("Garden", "庭園"),
    "梦境": ("Dreamscape", "夢境"), "星空": ("Starry Sky", "星空"),
    "宇宙": ("Cosmos", "宇宙"), "触须": ("Tentacle", "触手"),
    "繁星": ("Starlight", "星々"), "星点": ("Stardust", "星屑"),
    "霓虹": ("Neon", "霓虹"), "轮廓": ("Silhouette", "輪郭"),
    "溶洞": ("Cavern", "洞窟"), "洞穴": ("Cave", "洞穴"),
    "泡泡": ("Bubble", "泡"), "气泡": ("Bubble", "泡"),
    "印记": ("Mark", "刻印"), "秘密": ("Secret", "秘密"),
    "谜": ("Mystery", "謎"), "奇观": ("Wonder", "奇観"),
    "纹章": ("Crest", "紋章"), "图案": ("Pattern", "模様"),
    "皇冠": ("Crown", "王冠"), "宝冠": ("Crown", "宝冠"),
    "面具": ("Mask", "仮面"), "假面": ("Mask", "仮面"),
    "隐者": ("Hermit", "隠者"), "守望者": ("Watcher", "見守り者"),
    "守护者": ("Guardian", "守護者"), "画家": ("Painter", "画家"),
    "诗人": ("Poet", "詩人"), "梦游者": ("Sleepwalker", "夢遊者"),
    "猎人": ("Hunter", "狩人"), "漫步者": ("Wanderer", "彷徨者"),
    "宝石": ("Jewel", "宝石"), "宝玉": ("Gem", "宝玉"),
    "烛光": ("Candlelight", "灯火"), "灯火": ("Lamplight", "灯火"),
    "眼睛": ("Eye", "目"), "凝视": ("Gaze", "凝視"),
    "沉思": ("Contemplation", "瞑想"), "静思": ("Quiet Reflection", "静思"),
    "低语": ("Whisper", "囁き"), "轻咏": ("Gentle Song", "詠唱"),
    "韵律": ("Rhythm", "律動"), "绽放": ("Bloom", "開花"),
    "邂逅": ("Encounter", "邂逅"), "遇见": ("Meeting", "出会い"),
    "旅程": ("Journey", "旅"), "行记": ("Travelogue", "旅記録"),
    "肖像": ("Portrait", "肖像"), "图鉴": ("Field Guide", "図鑑"),
    "圆舞": ("Waltz", "円舞"), "芭蕾": ("Ballet", "バレエ"),
    "蓝色精灵": ("Blue Sprite", "青の精霊"), "精灵": ("Sprite", "精霊"),
    "绒羽": ("Down Feather", "綿羽"), "柔羽": ("Soft Feather", "柔羽"),
    "根": ("Root", "根"), "叶": ("Leaf", "葉"),
    "柔": ("Soft", "柔らかい"), "静": ("Quiet", "静か"),
    "安宁": ("Serene", "安寧"), "静谧": ("Tranquil", "静謐"),
    "幽暗": ("Gloom", "暗がり"), "黑暗": ("Darkness", "暗闇"),
    "生灵": ("Creature", "生き物"), "生命": ("Life", "生命"),
}

ACTION_MAP = {
    "轻舞": ("Gentle Dance", "軽やかな舞"), "起舞": ("Rising Dance", "舞い上がる"),
    "漫游": ("Wandering", "彷徨"), "巡游": ("Patrol", "巡回"),
    "漂浮": ("Floating", "漂う"), "漂浮者": ("Floater", "漂う者"),
    "穿行": ("Weaving Through", "縫うように進む"),
    "展开": ("Unfurling", "広がる"), "伸展": ("Stretching", "伸びる"),
    "点缀": ("Adorning", "飾る"), "装饰": ("Decorating", "装飾"),
}

STYLE_MAP = {
    "幻影": ("Phantom", "幻影"), "幻": ("Illusion", "幻"),
    "华丽": ("Gorgeous", "華麗"), "优雅": ("Elegant", "優雅"),
    "神秘": ("Mysterious", "神秘的"), "奇妙": ("Wonderous", "奇妙"),
    "温柔": ("Gentle", "優しい"), "温暖": ("Warm", "温かい"),
    "明亮": ("Bright", "明るい"), "闪耀": ("Shimmering", "煌めく"),
    "透明": ("Translucent", "透明"), "半透明": ("Semi-transparent", "半透明"),
    "微小": ("Tiny", "微小"), "微型": ("Micro", "ミクロ"),
    "帝王": ("Emperor", "皇帝"), "君主": ("Monarch", "君主"),
    "舞者": ("Dancer", "踊り子"), "舞蹈家": ("Dancer", "踊り子"),
}

# ---- 翻译函数 ----
def translate_title(cn_title):
    """基于规则的翻译"""
    cn = cn_title.strip()
    
    # 如果已是英文/日文（不含中文字符），直接返回
    if not re.search(r'[\u4e00-\u9fff]', cn):
        return {"en": cn, "ja": cn}
    
    en_parts = []
    ja_parts = []
    
    # 拆分中文短语（按常见分隔和词边界）
    # 先尝试匹配长词，再匹配短词
    words = []
    i = 0
    while i < len(cn):
        matched = False
        # 尝试最长匹配 (3字 → 2字 → 1字)
        for l in range(min(4, len(cn) - i), 0, -1):
            chunk = cn[i:i+l]
            # 检查所有映射表
            for m in [COLOR_MAP, NATURE_MAP, ACTION_MAP, STYLE_MAP]:
                if chunk in m:
                    words.append(chunk)
                    i += l
                    matched = True
                    break
            if matched:
                break
        if not matched:
            # 单个字符处理
            ch = cn[i]
            found = False
            for m in [COLOR_MAP, NATURE_MAP, ACTION_MAP, STYLE_MAP]:
                if ch in m:
                    words.append(ch)
                    found = True
                    break
            if not found:
                words.append(ch)  # 保留原文
            i += 1
    
    # 翻译每个词
    for w in words:
        translated = False
        for m in [COLOR_MAP, NATURE_MAP, ACTION_MAP, STYLE_MAP]:
            if w in m:
                en_parts.append(m[w][0])
                ja_parts.append(m[w][1])
                translated = True
                break
        
        # 特殊处理 "的" / "之" / "中" / "与" / "里的" / "下的"
        if w in ["的", "之"]:
            en_parts.append("of")
            ja_parts.append("の")
            translated = True
        elif w in ["中", "里", "内的"]:
            en_parts.append("in")
            ja_parts.append("の中の")
            translated = True
        elif w == "与":
            en_parts.append("&")
            ja_parts.append("と")
            translated = True
        elif w in ["下的", "下的"]:
            en_parts.append("beneath")
            ja_parts.append("の下の")
            translated = True
        
        if not translated:
            # 保留原文（用拼音或直译）
            en_parts.append(w)
            ja_parts.append(w)
    
    # 清理英文（调整语序：中文 "X的Y" → 英文 "Y of X"）
    en_result = " ".join(en_parts)
    # 简单后处理
    en_result = en_result.replace("of  ", "of ").replace("  ", " ")
    en_result = en_result.strip()
    
    ja_result = "".join(ja_parts)
    
    # 如果翻译结果就是原文本身（说明没匹配到），做简单处理
    if en_result == cn:
        en_result = cn  # 保留中文
    if ja_result == cn:
        ja_result = cn  # 保留中文
    
    return {"en": en_result, "ja": ja_result}


# ---- 主流程 ----
with open(METADATA) as f:
    meta = json.load(f)

titles = set()
for p in meta["photos"]:
    t = (p.get("ai_tags") or {}).get("poetic_title", "")
    if t and t.strip():
        titles.add(t.strip())

titles = sorted(titles)

# 读取已有翻译
existing = {}
if os.path.exists(I18N_JS):
    content = open(I18N_JS).read()
    for m in re.finditer(r"'([^']+)':\s*\{\s*en:\s*'([^']*)',\s*ja:\s*'([^']*)'\s*\}", content):
        existing[m.group(1)] = {"en": m.group(2), "ja": m.group(3)}

need_translate = [t for t in titles if t not in existing]
print(f"独立标题: {len(titles)}, 已有翻译: {len(existing)}, 待翻译: {len(need_translate)}")

# 生成翻译
new_translations = {}
for t in need_translate:
    new_translations[t] = translate_title(t)

# 写入 gallery-i18n.js
if new_translations:
    new_entries = []
    for title, trans in sorted(new_translations.items()):
        escaped_title = title.replace("\\", "\\\\").replace("'", "\\'")
        escaped_en = trans["en"].replace("\\", "\\\\").replace("'", "\\'")
        escaped_ja = trans["ja"].replace("\\", "\\\\").replace("'", "\\'")
        new_entries.append(f"    '{escaped_title}': {{ en: '{escaped_en}', ja: '{escaped_ja}' }},")
    
    new_block = "\n".join(new_entries)
    
    content = open(I18N_JS).read()
    marker = "  poeticTitles: {"
    start = content.index(marker)
    
    depth = 0
    insert_pos = start
    for j in range(start, len(content)):
        if content[j] == "{":
            depth += 1
        elif content[j] == "}":
            depth -= 1
            if depth == 0:
                insert_pos = j
                break
    
    updated = content[:insert_pos] + "\n" + new_block + "\n" + content[insert_pos:]
    
    with open(I18N_JS, "w") as f:
        f.write(updated)
    
    print(f"✅ 已添加 {len(new_translations)} 条翻译到 {I18N_JS}")

total = len(existing) + len(new_translations)
print(f"总翻译数: {total} / {len(titles)}")

# 打印样例
print("\n样例翻译:")
for t in list(new_translations.keys())[:5]:
    tr = new_translations[t]
    print(f"  {t}")
    print(f"    → EN: {tr['en']}")
    print(f"    → JA: {tr['ja']}")
