# HotSwap RAG 项目交接文档

> 创建日期: 2026-03-16
> 项目状态: 初始化完成，核心框架已搭建

## 1. 项目概况

### 1.1 项目简介
HotSwap RAG 是一个热插拔文档问答系统，支持运行时动态切换文档解析器、向量数据库和 LLM 提供商。

### 1.2 当前完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 项目结构 | 100% | 目录、配置文件全部创建 |
| 抽象基类 | 100% | BaseDocumentParser, BaseVectorStore, BaseLLM |
| 文档解析器 | 100% | PDF, Docx, OCR 解析器已实现 |
| 向量存储 | 70% | ChromaDB 完整，其他为框架代码 |
| LLM 提供商 | 100% | OpenAI, Anthropic, Ollama, OpenAI兼容 |
| 工厂函数 | 100% | parser_factory, store_factory, llm_factory |
| FastAPI 路由 | 80% | 路由定义完成，业务逻辑为占位符 |
| Streamlit 前端 | 90% | UI 完整，API 调用为模拟数据 |
| 数据库模型 | 100% | SQLAlchemy 模型已定义 |
| 测试 | 100% | 38 个测试全部通过 |

---

## 2. 环境配置

### 2.1 系统要求
- Python 3.10+
- Git
- (可选) Docker & Docker Compose
- (可选) Tesseract OCR (用于 OCR 解析)

### 2.2 快速启动 (venv)

```bash
# 1. 克隆项目
git clone <repository-url>
cd HotSwap-RAG

# 2. 创建虚拟环境
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API Keys

# 5. 启动后端
uvicorn backend.api.main:app --reload --port 8000

# 6. 启动前端 (新终端)
streamlit run frontend/app.py
```

### 2.2.1 快速启动 (Conda)

```bash
# 1. 克隆项目
git clone <repository-url>
cd HotSwap-RAG

# 2. 创建 Conda 环境
conda create -n hotswap-rag python=3.11
conda activate hotswap-rag

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API Keys

# 5. 启动后端
uvicorn backend.api.main:app --reload --port 8000

# 6. 启动前端 (新终端，需要先激活环境)
conda activate hotswap-rag
streamlit run frontend/app.py
```

### 2.3 环境变量配置

编辑 `.env` 文件：

```env
# 必需 - 至少配置一个 LLM
OPENAI_API_KEY=sk-xxx              # 使用 OpenAI
# ANTHROPIC_API_KEY=sk-ant-xxx     # 或使用 Anthropic

# 可选 - 使用 Pinecone
# PINECONE_API_KEY=xxx
# PINECONE_ENVIRONMENT=xxx

# 可选 - 使用本地 Ollama
# OLLAMA_BASE_URL=http://localhost:11434
```

### 2.4 Docker 部署 (可选)

```bash
docker-compose up -d
# 前端: http://localhost:8501
# 后端: http://localhost:8000
```

---

## 3. 项目架构速览

### 3.1 核心设计模式：策略模式

```
┌─────────────────┐
│   BaseParser    │◄─── 抽象基类 (core/)
└────────┬────────┘
         │ 继承
    ┌────┴────┬─────────┐
    ▼         ▼         ▼
PDFParser  DocxParser  OCRParser
    │         │         │
    └────┬────┴─────────┘
         │ 注册
    ┌────▼────┐
    │ Factory │◄─── 工厂函数 (factories/)
    └─────────┘
```

### 3.2 关键文件说明

| 文件 | 作用 | 修改频率 |
|------|------|----------|
| `backend/core/*.py` | 抽象基类定义 | 很少修改 |
| `backend/services/parsers/*.py` | 文档解析实现 | 需要时扩展 |
| `backend/services/stores/*.py` | 向量存储实现 | 需要时扩展 |
| `backend/services/llms/*.py` | LLM 实现 | 需要时扩展 |
| `backend/factories/*.py` | 工厂函数 | 新增组件时修改 |
| `backend/api/routes/*.py` | API 路由 | 开发主要区域 |
| `frontend/pages/*.py` | 前端页面 | 开发主要区域 |

### 3.3 数据流

```
用户上传文档
    ↓
DocumentParser.parse() → 文本块列表
    ↓
VectorStore.add_documents() → 向量化存储
    ↓
用户提问
    ↓
VectorStore.similarity_search() → 检索相关内容
    ↓
LLM.generate_with_context() → 生成回答
```

---

## 4. 开发工作流

### 4.1 添加新组件示例

**添加新的文档解析器：**

