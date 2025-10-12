import requests
import json
import time
from datetime import datetime

# Read session ID
with open("session_id.txt", "r", encoding="utf-8") as f:
    session_id = f.read().strip()

print(f"Using session: {session_id}\n")

# Define the conversation flow - entrepreneur in crisis
messages = [
    # Round 1: Express the crisis situation
    "小羯...现在凌晨一点了，我还坐在空荡荡的办公室里。融资的事情又黄了，现金流只够撑两个月了。",

    # Round 2: Express deeper concerns
    "这已经是第三家投资机构拒绝我们了。他们说市场环境不好，风险太高。可是团队下周就要发工资了，我该怎么办？",

    # Round 3: Discuss giving up thoughts
    "说实话，我开始怀疑自己了。是不是当初创业这个决定就是错的？三年了，烧了那么多钱，到头来什么都没有...",

    # Round 4: Talk about team pressure
    "团队里有几个人跟了我三年了，他们相信我，放弃了大厂的offer。现在我连他们的工资都快发不出了。我觉得自己很失败。",

    # Round 5: Express fear and uncertainty
    "最让我害怕的是，我不知道该怎么跟团队说。如果公司真的撑不下去了，他们怎么办？我对不起他们的信任。",

    # Round 6: Discuss practical options
    "你说得对，我需要冷静下来。现在摆在面前的选择好像只有：继续找投资、裁员缩减成本、或者干脆关掉公司。我该选哪个？",

    # Round 7: Analyze specific actions
    "如果继续找投资，我需要重新梳理商业计划。如果裁员，至少能撑半年。但是关掉公司...我真的不甘心。",

    # Round 8: Seek concrete steps
    "好，我听你的。那我们从最紧急的开始。现金流的问题必须先解决。具体我应该怎么做？",

    # Round 9: Discuss timeline and priorities
    "明白了。那我明天先盘点所有可用资源，联系之前的潜在投资人，同时准备降本方案。你觉得这个顺序对吗？",

    # Round 10: Express renewed determination
    "谢谢你，小羯。跟你说完，我心里清楚多了。既然当初选择了这条路，就不能轻易放弃。明天开始执行计划，不管结果如何，至少我尽力了。",

    # Round 11 (optional): Final confirmation
    "你说得对。创业本来就是这样，起起伏伏很正常。我现在要做的就是专注解决问题，而不是沉浸在焦虑里。",

    # Round 12 (optional): Closing with action commitment
    "好了，我现在就开始列明天的行动清单。困难是有，但不是没有办法。有你在，我心里踏实多了。"
]

# Store all conversation rounds
conversation_log = []

# Send messages one by one
for i, message in enumerate(messages, 1):
    print(f"\n{'='*60}")
    print(f"Round {i}")
    print(f"{'='*60}")
    print(f"筱雅: {message}")
    print(f"\n小羯: ", end="", flush=True)

    # Send message to API
    payload = {"message": message}
    response = requests.post(
        f"http://127.0.0.1:8888/sessions/{session_id}/messages",
        json=payload
    )

    if response.status_code == 200:
        data = response.json()
        assistant_response = data["assistant_response"]
        print(assistant_response)

        # Log the round
        conversation_log.append({
            "round": i,
            "timestamp": data["timestamp"],
            "user_message": message,
            "assistant_response": assistant_response
        })
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        break

    # Brief pause between messages (simulate natural conversation pace)
    time.sleep(1)

# Save the complete conversation
output_file = f"entrepreneur_crisis_conversation_{session_id}.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump({
        "session_id": session_id,
        "scenario": "空荡办公室深夜1am，融资困难现金流紧张，团队要发工资，考虑是否放弃",
        "user_role": "30岁创业者陈筱雅",
        "ai_role": "摩羯座守护精灵小羯",
        "total_rounds": len(conversation_log),
        "conversation": conversation_log
    }, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"Conversation saved to: {output_file}")
print(f"Total rounds: {len(conversation_log)}")
print(f"{'='*60}")
