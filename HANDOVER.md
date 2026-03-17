# HotSwap RAG 项目交接文档

> 创建日期: 2026-03-16
> 最后更新: 2026-03-17
> 项目状态: 核心框架已搭建，部分功能待实现

## 1. 项目概况

### 1.1 项目简介
HotSwap RAG 是一个热插拔文档问答系统，支持运行时动态切换文档解析器、向量数据库和 LLM 提供商。

### 1.2 当前完成度

| 模块 | 完成度 | 说明 |
|------|--------|------|
| 项目结构 | 100% | 目录、配置文件全部创建 |
| 抽象基类 | 100% | BaseDocumentParser, BaseVectorStore, BaseLLM |
| 文档解析器 | 100% | PDF, Docx, OCR 解析器已实现 |
| 向量存储 | 100% | ChromaDB/Pinecone/Milvus/FAISS 全部实现 |
| LLM 提供商 | 100% | OpenAI, Anthropic, Ollama, OpenAI兼容 |
| 工厂函数 | 100% | parser_factory, store_factory, llm_factory |
| 文档管理 API | 100% | 上传、列表、删除、解析已实现 |
| 知识库 API | 100% | CRUD 全部实现 |
| RAG 问答 API | 100% | 检索+生成流程已实现 |
| 配置管理 API | 100% | 查询+持久化已实现 |
| 文档管理前端 | 100% | 已连接后端 API |
| 知识库前端 | 30% | 使用硬编码数据 |
| 聊天前端 | 20% | 使用模拟数据 |
| 设置前端 | 100% | 已连接后端 API |
| 数据库模型 | 100% | SQLAlchemy 模型已定义 |
| 测试 | 100% | 61 个测试全部通过 |

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

## 4. 未实现功能详细清单

> ⚠️ **重要**: 以下是只写了接口但未实现的功能，开发时需优先处理

### 4.1 高优先级功能 - 已实现 ✅

| 文件位置 | 功能 | 实现说明 |
|----------|------|----------|
| `backend/api/routes/chat.py:106` | RAG 查询处理 | ✅ 实现检索+生成流程，返回来源引用 |
| `backend/api/routes/chat.py:160` | 流式 RAG 查询 (SSE) | ✅ 实现 SSE 流式响应 |
| `backend/api/routes/documents.py:67` | 文档解析处理 | ✅ 调用 Parser 解析 + VectorStore 存储 |

### 4.2 中优先级功能 - 已实现 ✅

| 文件位置 | 功能 | 实现说明 |
|----------|------|----------|
| `backend/api/routes/knowledge_base.py:84` | 知识库列表 | ✅ 连接数据库查询，返回文档计数 |
| `backend/api/routes/knowledge_base.py:106` | 创建知识库 | ✅ 创建数据库记录，返回真实 ID |
| `backend/api/routes/knowledge_base.py:140` | 获取知识库详情 | ✅ 数据库查询，含文档计数 |
| `backend/api/routes/knowledge_base.py:157` | 更新知识库 | ✅ 支持部分更新，数据库持久化 |
| `backend/api/routes/knowledge_base.py:198` | 删除知识库 | ✅ 删除记录+关联文档+文件清理 |
| `backend/api/routes/config.py:117` | 获取活跃配置 | ✅ 从数据库读取配置 |
| `backend/api/routes/config.py:130` | 更新活跃配置 | ✅ 持久化到数据库 |

### 4.3 向量存储服务 - 已实现 ✅

| 存储类型 | 状态 | 实现说明 |
|----------|------|----------|
| ChromaDB | ✅ 完全实现 | 本地开发首选，零配置 |
| Pinecone | ✅ 完全实现 | 云端托管，生产级 |
| Milvus | ✅ 完全实现 | 自托管，可扩展，支持所有操作 |
| FAISS | ✅ 完全实现 | 轻量级本地存储，不支持单文档删除 |

**Milvus 实现细节**:
- `add_documents`: 批量添加文档，自动生成嵌入向量
- `similarity_search`: 余弦相似度搜索
- `delete_documents`: 按ID删除文档
- `delete_collection`: 删除整个集合
- `count`: 获取文档数量

