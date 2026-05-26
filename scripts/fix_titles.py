"""Fix problematic poetic titles using ChatGPT (gpt-4o).

Reads data/survey_result.json, regenerates titles for photos with:
- Coral/reef in title but substrate is seagrass/algae
- Vague substrate descriptions
- Unconfirmed habitat mentions

New titles should be:
- Simple and poetic
- Only mention what's clearly identifiable (the animal itself)
- No forced coral/reef metaphors
- Short, 2-6 words in Chinese
"""
import json
import os
import time

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
META_PATH = os.path.join(DATA_DIR, "photos_metadata.json")
SURVEY_PATH = os.path.join(DATA_DIR, "survey_result.json")

# Get API key from environment
API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not API_KEY:
    # Try reading from file
    keyfile = os.path.expanduser("~/.workbuddy/openai_key.txt")
    if os.path.exists(keyfile):
        with open(keyfile) as f:
            API_KEY = f.read().strip()

if not API_KEY:
    print("ERROR: No OpenAI API key found.")
    print("Set OPENAI_API_KEY env var or put it in ~/.workbuddy/openai_key.txt")
    exit(1)

from openai import OpenAI
client = OpenAI(api_key=API_KEY)

def regenerate_title(photo):
    """Generate a new poetic title for a photo."""
    at = photo.get("ai_tags", {})
    species_cn = at.get("species_cn", "unknown")
    species_latin = at.get("species_latin", "")
    category = at.get("category", "")
    colors = ", ".join(at.get("primary_colors", []))
    behavior = at.get("behavior", "")
    old_title = at.get("poetic_title", "")
    substrate = at.get("substrate", "")
    
    prompt = f"""You are naming an underwater macro photograph. 

What we know:
- Subject: {species_cn} ({species_latin})
- Category: {category}
- Colors: {colors}
- Behavior: {behavior}
- Substrate/Habitat hint: {substrate}

Rules:
1. Write a short, poetic title in Chinese (2-6 characters)
2. Focus on the animal itself — its form, colors, posture, mood
3. Do NOT mention "coral/珊瑚" unless it is clearly confirmed
4. Do NOT invent habitats or surroundings
5. Be simple and evocative, not grandiose
6. Return ONLY the title, nothing else

Example good titles: 幽光之舞, 橙影独行, 蓝点之梦, 微光中的隐者

Previous title was: {old_title}"""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.7
        )
        new_title = resp.choices[0].message.content.strip()
        # Clean up: remove quotes, dashes, extra spaces
        new_title = new_title.strip('"\'-「」『』 \n')
        return new_title
    except Exception as e:
        print(f"  API error: {e}")
        return old_title  # keep original on error


def main():
    # Load data
    with open(META_PATH) as f:
        meta = json.load(f)
    with open(SURVEY_PATH) as f:
        survey = json.load(f)
    
    problems = survey["title_problems"]
    print(f"Found {len(problems)} photos to fix\n")
    
    # Build lookup
    photo_map = {p["filename"]: p for p in meta["photos"]}
    
    fixed = 0
    for i, pr in enumerate(problems):
        fn = pr["fn"]
        if fn not in photo_map:
            continue
        
        p = photo_map[fn]
        old_title = pr["title"]
        reason = pr["reason"]
        
        print(f"[{i+1}/{len(problems)}] {fn}")
        print(f"  Old: «{old_title}» ({reason})")
        
        new_title = regenerate_title(p)
        print(f"  New: «{new_title}»")
        
        # Update metadata
        if "ai_tags" in p:
            p["ai_tags"]["poetic_title"] = new_title
            p["ai_tags"]["poetic_reason"] = f"Regenerated: simple poetic title, habitat-neutral"
        fixed += 1
        
        # Rate limit
        time.sleep(0.5)
    
    # Save updated metadata
    with open(META_PATH, "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    
    print(f"\nFixed {fixed} titles. Metadata saved to {META_PATH}")


if __name__ == "__main__":
    main()
