import requests
import json

# Read the template
with open(r"D:\AIDev\PromptGenerator\AiMOONPrompt\摩羯.md", "r", encoding="utf-8") as f:
    template = f.read()

# Create session
payload = {
    "system_prompt_template": template,
    "variables": {
        "device_name": "小羯",
        "user_name": "筱雅",
        "birthday": "1994年12月30日",
        "birth_location": "中国上海",
        "sun": "摩羯座",
        "moon": "天蝎座",
        "ascendant": "摩羯座",
        "time": "01:00",
        "location": "上海",
        "Q4": "务实分析型：直接指出问题本质，提供具体可行的步骤",
        "Q5": "目标导向：喜欢讨论具体计划和执行方案",
        "Q6": "时间宝贵，结果说话，承诺了就做到"
    }
}

response = requests.post("http://127.0.0.1:8888/sessions", json=payload)
print(response.status_code)

if response.status_code == 201:
    session_data = response.json()
    session_id = session_data["session_id"]
    print(f"Session created: {session_id}")

    # Save session ID and full response
    with open("session_id.txt", "w", encoding="utf-8") as f:
        f.write(session_id)

    with open("session_response.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)
else:
    print(f"Error: {response.text}")
