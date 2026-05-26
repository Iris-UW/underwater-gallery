#!/usr/bin/env python3
"""Reclassify all photos into simplified 5-category system: 鱼/海兔/海牛/虾/蟹/其他"""

import json
import re

METADATA_JSON = "data/photos_metadata.json"

# Mapping rules: old_category → new_category (direct)
DIRECT_MAP = {
    "海兔": "海兔",
    "海牛": "海牛",
    "鱼": "鱼",
    "虾": "虾",
    "螃蟹": "蟹",
    "蟹": "蟹",
}

# Species name clues for reclassifying 头足类 and 其他
FISH_KEYWORDS = ["鱼", "虾虎", "虎鱼", "海龙", "鬼龙", "goby", "fish", "pipefish", "seadragon", "dragonet", "blenny", "gunnel", "eel"]
SHRIMP_KEYWORDS = ["虾", "shrimp", "prawn", "cleaner", "crustacean", "甲壳"]
CRAB_KEYWORDS = ["蟹", "crab", "spider"]
NUDI_KEYWORDS = ["海兔", "海牛", "nudibranch", "slug", "chromodoris", "phyllidia", "flabellina", "phyllodesmium", "tambja", "janolus", "facelina", "goniobranchus", "hypselodoris", "glossodoris", "miamira", "cuthona", "pteraeolidia"]
OCTOPUS_KEYWORDS = ["章鱼", "octopus", "wunderpus", "mimic", "蛸", "squid", "cuttlefish", "sepia", "sepiolid"]
NON_ANIMAL_KEYWORDS = ["珊瑚", "coral", "苔藓", "bryozoa", "海鞘", "tunicate", "ascidian", "海绵", "sponge", "海葵", "anemone", "软体", "软珊瑚"]


def guess_category(species_cn, species_latin, old_cat):
    """Try to guess the correct category from species name text."""
    text = f"{species_cn} {species_latin}".lower()
    
    # Check octopus/non-animal BEFORE fish (章鱼 contains 鱼!)
    for kw in OCTOPUS_KEYWORDS:
        if kw.lower() in text:
            return "其他"
    for kw in NON_ANIMAL_KEYWORDS:
        if kw.lower() in text:
            return "其他"
    
    for kw in FISH_KEYWORDS:
        if kw.lower() in text:
            return "鱼"
    for kw in SHRIMP_KEYWORDS:
        if kw.lower() in text:
            return "虾"
    for kw in CRAB_KEYWORDS:
        if kw.lower() in text:
            return "蟹"
    for kw in NUDI_KEYWORDS:
        if kw.lower() in text:
            return "海兔"
    
    # If old category was already a known one, keep it
    if old_cat in DIRECT_MAP:
        return DIRECT_MAP[old_cat]
    
    return "其他"


def main():
    with open(METADATA_JSON, "r") as f:
        data = json.load(f)
    
    stats = {}
    changes = []
    
    for i, p in enumerate(data["photos"]):
        ai = p.get("ai_tags", {})
        old_cat = ai.get("category", "其他")
        
        # Direct mapping for known categories
        if old_cat in DIRECT_MAP:
            new_cat = DIRECT_MAP[old_cat]
        else:
            # Try to guess from species name
            species_cn = ai.get("species_cn", "")
            species_latin = ai.get("species_latin", "")
            new_cat = guess_category(species_cn, species_latin, old_cat)
        
        ai["category"] = new_cat
        p["ai_tags"] = ai
        
        key = f"{old_cat} → {new_cat}"
        stats[key] = stats.get(key, 0) + 1
        
        if old_cat != new_cat:
            changes.append(f"  [{i}] {p['filename']}: {old_cat} → {new_cat} ({ai.get('species_cn', '?')})")
    
    # Write back
    with open(METADATA_JSON, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Report
    print("=== Reclassification Summary ===")
    for k, v in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v}")
    
    print(f"\n=== Changed ({len(changes)}) ===")
    for c in changes:
        print(c)
    
    # Final distribution
    from collections import Counter
    final = Counter(p["ai_tags"]["category"] for p in data["photos"])
    print(f"\n=== Final Distribution ===")
    for cat, count in final.most_common():
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
