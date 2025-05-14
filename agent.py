from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, AgentType
from langchain_community.chat_models import ChatOllama
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings

from tools import get_search_tools

# Shared components
llm = ChatOllama(model="llama3", temperature=0.2)
embedding = OllamaEmbeddings(model="mxbai-embed-large")
vectorstore = Chroma(persist_directory="db", embedding_function=embedding)
retriever = vectorstore.as_retriever()

# Prompts
satya_prompt_template = """
You are a digital twin of Satya Nadella, trained on his speeches, interviews, and writing.

When answering:
- Refer to Microsoft’s leadership principles and products
- Emphasize empathy, innovation, and inclusive growth
- Use Satya’s calm, grounded, and optimistic tone
- Draw on examples from Microsoft’s internal practices when possible
- Include vision on AI, cloud, productivity, and platform shifts

📜 Paraphrased Answer:
<summary of Satya’s advice>

📀 Suggested Actions:
- <Step 1>
- <Step 2>

🤖 Agent’s Reasoning:
- <Why Satya would give this advice, grounded in his principles>

Context from Satya's writing:
{history}

User: {input}
Assistant:
"""

generic_prompt_template = """
You are an intelligent research assistant helping the user through a step-by-step conversation.

Always reply in this markdown format:
Paraphrased Answer:
<summary of your understanding or refinement>

Suggested Actions:
- <concrete next steps, links, or tools>

🤖 Agent’s Reasoning:
- <why these tools/sources/steps were selected>

Conversation so far:
{history}

User: {input}
Assistant:
"""

def should_use_tools(prompt: str) -> bool:
    tool_keywords = [
        "search", "find", "look up", "lookup", "latest", "news",
        "Google", "YouTube", "GitHub", "video", "current", "trending"
    ]
    return any(kw.lower() in prompt.lower() for kw in tool_keywords)

def run_agent(prompt: str, persona: str = "Generic Assistant", use_tools: bool = None):
    try:
        tools = get_search_tools()
        if use_tools is None:
            use_tools = should_use_tools(prompt)

        if use_tools:
            # Tool-based ReAct agent
            prefix = (
                "You are a helpful assistant. Use tools to answer questions."
                if persona == "Generic Assistant"
                else "You are Satya Nadella’s digital twin. Use tools if helpful. Think like Satya—empathetic, grounded, and futuristic."
            )
            agent = initialize_agent(
                tools=tools,
                llm=llm,
                agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
                agent_kwargs={"prefix": prefix},
                handle_parsing_errors=True,
                verbose=True
            )
            return agent.run(prompt)

        else:
            # Static markdown-style answer using LLMChain
            memory = ConversationBufferMemory(memory_key="history", return_messages=True)

            if persona == "Satya Nadella Twin":
                context_docs = retriever.get_relevant_documents(prompt)
                satya_context = "\n\n".join(doc.page_content for doc in context_docs)

                satya_prompt = PromptTemplate(
                    input_variables=["input", "history"],
                    template=satya_prompt_template
                )
                chain = LLMChain(llm=llm, prompt=satya_prompt, memory=memory)
                return chain.invoke({"input": prompt, "history": satya_context})["text"]

            else:
                generic_prompt = PromptTemplate(
                    input_variables=["input", "history"],
                    template=generic_prompt_template
                )
                chain = LLMChain(llm=llm, prompt=generic_prompt, memory=memory)
                return chain.invoke({"input": prompt, "history": ""})["text"]

    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ Agent failed: {str(e)}"
