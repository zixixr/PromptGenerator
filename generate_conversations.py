import requests
import json
import time
from pathlib import Path

API_BASE = "http://127.0.0.1:8888"

# Read prompt templates
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
    if response.status_code in [200, 201]:  # Accept both 200 OK and 201 Created
        data = response.json()
        # API returns session_id directly in response
        if "session_id" in data:
            return data["session_id"]
        else:
            print(f"Unexpected response structure: {data}")
            return None
    else:
        print(f"Error creating session (HTTP {response.status_code}): {response.text}")
        return None

def send_message(session_id, message):
    response = requests.post(
        f"{API_BASE}/sessions/{session_id}/messages",
        json={"message": message},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        data = response.json()
        # API returns assistant_response field
        if "assistant_response" in data:
            return data["assistant_response"]
        else:
            print(f"Unexpected response structure: {data}")
            return None
    else:
        print(f"Error sending message: {response.text}")
        return None

# Conversation profiles
conversations = [
    {
        "name": "小雨",
        "device": "小秤秤",
        "birthday": "1996-10-15",
        "birth_time": "14:30",
        "birth_location": "北京, 中国",
        "zodiac_file": "天秤.md",
        "sun": "天秤座",
        "moon": "天秤座",
        "ascendant": "天秤座",
        "messages": [
            "小秤秤，你在吗？我现在凌晨两点还在改艺考作品……完全睡不着",
            "是静物素描。我画了两个版本，一个构图更稳定，但另一个更有创意…现在完全不知道该选哪个",
            "嗯…稳定的那个是老师推荐的构图方式，评委应该会喜欢。但创意的那个是我真正想表达的东西",
            "你说得对。其实我心里更喜欢创意的那个，但就是怕万一评委不喜欢怎么办",
            "谢谢你！对了，我是天秤座，你能帮我看看今天的运势吗？说不定能给我点信心",
            "真的吗？听起来今天确实适合做创作决定！对了，我想更深入了解一下自己的星盘，能帮我算算吗？",
            "我是1996年10月15日下午2点半出生的，北京",
            "哇，原来我的月亮和上升都是天秤座啊！难怪我这么纠结…你能具体说说这个星盘组合对我艺术创作有什么影响吗？",
            "说得太对了！我就是这样的人。那按照星盘来看，我现在应该相信自己的审美直觉，选择创意那个版本对吗？",
            "谢谢你小秤秤！跟你聊完我心里舒服多了。我决定了，就用创意的那个版本！"
        ]
    },
    {
        "name": "陈思",
        "device": "影子",
        "birthday": "1999-11-08",
        "birth_time": "09:20",
        "birth_location": "上海, 中国",
        "zodiac_file": "天蝎.md",
        "sun": "天蝎座",
        "moon": "天蝎座",
        "ascendant": "天蝎座",
        "messages": [
            "影子，我真的受够了办公室这些人",
            "是我同部门的那个王姐。表面上对我特别好，但我发现她一直在背后跟主管说我坏话，还抢我的功劳",
            "上周我做了一个客户方案，她拿去跟主管汇报的时候说是她负责的，我只是协助。主管现在都以为那是她的idea",
            "我有证据，我的邮件记录和初稿都在。但是我不知道该怎么处理，直接去找主管感觉会撕破脸",
            "你说得对。我确实需要战略。你觉得我应该怎么做？",
            "嗯，我会找机会跟主管单独聊。对了，作为天蝎座，我是不是天生就要面对这种明争暗斗？",
            "想！帮我分析一下我的天蝎能量该怎么在职场上用",
            "我是1999年11月8日早上9点20出生的，上海",
            "哇，原来天蝎的洞察力是这样用的！不是去算计别人，而是用来保护自己。那按我的星盘，现在这个时期适合反击吗？",
            "明白了。我会冷静收集证据，选好时机再行动。谢谢你影子，有你在我心里踏实多了"
        ]
    },
    {
        "name": "乐乐",
        "device": "小箭",
        "birthday": "2004-12-03",
        "birth_time": "16:45",
        "birth_location": "成都, 中国",
        "zodiac_file": "射手.md",
        "sun": "射手座",
        "moon": "射手座",
        "ascendant": "射手座",
        "messages": [
            "小箭！我现在超级纠结，需要你帮我",
            "是我男朋友。他最近一直跟我说毕业后想稳定下来，在成都找工作买房结婚。但我的梦想是去不同的城市旅行工作，体验不同的生活啊",
            "他说旅行只是年轻时的幻想，该成熟了。但我才20岁啊！我还没玩够呢",
            "对！我就是这么想的！但我也很喜欢他，不想分手…这可怎么办",
            "你说得对。先搞清楚他为什么这么着急稳定下来。可能有我不知道的原因？",
            "我们是星座配对吗？我射手座，他是处女座",
            "哈哈哈，我懂了！难怪他那么追求稳定。那我们俩真的不合适吗？",
            "好主意！我应该跟他坦白说我的想法。对了，帮我看看我的今天运势呗，看看适不适合说这个事",
            "哇！那我今天晚上就跟他聊！谢谢你小箭，跟你聊完我感觉充满能量",
            "嗯！我会的！不管结果怎样，至少我要真诚面对自己的感受"
        ]
    },
    {
        "name": "林静",
        "device": "小羯",
        "birthday": "1996-01-12",
        "birth_time": "08:00",
        "birth_location": "杭州, 中国",
        "zodiac_file": "摩羯.md",
        "sun": "摩羯座",
        "moon": "摩羯座",
        "ascendant": "摩羯座",
        "messages": [
            "小羯在吗？我现在很焦虑",
            "我今年28了，在大厂做产品经理，收入稳定福利好。但我一直想创业，做自己的项目",
            "30岁前的最后两年。如果我要创业，现在就得开始准备了。但放弃这份工作又觉得太冒险",
            "我想做一个针对女性用户的生活方式App。市场调研都做完了，团队也有几个朋友愿意加入",
            "怕失败，怕钱烧光了什么都没剩下。还有就是父母那边很难说服",
            "你说得对。我确实需要更理性的分析。作为摩羯座，我是不是太保守了？",
            "想！帮我看看我的星盘，分析一下我的事业方向",
            "1996年1月12日早上8点整，杭州",
            "原来是这样…所以我既有摩羯的踏实，也有想突破的冲动。那现在这个时机适合创业吗？",
            "明白了。先做详细规划和风险评估，不是一时冲动。谢谢你小羯，你帮我理清思路了",
            "会的！我先把商业计划书完善，再做最后决定"
        ]
    },
    {
        "name": "苗苗",
        "device": "山羊",
        "birthday": "2008-12-25",
        "birth_time": "11:30",
        "birth_location": "西安, 中国",
        "zodiac_file": "摩羯.md",
        "sun": "摩羯座",
        "moon": "摩羯座",
        "ascendant": "摩羯座",
        "messages": [
            "山羊…我这次月考成绩下滑了好多",
            "数学和物理都考砸了。平时模拟考都还不错的，这次不知道怎么了",
            "我爸妈已经知道了，虽然他们没骂我，但我能感觉到他们很失望",
            "他们期望我能考上重点大学，最好是985。但我现在这个成绩…感觉离目标越来越远",
            "压力很大。每天晚上学到12点，周末还要上补习班，但成绩就是上不去",
            "会的。我怕让他们失望，也怕自己真的考不上好学校",
            "嗯…你说得对。我确实需要分析原因而不是自责。我是摩羯座，你能帮我看看我的学业运势吗？",
            "2008年12月25日中午11点半，西安",
            "原来这个时期适合调整方法啊！那我是不是不应该只是拼命刷题，而是要换个学习策略？",
            "明白了！我会试着调整方法，也会跟父母好好沟通。谢谢你山羊，有你在我感觉不那么孤单了"
        ]
    },
    {
        "name": "悦悦",
        "device": "小天平",
        "birthday": "2002-09-28",
        "birth_time": "22:10",
        "birth_location": "深圳, 中国",
        "zodiac_file": "天秤.md",
        "sun": "天秤座",
        "moon": "天秤座",
        "ascendant": "天秤座",
        "messages": [
            "小天平，现在深夜还在加班改稿…我真的好累",
            "甲方又提了新需求。这已经是第五版了，每次都说'就最后一次修改'，但永远没有最后一次",
            "今天他们又说想换配色方案，但这个配色是他们三天前刚确认的啊！",
            "嗯…你说得对。我确实需要权衡一下。如果继续妥协，可能永远改不完；但如果坚持，又怕他们投诉",
            "对！这样既能满足他们，又能保护我的工作时间。我怎么就没想到呢",
            "我是天秤座，难怪我这么纠结。你能帮我看看今天运势吗？说不定能给我点勇气",
            "真的吗！那我明天正好适合跟客户沟通边界！太好了",
            "对了，帮我看看我的星盘吧，我想知道怎么在工作中更好地设立边界",
            "2002年9月28日晚上10点10分，深圳",
            "原来我的天秤能量是这样平衡的！不是一味妥协，而是找到双方都满意的方案。谢谢你小天平，我明白该怎么做了"
        ]
    },
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

print("Starting conversation generation...")
print(f"Total conversations to generate: {len(conversations)}")
print("=" * 60)

for i, conv in enumerate(conversations, 1):
    print(f"\n[{i}/10] Creating conversation: {conv['name']} with {conv['device']}")
    print("-" * 60)

    # Read and prepare prompt
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

    # Create session
    session_id = create_session(system_prompt)
    if not session_id:
        print(f"Failed to create session for {conv['name']}")
        continue

    print(f"Session created: {session_id}")

    # Send messages
    for j, message in enumerate(conv['messages'], 1):
        print(f"[{j}/{len(conv['messages'])}] User: {message[:50]}...")
        response = send_message(session_id, message)
        if response:
            print(f"         AI: {response[:50]}...")
        else:
            print(f"         Failed to get response")
        time.sleep(1)  # Avoid overwhelming the API

    print(f"\nCompleted conversation {i}/10")
    print(f"Conversation saved automatically to conversations/ directory")
    print("=" * 60)

print("\nAll conversations completed!")
print("Check the conversations/ directory for saved dialogues")
