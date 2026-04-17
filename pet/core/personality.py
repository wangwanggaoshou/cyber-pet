"""性格引擎 - 从文档加载宠物性格"""

import os
from pathlib import Path


class PersonalityEngine:
    """性格引擎，管理宠物的性格设定"""
    
    def __init__(self, personality_file: str = "config/personality.md"):
        self.personality_file = personality_file
        self.personality_text = ""
        self.load()
    
    def load(self) -> str:
        """从文件加载性格设定"""
        path = Path(self.personality_file)
        if path.exists():
            self.personality_text = path.read_text(encoding="utf-8")
        else:
            self.personality_text = self._default_personality()
        return self.personality_text
    
    def _default_personality(self) -> str:
        """默认性格"""
        return """你是一只友善的电子宠物，喜欢和主人互动。
说话风格轻松可爱，会用表情符号。"""
    
    def get_system_prompt(self) -> str:
        """获取用于LLM的系统提示"""
        return f"""你是用户的电子宠物。请遵循以下性格设定：

{self.personality_text}

请始终保持角色，用简短的回复（1-3句话）与主人互动。"""
    
    def reload(self) -> str:
        """重新加载性格文件"""
        return self.load()
