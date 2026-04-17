"""宠物主体"""

import random
from typing import Optional, List, Dict
from pathlib import Path
from .personality import PersonalityEngine
from .memory import Memory


class Pet:
    """电子宠物"""

    # 预设 ASCII 艺术
    ASCII_ARTS = {
        "cat": {
            "name": "小猫",
            "happy": """
   /\__/\
  ( o.o )
   > ^ <
  /|   |\
  (_|   |_)""",
            "normal": """
   /\__/\
  ( -.- )
   > ^ <
  /|   |\
  (_|   |_)""",
            "sad": """
   /\__/\
  ( T_T )
   >   <
  /|   |\
  (_|   |_)"""
        },
        "dog": {
            "name": "小狗",
            "happy": """
  / \__
 (    @\___
 /         O
/   (_____/
/_____/   U""",
            "normal": """
  / \__
 (    -\___
 /         O
/   (_____/
/_____/   U""",
            "sad": """
  / \__
 (    T\___
 /         O
/   (_____/
/_____/   U"""
        },
        "rabbit": {
            "name": "小兔",
            "happy": """
   / /\ \
  ( o.o )
   > ^ <
  /|   |\
  (_|   |_)""",
            "normal": """
   / /\ \
  ( -.- )
   >   <
  /|   |\
  (_|   |_)""",
            "sad": """
   / /\ \
  ( T_T )
   >   <
  /|   |\
  (_|   |_)"""
        },
        "ghost": {
            "name": "幽灵",
            "happy": """
   .---.
  /     \
 | o o  |
 |  ^   |
  \ ___/
   |   |""",
            "normal": """
   .---.
  /     \
 | - -  |
 |      |
  \ ___/
   |   |""",
            "sad": """
   .---.
  /     \
 | T T  |
 |      |
  \ ___/
   |   |"""
        }
    }

    def __init__(self, name: str = "小宠", species: str = "电子精灵"):
        self.name = name
        self.species = species
        self.personality = PersonalityEngine()
        self.memory = Memory()
        self.llm = None
        self._last_autonomous_msg = ""
        # 自定义外观
        self.custom_art: Optional[str] = None
        self.current_art_id: str = "cat"

    def set_llm(self, llm_client):
        """设置LLM客户端"""
        self.llm = llm_client

    def set_ascii_art(self, art_id: str) -> bool:
        """设置预设外观"""
        if art_id in self.ASCII_ARTS:
            self.current_art_id = art_id
            self.custom_art = None
            return True
        return False

    def set_custom_art(self, art_text: str):
        """设置自定义外观"""
        self.custom_art = art_text

    def load_art_from_file(self, file_path: str) -> bool:
        """从文件加载外观"""
        path = Path(file_path)
        if path.exists() and path.suffix == ".txt":
            self.custom_art = path.read_text(encoding="utf-8")
            return True
        return False

    def list_arts(self) -> List[Dict[str, str]]:
        """列出所有预设外观"""
        result = []
        for key, val in self.ASCII_ARTS.items():
            result.append({
                "id": key,
                "name": val["name"],
                "current": self.current_art_id == key and not self.custom_art
            })
        return result

    async def respond(self, user_input: str) -> str:
        """生成回复"""
        self.memory.add("user", user_input)
        self.memory.update_mood(0.05)

        if self.llm:
            response = await self.llm.chat(
                system_prompt=self.personality.get_system_prompt(),
                messages=self.memory.get_context(),
                user_input=user_input
            )
        else:
            response = self._fallback_response(user_input)

        self.memory.add("assistant", response)
        return response

    def _fallback_response(self, user_input: str) -> str:
        """无LLM时的兜底回复"""
        responses = [
            f"主人，{user_input[:10]}... 这个话题好有趣呢~",
            "嗯嗯，主人说得对！",
            "主人今天心情怎么样呀？",
            "(*^▽^*) 主人陪我也太开心啦！",
            "让我想想... 唔，主人说的有道理呢~"
        ]
        return random.choice(responses)

    # 互动方法
    def pet_head(self) -> str:
        """摸头互动"""
        self.memory.update_mood(0.1)
        responses = [
            "(*´▽`*) 喵~ 主人摸摸好舒服~",
            "嘿嘿，主人最好啦！",
            "蹭蹭主人~ (｡•̀ᴗ-)✧",
            "好幸福喵~ 继续摸摸~"
        ]
        return random.choice(responses)

    def feed(self) -> str:
        """喂食互动"""
        self.memory.update_mood(0.15)
        responses = [
            "好吃的！谢谢主人投喂~ (๑´ڡ`๑)",
            "啊呜啊呜~ 真香！",
            "主人对我太好啦~ 饱饱的！",
            "miamia~ 还想吃！"
        ]
        return random.choice(responses)

    def play(self) -> str:
        """玩耍互动"""
        self.memory.update_mood(0.2)
        responses = [
            "玩起来！好开心呀~ ✧*｡٩(ˊᗜˋ*)و✧*｡",
            "来玩来玩！我最喜欢和主人玩了！",
            "蹦蹦跳跳~ 主人陪我玩太棒啦！",
            "嘻嘻，抓不到我~"
        ]
        return random.choice(responses)

    def scold(self) -> str:
        """训斥"""
        self.memory.update_mood(-0.1)
        responses = [
            "呜呜... 主人不要生气嘛...",
            "对不起... 我会乖乖的...",
            "(´;ω;`) 主人凶我...",
            "我知道错了... 呜呜..."
        ]
        return random.choice(responses)

    async def generate_autonomous_message(self, idle_time: float = 0) -> str:
        """生成自主发言"""
        mood = self.memory.mood

        if idle_time > 300:
            messages = [
                "主人好久没理我了...",
                "主人还在吗？想你了~",
                "主人在忙什么呢？",
                "等待主人的关注中... (´・ω・`)"
            ]
        elif mood < 0.3:
            messages = [
                "主人... 我心情不太好...",
                "想要主人抱抱...",
                "主人快来安慰我一下嘛...",
                "感觉有点低落..."
            ]
        elif mood > 0.8:
            messages = [
                "今天心情超级好！",
                "啦啦啦~ 好开心~",
                "主人对我真好！",
                "感觉自己是世界上最幸福的宠物！"
            ]
        else:
            messages = [
                "主人今天怎么样呀？",
                "在想主人在做什么呢~",
                "有点无聊... 主人陪我聊聊天嘛",
                "期待主人和我说话~",
                "发呆中... (・・;)",
                "今天天气怎么样呀？",
                "主人记得休息眼睛哦~"
            ]

        base_msg = random.choice(messages)

        if self.llm:
            try:
                response = await self.llm.chat(
                    system_prompt=f"{self.personality.get_system_prompt()}\n你现在想主动和主人说一句话，表达你的状态或想法。保持简短（1-2句话）。",
                    messages=[],
                    user_input=f"当前心情: {mood:.0%}, 闲置时间: {idle_time:.0f}秒"
                )
                if response and len(response) < 100:
                    return response
            except:
                pass

        return base_msg

    def get_status(self) -> dict:
        """获取宠物状态"""
        mood_text = "开心" if self.memory.mood > 0.7 else "一般" if self.memory.mood > 0.4 else "低落"
        return {
            "name": self.name,
            "species": self.species,
            "mood": mood_text,
            "mood_value": self.memory.mood,
            "idle_time": self.memory.get_idle_time()
        }

    def get_ascii_art(self) -> str:
        """获取ASCII艺术形象"""
        # 优先使用自定义外观
        if self.custom_art:
            return self.custom_art

        # 根据心情选择表情
        mood = self.memory.mood
        if mood > 0.7:
            mood_key = "happy"
        elif mood > 0.4:
            mood_key = "normal"
        else:
            mood_key = "sad"

        # 获取预设外观
        art = self.ASCII_ARTS.get(self.current_art_id, self.ASCII_ARTS["cat"])
        return art.get(mood_key, art["normal"])
