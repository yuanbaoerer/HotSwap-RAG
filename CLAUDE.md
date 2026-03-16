# HotSwap RAG 项目开发指南

## 1. 项目概述

HotSwap RAG 是一个热插拔文档问答系统，核心目标是实现高度模块化的 RAG 架构。

### 核心特性
- 运行时动态切换文档解析器、向量数据库和 LLM 提供商
- 多知识库管理，每个知识库可独立配置
- 支持流式响应 (SSE)
- 完整的 Web UI (Streamlit)

### 支持的组件

| 组件类型 | 支持的实现 |
|---------|-----------|
| 文档解析器 | PDF (PyPDF2), Word/Docx, OCR (Tesseract/EasyOCR) |
| 向量数据库 | ChromaDB, Pinecone, Milvus, FAISS |
| LLM 提供商 | OpenAI, Anthropic, Ollama, OpenAI 兼容端点 |

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.10+ / FastAPI |
| 前端框架 | Streamlit |
| 数据库 | SQLite (SQLAlchemy ORM) |
| 配置管理 | pydantic-settings / .env |
| 部署 | Docker / Docker Compose |

## 3. 架构设计模式（核心约束）

**必须严格遵循策略模式 (Strategy Pattern)**。

### 3.1 核心原则
- 所有功能模块必须先定义抽象基类 (Interface)，再实现具体子类
- 必须通过工厂函数实例化对象，确保主引擎与底层实现解耦
- 新增组件时，只需实现抽象基类并注册到工厂

### 3.2 目录结构

```
backend/
├── core/                    # 抽象基类 (策略模式核心)
│   ├── base_parser.py       # BaseDocumentParser
│   ├── base_store.py        # BaseVectorStore
│   └── base_llm.py          # BaseLLM
│
├── services/                # 具体实现
│   ├── parsers/             # 文档解析器: PDF, Docx, OCR
│   ├── stores/              # 向量存储: ChromaDB, Pinecone, etc.
│   └── llms/                # LLM: OpenAI, Anthropic, Ollama
│
├── factories/               # 工厂函数
│   ├── parser_factory.py
│   ├── store_factory.py
│   └── llm_factory.py
│
├── api/                     # FastAPI 路由
│   ├── main.py
│   └── routes/
│
├── models/                  # Pydantic 模型
├── db/                      # SQLAlchemy 模型
└── utils/                   # 工具函数
```

### 3.3 扩展新组件

添加新的文档解析器示例：

```python
# 1. 在 services/parsers/ 创建实现
class MyParser(BaseDocumentParser):
    @property
    def name(self) -> str:
        return "My Parser"

    def parse(self, file_path: Path) -> List[str]:
        # 实现解析逻辑
        pass

    def supported_formats(self) -> List[str]:
        return [".myformat"]

# 2. 在工厂中注册
_PARSER_REGISTRY["myformat"] = MyParser
```

## 4. AI 编码规范 (Vibe Coding Rules)

### 4.1 基本规范
1. **类型提示 (Type Hints)**: 所有 Python 函数和方法必须包含完整的类型提示
2. **文档字符串 (Docstrings)**: 核心类、接口和复杂逻辑必须包含 Google 风格的 Docstrings
3. **稳步迭代**: 不要一次性重写大量文件。每次只专注于当前要求的模块，完成后提醒用户进行测试和 Commit
4. **错误处理**: 在处理文件 I/O、API 请求时，必须包含合理的 `try-except` 块和日志记录
5. **不要伪造数据/Key**: 需要 API Key 的地方请从 `os.environ` 或 `.env` 读取

### 4.2 代码风格
- 使用 `black` 进行代码格式化
- 使用 `isort` 进行 import 排序
- 单个文件不超过 400 行
- 函数不超过 50 行

### 4.3 日志规范
```python
import logging
logger = logging.getLogger(__name__)

# 使用方式
logger.info(f"Processing file: {file_path}")
logger.error(f"Failed to parse: {e}")
```

## 5. API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/documents` | GET, POST | 文档管理 |
| `/api/documents/{id}` | GET, DELETE | 文档操作 |
| `/api/knowledge-bases` | GET, POST | 知识库管理 |
| `/api/chat` | POST | RAG 问答 |
| `/api/chat/stream` | POST | 流式问答 (SSE) |
| `/api/config/*` | GET, PUT | 配置管理 |
| `/health` | GET | 健康检查 |

## 6. 开发流程

### 6.1 环境搭建
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Keys
```

### 6.2 启动服务
```bash
# 后端
uvicorn backend.api.main:app --reload --port 8000

# 前端
streamlit run frontend/app.py
```

### 6.3 运行测试
```bash
pytest tests/ -v
```

## 7. 环境变量

| 变量名 | 描述 | 必需 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | 使用 OpenAI 时 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 | 使用 Anthropic 时 |
| `PINECONE_API_KEY` | Pinecone API 密钥 | 使用 Pinecone 时 |
| `OLLAMA_BASE_URL` | Ollama 服务地址 | 使用 Ollama 时 |
| `DEFAULT_PARSER` | 默认解析器类型 | 否 (默认: pdf) |
| `DEFAULT_STORE` | 默认向量存储 | 否 (默认: chromadb) |
| `DEFAULT_LLM` | 默认 LLM 提供商 | 否 (默认: openai) |

## 8. 常见问题

### Q: 如何添加新的 LLM 提供商？
A: 继承 `BaseLLM` 类，实现所有抽象方法，然后在 `llm_factory.py` 中注册。

### Q: 如何切换向量数据库？
A: 在设置页面选择，或通过 API `/api/config/active` 更新配置。

### Q: OCR 解析需要什么依赖？
A: 需要安装 Tesseract OCR 引擎和相关的 Python 包：
```bash
pip install pytesseract pdf2image Pillow
# 还需要安装 Tesseract 系统应用
```

## 9. 相关文档

- [系统设计文档](docs/superpowers/specs/2026-03-16-hotswap-rag-design.md)
- [README.md](README.md)