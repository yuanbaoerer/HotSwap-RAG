"""Settings page for managing system configuration."""

import streamlit as st
import requests
import os

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="系统设置 - HotSwap RAG", page_icon="⚙️")

st.title("⚙️ 系统设置")
st.markdown("配置系统的解析器、向量数据库和 LLM 提供商。")


def get_config(endpoint):
    """Fetch config from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/config/{endpoint}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取配置失败: {e}")
    return []


def get_active_config():
    """Fetch active config from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/config/active", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取配置失败: {e}")
    return None


def update_active_config(config):
    """Update active config via API."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/config/active",
            json=config,
            timeout=10,
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"更新配置失败: {e}")
    return False


# API Keys configuration
st.subheader("🔑 API 密钥配置")

with st.expander("配置 API 密钥", expanded=True):
    st.markdown("""
API 密钥从环境变量或 `.env` 文件读取。
请在项目根目录创建 `.env` 文件并配置：
""")

    st.code("""
# OpenAI
OPENAI_API_KEY=sk-xxx

# Anthropic
ANTHROPIC_API_KEY=sk-ant-xxx

# Pinecone
PINECONE_API_KEY=xxx
PINECONE_ENVIRONMENT=xxx

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
    """, language="bash")

    # Show current status
    col1, col2 = st.columns(2)

    with col1:
        openai_status = "✅ 已配置" if os.environ.get("OPENAI_API_KEY") else "❌ 未配置"
        st.markdown(f"**OpenAI**: {openai_status}")

        anthropic_status = "✅ 已配置" if os.environ.get("ANTHROPIC_API_KEY") else "❌ 未配置"
        st.markdown(f"**Anthropic**: {anthropic_status}")

    with col2:
        pinecone_status = "✅ 已配置" if os.environ.get("PINECONE_API_KEY") else "❌ 未配置"
        st.markdown(f"**Pinecone**: {pinecone_status}")

        ollama_url = os.environ.get("OLLAMA_BASE_URL", "未设置")
        st.markdown(f"**Ollama URL**: `{ollama_url}`")

# Active configuration
st.subheader("🔄 当前活跃配置")

# Fetch available options
parsers = get_config("parsers")
stores = get_config("stores")
llms = get_config("llms")
active_config = get_active_config()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 文档解析器")
    parser_types = [p["type"] for p in parsers]
    current_parser = active_config.get("parser_type", "pdf") if active_config else "pdf"
    parser_index = parser_types.index(current_parser) if current_parser in parser_types else 0

    parser = st.selectbox(
        "选择解析器",
        parser_types,
        index=parser_index,
        key="active_parser",
    )
    st.markdown("""
**pdf**: 使用 PyPDF2 解析 PDF 文件
**docx**: 使用 python-docx 解析 Word 文档
**ocr**: 使用 Tesseract 解析扫描件和图片
    """)

with col2:
    st.markdown("### 向量数据库")
    store_types = [s["type"] for s in stores]
    current_store = active_config.get("store_type", "chromadb") if active_config else "chromadb"
    store_index = store_types.index(current_store) if current_store in store_types else 0

    store = st.selectbox(
        "选择向量库",
        store_types,
        index=store_index,
        key="active_store",
    )
    st.markdown("""
**chromadb**: 本地开发推荐，零配置
**pinecone**: 云端托管，生产级
**milvus**: 自托管，可扩展
**faiss**: Facebook 开源，轻量级
    """)

with col3:
    st.markdown("### LLM 提供商")
    llm_types = [l["type"] for l in llms]
    current_llm = active_config.get("llm_type", "openai") if active_config else "openai"
    llm_index = llm_types.index(current_llm) if current_llm in llm_types else 0

    llm = st.selectbox(
        "选择 LLM",
        llm_types,
        index=llm_index,
        key="active_llm",
    )
    st.markdown("""
**openai**: GPT-4, GPT-3.5
**anthropic**: Claude 系列
**ollama**: 本地模型
**openai_compatible**: 自定义端点
    """)

if st.button("💾 保存配置", type="primary"):
    new_config = {
        "parser_type": parser,
        "store_type": store,
        "llm_type": llm,
        "llm_model": active_config.get("llm_model", "gpt-4o-mini") if active_config else "gpt-4o-mini",
    }
    if update_active_config(new_config):
        st.success("配置已保存！")
    else:
        st.error("保存配置失败")

# Model selection
st.subheader("🤖 模型配置")

col1, col2 = st.columns(2)

with col1:
    current_model = active_config.get("llm_model", "gpt-4o-mini") if active_config else "gpt-4o-mini"
    llm_model = st.text_input(
        "LLM 模型名称",
        value=current_model,
        help="LLM 模型名称，如 gpt-4o-mini, claude-3-5-sonnet-20241022",
    )

with col2:
    embedding_model = st.text_input(
        "Embedding 模型",
        value="text-embedding-3-small",
        help="OpenAI embedding 模型名称",
    )

# Advanced settings
st.subheader("🔧 高级设置")

with st.expander("显示高级设置"):
    col1, col2 = st.columns(2)

    with col1:
        chunk_size = st.slider(
            "文本块大小",
            min_value=200,
            max_value=2000,
            value=1000,
            step=100,
            help="文档分割时的文本块大小（字符数）",
        )

        chunk_overlap = st.slider(
            "文本块重叠",
            min_value=0,
            max_value=500,
            value=200,
            step=50,
            help="相邻文本块之间的重叠字符数",
        )

    with col2:
        max_tokens = st.number_input(
            "最大 Token 数",
            min_value=100,
            max_value=8000,
            value=4096,
            step=256,
            help="LLM 响应的最大 token 数",
        )

        temperature_default = st.slider(
            "默认 Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="LLM 生成的默认温度值",
        )

# System info
st.subheader("ℹ️ 系统信息")

st.markdown(f"""
- **Python 版本**: 3.10+
- **平台**: {os.name}
- **数据目录**: `./data/`
- **文档目录**: `./data/documents/`
- **向量存储目录**: `./data/vector_stores/`
""")

# API Status
st.subheader("🔌 API 状态")

try:
    health = requests.get(f"{API_BASE_URL}/health", timeout=5)
    if health.status_code == 200:
        st.success(f"后端 API 运行中 - 版本: {health.json().get('version', 'unknown')}")
    else:
        st.error("后端 API 异常")
except Exception as e:
    st.error(f"无法连接后端 API: {e}")