```python
# 1. 创建 backend/services/parsers/markdown_parser.py
from backend.core.base_parser import BaseDocumentParser

class MarkdownParser(BaseDocumentParser):
    @property
    def name(self) -> str:
        return "Markdown Parser"

    def parse(self, file_path: Path) -> List[str]:
        # 实现解析逻辑
        pass

    def supported_formats(self) -> List[str]:
        return [".md", ".markdown"]

# 2. 在 factories/parser_factory.py 注册
from backend.services.parsers.markdown_parser import MarkdownParser

_PARSER_REGISTRY["markdown"] = MarkdownParser
```

### 4.2 代码规范

```python
# ✅ 正确示例
def parse(self, file_path: Path) -> List[str]:
    """Parse document and return text chunks.

    Args:
        file_path: Path to the document file.

    Returns:
        List of text chunks.

    Raises:
        FileNotFoundError: If file doesn't exist.
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        # 业务逻辑
        logger.info(f"Parsing: {file_path}")
        return chunks
    except Exception as e:
        logger.error(f"Parse failed: {e}")
        raise

# ❌ 错误示例
def parse(self, file_path):  # 缺少类型提示
    # 缺少 docstring
    return something  # 缺少错误处理
```

### 4.3 测试规范

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_parsers/ -v

# 带覆盖率
pytest tests/ --cov=backend --cov-report=html
```

---

## 5. 待完成工作

### 5.1 高优先级

| 任务 | 文件 | 说明 |
|------|------|------|
| 完善 Milvus Store | `backend/services/stores/milvus_store.py` | 当前为 NotImplementedError |
| 完善 FAISS Store | `backend/services/stores/faiss_store.py` | 当前为 NotImplementedError |
| 实现文档上传逻辑 | `backend/api/routes/documents.py` | 当前为占位符 |
| 实现 RAG 问答逻辑 | `backend/api/routes/chat.py` | 当前为占位符 |
| 连接前端与后端 | `frontend/pages/*.py` | 当前使用模拟数据 |

### 5.2 中优先级

| 任务 | 说明 |
|------|------|
| 添加 embedding 支持 | 支持本地 embedding 模型 |
| 完善知识库管理 | CRUD 操作完整实现 |
| 添加用户认证 | API Key 或 JWT 认证 |
| 性能优化 | 批量处理、缓存 |

### 5.3 低优先级

| 任务 | 说明 |
|------|------|
| 添加更多测试 | 目标覆盖率 80%+ |
| 国际化支持 | 多语言 UI |
| 监控和日志 | 结构化日志、性能监控 |

---

## 6. 重要注意事项

### 6.1 API Key 安全
- ⚠️ **永远不要**将 `.env` 文件提交到 Git
- 使用 `.env.example` 作为模板
- 生产环境使用环境变量或密钥管理服务

### 6.2 策略模式约束
- 新增组件**必须**继承对应的抽象基类
- **必须**实现所有抽象方法
- 通过工厂函数实例化，不要直接 `new`

### 6.3 依赖管理
```bash
# 添加新依赖
pip install package-name
pip freeze > requirements.txt

# 或手动添加到 requirements.txt
```

### 6.4 Git 工作流
```bash
# 功能开发
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 创建 PR 合并到主分支
```

---

## 7. 常见问题

### Q1: 启动报错 "Module not found"
```bash
# 确保虚拟环境已激活
# 确保依赖已安装
pip install -r requirements.txt
```

### Q2: ChromaDB 报错
```bash
# 可能需要安装额外依赖
pip install chromadb --upgrade
```

### Q3: 前端无法连接后端
```bash
# 确保后端已启动
uvicorn backend.api.main:app --reload

# 检查端口是否被占用
# Windows
netstat -ano | findstr :8000
# Linux/Mac
lsof -i :8000
```

### Q4: OCR 解析不工作
```bash
# 需要安装 Tesseract
# Windows: 下载安装包 https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: sudo apt install tesseract-ocr
```

---

## 8. 资源链接

| 资源 | 链接 |
|------|------|
| 项目设计文档 | `docs/superpowers/specs/2026-03-16-hotswap-rag-design.md` |
| 开发指南 | `CLAUDE.md` |
| API 文档 | 启动后访问 http://localhost:8000/docs |
| FastAPI 文档 | https://fastapi.tiangolo.com/ |
| Streamlit 文档 | https://docs.streamlit.io/ |
| ChromaDB 文档 | https://docs.trychroma.com/ |

---

## 9. 联系与支持

如遇问题，请：
1. 查阅 `CLAUDE.md` 开发指南
2. 查看项目设计文档
3. 检查 API 文档 (`/docs`)

---

**祝你开发顺利！**