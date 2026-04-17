"""宠物主体"""

import random
from .personality import PersonalityEngine
from .memory import Memory


class Pet:
    """电子宠物"""
    
    def __init__(self, name: str = "小宠", species: str = "电子精灵"):
        self.name = name
        self.species = species
        self.personality = PersonalityEngine()
        self.memory = Memory()
        self.llm = None  # 延迟加载
    
    def set_llm(self, llm_client):
        """设置LLM客户端"""
        self.llm = llm_client
    
    async def respond(self, user_input: str) -> str:
        """生成回复"""
        self.memory.add("user", user_input)
        
        # 更新心情：用户来互动，心情变好
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
    
    def get_status(self) -> dict:
        """获取宠物状态"""
        mood_text = "开心" if self.memory.mood > 0.7 else "一般" if self.memory.mood > 0.4 else "低落"
        return {
            "name": self.name,
            "species": self.species,
            "mood": mood_text,
            "mood_value": self.memory.mood
        }
    
    def get_ascii_art(self) -> str:
        """获取ASCII艺术形象"""
        mood = self.memory.mood
        if mood > 0.7:
            return """
   / \\__
  (    @\\___
  /         O
 /   (_____/
/_____/   U
"""
        elif mood > 0.4:
            return """
   / \\__
  (    -\\___
  /         O
 /   (_____/
/_____/   U
"""
        else:
            return """
   / \\__
  (    T\\___
  /         O
 /   (_____/
/_____/   U
"""
