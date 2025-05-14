import streamlit as st
from agent import run_agent
import re

# --- Helper to extract sections and links ---
def extract_sections(text):
    # Try to extract markdown-style or ReAct-style answers
    answer_match = re.search(r"(?:Paraphrased Answer|Final Answer)\s*[:\-]?\s*(.*?)(\n[A-Z][a-z]+:|Thought:|$)", text, re.DOTALL | re.IGNORECASE)
    final_text = answer_match.group(1).strip() if answer_match else text.strip() or "*No answer found.*"

    # Suggested actions from tool usage hints
    actions = []
    if "Google Search" in text:
        actions.append("- Searched Google for related information.")
    if "YouTube" in text:
        actions.append("- Queried YouTube for relevant tutorials.")
    if "GitHub" in text:
        actions.append("- Looked into GitHub issues or code examples.")
    if not actions:
        actions.append("*No actions found.*")

    # Agent’s Reasoning via Thought lines
    thoughts = re.findall(r"Thought:\s*(.+)", text)
    reasoning = "\n".join(f"- {line.strip()}" for line in thoughts) if thoughts else "*No reasoning found.*"

    # Extract all URLs
    links = re.findall(r"https?://\S+", text)

    return {
        "answer": final_text,
        "actions": "\n".join(actions),
        "reasoning": reasoning,
        "links": links
    }

# --- Session Initialization ---
st.set_page_config(page_title="Agentic Chat Assistant", layout="wide")
st.title("🤖 Agentic Chat Assistant")

col1, col2, col3 = st.columns([6, 1, 1])
with col3:
    if st.button("🧹 Clear Chat"):
        for key in ["chat_history", "current_question_id", "trigger_queue", "chat_closed", "last_open_question_id", "trigger_queue_logs"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# Initialize session state
for key, default in {
    "chat_history": [],
    "current_question_id": 0,
    "trigger_queue": [],
    "chat_closed": False,
    "last_open_question_id": None,
    "trigger_queue_logs": {},
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# --- Input box ---
if not st.session_state.chat_closed:
    user_input = st.chat_input("Ask your question...")
    if user_input:
        if user_input.strip().lower() == "done":
            st.session_state.chat_closed = True
            st.success("Chat ended. Refresh the page to start again.")
        else:
            qid = st.session_state.current_question_id
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input,
                "qid": qid
            })
            st.session_state.last_open_question_id = qid
            st.session_state.current_question_id += 1
else:
    st.info("Chat is closed. Refresh the page to start over.")

# --- Display full chat history ---
for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# --- Agent selection per question ---
for entry in st.session_state.chat_history:
    if entry["role"] != "user":
        continue

    qid = entry["qid"]
    question = entry["content"]

    agents = ["Generic Assistant", "Satya Nadella Twin"]
    answered = [h.get("agent") for h in st.session_state.chat_history if h.get("qid") == qid and h["role"] == "assistant"]
    pending = [a for a in agents if a not in answered]

    if not st.session_state.chat_closed and qid == st.session_state.last_open_question_id and pending:
        selected = st.multiselect(f"👥 Select agent(s) for Q{qid + 1}", options=pending, key=f"select_{qid}")
        for agent in selected:
            trigger_id = (qid, agent)
            if trigger_id not in st.session_state.trigger_queue and agent not in answered:
                st.session_state.trigger_queue.append(trigger_id)
                st.rerun()

# --- Trigger queued agents ---
if st.session_state.trigger_queue:
    qid, agent = st.session_state.trigger_queue.pop(0)

    if any(h["role"] == "assistant" and h.get("qid") == qid and h.get("agent") == agent for h in st.session_state.chat_history):
        st.rerun()

    user_msg = next((m for m in st.session_state.chat_history if m["qid"] == qid and m["role"] == "user"), None)
    if user_msg:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown(f"**{agent} is thinking...**")

            # Run agent
            result = run_agent(user_msg["content"], persona=agent)

            # Handle tuple or plain result
            if isinstance(result, tuple) and len(result) == 2:
                response, logs = result
            else:
                response, logs = result, []

            parsed = extract_sections(response)

            # Fallback if markdown not found
            if parsed["answer"] == response.strip():
                placeholder.markdown(f"""
Response from **{agent}**
```markdown
{response.strip()}
```""")
            else:
                rendered = f"""
Response from **{agent}**

**Paraphrased Answer**  
{parsed['answer']}

**Suggested Actions**  
{parsed['actions']}

**🤖 Agent’s Reasoning**  
{parsed['reasoning']}
"""
                placeholder.markdown(rendered.strip())

            # External Links
            if parsed["links"]:
                st.markdown("📎 **Links Referenced:**")
                for url in parsed["links"]:
                    st.markdown(f"- [🔗 {url}]({url})")

            # Tool Logs (optional)
            with st.expander(f"🔍 {agent} Tool Logs", expanded=False):
                st.markdown("\n".join(logs) if logs else "*No tool activity logged.*")

            # Save response
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response.strip(),
                "qid": qid,
                "agent": agent
            })
            st.session_state.trigger_queue_logs[(qid, agent)] = logs

        st.rerun()
