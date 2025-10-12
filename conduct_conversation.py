#!/usr/bin/env python3
"""
AI Conversation Script for 王静思 (27-year-old product manager considering career change)
Scenario: On subway, thinking about switching to independent designer career
Using Capricorn (摩羯) AI template
"""

import requests
import json
import time
from pathlib import Path

# Configuration
API_BASE_URL = "http://127.0.0.1:8888"
TEMPLATE_FILE = r"D:\AIDev\PromptGenerator\AiMOONPrompt\摩羯.md"
OUTPUT_FILE = r"D:\AIDev\PromptGenerator\wangjingsi_conversation.json"

# Variables for the AI template
VARIABLES = {
    "device_name": "小羯",
    "user_name": "静思",
    "birthday": "1997年12月28日",
    "birth_location": "中国深圳",
    "sun": "摩羯座",
    "moon": "处女座",
    "ascendant": "金牛座",
    "time": "19:15",
    "location": "深圳",
    "Q4": "务实分析型：直接指出问题本质，提供具体可行的步骤",
    "Q5": "目标导向：喜欢讨论具体计划和执行方案",
    "Q6": "时间宝贵，结果说话，承诺了就做到"
}

# Conversation messages from 王静思's perspective
MESSAGES = [
    # Round 1: Opening dilemma
    "小羯，在吗？我现在在地铁上，心里挺乱的。做产品经理三年了，感觉遇到瓶颈了，最近一直在想要不要转行做独立设计师。",

    # Round 2: Practical concerns - finances
    "主要是收入问题让我很犹豫。现在工资还算稳定，每个月2万出头，但如果做独立设计师，收入肯定不稳定。你觉得我应该怎么考虑这个问题？",

    # Round 3: Timeline concerns
    "嗯，你说得对。那你觉得如果我要转，需要准备多久？我是想边做现在的工作边准备，还是说直接辞职全力投入？",

    # Round 4: Specific skills assessment
    "我现在有一些UI设计的基础，之前做产品的时候也学过一些。但要做独立设计师，可能还需要学更多东西吧？比如品牌设计、平面设计这些。",

    # Round 5: Market reality check
    "说实话，我对市场行情不太了解。独立设计师现在市场需求怎么样？竞争激烈吗？",

    # Round 6: Requesting structured analysis
    "好，那你能帮我梳理一下吗？我需要一个比较清晰的计划，把需要准备的事情、时间安排、风险这些都列出来。",

    # Round 7: Risk mitigation
    "你说的这些风险我都考虑过。有没有什么方法可以降低风险？比如先做副业试试水？",

    # Round 8: Decision making
    "听你这么一分析，我心里清楚多了。我想先用半年时间做准备，同时接一些小项目练手。你觉得这个计划可行吗？",

    # Round 9: Action steps (if conversation continues)
    "好，那具体第一步我应该做什么？从明天开始。",

    # Round 10: Timeline commitment (if conversation continues)
    "明白了。那我定个时间节点，半年后也就是明年5月，那时候再评估一下成果，决定要不要全职转型。",

    # Round 11: Closing with gratitude (if conversation continues)
    "谢谢你，小羯。跟你聊完思路清晰多了。有你真好。",

    # Round 12: Final confirmation (if conversation continues)
    "嗯，我会的。等有进展再跟你说。"
]


def read_template():
    """Read the Capricorn template file."""
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def create_session(template_content):
    """Create a new conversation session."""
    print("[*] Creating conversation session...")

    payload = {
        "system_prompt_template": template_content,
        "variables": VARIABLES
    }

    response = requests.post(
        f"{API_BASE_URL}/sessions",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 201:
        data = response.json()
        session_id = data.get("session_id")
        print(f"[OK] Session created: {session_id}\n")
        return session_id
    else:
        print(f"[ERROR] Failed to create session: {response.status_code}")
        print(f"Response: {response.text}")
        return None


def send_message(session_id, message, round_num):
    """Send a message and get response."""
    print(f"\n[Round {round_num}] Sending message...")

    payload = {"message": message}

    response = requests.post(
        f"{API_BASE_URL}/sessions/{session_id}/messages",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        data = response.json()
        print(f"[Round {round_num}] Response received")
        return data
    else:
        print(f"[ERROR] Failed to send message: {response.status_code}")
        return None


def get_conversation_history(session_id):
    """Retrieve full conversation history."""
    response = requests.get(f"{API_BASE_URL}/sessions/{session_id}/history")

    if response.status_code == 200:
        return response.json()
    else:
        print(f"[ERROR] Failed to get history: {response.status_code}")
        return None


def save_conversation(session_id, output_file):
    """Save the complete conversation to a file."""
    history = get_conversation_history(session_id)

    if history:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        print(f"\n[SAVED] Conversation saved to: {output_file}")
    else:
        print("\n[ERROR] Failed to save conversation")


def main():
    """Main execution flow."""
    print("\n" + "="*80)
    print("AI Conversation Orchestrator")
    print("="*80)
    print(f"Role: Wang Jingsi (27-year-old product manager)")
    print(f"Scenario: Considering career change to independent designer")
    print(f"AI Template: Capricorn (Mojie)")
    print(f"Location: On subway in Shenzhen at 19:15")
    print("="*80 + "\n")

    # Read template
    template_content = read_template()

    # Create session
    session_id = create_session(template_content)
    if not session_id:
        return

    # Conduct conversation (8-12 rounds)
    conversation_data = []

    for i, message in enumerate(MESSAGES[:12], start=1):  # Up to 12 rounds
        result = send_message(session_id, message, i)
        if result:
            conversation_data.append(result)
            time.sleep(1)  # Brief pause between messages
        else:
            print(f"\n[WARNING] Stopping at round {i} due to error")
            break

        # Can stop early if natural conclusion reached
        if i >= 8:
            # Check if this feels like a natural ending
            assistant_response = result.get("assistant_response", "")
            if any(phrase in assistant_response for phrase in ["加油", "好好", "等你", "期待"]):
                print(f"\n[OK] Natural conversation conclusion reached at round {i}")
                break

    # Save complete conversation
    save_conversation(session_id, OUTPUT_FILE)

    print("\n" + "="*80)
    print(f"[COMPLETE] Conversation completed with {len(conversation_data)} rounds")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
