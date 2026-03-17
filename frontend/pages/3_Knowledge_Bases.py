"""Knowledge base management page."""

import streamlit as st
import requests
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="知识库管理 - HotSwap RAG", page_icon="📚")

st.title("📚 知识库管理")
st.markdown("创建和管理知识库，每个知识库可以有独立的解析器、向量库和 LLM 配置。")


def get_knowledge_bases():
    """Fetch knowledge bases from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge-bases/", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取知识库列表失败: {e}")
    return {"knowledge_bases": [], "total": 0}


def create_knowledge_base(name, description, parser_type, store_type, llm_type):
    """Create a knowledge base via API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/knowledge-bases/",
            json={
                "name": name,
                "description": description,
                "parser_type": parser_type,
                "store_type": store_type,
                "llm_type": llm_type,
            },
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"创建失败: {response.text}")
    except Exception as e:
        st.error(f"创建失败: {e}")
    return None


def get_knowledge_base(kb_id):
    """Get a specific knowledge base."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge-bases/{kb_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取知识库失败: {e}")
    return None


def delete_knowledge_base(kb_id):
    """Delete a knowledge base via API."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/knowledge-bases/{kb_id}", timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"删除失败: {e}")
    return None


def update_knowledge_base(kb_id, **kwargs):
    """Update a knowledge base via API."""
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/knowledge-bases/{kb_id}",
            json=kwargs,
            timeout=10,
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"更新失败: {e}")
    return None


# Initialize session state for selected KB
if "selected_kb_id" not in st.session_state:
    st.session_state.selected_kb_id = None


# Create new knowledge base
with st.expander("➕ 创建新知识库", expanded=False):
    col1, col2 = st.columns(2)

    with col1:
        kb_name = st.text_input("知识库名称", placeholder="例如：产品文档库", key="new_kb_name")
        kb_description = st.text_area("描述", placeholder="知识库的简要描述...", key="new_kb_desc")

    with col2:
        kb_parser = st.selectbox(
            "文档解析器",
            ["pdf", "docx", "ocr"],
            help="默认使用的文档解析器",
            key="new_kb_parser",
        )
        kb_store = st.selectbox(
            "向量数据库",
            ["chromadb", "pinecone", "milvus", "faiss"],
            help="存储文档向量的数据库",
            key="new_kb_store",
        )
        kb_llm = st.selectbox(
            "LLM 提供商",
            ["openai", "anthropic", "ollama", "openai_compatible"],
            help="用于生成回答的 LLM",
            key="new_kb_llm",
        )

    if st.button("创建", type="primary"):
        if kb_name:
            result = create_knowledge_base(kb_name, kb_description, kb_parser, kb_store, kb_llm)
            if result:
                st.success(f"知识库 '{kb_name}' 创建成功！ID: {result['id'][:8]}...")
                st.rerun()
        else:
            st.warning("请输入知识库名称")


# Knowledge base list
st.subheader("知识库列表")

col_refresh, col_count = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 刷新"):
        st.rerun()

with col_count:
    kbs_data = get_knowledge_bases()
    st.markdown(f"**共 {kbs_data.get('total', 0)} 个知识库**")

# Display knowledge bases
knowledge_bases = kbs_data.get("knowledge_bases", [])

if knowledge_bases:
    for kb in knowledge_bases:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.markdown(f"### {kb['name']}")
                st.markdown(kb.get('description') or '无描述')

            with col2:
                st.markdown(f"📄 解析器: `{kb['parser_type']}`")
                st.markdown(f"🗄️ 向量库: `{kb['store_type']}`")
                st.markdown(f"🤖 LLM: `{kb['llm_type']}`")

            with col3:
                st.metric("文档数", kb.get('document_count', 0))

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📂 打开", key=f"open-{kb['id']}"):
                    st.session_state.selected_kb_id = kb['id']
                    st.info(f"已选择知识库: {kb['name']}")

            with col2:
                if st.button("💬 问答", key=f"chat-{kb['id']}"):
                    st.session_state.selected_kb_id = kb['id']
                    st.info(f"跳转到问答页面，已选择: {kb['name']}")

            with col3:
                if st.button("⚙️ 设置", key=f"settings-{kb['id']}"):
                    st.session_state.editing_kb = kb['id']

            with col4:
                if st.button("🗑️ 删除", key=f"delete-{kb['id']}"):
                    st.session_state.deleting_kb = kb['id']

            # Show edit form if editing
            if st.session_state.get("editing_kb") == kb['id']:
                with st.form(f"edit-form-{kb['id']}"):
                    st.markdown("**编辑知识库**")
                    new_name = st.text_input("名称", value=kb['name'])
                    new_desc = st.text_area("描述", value=kb.get('description', ''))
                    new_parser = st.selectbox(
                        "解析器",
                        ["pdf", "docx", "ocr"],
                        index=["pdf", "docx", "ocr"].index(kb['parser_type']),
                    )
                    new_store = st.selectbox(
                        "向量库",
                        ["chromadb", "pinecone", "milvus", "faiss"],
                        index=["chromadb", "pinecone", "milvus", "faiss"].index(kb['store_type']),
                    )
                    new_llm = st.selectbox(
                        "LLM",
                        ["openai", "anthropic", "ollama", "openai_compatible"],
                        index=["openai", "anthropic", "ollama", "openai_compatible"].index(kb['llm_type']),
                    )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.form_submit_button("保存", type="primary"):
                            result = update_knowledge_base(
                                kb['id'],
                                name=new_name,
                                description=new_desc,
                                parser_type=new_parser,
                                store_type=new_store,
                                llm_type=new_llm,
                            )
                            if result:
                                st.success("更新成功！")
                                st.session_state.editing_kb = None
                                st.rerun()
                    with col_cancel:
                        if st.form_submit_button("取消"):
                            st.session_state.editing_kb = None
                            st.rerun()

            # Show delete confirmation
            if st.session_state.get("deleting_kb") == kb['id']:
                st.warning(f"确定要删除知识库 '{kb['name']}' 吗？此操作将删除所有关联文档！")
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("✅ 确认删除", key=f"confirm-del-{kb['id']}"):
                        result = delete_knowledge_base(kb['id'])
                        if result:
                            st.success(f"已删除知识库: {kb['name']}")
                            st.session_state.deleting_kb = None
                            st.rerun()
                with col_cancel:
                    if st.button("❌ 取消", key=f"cancel-del-{kb['id']}"):
                        st.session_state.deleting_kb = None
                        st.rerun()

            st.divider()

else:
    st.info("暂无知识库。点击上方创建新知识库。")


# Statistics
st.subheader("统计信息")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("知识库总数", len(knowledge_bases))

with col2:
    total_docs = sum(kb.get('document_count', 0) for kb in knowledge_bases)
    st.metric("文档总数", total_docs)

with col3:
    st.metric("选中的知识库", st.session_state.get('selected_kb_id', '无')[:8] if st.session_state.get('selected_kb_id') else '无')