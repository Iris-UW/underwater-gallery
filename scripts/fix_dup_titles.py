#!/usr/bin/env python3
"""
修复重复的诗意标题
从 photos_metadata.json 中找出标题不唯一的照片，
基于元数据（物种、颜色、行为等）生成新的不重复标题。
"""

import json, os, sys
from openai import OpenAI

METADATA_JSON = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")

PROMPT_TEMPLATE = """你是一位诗人兼水下摄影师。以下是多张水下微距照片的元数据，每张照片当前的诗意标题与其他照片重复了，需要为它们生成全新的、各不相同的诗意标题。

规则：
1. 不要使用生物学名称（不要出现"Chromodoris""海兔""帝王虾"等分类词汇）
2. 标题应该像一首短诗的标题，或当代艺术展品的名字
3. 基于颜色、形态、光影、情绪、行为来命名
4. 风格参考："蓝色迷宫里的旅人""橙色火焰的独白""珊瑚暗处的一瞥""无名的庆典""Amber Whisper""Cobalt Drift"
5. 字数控制在2-8个汉字为佳，也可以偶尔用英文短词
6. 所有标题在本次生成中必须各不相同
7. 每个标题都应该与这张照片的元数据有内在联系（颜色、行为等）

请为以下每张照片生成一个新的诗意标题，返回严格的JSON列表格式，每个元素包含 index 和 poetic_title：

[
  {"index": 0, "poetic_title": "珊瑚上的晨曦"},
  ...
]

以下是照片元数据：
{photos_text}"""


def build_photo_text(photos):
    """为每张照片构建简洁的文本描述"""
    lines = []
    for p in photos:
        idx = p["index"]
        species = p.get("species_cn", "未知生物")
        colors = "、".join(p.get("primary_colors", [])) or "未知"
        behavior = p.get("behavior", "未知")
        composition = p.get("composition", "未知")
        category = p.get("category", "未知")
        notes = p.get("notes", "")
        
        desc = f"[{idx}] 物种:{species} | 类别:{category} | 主色:{colors} | 行为:{behavior} | 构图:{composition}"
        if notes:
            desc += f" | 备注:{notes[:80]}"
        lines.append(desc)
    return "\n".join(lines)


def main():
    # 读取元数据
    with open(METADATA_JSON, "r") as f:
        data = json.load(f)
    
    photos = data["photos"]
    
    # 收集所有需要修复的索引
    to_fix = []
    from collections import Counter
    title_indices = {}
    for i, p in enumerate(photos):
        pt = (p.get("ai_tags") or {}).get("poetic_title", "")
        if pt:
            if pt not in title_indices:
                title_indices[pt] = []
            title_indices[pt].append(i)
    
    for title, indices in title_indices.items():
        if len(indices) > 1:
            for idx in indices:
                ai = photos[idx].get("ai_tags", {})
                to_fix.append({
                    "index": idx,
                    "filename": photos[idx]["filename"],
                    "poetic_title": title,
                    "species_cn": ai.get("species_cn", ""),
                    "species_latin": ai.get("species_latin", ""),
                    "category": ai.get("category", ""),
                    "primary_colors": ai.get("primary_colors", []),
                    "behavior": ai.get("behavior", ""),
                    "composition": ai.get("composition", ""),
                    "notes": ai.get("notes", "")
                })
    
    print(f"找到 {len(to_fix)} 张照片需要生成新标题")
    print(f"涉及 {len([k for k,v in title_indices.items() if len(v)>1])} 个重复标题\n")
    
    if not to_fix:
        print("没有重复标题，无需修复。")
        return
    
    # 分批处理，每批最多15张
    BATCH_SIZE = 15
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://iris-underwater.vercel.app",
            "X-Title": "Iris UW Poetic Fix"
        }
    )
    
    all_results = {}
    batches = [to_fix[i:i+BATCH_SIZE] for i in range(0, len(to_fix), BATCH_SIZE)]
    
    for batch_num, batch in enumerate(batches):
        print(f"--- 批次 {batch_num+1}/{len(batches)} ({len(batch)} 张) ---")
        
        photos_text = build_photo_text(batch)
        prompt = PROMPT_TEMPLATE.format(photos_text=photos_text)
        
        try:
            resp = client.chat.completions.create(
                model="qwen/qwen2.5-72b-instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.9,
            )
            text = resp.choices[0].message.content.strip()
            
            # 清理 markdown 包裹
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            
            results = json.loads(text)
            
            for r in results:
                idx = r["index"]
                new_title = r["poetic_title"]
                old_title = photos[idx]["ai_tags"]["poetic_title"]
                species = photos[idx]["ai_tags"].get("species_cn", "?")
                all_results[idx] = new_title
                print(f"  [{idx}] {species}: \"{old_title}\" → \"{new_title}\"")
            
        except Exception as e:
            print(f"  ❌ 批次 {batch_num+1} 失败: {e}")
            # 失败时保留原标题
            for p in batch:
                all_results[p["index"]] = p["poetic_title"]
        
        if batch_num < len(batches) - 1:
            import time
            time.sleep(2)
    
    # 验证唯一性
    all_new_titles = list(all_results.values())
    dup_check = Counter(all_new_titles)
    new_dupes = {k:v for k,v in dup_check.items() if v > 1}
    if new_dupes:
        print(f"\n⚠️ 新标题仍有 {len(new_dupes)} 个重复:")
        for t, c in new_dupes.items():
            print(f"  \"{t}\": {c}次")
    
    # 写入 JSON
    for idx, new_title in all_results.items():
        photos[idx].setdefault("ai_tags", {})["poetic_title"] = new_title
    
    # 备份
    backup = METADATA_JSON + ".bak"
    with open(backup, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 备份已保存: {backup}")
    
    with open(METADATA_JSON, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 已更新 {len(all_results)} 个标题到 {METADATA_JSON}")
    
    # 统计
    print(f"\n📊 修复统计:")
    print(f"  修复照片数: {len(all_results)}")
    print(f"  新标题唯一数: {len(set(all_new_titles))}")


if __name__ == "__main__":
    main()
