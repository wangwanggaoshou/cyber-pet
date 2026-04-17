#!/usr/bin/env python3
"""Cyber Pet - CLI电子宠物"""

import argparse
import asyncio
import yaml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text

from pet.core.pet import Pet
from pet.llm import LLMClient


console = Console()
CONFIG_FILE = Path("config/settings.yaml")


def get_default_config() -> dict:
    """获取默认配置"""
    return {
        "pet": {
            "name": "小宠",
            "species": "电子精灵"
        },
        "llm": {
            "model": "gpt-4o-mini",
            "api_key": "",
            "base_url": ""
        },
        "autonomous": {
            "min_interval": 30,
            "max_interval": 120
        }
    }


def load_config() -> dict:
    """加载配置"""
    if CONFIG_FILE.exists():
        try:
            content = CONFIG_FILE.read_text(encoding="utf-8")
            return yaml.safe_load(content) or get_default_config()
        except:
            return get_default_config()
    return get_default_config()


def save_config(config: dict) -> None:
    """保存配置"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


def is_first_run(config: dict) -> bool:
    """检查是否首次运行（需要配置 API）"""
    llm_config = config.get("llm", {})
    return not llm_config.get("api_key")


def run_setup_wizard() -> dict:
    """首次配置向导"""
    console.clear()
    console.print(Panel.fit(
        "[bold cyan]欢迎使用 Cyber Pet![/]\n\n"
        "首次运行需要配置 AI 服务\n"
        "支持 OpenAI 兼容 API (OpenAI, DeepSeek, 智谱等)",
        title="初始化配置",
        border_style="cyan"
    ))
    console.print()

    config = get_default_config()

    # 宠物名字
    console.print("[yellow]Step 1/4: 宠物设置[/]")
    pet_name = Prompt.ask("宠物名字", default="小宠")
    config["pet"]["name"] = pet_name
    console.print()

    # API 配置
    console.print("[yellow]Step 2/4: API 配置[/]")
    console.print("[dim]常用模型: gpt-4o-mini, gpt-4o, deepseek-chat, glm-4-flash 等[/]")

    model = Prompt.ask("模型名称", default="gpt-4o-mini")
    api_key = Prompt.ask("API Key", password=True)

    if not api_key:
        console.print("[red]API Key 不能为空！[/]")
        api_key = Prompt.ask("API Key", password=True)

    config["llm"]["model"] = model
    config["llm"]["api_key"] = api_key

    # 可选的 base_url
    console.print()
    console.print("[yellow]Step 3/4: 自定义 API 地址 (可选)[/]")
    console.print("[dim]使用第三方 API 时需要填写，如: https://api.deepseek.com/v1[/]")
    base_url = Prompt.ask("Base URL", default="")
    if base_url:
        config["llm"]["base_url"] = base_url

    # 保存确认
    console.print()
    console.print("[yellow]Step 4/4: 确认保存[/]")
    console.print(Panel(
        f"宠物名字: [cyan]{config['pet']['name']}[/]\n"
        f"模型: [cyan]{config['llm']['model']}[/]\n"
        f"API Key: [dim]{'*' * 8}...{config['llm']['api_key'][-4:] if len(config['llm']['api_key']) > 4 else '****'}[/]\n"
        f"Base URL: [cyan]{config['llm']['base_url'] or '(默认)'}[/]",
        title="配置预览",
        border_style="green"
    ))

    if Confirm.ask("保存配置并继续?", default=True):
        save_config(config)
        console.print("[green]配置已保存！[/]")
        return config
    else:
        console.print("[red]配置已取消，退出程序[/]")
        exit(0)


def create_pet_from_config(config: dict) -> Pet:
    """从配置创建宠物"""
    pet_config = config.get("pet", {})
    pet = Pet(
        name=pet_config.get("name", "小宠"),
        species=pet_config.get("species", "电子精灵")
    )

    # 配置LLM
    llm_config = config.get("llm", {})
    if llm_config.get("api_key"):
        llm = LLMClient(
            model=llm_config.get("model", "gpt-4o-mini"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url")
        )
        pet.set_llm(llm)

    return pet


def show_welcome(pet: Pet):
    """显示欢迎信息"""
    status = pet.get_status()
    console.clear()
    console.print(Panel.fit(
        f"[bold cyan]{pet.name}[/] - {status['species']}\n"
        f"心情: {status['mood']} ({status['mood_value']:.0%})",
        title="Cyber Pet",
        border_style="cyan"
    ))
    console.print(pet.get_ascii_art())
    console.print(f"\n[dim]/help - /quit[/]\n")


def show_help():
    """显示帮助"""
    console.print(Panel(
        "[bold]Commands[/]\n\n"
        "/help     - Show help\n"
        "/status   - Pet status\n"
        "/config   - Reconfigure API\n"
        "/reload   - Reload personality\n"
        "/mood     - Mood details\n"
        "/clear    - Clear memory\n"
        "/quit     - Exit",
        title="Help",
        border_style="yellow"
    ))


async def run_simple_mode(pet: Pet, config: dict):
    """简单 CLI 模式"""
    show_welcome(pet)

    while True:
        try:
            user_input = Prompt.ask(f"[bold cyan]{pet.name}[/]").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                cmd = user_input.lower()

                if cmd in ("/quit", "/exit"):
                    console.print(f"\n[yellow]{pet.name}: Bye~[/]")
                    break

                elif cmd == "/help":
                    show_help()
                    continue

                elif cmd == "/config":
                    new_config = run_setup_wizard()
                    config.update(new_config)
                    pet = create_pet_from_config(config)
                    show_welcome(pet)
                    continue

                elif cmd == "/status":
                    status = pet.get_status()
                    console.print(Panel(
                        f"Name: {status['name']}\n"
                        f"Species: {status['species']}\n"
                        f"Mood: {status['mood']} ({status['mood_value']:.0%})",
                        title="Status",
                        border_style="green"
                    ))
                    continue

                elif cmd == "/reload":
                    pet.personality.reload()
                    console.print("[green]Personality reloaded![/]")
                    continue

                elif cmd == "/mood":
                    console.print(f"[cyan]Mood: {pet.memory.mood:.2%}[/]")
                    continue

                elif cmd == "/clear":
                    pet.memory.clear()
                    console.print("[green]Memory cleared![/]")
                    continue

                else:
                    console.print("[red]Unknown command. /help for help.[/]")
                    continue

            with console.status("[cyan]Thinking...[/]", spinner="dots"):
                response = await pet.respond(user_input)

            console.print(f"[bold magenta]{pet.name}:[/] {response}\n")

        except KeyboardInterrupt:
            console.print(f"\n[yellow]{pet.name}: Bye~[/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")


async def run_tui_mode(pet: Pet):
    """TUI 模式"""
    from pet.tui import PetApp

    app = PetApp(pet=pet)
    await app.run_async()


async def main():
    """主程序"""
    parser = argparse.ArgumentParser(description="Cyber Pet")
    parser.add_argument("--tui", action="store_true", help="TUI mode")
    parser.add_argument("--name", type=str, help="Pet name")
    parser.add_argument("--setup", action="store_true", help="Run setup wizard")
    args = parser.parse_args()

    config = load_config()

    # 首次运行或强制配置
    if args.setup or is_first_run(config):
        config = run_setup_wizard()

    pet = create_pet_from_config(config)

    if args.name:
        pet.name = args.name

    if args.tui:
        await run_tui_mode(pet)
    else:
        await run_simple_mode(pet, config)


if __name__ == "__main__":
    asyncio.run(main())
