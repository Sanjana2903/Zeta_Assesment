import streamlit as st
from agent import run_agent
import re

# --- Helper to extract sections from agent output ---
def extract_sections(text):
    answer = re.search(r"Paraphrased Answer:\s*(.*?)", text, re.DOTALL)
    actions = re.search(r"Suggested Actions:\s*(.*?)", text, re.DOTALL)
    reasoning = re.search(r"Agent’s Reasoning:\s*(.*)", text, re.DOTALL)
    return {
        "answer": answer.group(1).strip() if answer else "*No answer found.*",
        "actions": '\n'.join(f"- {line.strip()}" for line in actions.group(1).splitlines() if line.strip()) if actions else "*No actions found.*",
        "reasoning": reasoning.group(1).strip() if reasoning else "*No reasoning found.*",
    }

# --- Session Initialization ---
st.set_page_config(page_title="Agentic Chat Assistant", layout="wide")
st.title("🤖 Agentic Chat Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  

if "current_question_id" not in st.session_state:
    st.session_state.current_question_id = 0

if "trigger_queue" not in st.session_state:
    st.session_state.trigger_queue = []  

if "chat_closed" not in st.session_state:
    st.session_state.chat_closed = False

if "last_open_question_id" not in st.session_state:
    st.session_state.last_open_question_id = None

# --- Input ---
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

for entry in st.session_state.chat_history:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

for entry in st.session_state.chat_history:
    if entry["role"] != "user":
        continue

    qid = entry["qid"]
    question = entry["content"]

    agents = ["Generic Assistant", "Satya Nadella Twin"]
    answered = [
        h.get("agent") for h in st.session_state.chat_history
        if h.get("qid") == qid and h["role"] == "assistant"
    ]
    pending = [a for a in agents if a not in answered]

    if not st.session_state.chat_closed and qid == st.session_state.last_open_question_id and pending:
        selected = st.multiselect(
            f"👥 Select agent(s) for Q{qid + 1}",
            options=pending,
            key=f"select_{qid}"
        )
        for agent in selected:
            trigger_id = (qid, agent)
            if trigger_id not in st.session_state.trigger_queue and agent not in answered:
                st.session_state.trigger_queue.append(trigger_id)
                st.rerun()  

if st.session_state.trigger_queue:
    qid, agent = st.session_state.trigger_queue.pop(0)

    if any(
        h["role"] == "assistant" and h.get("qid") == qid and h.get("agent") == agent
        for h in st.session_state.chat_history
    ):
        st.rerun() 

    user_msg = next((m for m in st.session_state.chat_history if m["qid"] == qid and m["role"] == "user"), None)
    if user_msg:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown(f"**{agent} is thinking...**")

            result = run_agent(user_msg["content"], persona=agent)
            parsed = extract_sections(result)

            response = f"""
### Response from **{agent}**

**Paraphrased Answer**  
{parsed['answer']}

**Suggested Actions**  
{parsed['actions']}

**Agent’s Reasoning**  
{parsed['reasoning']}
"""
            placeholder.markdown(response.strip())

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response.strip(),
                "qid": qid,
                "agent": agent
            })

        st.rerun()
