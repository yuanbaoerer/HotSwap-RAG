"""Documents management page."""

import streamlit as st
import requests
import pandas as pd
import json

from frontend.config import API_BASE_URL

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


def get_knowledge_bases():
    """Fetch knowledge bases from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge-bases/", timeout=10)
        if response.status_code == 200:
            return response.json().get("knowledge_bases", [])
    except Exception as e:
        st.error(f"获取知识库列表失败: {e}")
    return []


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


def delete_all_documents(documents):
    """Delete all documents."""
    deleted = 0
    failed = 0
    for doc in documents:
        if delete_document(doc["id"]):
            deleted += 1
        else:
            failed += 1
    return deleted, failed


# Upload section
st.subheader("上传文档")

uploaded_files = st.file_uploader(
    "选择文件上传",
    type=["pdf", "docx", "png", "jpg", "jpeg", "tiff", "md", "txt"],
    accept_multiple_files=True,
)

# Get knowledge bases for selection
kbs = get_knowledge_bases()
kb_options = ["默认知识库"] + [f"{kb['name']} ({kb['id'][:8]}...)" for kb in kbs]
kb_ids = [None] + [kb['id'] for kb in kbs]

selected_kb_index = st.selectbox("选择知识库", range(len(kb_options)), format_func=lambda i: kb_options[i])
selected_kb_id = kb_ids[selected_kb_index]

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
                result = upload_document(file, selected_kb_id)
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

# Other actions
st.subheader("其他操作")

col1, col2, col3 = st.columns(3)

with col1:
    # Export index
    if st.button("📥 导出索引"):
        if documents:
            # Create export data
            export_data = {
                "export_time": pd.Timestamp.now().isoformat(),
                "total_documents": len(documents),
                "documents": documents,
            }

            # Convert to JSON
            json_data = json.dumps(export_data, ensure_ascii=False, indent=2)

            # Download button
            st.download_button(
                label="下载索引文件",
                data=json_data,
                file_name=f"document_index_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
            )
        else:
            st.warning("没有文档可以导出")

with col2:
    # Reprocess all documents
    if st.button("🔄 重新处理所有文档"):
        if documents:
            # Filter documents that can be reprocessed
            reprocessable = [d for d in documents if d["status"] in ["completed", "failed"]]
            if reprocessable:
                st.info(f"将重新处理 {len(reprocessable)} 个文档。")
                st.warning("注意：此功能需要重新上传文档才能触发处理。")
            else:
                st.info("没有需要重新处理的文档。")
        else:
            st.warning("没有文档可以处理")

with col3:
    # Clear all documents
    if st.button("🗑️ 清空所有文档"):
        st.session_state.confirm_clear = True

    # Confirmation dialog
    if st.session_state.get("confirm_clear"):
        st.warning(f"确定要删除所有 {len(documents)} 个文档吗？此操作不可撤销！")
        col_confirm, col_cancel = st.columns(2)

        with col_confirm:
            if st.button("✅ 确认清空", type="primary"):
                deleted, failed = delete_all_documents(documents)
                st.session_state.confirm_clear = False
                if failed == 0:
                    st.success(f"已删除所有 {deleted} 个文档")
                else:
                    st.warning(f"删除 {deleted} 个，失败 {failed} 个")
                st.rerun()

        with col_cancel:
            if st.button("❌ 取消"):
                st.session_state.confirm_clear = False
                st.rerun()

# Statistics
st.subheader("统计信息")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("文档总数", len(documents))

with col2:
    completed = sum(1 for d in documents if d["status"] == "completed")
    st.metric("处理完成", completed)

with col3:
    processing = sum(1 for d in documents if d["status"] == "processing")
    st.metric("处理中", processing)

with col4:
    failed = sum(1 for d in documents if d["status"] == "failed")
    st.metric("处理失败", failed)