# Paper Servant 

Paper Servant 是一款基于 **Agno** 框架开发的、面向科研人员的自动化 AI 论文处理系统。系统采用 **Multi-Agent (多智能体)** 协作架构，实现了从 ArXiv 论文检索、自动化归类、深度阅读解读到 RAG 知识问答的完整闭环。

## 核心特性

- **多代理协作架构**：由智能路由 (Router) 统一调度，Fetcher、Reader、QA、Knowledge 等多个 Agent 协同工作，任务解耦，逻辑清晰。
- **深度 RAG 知识引擎**：集成 **LanceDB** 本地向量数据库，支持对大量 PDF 论文进行语义级检索与问答。
- **自动化科研流**：一键完成“检索-下载-元数据记录-自动分类-笔记生成”全流程，显著提升文献调研效率。
- **持久化知识沉淀**：系统自动将问答历史与核心概念提取为结构化的 Wiki 文档，构建个人科研知识库。


## 系统架构

系统设计遵循模块化与高内聚原则，核心组件包括：

- **Router Agent (调度)**：负责语义解析与工具分发。
- **Paper Fetcher (检索)**：对接 ArXiv API 与 OpenAlex/Semantic Scholar 引用数据。
- **Reader Agent (解读)**：针对 PDF 长文本进行多维度分析，生成结构化阅读笔记。
- **Knowledge Base (知识)**：基于向量检索 (LanceDB) 与文件系统 (Wiki) 的双模知识库。

## 快速开始

### 1. 环境准备


```bash
# 安装依赖并创建虚拟环境
uv sync
```

### 2. 配置环境

在 `.env` 文件中配置你的 LLM API 密钥和网址（需要兼容 OpenAI 格式）：

```env
LLM_API_KEY=sk-...
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4o
```

### 3. 运行系统

- **命令行模式**：
  ```bash
  psv chat  # 进入智能对话模式，建议用于临时调试
  ```
- **Web 界面模式**：
  ```bash
  ./start_services.sh  # 一键启动前后端并在 Edge 浏览器打开
  ```

## 🛠️ 技术栈

- **Core**: Python 3.12+, Agno (Agentic Framework)
- **Database**: LanceDB (Vector Storage), Local File System
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Tools**: Typer, Rich, Inquirer, PyPDF

---
*本项目仅用于科研辅助与学术研究目的。*
