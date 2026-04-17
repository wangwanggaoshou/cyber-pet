"""自主发言系统"""

import asyncio
import random
from typing import Callable, Optional


class AutonomousSpeaker:
    """自主发言系统 - 让宠物能定时自己说话"""

    def __init__(
        self,
        pet,
        min_interval: int = 30,
        max_interval: int = 120,
        idle_threshold: int = 300,
        on_speak: Optional[Callable[[str], None]] = None
    ):
        self.pet = pet
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.idle_threshold = idle_threshold  # 闲置多久触发求关注
        self.on_speak = on_speak  # 发言回调
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """启动自主发言循环"""
        self._running = True
        self._task = asyncio.create_task(self._speak_loop())

    async def stop(self):
        """停止自主发言"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _speak_loop(self):
        """发言循环"""
        while self._running:
            # 计算下次发言间隔
            # 心情低时更频繁发言求关注
            mood = self.pet.memory.mood
            if mood < 0.3:
                interval = random.randint(self.min_interval // 2, self.min_interval)
            elif mood < 0.5:
                interval = random.randint(self.min_interval, (self.min_interval + self.max_interval) // 2)
            else:
                interval = random.randint(
                    (self.min_interval + self.max_interval) // 2,
                    self.max_interval
                )

            await asyncio.sleep(interval)

            if not self._running:
                break

            # 检查是否闲置太久需要求关注
            idle_time = self.pet.memory.get_idle_time()

            # 心情衰减（每轮循环）
            self.pet.memory.decay_mood(0.01)

            # 生成发言
            message = await self.pet.generate_autonomous_message(idle_time)

            # 调用回调
            if self.on_speak:
                self.on_speak(message)

    def update_intervals(self, min_interval: int, max_interval: int):
        """更新发言间隔"""
        self.min_interval = min_interval
        self.max_interval = max_interval
