# HotSwap RAG

🔄 **热插拔文档问答系统**

一个高度模块化的 RAG（检索增强生成）系统，支持在运行时动态切换文档解析器、向量数据库和 LLM 提供商。

## 特性

- 🔄 **热插拔架构**: 运行时切换组件，无需重启
- 📄 **多格式支持**: PDF, Word, OCR (扫描件/图片)
- 🗄️ **多向量库**: ChromaDB, Pinecone, Milvus, FAISS
- 🤖 **多 LLM**: OpenAI, Anthropic, Ollama, OpenAI 兼容端点
- 📚 **知识库管理**: 独立配置的知识库
- 💬 **RAG 问答**: 带引用来源的智能问答
- 🌊 **流式输出**: 支持 SSE 流式响应

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/your-repo/HotSwap-RAG.git
cd HotSwap-RAG
```

### 2. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥
```

### 4. 启动服务

**方式一: 直接运行**

```bash
# 启动后端 API
uvicorn backend.api.main:app --reload --port 8000

# 启动前端 (新终端)
streamlit run frontend/app.py
```

**方式二: Docker Compose**

```bash
docker-compose up -d
```

### 5. 访问应用

- 前端界面: http://localhost:8501
- API 文档: http://localhost:8000/docs

## 项目结构

```
HotSwap-RAG/
├── backend/
│   ├── core/           # 抽象基类 (策略模式)
│   ├── services/       # 具体实现
│   ├── factories/      # 工厂函数
│   ├── api/            # FastAPI 路由
│   ├── models/         # Pydantic 模型
│   ├── db/             # 数据库模型
│   └── utils/          # 工具函数
├── frontend/
│   ├── app.py          # Streamlit 入口
│   ├── pages/          # 多页面
│   └── components/     # 可复用组件
├── data/               # 数据存储
├── tests/              # 测试
└── docs/               # 文档
```

## 使用指南

### 创建知识库

1. 进入 "知识库管理" 页面
2. 点击 "创建新知识库"
3. 配置解析器、向量库和 LLM

### 上传文档

1. 进入 "文档管理" 页面
2. 选择文件上传
3. 选择目标知识库

### 开始问答

1. 进入 "智能问答" 页面
2. 选择知识库和模型
3. 输入问题，获取答案

## 开发指南

参见 [CLAUDE.md](./CLAUDE.md) 获取完整的开发指南。

### 运行测试

```bash
pytest tests/ -v
```

### 代码格式化

```bash
black .
isort .
```

## 扩展组件

### 添加新的文档解析器

```python
# backend/services/parsers/my_parser.py
from backend.core.base_parser import BaseDocumentParser

class MyParser(BaseDocumentParser):
    @property
    def name(self) -> str:
        return "My Custom Parser"

    def parse(self, file_path):
        # 实现解析逻辑
        pass

    def supported_formats(self):
        return [".myformat"]
```

### 添加新的 LLM 提供商

```python
# backend/services/llms/my_llm.py
from backend.core.base_llm import BaseLLM

class MyLLM(BaseLLM):
    @property
    def model_name(self) -> str:
        return "my-model"

    def generate(self, prompt, **kwargs):
        # 实现生成逻辑
        pass

    def stream_generate(self, prompt, **kwargs):
        # 实现流式生成
        pass
```

## License

MIT License