**FAISS 实现细节**:
- `add_documents`: 添加文档，支持持久化保存
- `similarity_search`: 带分数的相似度搜索
- `delete_documents`: 不支持（抛出 NotImplementedError）
- `delete_collection`: 清空索引并删除文件
- `count`: 返回文档数量（排除占位符）

### 4.4 前端页面

| 文件位置 | 功能 | 当前状态 | 实现建议 |
|----------|------|----------|----------|
| `frontend/pages/3_Knowledge_Bases.py:45` | 知识库列表 | 硬编码数据 kb-001 | 调用 API 获取 |
| `frontend/pages/3_Knowledge_Bases.py:36` | 创建知识库 | 仅显示成功消息 | 调用 API 创建 |
| `frontend/pages/2_Chat.py:67-93` | 问答功能 | 模拟回答 | 调用 chat API |
| `frontend/pages/1_Documents.py:157` | 导出索引 | "功能开发中" | 实现导出逻辑 |
| `frontend/pages/1_Documents.py:161` | 重新处理文档 | "功能开发中" | 实现重新解析 |
| `frontend/pages/1_Documents.py:165` | 清空所有文档 | 按钮不可用 | 实现批量删除 |

---

## 5. 开发优先级建议

### 5.1 第一阶段：核心功能 - 已完成 ✅

1. ✅ **RAG 问答逻辑** (`backend/api/routes/chat.py`)
   - 实现检索：调用 VectorStore.similarity_search()
   - 实现生成：调用 LLM.generate_with_context()
   - 实现流式：使用 SSE 返回

2. ✅ **文档处理流程** (`backend/api/routes/documents.py:process_document`)
   - 根据文件类型选择 Parser
   - 解析文档获取文本块
   - 调用 VectorStore.add_documents()

3. **知识库 CRUD** (`backend/api/routes/knowledge_base.py`) - 待实现
   - 连接数据库实现所有操作

### 5.2 第二阶段：完善功能 - 已完成 ✅

1. ✅ 完善 Milvus Store 实现
2. ✅ 完善 FAISS Store 实现
3. ✅ 配置持久化到数据库
4. 前端连接真实 API - 部分完成（文档、设置已连接）

### 5.3 第三阶段：增强功能

1. 添加 embedding 支持本地模型
2. 添加用户认证
3. 性能优化（批量处理、缓存）
4. 监控和日志

---

## 6. 开发工作流

### 6.1 添加新组件示例

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

### 6.2 代码规范

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

### 6.3 测试规范

```bash
# 运行测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_parsers/ -v

# 带覆盖率
pytest tests/ --cov=backend --cov-report=html
```

---

## 7. 重要注意事项

### 7.1 API Key 安全
- ⚠️ **永远不要**将 `.env` 文件提交到 Git
- 使用 `.env.example` 作为模板
- 生产环境使用环境变量或密钥管理服务

### 7.2 策略模式约束
- 新增组件**必须**继承对应的抽象基类
- **必须**实现所有抽象方法
- 通过工厂函数实例化，不要直接 `new`

### 7.3 依赖管理
```bash
# 添加新依赖
pip install package-name
pip freeze > requirements.txt

# 或手动添加到 requirements.txt
```

### 7.4 Git 工作流
```bash
# 功能开发
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# 创建 PR 合并到主分支
```

---

## 8. 常见问题

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

## 9. 资源链接

| 资源 | 链接 |
|------|------|
| 项目设计文档 | `docs/superpowers/specs/2026-03-16-hotswap-rag-design.md` |
| 开发指南 | `CLAUDE.md` |
| API 文档 | 启动后访问 http://localhost:8000/docs |
| FastAPI 文档 | https://fastapi.tiangolo.com/ |
| Streamlit 文档 | https://docs.streamlit.io/ |
| ChromaDB 文档 | https://docs.trychroma.com/ |

---

## 10. 联系与支持

如遇问题，请：
1. 查阅 `CLAUDE.md` 开发指南
2. 查看项目设计文档
3. 检查 API 文档 (`/docs`)

---

**祝你开发顺利！**