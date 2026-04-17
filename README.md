# Cyber Pet CLI 电子宠物

一个可定制性格的CLI电子宠物，通过配置文档定义宠物个性。

## 快速开始

```bash
pip install -r requirements.txt
python main.py
```

## 自定义性格

编辑 `config/personality.md` 文件来定义宠物的性格特征。

## 结构

```
cyber-pet/
├── main.py              # 入口
├── pet/                 # 宠物核心模块
│   ├── core/
│   │   ├── personality.py   # 性格引擎
│   │   ├── memory.py        # 记忆系统
│   │   └── pet.py           # 宠物主体
│   └── llm.py               # LLM调用
├── config/              # 配置目录
│   ├── settings.yaml        # 基础配置
│   └── personality.md       # 性格文档
└── docs/                # 文档
```
