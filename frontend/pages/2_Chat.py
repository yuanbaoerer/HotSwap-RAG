"""Chat page for RAG Q&A."""

import streamlit as st
import requests
import json

from frontend.config import API_BASE_URL

st.set_page_config(page_title="智能问答 - HotSwap RAG", page_icon="💬")

st.title("💬 智能问答")
st.markdown("基于知识库的文档问答，支持引用来源追溯。")


def get_knowledge_bases():
    """Fetch knowledge bases from API."""
    try:
        response = requests.get(f"{API_BASE_URL}/api/knowledge-bases/", timeout=10)
        if response.status_code == 200:
            return response.json().get("knowledge_bases", [])
    except Exception as e:
        st.error(f"获取知识库列表失败: {e}")
    return []


def send_chat(question, kb_id=None, temperature=0.7, top_k=4, stream=False):
    """Send a chat request to the API."""
    try:
        if stream:
            # Use streaming endpoint
            response = requests.post(
                f"{API_BASE_URL}/api/chat/stream",
                json={
                    "question": question,
                    "kb_id": kb_id,
                    "temperature": temperature,
                    "top_k": top_k,
                },
                stream=True,
                timeout=60,
            )
            return response
        else:
            # Use regular endpoint
            response = requests.post(
                f"{API_BASE_URL}/api/chat/",
                json={
                    "question": question,
                    "kb_id": kb_id,
                    "temperature": temperature,
                    "top_k": top_k,
                },
                timeout=60,
            )
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"请求失败: {response.text}")
    except Exception as e:
        st.error(f"请求失败: {e}")
    return None


# Initialize chat history in session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# Sidebar for settings
with st.sidebar:
    st.subheader("配置")

    # Get knowledge bases from API
    kbs = get_knowledge_bases()
    kb_options = ["默认知识库 (default)"] + [f"{kb['name']} ({kb['id'][:8]}...)" for kb in kbs]
    kb_ids = [None] + [kb['id'] for kb in kbs]

    selected_kb_index = st.selectbox(
        "知识库",
        range(len(kb_options)),
        format_func=lambda i: kb_options[i],
        help="选择要查询的知识库",
    )
    selected_kb_id = kb_ids[selected_kb_index]

    llm = st.selectbox(
        "LLM 模型",
        ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "claude-3-5-sonnet-20241022", "llama3.2"],
        help="选择生成回答的模型",
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=0.7,
        step=0.1,
        help="控制回答的随机性，值越低越确定",
    )

    top_k = st.slider(
        "检索数量",
        min_value=1,
        max_value=10,
        value=4,
        help="从知识库检索的相关文档数量",
    )

    stream_response = st.checkbox("流式输出", value=True, help="实时显示生成内容")

    st.divider()

    # Clear history button
    if st.button("🗑️ 清空对话历史", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

    # API status
    st.divider()
    st.subheader("API 状态")
    try:
        health = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if health.status_code == 200:
            st.success("后端连接正常")
        else:
            st.error("后端异常")
    except Exception:
        st.error("无法连接后端")

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Show sources if available
        if msg.get("sources"):
            with st.expander("📚 查看引用来源"):
                for i, source in enumerate(msg["sources"], 1):
                    filename = source.get("filename", "未知文档")
                    snippet = source.get("content_snippet", "")
                    score = source.get("score")

                    st.markdown(f"**来源 {i}**: `{filename}`")
                    if score:
                        st.caption(f"相关度: {score:.3f}")
                    st.markdown(f"> {snippet[:200]}...")
                    st.divider()

# Chat input
if prompt := st.chat_input("输入你的问题..."):
    # Add user message to history
    st.session_state.chat_history.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        if stream_response:
            # Streaming response
            response = send_chat(
                prompt,
                kb_id=selected_kb_id,
                temperature=temperature,
                top_k=top_k,
                stream=True,
            )

            if response:
                placeholder = st.empty()
                full_response = ""
                sources = []

                for line in response.iter_lines():
                    if line:
                        line = line.decode("utf-8")
                        if line.startswith("data: "):
                            try:
                                data = json.loads(line[6:])
                                if "content" in data:
                                    full_response += data["content"]
                                    placeholder.markdown(full_response + "▌")
                                if "sources" in data:
                                    sources = data["sources"]
                                if data.get("done"):
                                    placeholder.markdown(full_response)
                            except json.JSONDecodeError:
                                continue

                # Show sources
                if sources:
                    with st.expander("📚 查看引用来源"):
                        for i, source in enumerate(sources, 1):
                            filename = source.get("filename", "未知文档")
                            snippet = source.get("content_snippet", "")
                            score = source.get("score")

                            st.markdown(f"**来源 {i}**: `{filename}`")
                            if score:
                                st.caption(f"相关度: {score:.3f}")
                            st.markdown(f"> {snippet}")
                            st.divider()

                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources,
                })
        else:
            # Non-streaming response
            with st.spinner("思考中..."):
                response = send_chat(
                    prompt,
                    kb_id=selected_kb_id,
                    temperature=temperature,
                    top_k=top_k,
                    stream=False,
                )

            if response:
                answer = response.get("answer", "")
                sources = response.get("sources", [])
                model = response.get("model", "")

                st.markdown(answer)
                if model:
                    st.caption(f"模型: {model}")

                # Show sources
                if sources:
                    with st.expander("📚 查看引用来源"):
                        for i, source in enumerate(sources, 1):
                            filename = source.get("filename", "未知文档")
                            snippet = source.get("content_snippet", "")
                            score = source.get("score")

                            st.markdown(f"**来源 {i}**: `{filename}`")
                            if score:
                                st.caption(f"相关度: {score:.3f}")
                            st.markdown(f"> {snippet}")
                            st.divider()

                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                })