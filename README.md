# ohmy-ai-opencode

AI资讯智能体 — 自动抓取 AI 领域最新资讯，并通过大语言模型生成一句话洞察摘要。

---

## 功能特性

- 从多个知名 AI 资讯 RSS 源自动抓取最新文章
- 调用 OpenAI Chat API 对每条资讯生成一句话智能摘要
- 支持自定义 RSS 源（JSON 格式）
- 支持将结果导出为 JSON 文件
- 无 API Key 时仍可正常运行（仅跳过 AI 摘要步骤）

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置 OpenAI API Key（可选）

创建 `.env` 文件或直接设置环境变量：

```bash
export OPENAI_API_KEY=your_api_key_here
```

### 运行智能体

```bash
# 使用默认源抓取并生成 AI 摘要
python -m src.agent

# 跳过 AI 摘要（无需 API Key）
python -m src.agent --no-ai

# 限制每个源最多抓取 3 条
python -m src.agent --max 3

# 使用自定义 RSS 源文件
python -m src.agent --sources my_sources.json

# 将结果保存到 JSON 文件
python -m src.agent --output news.json
```

### 自定义 RSS 源格式

```json
[
  {"name": "My AI Blog", "url": "https://example.com/feed.xml"},
  {"name": "Another Source", "url": "https://other.com/rss"}
]
```

---

## 项目结构

```
ohmy-ai-opencode/
├── src/
│   ├── agent.py          # 主入口：CLI 解析 + 流程编排
│   ├── news_fetcher.py   # RSS 抓取模块
│   └── summarizer.py     # OpenAI 摘要模块
├── tests/
│   ├── test_agent.py
│   ├── test_news_fetcher.py
│   └── test_summarizer.py
├── requirements.txt
└── README.md
```

---

## 内置 RSS 源

| 来源 | 类型 |
|------|------|
| MIT Technology Review – AI | 技术评论 |
| The Verge – AI | 科技媒体 |
| VentureBeat – AI | 行业资讯 |
| AI News | 专业 AI 新闻 |
| Hacker News – AI | 社区热点 |

---

## 运行测试

```bash
python -m pytest tests/ -v
```