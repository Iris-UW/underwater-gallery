#!/usr/bin/env python3
"""
批量翻译所有诗意标题 → 英文 / 日文
通过 OpenAI GPT-4o API 进行翻译，生成 gallery-i18n.js 需要的 poeticTitles 字典。
"""

import json, os, sys, time
from pathlib import Path

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    key_file = os.path.expanduser("~/.workbuddy/openai_key.txt")
    if os.path.exists(key_file):
        OPENAI_KEY = open(key_file).read().strip()

if not OPENAI_KEY:
    print("❌ 未找到 OpenAI API Key")
    sys.exit(1)

METADATA = os.path.join(os.path.dirname(__file__), "..", "data", "photos_metadata.json")
I18N_JS = os.path.join(os.path.dirname(__file__), "..", "docs", "gallery-i18n.js")

# Load metadata, collect unique poetic titles
with open(METADATA) as f:
    meta = json.load(f)

titles = set()
for p in meta["photos"]:
    t = (p.get("ai_tags") or {}).get("poetic_title", "")
    if t and t.strip():
        titles.add(t.strip())

titles = sorted(titles)
print(f"📝 共 {len(titles)} 个独立诗意标题待翻译")

# Read existing i18n to check which are already translated
existing = {}
if os.path.exists(I18N_JS):
    content = open(I18N_JS).read()
    import re
    # Extract existing entries
    for m in re.finditer(r"'([^']+)':\s*\{\s*en:\s*'([^']*)',\s*ja:\s*'([^']*)'\s*\}", content):
        existing[m.group(1)] = {"en": m.group(2), "ja": m.group(3)}

need_translate = [t for t in titles if t not in existing]
print(f"  已有翻译: {len(existing)}")
print(f"  待翻译: {len(need_translate)}")

if not need_translate:
    print("✅ 全部已有翻译，无需操作")
    sys.exit(0)

# ---- OpenAI API call ----
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
except ImportError:
    print("❌ 请安装 openai 包: pip install openai")
    sys.exit(1)

BATCH_SIZE = 20
new_translations = {}

for i in range(0, len(need_translate), BATCH_SIZE):
    batch = need_translate[i:i+BATCH_SIZE]
    titles_list = "\n".join([f"{j+1}. {t}" for j, t in enumerate(batch)])
    
    prompt = f"""Translate the following Chinese poetic titles of underwater macro photographs into English and Japanese.

Requirements:
- English: natural, evocative, poetic — not literal translation. Preserve the mood and imagery.
- Japanese: elegant, literary Japanese with appropriate kanji usage. Use の particle naturally.
- Output ONLY valid JSON in this exact format:
{{"1": {{"en": "English title", "ja": "Japanese title"}}, "2": ...}}

Titles:
{titles_list}"""

    print(f"\n🔄 翻译第 {i//BATCH_SIZE + 1} 批 ({len(batch)} 条)...")
    time.sleep(0.5)  # rate limit prevention
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=4096,
        )
        result_text = resp.choices[0].message.content.strip()
        # Extract JSON from response
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("```", 1)[0]
        
        batch_result = json.loads(result_text)
        for idx_str, trans in batch_result.items():
            idx = int(idx_str) - 1
            if idx < len(batch):
                new_translations[batch[idx]] = trans
        
        print(f"  ✅ 完成 {len(batch_result)} 条")
    except Exception as e:
        print(f"  ❌ 批次失败: {e}")
        # Save progress so far
        break

print(f"\n📊 本批次新增翻译: {len(new_translations)}")

# ---- Update gallery-i18n.js ----
if new_translations:
    # Build the JS object string for new entries
    new_entries = []
    for title, trans in sorted(new_translations.items()):
        escaped_title = title.replace("'", "\\'")
        escaped_en = trans["en"].replace("'", "\\'")
        escaped_ja = trans["ja"].replace("'", "\\'")
        new_entries.append(f"    '{escaped_title}': {{ en: '{escaped_en}', ja: '{escaped_ja}' }},")
    
    new_block = "\n".join(new_entries)
    
    # Insert after the last existing entry in poeticTitles
    content = open(I18N_JS).read()
    
    # Find the closing of poeticTitles
    marker = "  poeticTitles: {"
    start = content.index(marker)
    
    # Find the matching closing brace
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
    
    # Insert new entries before the closing brace
    updated = content[:insert_pos] + "\n" + new_block + "\n" + content[insert_pos:]
    
    with open(I18N_JS, "w") as f:
        f.write(updated)
    
    print(f"✅ 已更新 {I18N_JS}")

# Final summary
total = len(existing) + len(new_translations)
print(f"\n📊 总翻译数: {total} / {len(titles)} ({100*total//len(titles)}%)")
