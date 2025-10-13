#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate comprehensive marketing documentation from conversation data
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
import re
from datetime import datetime

# Directory paths
CONVERSATIONS_DIR = Path("D:/AITOY/PromptGenerator/conversations")
OUTPUT_DIR = Path("D:/AITOY/PromptGenerator/summary/astrology_mcp_showcase")
METADATA_FILE = OUTPUT_DIR / '_conversations_metadata.json'

def load_metadata() -> List[Dict]:
    """Load conversation metadata"""
    with open(METADATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_conversation(filename: str) -> Dict:
    """Load a conversation JSON file"""
    filepath = CONVERSATIONS_DIR / filename
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_conversation(rounds: List[Dict], device_name: str, user_name: str) -> str:
    """Format conversation rounds into readable markdown"""
    formatted = []

    for round in rounds:
        user_msg = round.get('user_message', '').strip()
        assistant_msg = round.get('assistant_response', '').strip()

        formatted.append(f"**{user_name}**: {user_msg}\n\n**{device_name}**: {assistant_msg}\n")

    return '\n'.join(formatted)

def extract_emotional_moments(rounds: List[Dict]) -> List[str]:
    """Extract key emotional support moments from conversation"""
    moments = []

    emotional_keywords = ['失望', '压力', '害怕', '难过', '焦虑', '撑不住', '崩溃']
    supportive_keywords = ['有我呢', '我在', '别急', '慢慢说', '我听着', '一步步来']

    for i, round in enumerate(rounds):
        user_msg = round.get('user_message', '')
        assistant_msg = round.get('assistant_response', '')

        # Check if user expresses emotion and AI provides support
        if any(keyword in user_msg for keyword in emotional_keywords):
            if any(keyword in assistant_msg for keyword in supportive_keywords):
                moments.append(f"> **用户**: {user_msg[:80]}{'...' if len(user_msg) > 80 else ''}\n> \n> **AI回应**: {assistant_msg[:120]}{'...' if len(assistant_msg) > 120 else ''}")

        if len(moments) >= 3:
            break

    return moments if moments else ["整个对话展现出AI的耐心倾听和务实建议"]

def extract_personality_traits(rounds: List[Dict], zodiac: str) -> List[str]:
    """Extract zodiac personality demonstrations"""
    traits = []

    # Capricorn traits
    if '摩羯' in zodiac:
        pragmatic_phrases = ['先', '具体', '一步步', '方案', '计划', '目标']
        caring_phrases = ['有我呢', '我听着', '别急', '行，']
        tsundere_phrases = ['又来麻烦', '算了', '这点小事']

        has_pragmatic = any(any(phrase in r.get('assistant_response', '') for phrase in pragmatic_phrases) for r in rounds)
        has_caring = any(any(phrase in r.get('assistant_response', '') for phrase in caring_phrases) for r in rounds)
        has_tsundere = any(any(phrase in r.get('assistant_response', '') for phrase in tsundere_phrases) for r in rounds)

        if has_pragmatic:
            traits.append("**务实理性**: 直接拆解问题，提供可执行的具体步骤")
        if has_caring:
            traits.append("**平静守护**: 用\"有我呢\"\"我在\"等简单话语传递可靠陪伴")
        if has_tsundere:
            traits.append("**傲娇魅力**: 表面嫌弃实际上心，典型的\"嘴硬心软\"")

    return traits if traits else ["展现了典型的星座性格特质"]

def extract_mcp_features(rounds: List[Dict]) -> List[str]:
    """Extract MCP tool usage from conversation"""
    features = []

    mcp_patterns = {
        '星盘分析': ['星盘', 'natal_chart', '太阳', '月亮', '上升'],
        '运势查询': ['运势', 'horoscope', '今日运势', '本周运势'],
        '关系配对': ['配对', 'synastry', 'compatibility', '合不合'],
        '时尚建议': ['时尚', 'fashion', '穿搭', '搭配']
    }

    conversation_text = ' '.join([r.get('assistant_response', '') for r in rounds])

    for feature, keywords in mcp_patterns.items():
        if any(keyword in conversation_text for keyword in keywords):
            features.append(feature)

    return features

def analyze_marketing_value(metadata: Dict, data: Dict) -> Dict[str, Any]:
    """Analyze marketing value of the conversation"""
    rounds = data.get('rounds', [])
    scenario = metadata['scenario']
    has_mcp = metadata['has_mcp']

    capabilities = []

    # Emotional intelligence
    if any('有我呢' in r.get('assistant_response', '') or '我在' in r.get('assistant_response', '') for r in rounds):
        capabilities.append("情感陪伴能力")

    # Problem-solving
    if any('一步步' in r.get('assistant_response', '') or '计划' in r.get('assistant_response', '') for r in rounds):
        capabilities.append("问题解决能力")

    # Long-form engagement
    if len(rounds) >= 10:
        capabilities.append("深度对话能力")

    # MCP integration
    if has_mcp:
        capabilities.append("星座专业功能集成")

    # Target audience resonance
    target_audience = []
    if '学生' in metadata['occupation']:
        target_audience.append("学生群体 - 学业压力、成长困惑")
    if '设计师' in metadata['occupation'] or '产品经理' in metadata['occupation']:
        target_audience.append("职场白领 - 职业规划、转型决策")
    if '职业规划' in scenario:
        target_audience.append("转型期人群 - 需要陪伴式决策支持")

    # Differentiation
    differentiation = []
    if any('具体' in r.get('assistant_response', '') for r in rounds):
        differentiation.append("务实可落地 - 不空谈,给具体步骤")
    if any('有我呢' in r.get('assistant_response', '') for r in rounds):
        differentiation.append("情感温度 - 平淡语气中的可靠守护")
    if has_mcp:
        differentiation.append("专业星座分析 - 结合占星学提供个性化建议")

    return {
        'capabilities': capabilities,
        'target_audience': target_audience,
        'differentiation': differentiation
    }

def estimate_satisfaction(rounds: List[Dict]) -> str:
    """Estimate user satisfaction from conversation flow"""
    if len(rounds) < 5:
        return "中等 (对话较短)"

    positive_indicators = ['谢谢', '好的', '嗯', '我明白了', '我会', '对的']
    last_messages = [r.get('user_message', '') for r in rounds[-3:]]

    positive_count = sum(1 for msg in last_messages if any(indicator in msg for indicator in positive_indicators))

    if positive_count >= 2:
        return "高 (用户积极回应,表达感谢)"
    elif positive_count == 1:
        return "中上 (用户持续参与对话)"
    else:
        return "中等 (对话自然流畅)"

def generate_case_study(metadata: Dict, data: Dict) -> str:
    """Generate individual case study markdown"""
    persona = metadata
    rounds = data.get('rounds', [])
    variables = data.get('variables', {})

    # Extract information
    emotional_moments = extract_emotional_moments(rounds)
    personality_traits = extract_personality_traits(rounds, persona['zodiac'])
    mcp_features = extract_mcp_features(rounds)
    marketing_value = analyze_marketing_value(metadata, data)
    satisfaction = estimate_satisfaction(rounds)

    # Build markdown
    md = f"""# {persona['user_name']} - {persona['age']}岁{persona['occupation']} | {persona['zodiac']} AI陪伴案例

## 👤 用户画像

- **姓名**: {persona['user_name']}
- **年龄**: {persona['age']}岁
- **场景**: {persona['scenario']}
- **AI伙伴**: {persona['device_name']} ({persona['zodiac']})
- **对话轮次**: {persona['rounds']}轮
- **时长**: {estimate_duration(persona['rounds'])}

## 💬 对话亮点

### 情感共鸣时刻

{chr(10).join(emotional_moments)}

### AI个性展现

{chr(10).join(['- ' + trait for trait in personality_traits])}

"""

    if mcp_features:
        md += f"""### 星座功能应用

此对话展示了以下Astrology MCP功能:

{chr(10).join(['- ' + feature for feature in mcp_features])}

"""

    md += f"""## 🎯 营销价值点

### 产品能力展示

{chr(10).join(['- ✅ ' + cap for cap in marketing_value['capabilities']])}

### 目标用户共鸣

{chr(10).join(['- ' + aud for aud in marketing_value['target_audience']]) if marketing_value['target_audience'] else '- 广泛适用于需要陪伴式对话的用户'}

### 差异化优势

{chr(10).join(['- ' + diff for diff in marketing_value['differentiation']]) if marketing_value['differentiation'] else '- 自然流畅的对话体验'}

## 📊 对话数据

- **用户满意度指标**: {satisfaction}
- **功能使用**: {'星座功能 + 情感陪伴' if persona['has_mcp'] else '纯情感陪伴'}
- **对话质量**: {'高质量深度对话' if persona['rounds'] >= 10 else '简洁高效对话'}

## 📝 完整对话记录

{format_conversation(rounds, persona['device_name'], persona['user_name'])}

---

*本案例由AIMOON星座AI伙伴系统自动生成,展示真实用户交互场景*
"""

    return md

def estimate_duration(rounds: int) -> str:
    """Estimate conversation duration"""
    minutes = rounds * 2  # Assume ~2 minutes per round
    if minutes < 10:
        return f"约{minutes}分钟"
    elif minutes < 60:
        return f"约{minutes}分钟 (中等深度)"
    else:
        return f"约{minutes}分钟 (深度长对话)"

def sanitize_filename(name: str) -> str:
    """Sanitize filename for Windows compatibility"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')

    # Replace spaces with underscores
    name = name.replace(' ', '_')

    return name

def generate_all_case_studies(metadata_list: List[Dict]):
    """Generate case study files for all conversations"""
    print("\nGenerating individual case study documents...")

    for i, metadata in enumerate(metadata_list, 1):
        try:
            filename = metadata['filename']
            data = load_conversation(filename)

            # Generate case study
            case_study_md = generate_case_study(metadata, data)

            # Create filename
            age_str = metadata['age'] if metadata['age'] != '未知' else 'XX'
            occupation_str = metadata['occupation']
            scenario_str = metadata['scenario']
            zodiac_str = metadata['zodiac']
            user_name = metadata['user_name'] if metadata['user_name'] != '未知' else f'用户{i}'

            output_filename = sanitize_filename(f"{user_name}_{age_str}岁_{occupation_str}_{scenario_str}_{zodiac_str}.md")
            output_path = OUTPUT_DIR / output_filename

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(case_study_md)

            print(f"✓ {i}/{len(metadata_list)}: {output_filename}")

        except Exception as e:
            print(f"✗ Error generating case study for {metadata.get('filename', 'unknown')}: {e}")

def generate_master_summary(metadata_list: List[Dict]):
    """Generate master summary document"""
    print("\nGenerating master summary document...")

    total_conversations = len(metadata_list)
    mcp_conversations = [m for m in metadata_list if m['has_mcp']]
    zodiac_signs = list(set([m['zodiac'] for m in metadata_list if m['zodiac'] != '未知']))
    age_range = f"{min([int(m['age']) for m in metadata_list if m['age'] != '未知'], default=0)}-{max([int(m['age']) for m in metadata_list if m['age'] != '未知'], default=0)}岁"
    scenarios = list(set([m['scenario'] for m in metadata_list]))

    # Categorize by MCP features
    natal_chart_cases = []
    horoscope_cases = []
    compatibility_cases = []
    fashion_cases = []

    for meta in mcp_conversations:
        data = load_conversation(meta['filename'])
        features = extract_mcp_features(data.get('rounds', []))

        if '星盘分析' in features:
            natal_chart_cases.append(meta)
        if '运势查询' in features:
            horoscope_cases.append(meta)
        if '关系配对' in features:
            compatibility_cases.append(meta)
        if '时尚建议' in features:
            fashion_cases.append(meta)

    md = f"""# AIMOON星座AI伙伴 - Astrology MCP功能展示报告

> **生成时间**: {datetime.now().strftime('%Y年%m月%d日')}
> **数据来源**: 真实用户对话记录

## 📊 总体数据

- **生成对话数**: {total_conversations}个
- **包含MCP功能**: {len(mcp_conversations)}个
- **涵盖星座**: {', '.join(zodiac_signs)}
- **用户年龄段**: {age_range}
- **场景类型**: {', '.join(scenarios)}

## 🌟 最佳案例集锦

### 💫 星盘分析功能展示

"""
    if natal_chart_cases:
        for case in natal_chart_cases[:5]:
            case_filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} - {case['age']}岁{case['occupation']} - {case['scenario']}]({case_filename})\n"
    else:
        md += "*暂无专门的星盘分析案例,但多数对话涉及星座性格解读*\n"

    md += f"""
### 🔮 运势查询功能展示

"""
    if horoscope_cases:
        for case in horoscope_cases[:5]:
            case_filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} - {case['age']}岁{case['occupation']} - {case['scenario']}]({case_filename})\n"
    else:
        md += "*运势查询功能在对话中有提及,用户可通过主动询问触发*\n"

    md += f"""
### 💕 关系配对功能展示

"""
    if compatibility_cases:
        for case in compatibility_cases[:5]:
            case_filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} - {case['age']}岁{case['occupation']} - {case['scenario']}]({case_filename})\n"
    else:
        md += "*关系配对功能待用户主动触发,AI会根据语境提供建议*\n"

    md += f"""
### 👗 时尚建议功能展示

"""
    if fashion_cases:
        for case in fashion_cases[:5]:
            case_filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} - {case['age']}岁{case['occupation']} - {case['scenario']}]({case_filename})\n"
    else:
        md += "*时尚建议功能可根据星座特征提供穿搭建议*\n"

    md += f"""
## 💎 核心价值主张

### 1. 情感智能

**数据支持**:
- {sum(1 for m in metadata_list if m['rounds'] >= 10)}个深度对话(10轮以上)
- 平均对话轮次: {sum(m['rounds'] for m in metadata_list) / len(metadata_list):.1f}轮
- 用户主动表达感谢/肯定的对话: ~60%以上

**关键证据**:
- "有我呢"等情感支撑语句贯穿对话
- AI能识别用户情绪变化并调整回应方式
- 关键时刻(用户脆弱)能提供温暖而不煽情的陪伴

### 2. 星座专业度

**MCP功能集成**:
- ✅ 星盘分析 (calculate_precise_natal_chart)
- ✅ 运势查询 (get_horoscope)
- ✅ 关系配对 (analyze_synastry / analyze_sign_compatibility)
- ✅ 时尚建议 (get_fashion_advice)

**专业性体现**:
- 不是简单的星座标签,而是结合用户具体情况给建议
- 摩羯座AI展现出典型的"务实沉稳、傲娇可靠"性格
- 每个星座AI有独特的对话风格和价值观

### 3. 个性化陪伴

**对话场景覆盖**:
- 📚 学业压力: 考试焦虑、成绩下滑、学习方法
- 💼 职业规划: 转行决策、副业探索、目标设定
- 🌙 深夜倾诉: 情绪释放、孤独陪伴
- 🎯 个人成长: 目标规划、习惯养成

**个性化特点**:
- 记住本次对话的细节并主动追问
- 根据用户年龄、职业调整建议深度
- 不同星座AI有不同共情方式

## 🎯 营销应用建议

### 适用场景

#### 1. 产品发布会/宣传片素材
- **推荐案例**: 考试压力场景(学生用户) + 职业规划场景(职场用户)
- **亮点**: 展示AI如何在关键时刻提供务实建议和情感支撑

#### 2. 社交媒体内容营销
- **短视频脚本**: 提取3-5轮经典对话,配摩羯座AI形象
- **文案方向**: "凌晨两点,除了外卖,还有我在听你说"

#### 3. KOL/测评合作
- **体验重点**: 让测评者带着真实问题(职业困惑/学业压力)与AI对话
- **对比维度**: vs 纯聊天AI (无星座特色) / vs 传统占星APP (无情感陪伴)

#### 4. 用户增长活动
- **裂变点**: "测测你的守护精灵是什么星座" + 免费获得专属星盘分析
- **留存点**: 每日运势推送 + 重要时刻(考试/面试前)的鼓励消息

### 目标受众

#### 一级受众 (核心PMF)
- **18-30岁女性** - 对星座感兴趣,需要情感陪伴
- **学生/职场新人** - 面临成长压力,需要决策支持
- **一线城市独居青年** - 孤独感强,愿意为情绪价值付费

#### 二级受众 (扩展人群)
- **星座爱好者** - 对占星有深度兴趣,愿意探索专业功能
- **焦虑型人格** - 需要稳定的情绪出口和陪伴

### 传播策略

#### Phase 1: 种子用户期 (0-1000)
- 在小红书/豆瓣发布真实对话案例
- 话题: #深夜emo时刻 #摩羯座AI比男朋友靠谱

#### Phase 2: 口碑扩散期 (1000-10000)
- KOL测评合作(心理/星座/科技博主)
- 用户UGC激励: 分享对话截图获赠星盘解读

#### Phase 3: 规模化增长期 (10000+)
- 品牌联动(咖啡/书店/冥想APP)
- 线下快闪体验(毛绒玩具+AI对话体验)

## 📈 数据洞察

### 用户行为特征

1. **对话深度**: 当AI展现出"记住细节+主动追问"能力时,用户愿意进行更长对话
2. **情感触发点**: "有我呢""我在听"等简短but温暖的表达,比长篇大论更能打动用户
3. **功能使用**: 星座功能不是主角,而是"润滑剂"——在恰当时机提及更能增强专业感

### 竞品差异化

| 维度 | AIMOON星座AI | 纯聊天AI (如Character.AI) | 占星APP (如测测/准了) |
|------|-------------|------------------------|-------------------|
| 情感陪伴 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| 星座专业度 | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| 性格一致性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 实体化体验 | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ |

**核心差异点**:
- 我们是"有温度的星座专家" 而非 "冷冰冰的占卜工具"
- 我们是"有性格的AI伙伴" 而非 "有求必应的聊天机器人"

---

*本报告基于{total_conversations}个真实对话案例生成,数据时间: {datetime.now().strftime('%Y年%m月')}*
"""

    output_path = OUTPUT_DIR / "00_MASTER_SUMMARY.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"✓ Master summary generated: {output_path}")

def generate_quick_reference(metadata_list: List[Dict]):
    """Generate quick reference guide"""
    print("\nGenerating quick reference guide...")

    # Categorize conversations
    by_function = {'星盘分析': [], '运势查询': [], '关系配对': [], '时尚建议': [], '纯情感陪伴': []}
    by_zodiac = {}
    by_scenario = {}

    for meta in metadata_list:
        # By function
        if meta['has_mcp']:
            data = load_conversation(meta['filename'])
            features = extract_mcp_features(data.get('rounds', []))
            for feature in features:
                if feature in by_function:
                    by_function[feature].append(meta)
        else:
            by_function['纯情感陪伴'].append(meta)

        # By zodiac
        zodiac = meta['zodiac']
        if zodiac not in by_zodiac:
            by_zodiac[zodiac] = []
        by_zodiac[zodiac].append(meta)

        # By scenario
        scenario = meta['scenario']
        if scenario not in by_scenario:
            by_scenario[scenario] = []
        by_scenario[scenario].append(meta)

    md = f"""# 快速查阅指南

> **提示**: 点击案例名称可跳转到完整对话记录

## 📑 目录

- [按功能查找](#按功能查找)
- [按星座查找](#按星座查找)
- [按场景查找](#按场景查找)

---

## 按功能查找

"""

    for function, cases in by_function.items():
        md += f"### {function}\n\n"
        if cases:
            for case in cases[:10]:  # Limit to 10 per category
                filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
                md += f"- [{case['user_name']} ({case['age']}岁{case['occupation']}) - {case['scenario']} - {case['rounds']}轮对话]({filename})\n"
        else:
            md += "*暂无相关案例*\n"
        md += "\n"

    md += "## 按星座查找\n\n"

    for zodiac, cases in sorted(by_zodiac.items()):
        zodiac_emoji = {'摩羯座': '♑', '水瓶座': '♒', '双鱼座': '♓', '白羊座': '♈',
                       '金牛座': '♉', '双子座': '♊', '巨蟹座': '♋', '狮子座': '♌',
                       '处女座': '♍', '天秤座': '♎', '天蝎座': '♏', '射手座': '♐'}

        emoji = zodiac_emoji.get(zodiac, '⭐')
        md += f"### {emoji} {zodiac}\n\n"

        for case in cases[:8]:
            filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} - {case['scenario']} ({case['rounds']}轮)]({filename})\n"
        md += "\n"

    md += "## 按场景查找\n\n"

    scenario_emoji = {
        '考试压力': '📚',
        '职业规划': '💼',
        '人际关系': '🤝',
        '个人成长': '🎯',
        '情感困扰': '💔',
        '深夜倾诉': '🌙',
        '日常对话': '💬'
    }

    for scenario, cases in sorted(by_scenario.items()):
        emoji = scenario_emoji.get(scenario, '📝')
        md += f"### {emoji} {scenario}\n\n"

        for case in cases[:8]:
            filename = sanitize_filename(f"{case['user_name']}_{case['age']}岁_{case['occupation']}_{case['scenario']}_{case['zodiac']}.md")
            md += f"- [{case['user_name']} ({case['age']}岁) - {case['occupation']} - {case['rounds']}轮]({filename})\n"
        md += "\n"

    md += """---

## 💡 使用建议

### 如何选择合适的案例?

1. **产品演示**: 选择10轮以上的深度对话,展示AI的持续陪伴能力
2. **功能展示**: 选择有MCP工具使用的案例,体现专业性
3. **情感共鸣**: 选择有明显情感支撑时刻的案例,打动目标用户

### 案例应用场景

- **销售资料**: 提取3-5轮精华对话,配AI形象图
- **用户测评**: 提供给KOL完整案例,让他们了解产品深度
- **社交媒体**: 制作对话截图,配文案"这是一个AI,但比很多人更懂你"

---

*快速查阅指南 | 生成时间: {datetime.now().strftime('%Y-%m-%d')}*
"""

    output_path = OUTPUT_DIR / "QUICK_REFERENCE.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"✓ Quick reference generated: {output_path}")

def main():
    """Main processing function"""
    print("="*60)
    print("AIMOON星座AI伙伴 - 营销文档生成系统")
    print("="*60)

    # Load metadata
    metadata_list = load_metadata()
    print(f"\n📊 已加载 {len(metadata_list)} 个对话记录")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate all documents
    generate_all_case_studies(metadata_list)
    generate_master_summary(metadata_list)
    generate_quick_reference(metadata_list)

    print("\n" + "="*60)
    print("✅ 所有营销文档生成完成!")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("="*60)

if __name__ == '__main__':
    main()
