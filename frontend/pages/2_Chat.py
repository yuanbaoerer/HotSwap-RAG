"""Chat page for RAG Q&A."""

import streamlit as st

st.set_page_config(page_title="智能问答 - HotSwap RAG", page_icon="💬")

st.title("💬 智能问答")
st.markdown("基于知识库的文档问答，支持引用来源追溯。")

# Sidebar for settings
with st.sidebar:
    st.subheader("配置")

    kb = st.selectbox(
        "知识库",
        ["默认知识库"],
        help="选择要查询的知识库",
    )

    llm = st.selectbox(
        "LLM 模型",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "claude-3-5-sonnet", "llama3.2"],
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="控制回答的随机性",
    )

    top_k = st.slider(
        "检索数量",
        min_value=1,
        max_value=10,
        value=4,
        help="从知识库检索的相关文档数量",
    )

    stream_response = st.checkbox("流式输出", value=True)

# Main chat area
chat_container = st.container()

# Input area
st.subheader("提问")

col1, col2 = st.columns([4, 1])

with col1:
    question = st.text_area(
        "输入你的问题",
        height=100,
        placeholder="例如：这份文档的主要内容是什么？",
    )

with col2:
    st.write("")  # Spacing
    st.write("")
    submit = st.button("发送", type="primary", use_container_width=True)

# Process question
if submit and question:
    with st.spinner("思考中..."):
        # Placeholder response
        response = f"""
这是对问题的示例回答："{question[:50]}..."

实际使用时，系统会：
1. 从知识库检索相关文档片段
2. 将问题和上下文发送给 LLM
3. 生成带有引用来源的回答

当前配置：
- 知识库: {kb}
- 模型: {llm}
- Temperature: {temperature}
- 检索数量: {top_k}
        """

        st.markdown(response)

        # Sources
        with st.expander("📚 查看引用来源"):
            st.markdown("""
**来源 1**: document1.pdf (第 3 页)
> 相关文本片段...

**来源 2**: document2.pdf (第 15 页)
> 相关文本片段...
            """)
elif submit:
    st.warning("请输入问题")

# Chat history
st.subheader("对话历史")
if st.button("🗑️ 清空历史"):
    st.success("对话历史已清空")

st.info("对话历史将在此显示。")