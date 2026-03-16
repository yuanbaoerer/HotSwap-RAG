# HotSwap RAG 系统设计文档

## 1. 项目概述

HotSwap RAG 是一个热插拔文档问答系统，核心特性是支持运行时动态切换：
- 文档解析器（PDF, Word, OCR, 自定义插件）
- 向量数据库（ChromaDB, Pinecone, Milvus, FAISS）
- LLM提供商（OpenAI, Anthropic, Ollama, OpenAI兼容）

## 2. 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.10+ / FastAPI |
| 前端框架 | Streamlit |
| 数据库 | SQLite |
| 向量存储 | ChromaDB (默认) / Pinecone / Milvus / FAISS |
| LLM | OpenAI / Anthropic / Ollama |

## 3. 架构设计

### 3.1 设计模式

严格遵循**策略模式 (Strategy Pattern)**：
- 抽象基类定义接口契约
- 具体实现类封装算法细节
- 工厂函数负责实例化
- 主引擎与具体实现解耦

### 3.2 目录结构

```
HotSwap-RAG/
├── backend/
│   ├── core/                    # 抽象基类
│   │   ├── __init__.py
│   │   ├── base_parser.py       # BaseDocumentParser
│   │   ├── base_store.py        # BaseVectorStore
│   │   └── base_llm.py          # BaseLLM
│   │
│   ├── services/                # 具体实现
│   │   ├── parsers/             # 文档解析器
│   │   ├── stores/              # 向量存储
│   │   └── llms/                # LLM实现
│   │
│   ├── factories/               # 工厂函数
│   ├── api/                     # FastAPI路由
│   ├── models/                  # Pydantic模型
│   ├── db/                      # 数据库模型
│   └── utils/                   # 工具函数
│
├── frontend/
│   ├── app.py                   # Streamlit入口
│   ├── pages/                   # 多页面
│   └── components/              # 可复用组件
│
├── data/                        # 数据目录
├── tests/                       # 测试
└── docs/                        # 文档
```

### 3.3 核心组件

#### 抽象基类

```python
# BaseDocumentParser - 文档解析器接口
class BaseDocumentParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> List[str]: ...
    @abstractmethod
    def supported_formats(self) -> List[str]: ...

# BaseVectorStore - 向量存储接口
class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, docs: List[str], metadatas: List[dict]) -> None: ...
    @abstractmethod
    def similarity_search(self, query: str, k: int = 4) -> List[dict]: ...
    @abstractmethod
    def delete_collection(self) -> None: ...

# BaseLLM - LLM接口
class BaseLLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str: ...
    @abstractmethod
    def stream_generate(self, prompt: str): ...
```

#### 主引擎

```python
class HotSwapRAG:
    def __init__(self, parser, store, llm): ...
    def swap_parser(self, parser) -> None: ...
    def swap_store(self, store) -> None: ...
    def swap_llm(self, llm) -> None: ...
    def ingest_document(self, file_path) -> None: ...
    def query(self, question: str) -> str: ...
```

## 4. API设计

### 4.1 RESTful端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/documents` | GET, POST | 文档管理 |
| `/api/documents/{id}` | GET, DELETE | 文档操作 |
| `/api/knowledge-bases` | GET, POST | 知识库管理 |
| `/api/chat` | POST | RAG问答 |
| `/api/config/*` | GET, PUT | 配置管理 |

### 4.2 SSE流式响应

`/api/chat` 支持Server-Sent Events流式输出：
```
Content-Type: text/event-stream
```

## 5. 前端页面

| 页面 | 文件 | 功能 |
|------|------|------|
| 首页 | app.py | 概览和导航 |
| Documents | 1_Documents.py | 文档上传管理 |
| Chat | 2_Chat.py | RAG问答界面 |
| Knowledge Bases | 3_Knowledge_Bases.py | 知识库管理 |
| Settings | 4_Settings.py | 组件切换配置 |

## 6. 数据模型

### SQLite表结构

```sql
-- 知识库
CREATE TABLE knowledge_bases (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    parser_type TEXT,
    store_type TEXT,
    llm_type TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 文档
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    kb_id TEXT REFERENCES knowledge_bases(id),
    filename TEXT,
    file_path TEXT,
    file_size INTEGER,
    status TEXT,
    created_at TIMESTAMP
);

-- 配置
CREATE TABLE configs (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP
);
```

## 7. 配置管理

### 环境变量 (.env)

```env
# LLM配置
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
OLLAMA_BASE_URL=

# 向量存储配置
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=
MILVUS_HOST=

# 应用配置
DEFAULT_PARSER=pdf
DEFAULT_STORE=chromadb
DEFAULT_LLM=openai
EMBEDDING_MODEL=text-embedding-3-small
```

## 8. 部署方式

### Docker
```bash
docker build -t hotswap-rag .
docker run -p 8000:8000 -p 8501:8501 hotswap-rag
```

### Docker Compose
```bash
docker-compose up -d
```

### 直接运行
```bash
# 后端
uvicorn backend.api.main:app --reload

# 前端
streamlit run frontend/app.py
```

## 9. 扩展机制

### 添加新的文档解析器

1. 在 `backend/services/parsers/` 创建新解析器
2. 继承 `BaseDocumentParser`
3. 实现所有抽象方法
4. 在工厂函数中注册

### 添加新的向量存储

1. 在 `backend/services/stores/` 创建新存储
2. 继承 `BaseVectorStore`
3. 实现所有抽象方法
4. 在工厂函数中注册

### 添加新的LLM提供商

1. 在 `backend/services/llms/` 创建新LLM
2. 继承 `BaseLLM`
3. 实现所有抽象方法
4. 在工厂函数中注册

## 10. 测试策略

- 单元测试：每个解析器、存储、LLM的独立测试
- 集成测试：API端点测试
- E2E测试：完整RAG流程测试
- 目标覆盖率：80%+