"""LLM调用模块"""

import os
from typing import List, Dict, Optional


class LLMClient:
    """LLM客户端封装"""
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "")
        self.client = None
    
    def _init_client(self):
        """延迟初始化客户端"""
        if self.client is None:
            try:
                from openai import OpenAI
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.client = OpenAI(**kwargs)
            except ImportError:
                raise ImportError("请安装 openai: pip install openai")
        return self.client
    
    async def chat(
        self,
        system_prompt: str,
        messages: List[Dict],
        user_input: str,
        temperature: float = 0.8
    ) -> str:
        """调用LLM生成回复"""
        client = self._init_client()
        
        # 构建消息列表
        full_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            full_messages.append({"role": msg["role"], "content": msg["content"]})
        full_messages.append({"role": "user", "content": user_input})
        
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"(连接出了点问题... {str(e)[:20]})"
