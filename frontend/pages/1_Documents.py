"""Documents management page."""

import streamlit as st
import requests
import pandas as pd
from pathlib import Path

# Configuration
API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="文档管理 - HotSwap RAG", page_icon="📄")

st.title("📄 文档管理")
st.markdown("上传和管理文档，支持 PDF、Word 和图片格式。")


def get_documents():
    """Fetch documents from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/documents/", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"获取文档列表失败: {e}")
    return {"documents": [], "total": 0}


def upload_document(file, kb_id=None):
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file, file.type)}
        data = {}
        if kb_id:
            data["kb_id"] = kb_id

        response = requests.post(
            f"{API_BASE_URL}/api/documents/",
            files=files,
            data=data,
            timeout=30,
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"上传失败: {response.text}")
    except Exception as e:
        st.error(f"上传失败: {e}")
    return None


def delete_document(doc_id):
    """Delete a document via API."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/documents/{doc_id}", timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        st.error(f"删除失败: {e}")
    return False


# Upload section
st.subheader("上传文档")

uploaded_files = st.file_uploader(
    "选择文件上传",
    type=["pdf", "docx", "png", "jpg", "jpeg", "tiff", "md", "txt"],
    accept_multiple_files=True,
)

kb_options = ["默认知识库"]
selected_kb = st.selectbox("选择知识库", kb_options)

col1, col2 = st.columns(2)

with col1:
    parser_type = st.selectbox(
        "文档解析器",
        ["pdf", "docx", "ocr"],
        help="选择用于解析文档的解析器类型",
    )

with col2:
    if st.button("上传", type="primary", use_container_width=True):
        if uploaded_files:
            progress_bar = st.progress(0)
            for i, file in enumerate(uploaded_files):
                result = upload_document(file)
                if result:
                    st.success(f"已上传: {file.name} (ID: {result['id'][:8]}...)")
                progress_bar.progress((i + 1) / len(uploaded_files))
            st.rerun()
        else:
            st.warning("请先选择文件")

# Document list
st.subheader("文档列表")

col_refresh, col_count = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 刷新"):
        st.rerun()

with col_count:
    docs_data = get_documents()
    st.markdown(f"**共 {docs_data.get('total', 0)} 个文档**")

# Display documents
documents = docs_data.get("documents", [])

if documents:
    # Create dataframe
    df_data = {
        "ID": [doc["id"][:8] + "..." for doc in documents],
        "文件名": [doc["filename"] for doc in documents],
        "类型": [doc.get("file_type", "-") for doc in documents],
        "大小": [f"{doc['size'] / 1024:.1f} KB" for doc in documents],
        "状态": [doc["status"] for doc in documents],
        "上传时间": [doc["created_at"][:19].replace("T", " ") for doc in documents],
    }

    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Delete functionality
    st.subheader("操作")

    col1, col2 = st.columns([2, 3])

    with col1:
        doc_to_delete = st.text_input("输入文档 ID 删除", placeholder="如: da181e56")

    with col2:
        if st.button("🗑️ 删除文档"):
            if doc_to_delete:
                # Find full ID
                for doc in documents:
                    if doc["id"].startswith(doc_to_delete):
                        if delete_document(doc["id"]):
                            st.success(f"已删除: {doc['filename']}")
                            st.rerun()
                        break
                else:
                    st.warning("未找到匹配的文档 ID")
            else:
                st.warning("请输入要删除的文档 ID")

else:
    st.info("暂无文档。上传文档后将在此显示。")

# Actions
st.subheader("其他操作")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📥 导出索引"):
        st.info("功能开发中...")

with col2:
    if st.button("🔄 重新处理所有文档"):
        st.info("功能开发中...")

with col3:
    if st.button("🗑️ 清空所有文档"):
        st.warning("此功能需要确认，暂不可用")