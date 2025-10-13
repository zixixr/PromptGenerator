import requests
import json
import time
from pathlib import Path

API_BASE = "http://127.0.0.1:8888"

def read_prompt(zodiac_file):
    with open(f"D:\\AITOY\\PromptGenerator\\AiMOONPrompt\\{zodiac_file}", "r", encoding="utf-8") as f:
        return f.read()

def replace_variables(template, variables):
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result

def create_session(system_prompt):
    response = requests.post(
        f"{API_BASE}/sessions",
        json={"system_prompt_template": system_prompt, "variables": {}},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code in [200, 201]:
        data = response.json()
        if "session_id" in data:
            return data["session_id"]
    return None

def send_message(session_id, message):
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/messages",
        json={"message": message},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        if "assistant_response" in data:
            return data["assistant_response"]
    return None

# Remaining 4 conversations (7-10)
conversations = [
    {
        "name": "苏晴",
        "device": "流星",
        "birthday": "1997-11-25",
        "birth_time": "19:30",
        "birth_location": "南京, 中国",
        "zodiac_file": "射手.md",
        "sun": "射手座",
        "moon": "射手座",
        "ascendant": "射手座",
        "messages": [
            "流星，我现在遇到瓶颈了",
            "我是自由职业写作者，但最近一个月完全写不出东西来",
            "什么都试过了，换环境、听音乐、看书…但就是没灵感。我开始怀疑自己是不是不适合写作",
            "会啊。我本来就是因为不喜欢朝九晚五才辞职做自由职业的，现在写不出来，收入也没了",
            "对！我就是这种感觉！你懂我。那作为射手座，我该怎么突破这个瓶颈？",
            "好主意！出去走走说不定真的能找到灵感。对了，帮我看看我的今日运势呗",
            "哇，看来今天确实适合出门！那我现在就收拾东西出去转转",
            "对了流星，帮我算算我的星盘吧，看看我这个创作瓶颈期大概什么时候能过去",
            "1997年11月25日晚上7点半，南京",
            "原来如此！所以我不是不适合写作，只是需要新的体验来充电。谢谢你流星，我明白了",
            "会的！我决定明天就去旅行，找找新的灵感！"
        ]
    },
    {
        "name": "江月",
        "device": "小蝎",
        "birthday": "2000-10-30",
        "birth_time": "07:15",
        "birth_location": "武汉, 中国",
        "zodiac_file": "天蝎.md",
        "sun": "天蝎座",
        "moon": "天蝎座",
        "ascendant": "天蝎座",
        "messages": [
            "小蝎，我的实验数据出问题了",
            "做生物实验的，连续三个月的数据都不理想，导师现在对我态度很冷淡",
            "他觉得是我实验操作有问题，但我反复检查过了，操作没有错。我怀疑是实验设计本身有问题",
            "不敢。他是权威，而且脾气不太好。如果我说设计有问题，他肯定会很生气",
            "对…我确实需要证据。但我现在很慌，不知道该从哪里开始查",
            "你说得对！我应该先冷静下来系统排查。作为天蝎座，我的洞察力应该能找到问题所在吧？",
            "想！帮我看看我的星盘，分析一下我现在的学业和导师关系",
            "2000年10月30日早上7点15分，武汉",
            "原来这段时间适合深入研究和找出真相！那我就系统地重新审视整个实验流程",
            "明白了！我会冷静客观地找出问题，然后用数据说话。谢谢你小蝎，你让我找回了信心"
        ]
    },
    {
        "name": "糖糖",
        "device": "粉秤",
        "birthday": "2005-10-10",
        "birth_time": "15:20",
        "birth_location": "广州, 中国",
        "zodiac_file": "天秤.md",
        "sun": "天秤座",
        "moon": "天秤座",
        "ascendant": "天秤座",
        "messages": [
            "粉秤，我现在很迷茫",
            "我是美妆博主，表面上看起来很光鲜，但我感觉自己好空虚",
            "每天拍视频、修图、回复评论…粉丝们都觉得我生活很精彩，但其实我连自己真正喜欢什么都不知道了",
            "害怕。我现在有10万粉丝了，如果我突然改变风格，他们会不会都取关？",
            "你说得对…我确实需要想清楚我到底想要什么。但我真的不知道",
            "会的。除了美妆，我其实还喜欢画画、旅行、读书…但这些好像都不如美妆赚钱",
            "对！我一直在满足粉丝期待，忘了问自己真正想做什么。我是天秤座，你能帮我看看我的星盘吗？看看我的真实自我是什么样的",
            "2005年10月10日下午3点20分，广州",
            "原来我需要在外在美和内在真实之间找到平衡！不是放弃美妆，而是加入更真实的自我表达",
            "谢谢你粉秤！我明白了，我可以继续做美妆内容，但也分享我的其他兴趣。做真实的自己才能真正快乐"
        ]
    },
    {
        "name": "张婷",
        "device": "老山",
        "birthday": "1994-12-20",
        "birth_time": "10:00",
        "birth_location": "北京, 中国",
        "zodiac_file": "摩羯.md",
        "sun": "摩羯座",
        "moon": "摩羯座",
        "ascendant": "摩羯座",
        "messages": [
            "老山，我现在压力很大",
            "我创业做了一个教育科技公司，现在公司现金流很紧张，账上的钱只够撑两个月了",
            "在谈的有几个，但他们都在观望，说要再看看我们的数据。但我现在没时间等了",
            "有考虑过，但我不想就这么放弃。这个项目是我两年的心血",
            "要么赌一把，用剩下的钱做最后的市场推广，要么保守点，削减开支慢慢熬",
            "你说得对。我需要冷静分析。作为摩羯座，我应该更理性才对",
            "对！我应该列出详细的财务规划和风险评估。老山，能帮我看看我的星盘吗？看看我的事业运势",
            "1994年12月20日上午10点，北京",
            "原来现在是考验耐力的时期…所以我不应该冒险all in，而是稳扎稳打熬过这段时间？",
            "明白了！我会制定详细计划，同时继续跟投资人沟通。谢谢你老山，你帮我冷静下来了",
            "会的。我会用理性和耐力度过这个难关"
        ]
    }
]

print("Generating remaining 4 conversations (7-10)...")
print("=" * 60)

for i, conv in enumerate(conversations, 7):
    print(f"\n[{i}/10] Creating conversation: {conv['name']} with {conv['device']}")
    print("-" * 60)

    template = read_prompt(conv['zodiac_file'])
    variables = {
        "device_name": conv['device'],
        "user_name": conv['name'],
        "birthday": conv['birthday'],
        "birth_location": conv['birth_location'],
        "sun": conv['sun'],
        "moon": conv['moon'],
        "ascendant": conv['ascendant'],
        "Q4": "",
        "Q5": "",
        "Q6": "",
        "time": "2025-10-13 02:00",
        "location": conv['birth_location'].split(',')[0]
    }

    system_prompt = replace_variables(template, variables)
    session_id = create_session(system_prompt)

    if not session_id:
        print(f"Failed to create session for {conv['name']}")
        continue

    print(f"Session created: {session_id}")

    for j, message in enumerate(conv['messages'], 1):
        print(f"[{j}/{len(conv['messages'])}] User: {message[:50]}...")
        response = send_message(session_id, message)
        if response:
            print(f"         AI: {response[:50]}...")
        else:
            print(f"         Failed to get response")
        time.sleep(1)

    print(f"\nCompleted conversation {i}/10")
    print("=" * 60)

print("\n✅ All remaining conversations completed!")
print("📁 Check the conversations/ directory for saved dialogues")
