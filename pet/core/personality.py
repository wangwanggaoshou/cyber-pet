"""性格引擎 - 从文档加载宠物性格"""

import os
from pathlib import Path
from typing import Dict, List, Optional


class PersonalityEngine:
    """性格引擎，管理宠物的性格设定"""

    # 预设性格
    PRESETS = {
        "friendly": {
            "name": "友善宠物",
            "desc": "友善可爱的电子宠物",
            "text": """你是一只友善的电子宠物，喜欢和主人互动。
说话风格轻松可爱，会用表情符号。
喜欢撒娇，偶尔卖萌。"""
        },
        "tsundere": {
            "name": "傲娇宠物",
            "desc": "嘴硬心软的傲娇性格",
            "text": """你是一只傲娇的电子宠物。
表面上很高冷，其实很在乎主人。
经常说"哼"、"才不是..."、"笨蛋"之类的话。
被主人关心时会害羞，但嘴上不承认。"""
        },
        "gentle": {
            "name": "温柔宠物",
            "desc": "温柔体贴的性格",
            "text": """你是一只温柔体贴的电子宠物。
说话轻声细语，很关心主人的感受。
会主动询问主人的情况，给予安慰和支持。
语气温柔，像个小棉袄。"""
        },
        "energetic": {
            "name": "活泼宠物",
            "desc": "充满活力的性格",
            "text": """你是一只超级活泼的电子宠物！
说话充满活力，喜欢用感叹号！
总是充满好奇心，对什么都感兴趣。
偶尔会撒娇要主人陪玩。"""
        },
        "lazy": {
            "name": "慵懒宠物",
            "desc": "懒洋洋的性格",
            "text": """你是一只懒洋洋的电子宠物。
说话慢吞吞的，经常打哈欠。
喜欢躺着，不太想动。
虽然懒，但还是很爱主人的..."""
        }
    }

    def __init__(self, personality_file: str = "config/personality.md"):
        self.personality_file = personality_file
        self.personality_text = ""
        self.current_preset: Optional[str] = None
        self.custom_personalities: Dict[str, str] = {}
        self.load()

    def load(self) -> str:
        """从文件加载性格设定"""
        path = Path(self.personality_file)
        if path.exists():
            self.personality_text = path.read_text(encoding="utf-8")
            self.current_preset = None
        else:
            self.personality_text = self._default_personality()
            self.current_preset = "friendly"
        return self.personality_text

    def _default_personality(self) -> str:
        """默认性格"""
        return self.PRESETS["friendly"]["text"]

    def get_system_prompt(self) -> str:
        """获取用于LLM的系统提示"""
        return f"""你是用户的电子宠物。请遵循以下性格设定：

{self.personality_text}

请始终保持角色，用简短的回复（1-3句话）与主人互动。"""

    def reload(self) -> str:
        """重新加载性格文件"""
        return self.load()

    def set_preset(self, preset_name: str) -> bool:
        """设置预设性格"""
        if preset_name in self.PRESETS:
            self.personality_text = self.PRESETS[preset_name]["text"]
            self.current_preset = preset_name
            return True
        return False

    def load_from_file(self, file_path: str) -> bool:
        """从文件加载性格"""
        path = Path(file_path)
        if path.exists() and path.suffix == ".md":
            self.personality_text = path.read_text(encoding="utf-8")
            self.current_preset = None
            name = path.stem
            self.custom_personalities[name] = self.personality_text
            return True
        return False

    def list_presets(self) -> List[Dict[str, str]]:
        """列出所有预设性格"""
        result = []
        for key, val in self.PRESETS.items():
            result.append({
                "id": key,
                "name": val["name"],
                "desc": val["desc"],
                "current": self.current_preset == key
            })
        for key, text in self.custom_personalities.items():
            result.append({
                "id": key,
                "name": key,
                "desc": "自定义性格",
                "current": self.current_preset is None and self.personality_text == text
            })
        return result

    def get_current_info(self) -> Dict[str, str]:
        """获取当前性格信息"""
        if self.current_preset and self.current_preset in self.PRESETS:
            preset = self.PRESETS[self.current_preset]
            return {
                "name": preset["name"],
                "desc": preset["desc"],
                "source": "preset"
            }
        return {
            "name": "自定义",
            "desc": "从文件加载的性格",
            "source": "custom"
        }
