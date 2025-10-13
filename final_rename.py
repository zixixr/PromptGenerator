#!/usr/bin/env python3
"""
Final script to rename and update remaining markdown files by reading their conversation content.
"""

import os
import re
from pathlib import Path

SUMMARY_DIR = Path("D:/AITOY/PromptGenerator/summary/astrology_mcp_showcase")

def extract_user_from_conversation(md_path):
    """Extract user name and device name from the conversation content."""
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find first user message (pattern: **Name**: message)
    user_match = re.search(r'\*\*未知\*\*:\s*(.+?)(?:\n\n|\n\*\*)', content, re.DOTALL)

    if user_match:
        first_message = user_match.group(1).strip()
        # Look for self-introduction or names in the message
        name_patterns = [
            r'我是([^！。，,\s]+)',  # "我是XXX"
            r'你好呀，我是([^！。，,\s]+)',  # "你好呀，我是XXX"
            r'叫我([^！。，,\s]+)',  # "叫我XXX"
        ]

        for pattern in name_patterns:
            match = re.search(pattern, first_message)
            if match:
                user_name = match.group(1)
                print(f"Found user name in conversation: {user_name}")
                return user_name

    # Look for mentions in the AI's response
    ai_responses = re.findall(r'\*\*未知\*\*:\s*[""""]([^"""""""]+)[""""]', content)
    for response in ai_responses[:3]:  # Check first 3 responses
        if '你好' in response or '我是' in response:
            # Extract names from the response
            match = re.search(r'([^，。！\s]{2,4})你好', response)
            if match:
                user_name = match.group(1)
                print(f"Found user name from AI greeting: {user_name}")
                return user_name

    return None

def infer_zodiac_from_ai(content):
    """Infer zodiac sign from AI companion name."""
    # Common zodiac AI names
    zodiac_map = {
        '小秤': '天秤座',
        '秤秤': '天秤座',
        '粉秤': '天秤座',
        '小蝎': '天蝎座',
        '蝎儿': '天蝎座',
        '流星': '射手座',
        '星星': '射手座',
        '小箭': '射手座',
        '山羊': '摩羯座',
        '老山': '摩羯座',
        '小羊': '摩羯座',
        '小羯': '摩羯座',
    }

    for ai_name, zodiac in zodiac_map.items():
        if ai_name in content:
            return ai_name, zodiac

    return None, None

def process_file(md_path):
    """Process a single markdown file."""
    print(f"\nProcessing: {md_path.name}")
    print("-" * 60)

    user_name = extract_user_from_conversation(md_path)

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    ai_name, zodiac = infer_zodiac_from_ai(content)

    if not user_name:
        print(f"⚠ Could not extract user name from {md_path.name}")
        return False

    # Estimate age from scenario context (fallback to reasonable defaults)
    age = 25  # Default
    if '学生' in md_path.name or '考试' in content[:500]:
        age = 20
    elif '职场' in content[:500] or '工作' in content[:500]:
        age = 28
    elif '创业' in content[:500]:
        age = 30

    # Determine scenario
    if '考试' in content[:500] or '学业' in content[:500]:
        scenario = '学业压力'
    elif '职业' in content[:500] or '工作' in content[:500] or '职场' in content[:500]:
        scenario = '职业规划'
    elif '创业' in content[:500]:
        scenario = '创业挑战'
    else:
        scenario = '日常对话'

    # Determine occupation
    if '学生' in content[:500] or '考试' in content[:500]:
        occupation = '学生'
    elif '创业' in content[:500]:
        occupation = '创业者'
    elif '设计' in content[:500]:
        occupation = '设计师'
    else:
        occupation = '用户'

    print(f"User: {user_name}, Age: {age}, Zodiac: {zodiac or '未知'}, AI: {ai_name or '未知'}")
    print(f"Occupation: {occupation}, Scenario: {scenario}")

    # Update content
    new_content = content
    new_content = re.sub(
        r'# 未知 - 未知岁[^|]*\| 未知 AI陪伴案例',
        f'# {user_name} - {age}岁{occupation} | {ai_name or "AI"} AI陪伴案例',
        new_content
    )
    new_content = re.sub(r'- \*\*姓名\*\*: 未知', f'- **姓名**: {user_name}', new_content)
    new_content = re.sub(r'- \*\*年龄\*\*: 未知岁', f'- **年龄**: {age}岁', new_content)
    new_content = re.sub(
        r'- \*\*AI伙伴\*\*: 未知 \(未知\)',
        f'- **AI伙伴**: {ai_name or "AI"} ({zodiac or "未知"})',
        new_content
    )

    # Update speaker names in dialogue
    # First pass: replace first "未知" with user name
    new_content = re.sub(r'(\*\*未知\*\*:)', f'**{user_name}**:', new_content, count=1)
    # Then alternate pattern - assume user and AI alternate
    lines = new_content.split('\n')
    in_dialogue = False
    is_user_turn = True

    for i, line in enumerate(lines):
        if '## 📝 完整对话记录' in line:
            in_dialogue = True
            continue

        if in_dialogue and '**未知**:' in line:
            if is_user_turn:
                lines[i] = line.replace('**未知**:', f'**{user_name}**:', 1)
            else:
                lines[i] = line.replace('**未知**:', f'**{ai_name or "AI"}**:', 1)
            is_user_turn = not is_user_turn

    new_content = '\n'.join(lines)

    # Write updated content
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    # Rename file
    new_name = f"{user_name}_{age}岁_{occupation}_{scenario}_{zodiac or '未知'}.md"
    new_path = md_path.parent / new_name

    if new_path != md_path:
        if new_path.exists():
            print(f"⚠ Target exists: {new_name}")
            return False
        else:
            md_path.rename(new_path)
            print(f"✓ Renamed to: {new_name}")
            return True

    return True

def main():
    print("=" * 60)
    print("FINAL BATCH RENAME AND UPDATE")
    print("=" * 60)

    # Find all files starting with "用户"
    problem_files = list(SUMMARY_DIR.glob("用户*.md"))

    print(f"\nFound {len(problem_files)} files to process\n")

    success_count = 0
    for md_file in problem_files:
        if process_file(md_file):
            success_count += 1

    print()
    print("=" * 60)
    print(f"Successfully processed {success_count}/{len(problem_files)} files")
    print("=" * 60)

if __name__ == "__main__":
    main()
