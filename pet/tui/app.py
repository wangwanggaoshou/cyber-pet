"""Textual TUI 应用 - 终端分屏界面"""

import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, Button
from textual.reactive import reactive
from textual.screen import Screen
from rich.text import Text
from rich.panel import Panel

from pet.core.pet import Pet
from pet.core.memory import Memory
from pet.autonomous import AutonomousSpeaker


class PetPanel(Container):
    """右侧宠物面板"""

    mood_text = reactive("开心")
    pet_message = reactive("")
    ascii_art = reactive("")
    pet_name = reactive("小宠")

    def __init__(self, pet: Pet, **kwargs):
        super().__init__(**kwargs)
        self.pet = pet
        self.pet_name = pet.name
        self.messages: list = []  # 最近的消息历史

    def compose(self) -> ComposeResult:
        yield Static(id="pet-header")
        yield Static(id="pet-art")
        yield Static(id="pet-mood")
        yield Static(id="pet-messages")
        yield Static(id="pet-commands")

    def on_mount(self) -> None:
        """挂载时更新显示"""
        self._update_display()
        self.set_interval(1, self._tick)

    def _tick(self) -> None:
        """定时更新"""
        self._update_display()

    def _update_display(self) -> None:
        """更新显示内容"""
        status = self.pet.get_status()
        self.mood_text = status["mood"]
        self.ascii_art = self.pet.get_ascii_art()

        # 更新各个组件
        header = self.query_one("#pet-header", Static)
        header.update(f"🐾 {self.pet_name}")

        art = self.query_one("#pet-art", Static)
        art.update(self.ascii_art)

        mood = self.query_one("#pet-mood", Static)
        mood_bar = "█" * int(self.pet.memory.mood * 5) + "░" * (5 - int(self.pet.memory.mood * 5))
        mood.update(f"心情: {mood_bar} {status['mood']}")

        msgs = self.query_one("#pet-messages", Static)
        if self.messages:
            # 显示最近5条消息
            recent = self.messages[-5:]
            msg_text = "\n".join(recent)
            msgs.update(msg_text)
        else:
            msgs.update("等待宠物发言...")

        cmds = self.query_one("#pet-commands", Static)
        cmds.update("—— 命令 ——\n/pet /feed\n/play /quit")

    def add_message(self, message: str) -> None:
        """添加消息"""
        self.messages.append(f"[dim]{self.pet_name}:[/] {message}")
        self._update_display()


class ShellPanel(Container):
    """左侧 Shell 工作面板"""

    output_lines: reactive[list] = reactive(list)

    def __init__(self, pet: Pet, **kwargs):
        super().__init__(**kwargs)
        self.pet = pet

    def compose(self) -> ComposeResult:
        yield Static(id="shell-output")
        yield Input(placeholder="输入命令或 /help 查看帮助", id="shell-input")

    def on_mount(self) -> None:
        """挂载"""
        self.output_lines.append("欢迎使用 Cyber Pet Shell！")
        self.output_lines.append("输入 shell 命令执行，或 /命令 与宠物互动")
        self._update_output()
        self.query_one("#shell-input", Input).focus()

    def _update_output(self) -> None:
        """更新输出显示"""
        output = self.query_one("#shell-output", Static)
        # 只显示最近20行
        lines = self.output_lines[-20:]
        output.update("\n".join(lines))

    def add_output(self, text: str) -> None:
        """添加输出"""
        self.output_lines.append(text)
        self._update_output()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """处理输入"""
        if event.input_id == "shell-input":
            cmd = event.value.strip()
            if not cmd:
                return

            self.add_output(f"[cyan]>[/] {cmd}")
            event.input.value = ""

            await self.handle_command(cmd)

    async def handle_command(self, cmd: str) -> None:
        """处理命令"""
        # Shell 命令 vs 宠物互动
        if cmd.startswith("/"):
            response = await self.handle_pet_cmd(cmd)
            if response:
                self.add_output(f"[magenta]{self.pet.name}:[/] {response}")
        else:
            # 执行 shell 命令
            import subprocess
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.stdout:
                    for line in result.stdout.strip().split("\n")[:10]:
                        self.add_output(line)
                if result.stderr:
                    self.add_output(f"[red]{result.stderr[:200]}[/]")
            except subprocess.TimeoutExpired:
                self.add_output("[red]命令超时[/]")
            except Exception as e:
                self.add_output(f"[red]错误: {e}[/]")

    async def handle_pet_cmd(self, cmd: str) -> Optional[str]:
        """处理宠物互动命令"""
        cmd = cmd.lower()

        if cmd in ("/quit", "/exit"):
            self.app.exit()
            return "下次再见，主人~"

        elif cmd in ("/help", "/?"):
            return "命令: /pet(摸头) /feed(喂食) /play(玩耍) /scold(训斥) /status /quit"

        elif cmd == "/pet":
            return self.pet.pet_head()

        elif cmd == "/feed":
            return self.pet.feed()

        elif cmd == "/play":
            return self.pet.play()

        elif cmd == "/scold":
            return self.pet.scold()

        elif cmd == "/status":
            status = self.pet.get_status()
            return f"状态: 心情 {status['mood']} ({status['mood_value']:.0%})"

        elif cmd.startswith("/"):
            # 普通对话
            user_input = cmd[1:] if len(cmd) > 1 else ""
            if user_input and not user_input.startswith("/"):
                return await self.pet.respond(user_input)

        return None


class PetApp(App):
    """主应用"""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 28;
    }

    PetPanel {
        background: $surface;
        border-left: solid $primary;
        padding: 1;
    }

    #pet-header {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #pet-art {
        color: $primary;
    }

    #pet-mood {
        margin-top: 1;
        margin-bottom: 1;
    }

    #pet-messages {
        color: $text;
        height: auto;
        max-height: 10;
        margin-top: 1;
    }

    #pet-commands {
        color: $text-muted;
        margin-top: 1;
    }

    ShellPanel {
        background: $panel;
        padding: 1;
    }

    #shell-output {
        height: 1fr;
        overflow: hidden;
    }

    #shell-input {
        dock: bottom;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "退出"),
        ("ctrl+l", "clear", "清屏"),
    ]

    def __init__(self, pet: Pet = None, **kwargs):
        super().__init__(**kwargs)
        self.pet = pet or Pet()
        self.speaker: Optional[AutonomousSpeaker] = None

    def compose(self) -> ComposeResult:
        yield ShellPanel(self.pet)
        yield PetPanel(self.pet)

    def on_mount(self) -> None:
        """启动时初始化"""
        # 启动自主发言
        self.speaker = AutonomousSpeaker(
            self.pet,
            min_interval=30,
            max_interval=120,
            on_speak=self._on_pet_speak
        )
        asyncio.create_task(self.speaker.start())

    def _on_pet_speak(self, message: str) -> None:
        """宠物发言回调"""
        try:
            pet_panel = self.query_one(PetPanel)
            pet_panel.add_message(message)
            # 同时在 shell 面板显示
            shell = self.query_one(ShellPanel)
            shell.add_output(f"[magenta]{self.pet.name}:[/] {message}")
        except:
            pass

    def action_clear(self) -> None:
        """清屏"""
        shell = self.query_one(ShellPanel)
        shell.output_lines = []
        shell._update_output()

    def on_unmount(self) -> None:
        """退出时清理"""
        if self.speaker:
            asyncio.create_task(self.speaker.stop())
