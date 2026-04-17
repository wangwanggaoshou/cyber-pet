"""记忆系统 - 管理对话历史"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class Memory:
    """宠物的记忆系统"""

    def __init__(self, save_file: str = "config/memory.json", max_history: int = 50):
        self.save_file = Path(save_file)
        self.max_history = max_history
        self.history: List[Dict] = []
        self.mood: float = 0.7  # 心情值 0-1
        self.last_interaction: str = ""
        self.load()

    def load(self):
        """加载记忆"""
        if self.save_file.exists():
            try:
                data = json.loads(self.save_file.read_text(encoding="utf-8"))
                self.history = data.get("history", [])[-self.max_history:]
                self.mood = data.get("mood", 0.7)
                self.last_interaction = data.get("last_interaction", "")
            except:
                pass

    def save(self):
        """保存记忆"""
        self.save_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "history": self.history[-self.max_history:],
            "mood": self.mood,
            "last_interaction": self.last_interaction
        }
        self.save_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, role: str, content: str):
        """添加对话记录"""
        self.history.append({
            "role": role,
            "content": content,
            "time": datetime.now().isoformat()
        })
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        self.last_interaction = datetime.now().isoformat()
        self.save()

    def get_context(self, limit: int = 10) -> List[Dict]:
        """获取最近的对话上下文"""
        return self.history[-limit:]

    def update_mood(self, delta: float):
        """更新心情"""
        self.mood = max(0, min(1, self.mood + delta))
        self.save()

    def decay_mood(self, amount: float = 0.01):
        """心情衰减"""
        self.mood = max(0, self.mood - amount)
        self.save()

    def get_idle_time(self) -> float:
        """获取闲置时间（秒）"""
        if not self.last_interaction:
            return 0
        try:
            last = datetime.fromisoformat(self.last_interaction)
            return (datetime.now() - last).total_seconds()
        except:
            return 0

    def clear(self):
        """清空记忆"""
        self.history = []
        self.mood = 0.7
        self.save()
