#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process conversation JSON files and generate marketing documentation
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re

# Directory paths
CONVERSATIONS_DIR = Path("D:/AITOY/PromptGenerator/conversations")
OUTPUT_DIR = Path("D:/AITOY/PromptGenerator/summary/astrology_mcp_showcase")

def load_conversation(filepath: Path) -> Dict:
    """Load a conversation JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_persona_info(data: Dict) -> Dict[str, str]:
    """Extract persona information from conversation data"""
    variables = data.get('variables', {})

    user_name = variables.get('user_name', '未知')
    age = calculate_age(variables.get('birthday', ''))
    sun_sign = variables.get('sun', '未知')
    device_name = variables.get('device_name', '未知')
    occupation = extract_occupation(data)
    scenario = extract_scenario(data)

    return {
        'user_name': user_name,
        'age': age,
        'sun_sign': sun_sign,
        'device_name': device_name,
        'occupation': occupation,
        'scenario': scenario,
        'birthday': variables.get('birthday', ''),
        'birth_location': variables.get('birth_location', ''),
        'moon': variables.get('moon', ''),
        'ascendant': variables.get('ascendant', '')
    }

def calculate_age(birthday: str) -> str:
    """Calculate age from birthday string"""
    if not birthday:
        return '未知'

    # Try different formats
    patterns = [
        r'(\d{4})年?-?(\d{1,2})月?-?(\d{1,2})',
        r'(\d{4})-(\d{1,2})-(\d{1,2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, birthday)
        if match:
            year = int(match.group(1))
            current_year = 2025
            age = current_year - year
            return str(age)

    return '未知'

def extract_occupation(data: Dict) -> str:
    """Extract occupation from conversation context"""
    # Look for occupation keywords in the conversation
    rounds = data.get('rounds', [])

    occupation_keywords = {
        '学生': ['学校', '作业', '考试', '老师', '同学', '月考', '补习班'],
        '设计师': ['设计', 'UI', '品牌', '作品集', '客户'],
        '产品经理': ['产品', '需求', '项目', 'PM'],
        '程序员': ['代码', '编程', '开发', 'bug'],
        '上班族': ['公司', '领导', '同事', '加班'],
    }

    text = ' '.join([r.get('user_message', '') + ' ' + r.get('assistant_response', '') for r in rounds[:3]])

    for occupation, keywords in occupation_keywords.items():
        if any(keyword in text for keyword in keywords):
            return occupation

    return '用户'

def extract_scenario(data: Dict) -> str:
    """Extract scenario from conversation context"""
    rounds = data.get('rounds', [])
    if not rounds:
        return '日常对话'

    first_messages = ' '.join([rounds[i].get('user_message', '') for i in range(min(2, len(rounds)))])

    # Scenario patterns
    scenarios = {
        '考试压力': ['考试', '成绩', '考砸', '月考', '分数'],
        '职业规划': ['转行', '辞职', '职业', '工作', '副业'],
        '人际关系': ['朋友', '同事', '关系', '相处'],
        '个人成长': ['目标', '计划', '改变', '成长'],
        '情感困扰': ['失恋', '感情', '喜欢', '分手'],
        '深夜倾诉': ['睡不着', '深夜', '难过'],
    }

    for scenario, keywords in scenarios.items():
        if any(keyword in first_messages for keyword in keywords):
            return scenario

    return '日常对话'

def has_mcp_tool_usage(data: Dict) -> bool:
    """Check if conversation uses MCP tools"""
    rounds = data.get('rounds', [])

    mcp_keywords = [
        '星盘', '运势', '配对', '时尚', '穿搭',
        'natal_chart', 'horoscope', 'synastry', 'compatibility', 'fashion'
    ]

    for round in rounds:
        response = round.get('assistant_response', '')
        if any(keyword in response for keyword in mcp_keywords):
            return True

    return False

def scan_all_conversations() -> List[Dict]:
    """Scan all conversation files and extract metadata"""
    results = []

    for filepath in CONVERSATIONS_DIR.glob('*.json'):
        try:
            data = load_conversation(filepath)
            persona = extract_persona_info(data)

            results.append({
                'filename': filepath.name,
                'filepath': filepath,
                'persona': persona,
                'rounds_count': len(data.get('rounds', [])),
                'has_mcp': has_mcp_tool_usage(data),
                'data': data
            })
        except Exception as e:
            print(f"Error processing {filepath.name}: {e}")

    return results

def main():
    """Main processing function"""
    print("Scanning conversation files...")
    conversations = scan_all_conversations()

    print(f"\nTotal conversations: {len(conversations)}")
    print(f"With MCP tools: {sum(1 for c in conversations if c['has_mcp'])}")

    # Print summary
    print("\n=== Conversation Summary ===")
    for i, conv in enumerate(conversations, 1):
        persona = conv['persona']
        print(f"{i}. {persona['user_name']} ({persona['age']}岁) - {persona['occupation']} - {persona['scenario']} - {conv['rounds_count']}轮 - MCP:{conv['has_mcp']}")

    # Export summary JSON
    output_file = OUTPUT_DIR / '_conversations_metadata.json'
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    export_data = [{
        'filename': c['filename'],
        'user_name': c['persona']['user_name'],
        'age': c['persona']['age'],
        'occupation': c['persona']['occupation'],
        'scenario': c['persona']['scenario'],
        'zodiac': c['persona']['sun_sign'],
        'device_name': c['persona']['device_name'],
        'rounds': c['rounds_count'],
        'has_mcp': c['has_mcp']
    } for c in conversations]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"\nMetadata exported to: {output_file}")

if __name__ == '__main__':
    main()
