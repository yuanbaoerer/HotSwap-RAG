"""Settings page for managing system configuration."""

import streamlit as st
import requests
import os

from frontend.config import API_BASE_URL

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


def get_api_keys():
    """Fetch API keys from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/config/api-keys", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取 API 密钥失败: {e}")
    return {}


def update_api_keys(api_keys):
    """Update API keys via API."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/config/api-keys",
            json=api_keys,
            timeout=10,
        )
        if response.status_code == 200:
            return True
        else:
            st.error(f"更新失败: {response.text}")
    except Exception as e:
        st.error(f"更新失败: {e}")
    return False


def delete_api_key(key_name):
    """Delete a specific API key."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/config/api-keys/{key_name}",
            timeout=10,
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"删除失败: {e}")
    return False


# API Keys configuration
st.subheader("🔑 API 密钥配置")

# Get current API keys status
api_keys = get_api_keys()

with st.expander("管理 API 密钥", expanded=True):
    st.markdown("""
API 密钥存储在数据库中，优先级高于环境变量。
留空则使用环境变量或删除已存储的密钥。
""")

    # Create form for API keys
    with st.form("api_keys_form"):
        st.markdown("#### LLM 提供商密钥")

        col1, col2 = st.columns(2)

        with col1:
            openai_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-...",
                help="用于 OpenAI GPT 模型",
            )

            anthropic_key = st.text_input(
                "Anthropic API Key",
                type="password",
                placeholder="sk-ant-...",
                help="用于 Claude 模型",
            )

        with col2:
            ollama_url = st.text_input(
                "Ollama Base URL",
                value=api_keys.get("ollama_base_url", {}).get("masked_value", "http://localhost:11434"),
                help="Ollama 服务地址",
            )

        st.markdown("#### 向量数据库密钥")

        col1, col2 = st.columns(2)

        with col1:
            pinecone_key = st.text_input(
                "Pinecone API Key",
                type="password",
                placeholder="Enter Pinecone API key",
                help="用于 Pinecone 向量数据库",
            )

        with col2:
            pinecone_env = st.text_input(
                "Pinecone Environment",
                placeholder="us-east-1",
                help="Pinecone 环境名称",
            )

        st.markdown("#### Milvus 配置")

        col1, col2 = st.columns(2)

        with col1:
            milvus_host = st.text_input(
                "Milvus Host",
                value="localhost",
                help="Milvus 服务器地址",
            )

        with col2:
            milvus_port = st.number_input(
                "Milvus Port",
                value=19530,
                help="Milvus 服务器端口",
            )

        col1, col2 = st.columns(2)

        with col1:
            submitted = st.form_submit_button("💾 保存密钥", type="primary")

        with col2:
            clear = st.form_submit_button("🗑️ 清空所有密钥")

    if submitted:
        # Build API keys dict
        keys_to_save = {}

        if openai_key:
            keys_to_save["openai_api_key"] = openai_key
        if anthropic_key:
            keys_to_save["anthropic_api_key"] = anthropic_key
        if ollama_url:
            keys_to_save["ollama_base_url"] = ollama_url
        if pinecone_key:
            keys_to_save["pinecone_api_key"] = pinecone_key
        if pinecone_env:
            keys_to_save["pinecone_environment"] = pinecone_env
        if milvus_host:
            keys_to_save["milvus_host"] = milvus_host
        if milvus_port:
            keys_to_save["milvus_port"] = milvus_port

        if update_api_keys(keys_to_save):
            st.success("API 密钥已保存！")
            st.rerun()

    if clear:
        # Delete all keys
        for key_name in ["openai_api_key", "anthropic_api_key", "pinecone_api_key", "pinecone_environment"]:
            delete_api_key(key_name)
        st.success("已清空所有存储的密钥")
        st.rerun()

    # Show current status
    st.markdown("---")
    st.markdown("#### 当前密钥状态")

    col1, col2 = st.columns(2)

    with col1:
        openai_info = api_keys.get("openai_api_key", {})
        if openai_info.get("configured"):
            st.success(f"✅ OpenAI: {openai_info.get('masked_value', '')} ({openai_info.get('source', '')})")
        else:
            st.warning("❌ OpenAI: 未配置")

        anthropic_info = api_keys.get("anthropic_api_key", {})
        if anthropic_info.get("configured"):
            st.success(f"✅ Anthropic: {anthropic_info.get('masked_value', '')} ({anthropic_info.get('source', '')})")
        else:
            st.warning("❌ Anthropic: 未配置")

    with col2:
        pinecone_info = api_keys.get("pinecone_api_key", {})
        if pinecone_info.get("configured"):
            st.success(f"✅ Pinecone: {pinecone_info.get('masked_value', '')} ({pinecone_info.get('source', '')})")
        else:
            st.warning("❌ Pinecone: 未配置")

        ollama_info = api_keys.get("ollama_base_url", {})
        if ollama_info.get("configured"):
            st.success(f"✅ Ollama: {ollama_info.get('masked_value', '')} ({ollama_info.get('source', '')})")
        else:
            st.warning("❌ Ollama: 未配置")

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