"""Streamlit frontend application entry point."""

import streamlit as st

st.set_page_config(
    page_title="HotSwap RAG",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🔄 HotSwap RAG")
st.markdown("""
**热插拔文档问答系统**

在运行时动态切换：
- 📄 文档解析器 (PDF, Word, OCR)
- 🗄️ 向量数据库 (ChromaDB, Pinecone, Milvus, FAISS)
- 🤖 LLM 提供商 (OpenAI, Anthropic, Ollama)

👈 使用侧边栏导航到不同页面。
""")

# Quick stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="📄 文档数量", value="0")

with col2:
    st.metric(label="📚 知识库", value="0")

with col3:
    st.metric(label="💬 对话次数", value="0")

with col4:
    st.metric(label="🔍 检索次数", value="0")

# Current configuration
st.subheader("当前配置")
with st.expander("查看当前活跃配置", expanded=False):
    st.json({
        "parser": "pdf",
        "store": "chromadb",
        "llm": "openai",
        "model": "gpt-4o-mini",
    })