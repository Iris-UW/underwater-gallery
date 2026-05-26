#!/usr/bin/env python3
"""将手动生成的不重复诗意标题写入 photos_metadata.json"""

import json, os, sys
from collections import Counter

METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")

# 43个新标题，基于每张照片的物种、颜色、行为、构图手工生成
# key = photos数组中的index
NEW_TITLES = {
    # "珊瑚上的晨曦" (4) →
    0: "橙色晨光",
    1: "粉橘色的凝视",
    2: "橙黄的诗笺",
    103: "晨光乍泄",

    # "幽光之舞" (2) →
    38: "蓝色微光",
    98: "紫韵流光",

    # "深海的条纹梦" (2) →
    50: "橙色条纹的私语",
    67: "透明橙带",

    # "幽蓝梦境" (3) →
    52: "蓝色的无声剧场",
    176: "瓷白微光",
    206: "淡黄的呢喃",

    # "幽暗中的舞者" (3) →
    53: "荆棘王冠",
    78: "紫色丘陵",
    88: "暮色三重奏",

    # "珊瑚间的隐者" (8) →
    56: "珊瑚之瞳",
    66: "琥珀色的隐士",
    73: "暗处的静默",
    89: "紫气东来",
    100: "微缩王国的君主",
    192: "寂静的守望",
    193: "陶瓷的伪装",
    203: "落叶之影",

    # "幽影之舞" (7) →
    54: "蓝黄交织",
    58: "粉色火焰",
    60: "四色谱",
    61: "伊丽莎白的裙摆",
    62: "朝霞之羽",
    90: "琥珀猎手",
    151: "蓝色信使",

    # "金色梦境" (3) →
    69: "沙漠玫瑰",
    141: "斑驳岁月",
    182: "沙地上的守望者",

    # "珊瑚上的舞者" (3) →
    105: "无名的旋转",
    132: "寂静芭蕾",
    175: "白紫华尔兹",

    # "珊瑚间的幽灵" (2) →
    76: "珊瑚枝上的精灵",
    92: "雪中红樱",

    # "橙色梦境中的幽灵" (2) →
    79: "紫雾中的行者",
    80: "斑驳记忆",

    # "海底的珍珠梦" (2) →
    177: "橙光入梦",
    179: "沉没的星辰",

    # "幽灵之舞" (2) →
    204: "黄昏的翅膀",
    210: "暮光羽翼",
}


def main():
    with open(METADATA_JSON, "r") as f:
        data = json.load(f)
    
    photos = data["photos"]
    
    # 收集所有现有标题（包括不改的），用于冲突检查
    all_existing_titles = set()
    for i, p in enumerate(photos):
        pt = (p.get("ai_tags") or {}).get("poetic_title", "")
        if pt and i not in NEW_TITLES:
            all_existing_titles.add(pt)
    
    # 冲突检查
    conflicts = []
    for idx, new_title in NEW_TITLES.items():
        if new_title in all_existing_titles:
            conflicts.append((idx, new_title))
    
    if conflicts:
        print("❌ 新标题与现有标题冲突：")
        for idx, title in conflicts:
            print(f"  [{idx}] \"{title}\" 已存在")
        sys.exit(1)
    
    # 新标题自身唯一性检查
    new_titles_only = list(NEW_TITLES.values())
    dup_new = {k: v for k, v in Counter(new_titles_only).items() if v > 1}
    if dup_new:
        print("❌ 新标题之间不唯一：")
        for t, c in dup_new.items():
            print(f"  \"{t}\": {c}次")
        sys.exit(1)
    
    print(f"✅ 新标题全部唯一，无冲突")
    print(f"准备写入 {len(NEW_TITLES)} 个标题\n")
    
    # 写入
    for idx, new_title in NEW_TITLES.items():
        old_title = photos[idx]["ai_tags"]["poetic_title"]
        species = photos[idx]["ai_tags"].get("species_cn", "?")
        photos[idx]["ai_tags"]["poetic_title"] = new_title
        print(f"  [{idx}] {species}: \"{old_title}\" → \"{new_title}\"")
    
    # 备份
    import shutil
    backup = METADATA_JSON + ".bak"
    shutil.copy2(METADATA_JSON, backup)
    
    with open(METADATA_JSON, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 已写入 {METADATA_JSON}")
    print(f"✅ 备份: {backup}")
    
    # 最终验证
    with open(METADATA_JSON, "r") as f:
        verify = json.load(f)
    
    all_titles = []
    for p in verify["photos"]:
        pt = (p.get("ai_tags") or {}).get("poetic_title", "")
        if pt:
            all_titles.append(pt)
    
    dup_final = {k: v for k, v in Counter(all_titles).items() if v > 1}
    if dup_final:
        print(f"\n⚠️ 最终检查：仍有 {len(dup_final)} 个重复标题")
        for t, c in list(dup_final.items())[:5]:
            print(f"  \"{t}\": {c}次")
    else:
        print(f"\n🎉 最终检查：{len(all_titles)} 个标题全部唯一！")


if __name__ == "__main__":
    main()
