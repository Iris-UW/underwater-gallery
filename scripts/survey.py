"""Quick survey: jerryliang + problematic titles count"""
import json, os, glob

meta_path = 'data/photos_metadata.json'
img_dir = 'docs/images/full'

# 1. jerryliang check
files = glob.glob(f'{img_dir}/*.jpg') + glob.glob(f'{img_dir}/*.JPG')
jerry = []
for f in files:
    with open(f, 'rb') as fh:
        if b'jerry' in fh.read().lower():
            jerry.append(os.path.basename(f))

print(f"=== jerryliang ===")
print(f"找到 {len(jerry)} 张")
for j in jerry:
    print(f"  {j}")

# 2. Problematic titles
with open(meta_path) as f:
    data = json.load(f)

problems = []
for p in data['photos']:
    at = p.get('ai_tags', {})
    pt = str(at.get('poetic_title', ''))
    sub = str(at.get('substrate', ''))
    cn = str(at.get('species_cn', ''))
    fn = p['filename']
    
    # 珊瑚标题 + 海藻底
    if ('珊瑚' in pt) and ('海藻' in sub or '海草' in sub):
        problems.append({'fn': fn, 'title': pt, 'sub': sub, 'sp': cn, 'reason': '珊瑚→海藻'})
    # 珊瑚标题 + 底质不明
    elif ('珊瑚' in pt) and ('不明' in sub or '无法' in sub or '未知' in sub):
        problems.append({'fn': fn, 'title': pt, 'sub': sub, 'sp': cn, 'reason': '标题珊瑚+底质不明'})
    # 底质模糊
    elif sub and any(k in sub for k in ['可能', '疑似', '不确定', '无法', '看来', '似乎']):
        problems.append({'fn': fn, 'title': pt, 'sub': sub, 'sp': cn, 'reason': '底质模糊'})

print(f"\n=== 需修复诗意标题: {len(problems)} 张 ===")
for pr in problems[:30]:
    print(f"  {pr['fn']}: «{pr['title'][:40]}» [{pr['reason']}]")
if len(problems) > 30:
    print(f"  ... 还有 {len(problems)-30} 张")

# Save for reference
with open('data/survey_result.json', 'w') as f:
    json.dump({'jerryliang': jerry, 'title_problems': problems}, f, ensure_ascii=False, indent=2)
print("\n结果已保存到 data/survey_result.json")
