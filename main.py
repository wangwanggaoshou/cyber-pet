#!/usr/bin/env python3
"""Cyber Pet - CLI电子宠物"""

import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

from pet.core.pet import Pet
from pet.llm import LLMClient


console = Console()


def load_config() -> dict:
    """加载配置"""
    config_file = Path("config/settings.yaml")
    if config_file.exists():
        return yaml.safe_load(config_file.read_text(encoding="utf-8"))
    return {}


def show_welcome(pet: Pet):
    """显示欢迎信息"""
    status = pet.get_status()
    console.clear()
    console.print(Panel.fit(
        f"[bold cyan]{pet.name}[/] - {status['species']}\n"
        f"心情: {status['mood']} ({status['mood_value']:.0%})",
        title="🐾 电子宠物",
        border_style="cyan"
    ))
    console.print(pet.get_ascii_art())
    console.print(f"\n[dim]输入 /help 查看命令，/quit 退出[/]\n")


def show_help():
    """显示帮助"""
    console.print(Panel(
        "[bold]命令列表[/]\n\n"
        "/help     - 显示帮助\n"
        "/status   - 查看宠物状态\n"
        "/reload   - 重新加载性格配置\n"
        "/mood     - 查看心情详情\n"
        "/clear    - 清空对话记忆\n"
        "/quit     - 退出程序",
        title="帮助",
        border_style="yellow"
    ))


async def main():
    """主程序"""
    config = load_config()
    
    # 创建宠物
    pet_config = config.get("pet", {})
    pet = Pet(
        name=pet_config.get("name", "小宠"),
        species=pet_config.get("species", "电子精灵")
    )
    
    # 配置LLM
    llm_config = config.get("llm", {})
    if llm_config.get("api_key") or llm_config.get("model"):
        llm = LLMClient(
            model=llm_config.get("model", "gpt-4o-mini"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url")
        )
        pet.set_llm(llm)
    
    show_welcome(pet)
    
    # 主循环
    while True:
        try:
            user_input = Prompt.ask(f"[bold cyan]{pet.name}[/]").strip()
            
            if not user_input:
                continue
            
            # 命令处理
            if user_input.startswith("/"):
                cmd = user_input.lower()
                
                if cmd == "/quit" or cmd == "/exit":
                    console.print(f"\n[yellow]{pet.name}: 主人下次再来找我玩哦~ 拜拜！[/]")
                    break
                
                elif cmd == "/help":
                    show_help()
                    continue
                
                elif cmd == "/status":
                    status = pet.get_status()
                    console.print(Panel(
                        f"名字: {status['name']}\n"
                        f"种类: {status['species']}\n"
                        f"心情: {status['mood']} ({status['mood_value']:.0%})",
                        title="宠物状态",
                        border_style="green"
                    ))
                    continue
                
                elif cmd == "/reload":
                    pet.personality.reload()
                    console.print("[green]性格配置已重新加载！[/]")
                    continue
                
                elif cmd == "/mood":
                    console.print(f"[cyan]当前心情值: {pet.memory.mood:.2%}[/]")
                    continue
                
                elif cmd == "/clear":
                    pet.memory.clear()
                    console.print("[green]记忆已清空！[/]")
                    continue
                
                else:
                    console.print("[red]未知命令，输入 /help 查看帮助[/]")
                    continue
            
            # 正常对话
            with console.status("[cyan]思考中...[/]", spinner="dots"):
                response = await pet.respond(user_input)
            
            console.print(f"[bold magenta]{pet.name}:[/] {response}\n")
        
        except KeyboardInterrupt:
            console.print(f"\n[yellow]{pet.name}: 主人下次再来找我玩哦~[/]")
            break
        except Exception as e:
            console.print(f"[red]出错啦: {e}[/]")


if __name__ == "__main__":
    asyncio.run(main())