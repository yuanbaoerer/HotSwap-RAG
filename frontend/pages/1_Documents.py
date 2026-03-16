"""Documents management page."""

import streamlit as st
from pathlib import Path

st.set_page_config(page_title="文档管理 - HotSwap RAG", page_icon="📄")

st.title("📄 文档管理")
st.markdown("上传和管理文档，支持 PDF、Word 和图片格式。")

# Upload section
st.subheader("上传文档")

uploaded_files = st.file_uploader(
    "选择文件上传",
    type=["pdf", "docx", "png", "jpg", "jpeg", "tiff"],
    accept_multiple_files=True,
)

kb_options = ["默认知识库", "创建新知识库..."]
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
            for file in uploaded_files:
                st.success(f"已上传: {file.name}")
        else:
            st.warning("请先选择文件")

# Document list
st.subheader("文档列表")

# Placeholder for document list
if st.button("🔄 刷新"):
    st.rerun()

# Sample table (placeholder)
import pandas as pd

data = {
    "文件名": [],
    "类型": [],
    "大小": [],
    "状态": [],
    "上传时间": [],
}

if data["文件名"]:
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)
else:
    st.info("暂无文档。上传文档后将在此显示。")

# Actions
st.subheader("操作")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🗑️ 批量删除"):
        st.warning("请先选择要删除的文档")

with col2:
    if st.button("📥 导出索引"):
        st.info("功能开发中...")

with col3:
    if st.button("🔄 重新处理"):
        st.info("功能开发中...")