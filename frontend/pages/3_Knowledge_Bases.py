"""Knowledge base management page."""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="知识库管理 - HotSwap RAG", page_icon="📚")

st.title("📚 知识库管理")
st.markdown("创建和管理知识库，每个知识库可以有独立的解析器、向量库和 LLM 配置。")

# Create new knowledge base
with st.expander("➕ 创建新知识库", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        kb_name = st.text_input("知识库名称", placeholder="例如：产品文档库")
        kb_description = st.text_area("描述", placeholder="知识库的简要描述...")

    with col2:
        kb_parser = st.selectbox(
            "文档解析器",
            ["pdf", "docx", "ocr"],
            help="默认使用的文档解析器",
        )
        kb_store = st.selectbox(
            "向量数据库",
            ["chromadb", "pinecone", "milvus", "faiss"],
            help="存储文档向量的数据库",
        )
        kb_llm = st.selectbox(
            "LLM 提供商",
            ["openai", "anthropic", "ollama", "openai_compatible"],
            help="用于生成回答的 LLM",
        )

    if st.button("创建", type="primary"):
        if kb_name:
            st.success(f"知识库 '{kb_name}' 创建成功！")
        else:
            st.warning("请输入知识库名称")

# Knowledge base list
st.subheader("知识库列表")

# Sample data (placeholder)
knowledge_bases = [
    {
        "id": "kb-001",
        "name": "默认知识库",
        "description": "系统默认知识库",
        "parser": "pdf",
        "store": "chromadb",
        "llm": "openai",
        "documents": 0,
        "created": "2024-01-01",
    },
]

for kb in knowledge_bases:
    with st.container():
        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            st.markdown(f"### {kb['name']}")
            st.markdown(kb['description'])

        with col2:
            st.markdown(f"📄 解析器: `{kb['parser']}`")
            st.markdown(f"🗄️ 向量库: `{kb['store']}`")
            st.markdown(f"🤖 LLM: `{kb['llm']}`")

        with col3:
            st.metric("文档数", kb['documents'])

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📂 打开", key=f"open-{kb['id']}"):
                st.info("跳转到文档管理...")

        with col2:
            if st.button("💬 问答", key=f"chat-{kb['id']}"):
                st.info("跳转到问答页面...")

        with col3:
            if st.button("⚙️ 设置", key=f"settings-{kb['id']}"):
                st.info("打开设置...")

        with col4:
            if st.button("🗑️ 删除", key=f"delete-{kb['id']}"):
                st.warning("确认删除？此操作不可恢复。")

        st.divider()

# Statistics
st.subheader("统计信息")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("知识库总数", len(knowledge_bases))

with col2:
    total_docs = sum(kb['documents'] for kb in knowledge_bases)
    st.metric("文档总数", total_docs)

with col3:
    st.metric("存储占用", "0 MB")