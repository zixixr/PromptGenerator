#!/usr/bin/env python3
"""
Update summary markdown files with accurate user information from JSON conversation files.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# Base directories
SUMMARY_DIR = Path("D:/AITOY/PromptGenerator/summary/astrology_mcp_showcase")
CONVERSATIONS_DIR = Path("D:/AITOY/PromptGenerator/conversations")

# Known mappings from the generation report and JSON analysis
USER_MAPPINGS = {
    # From JSON file session IDs we've confirmed
    "2864e28855444dd98cf89a10ad221f05": {
        "name": "苗苗",
        "age": 24,
        "zodiac": "摩羯座",
        "device": "山羊",
        "occupation": "学生",
        "scenario": "考试压力"
    },
    "86536624f19b4210904ba897013c25f4": {
        "name": "江月",
        "age": 25,
        "zodiac": "天蝎座",
        "device": "小蝎",
        "occupation": "研究生",
        "scenario": "学术问题"
    },
    "b9e6835c55404dfe80e46cf6f73c2723": {
        "name": "苏晴",
        "age": 28,
        "zodiac": "射手座",
        "device": "流星",
        "occupation": "自由职业写作者",
        "scenario": "创作瓶颈"
    },
    "bb5c00d5dcd64fa08c095379f8665bb6": {
        "name": "糖糖",
        "age": 20,
        "zodiac": "天秤座",
        "device": "粉秤",
        "occupation": "美妆博主",
        "scenario": "身份认同"
    },
    "dfb1ecfb4b384886bc23a132e850448c": {
        "name": "张婷",
        "age": 31,
        "zodiac": "摩羯座",
        "device": "老山",
        "occupation": "创业者",
        "scenario": "创业危机"
    }
}

def extract_user_info_from_json(json_path):
    """Extract user information from a JSON conversation file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        prompt = data.get('resolved_system_prompt', '')

        # Extract user name (look for pattern like `用户姓名` - )
        name_match = re.search(r'`([^`]+)` - 用户姓名', prompt)
        name = name_match.group(1) if name_match else "未知"

        # Extract birth date
        date_match = re.search(r'`(\d{4}-\d{2}-\d{2})` - 用户生日', prompt)
        if date_match:
            birth_date = date_match.group(1)
            birth_year = int(birth_date.split('-')[0])
            age = 2025 - birth_year  # Current year in the system
        else:
            age = "未知"

        # Extract zodiac (look for pattern like `星座` )
        zodiac_match = re.search(r'衍生数据: `([^`]+)` `([^`]+)` `([^`]+)`', prompt)
        zodiac = zodiac_match.group(1) if zodiac_match else "未知"

        # Extract device name (AI companion)
        device_match = re.search(r'`([^`]+)` - 你的名字', prompt)
        device = device_match.group(1) if device_match else "未知"

        return {
            "name": name,
            "age": age,
            "zodiac": zodiac,
            "device": device
        }
    except Exception as e:
        print(f"Error reading {json_path}: {e}")
        return None

def get_all_json_mappings():
    """Scan all JSON files and extract user information."""
    mappings = {}

    for json_file in CONVERSATIONS_DIR.glob("*.json"):
        session_id = json_file.stem
        user_info = extract_user_info_from_json(json_file)

        if user_info and user_info['name'] != "未知":
            mappings[session_id] = user_info
            print(f"Found: {session_id} -> {user_info['name']} ({user_info['age']}岁, {user_info['zodiac']}, {user_info['device']})")

    return mappings

def update_markdown_file(md_path, user_info):
    """Update a markdown file with accurate user information."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update title
    content = re.sub(
        r'# 未知 - 未知岁[^|]*\| 未知 AI陪伴案例',
        f'# {user_info["name"]} - {user_info["age"]}岁{user_info.get("occupation", "用户")} | {user_info["device"]} AI陪伴案例',
        content
    )

    # Update user profile section
    content = re.sub(r'- \*\*姓名\*\*: 未知', f'- **姓名**: {user_info["name"]}', content)
    content = re.sub(r'- \*\*年龄\*\*: 未知岁', f'- **年龄**: {user_info["age"]}岁', content)
    content = re.sub(r'- \*\*AI伙伴\*\*: 未知 \(未知\)', f'- **AI伙伴**: {user_info["device"]} ({user_info["zodiac"]})', content)

    # Update scenario if provided
    if "scenario" in user_info:
        content = re.sub(r'- \*\*场景\*\*: [^\n]+', f'- **场景**: {user_info["scenario"]}', content)

    # Update conversation content - replace "未知" speaker names with actual names
    content = re.sub(r'\*\*未知\*\*:', f'**{user_info["name"]}**:', content)
    content = re.sub(r'\*\*未知\*\*:', f'**{user_info["device"]}**:', content, count=999)  # Replace AI responses

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated: {md_path.name}")

def main():
    print("=" * 60)
    print("UPDATING MARKDOWN SUMMARIES WITH ACCURATE USER DATA")
    print("=" * 60)
    print()

    # Get all JSON mappings
    print("Step 1: Scanning JSON conversation files...")
    print("-" * 60)
    all_mappings = get_all_json_mappings()

    # Merge with known mappings
    all_mappings.update(USER_MAPPINGS)

    print()
    print(f"Total mappings found: {len(all_mappings)}")
    print()

    # Process markdown files
    print("Step 2: Updating markdown files...")
    print("-" * 60)

    updated_files = []

    # Find all markdown files that need updating
    for md_file in SUMMARY_DIR.glob("*.md"):
        # Skip non-user files
        if not (md_file.name.startswith("用户") or "未知" in md_file.name):
            continue

        # Read the file to determine which session it belongs to
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Try to match with our mappings based on content
        matched = False
        for session_id, user_info in all_mappings.items():
            # Check if this markdown file matches this user
            # We can check rounds, scenario, or other identifying features
            if user_info.get("scenario") and user_info["scenario"] in content:
                # Found a match!
                update_markdown_file(md_file, user_info)

                # Rename the file
                new_name = f"{user_info['name']}_{user_info['age']}岁_{user_info.get('occupation', '用户')}_{user_info.get('scenario', '日常对话')}_{user_info['zodiac']}.md"
                new_path = md_file.parent / new_name

                if new_path != md_file:
                    if new_path.exists():
                        print(f"⚠ Target already exists, skipping rename: {new_name}")
                    else:
                        md_file.rename(new_path)
                        print(f"Renamed: {md_file.name} -> {new_name}")

                updated_files.append(new_name)
                matched = True
                break

        if not matched:
            print(f"⚠ Could not match: {md_file.name}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files updated: {len(updated_files)}")
    print(f"Updated files:")
    for filename in updated_files:
        print(f"  - {filename}")

if __name__ == "__main__":
    main()
