"""Settings page for managing system configuration."""

import streamlit as st
import os

st.set_page_config(page_title="系统设置 - HotSwap RAG", page_icon="⚙️")

st.title("⚙️ 系统设置")
st.markdown("配置系统的解析器、向量数据库和 LLM 提供商。")

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

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 文档解析器")
    parser = st.selectbox(
        "选择解析器",
        ["pdf", "docx", "ocr"],
        index=0,
        key="active_parser",
    )
    st.markdown("""
**PDF Parser**: 使用 PyPDF2 解析 PDF 文件
**DOCX Parser**: 使用 python-docx 解析 Word 文档
**OCR Parser**: 使用 Tesseract 解析扫描件和图片
    """)

with col2:
    st.markdown("### 向量数据库")
    store = st.selectbox(
        "选择向量库",
        ["chromadb", "pinecone", "milvus", "faiss"],
        index=0,
        key="active_store",
    )
    st.markdown("""
**ChromaDB**: 本地开发推荐，零配置
**Pinecone**: 云端托管，生产级
**Milvus**: 自托管，可扩展
**FAISS**: Facebook 开源，轻量级
    """)

with col3:
    st.markdown("### LLM 提供商")
    llm = st.selectbox(
        "选择 LLM",
        ["openai", "anthropic", "ollama", "openai_compatible"],
        index=0,
        key="active_llm",
    )
    st.markdown("""
**OpenAI**: GPT-4, GPT-3.5
**Anthropic**: Claude 系列
**Ollama**: 本地模型
**OpenAI 兼容**: 自定义端点
    """)

if st.button("💾 保存配置", type="primary"):
    st.success("配置已保存！")

# Model selection
st.subheader("🤖 模型配置")

col1, col2 = st.columns(2)

with col1:
    llm_model = st.text_input(
        "LLM 模型名称",
        value="gpt-4o-mini",
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