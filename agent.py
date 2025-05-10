from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOllama
from langchain.memory import ConversationBufferMemory


llm = ChatOllama(model="llama3")

# Memory per agent
# memory_store = {
#     "Generic Assistant": ConversationBufferMemory(memory_key="history", return_messages=True),
#     "Satya Nadella Twin": ConversationBufferMemory(memory_key="history", return_messages=True)
# }


prompt_template = PromptTemplate(
    input_variables=["history", "input"],
    template="""
You are an intelligent research assistant helping the user through a step-by-step conversation.

Always reply in this markdown format:
Paraphrased Answer:
<summary of your current understanding or refinement>

Suggested Actions:
- <concrete next steps, links, or tools>

Agent’s Reasoning:
- <why these tools/sources/steps were selected>

Conversation so far:
{history}

User: {input}
Assistant:
"""
)

chains = {}

# def run_agent(prompt, persona="Generic Assistant"):
#     try:
#         if persona not in chains:
#             chains[persona] = LLMChain(
#                 llm=llm,
#                 prompt=prompt_template,
#                 memory=memory
#             )
#         return chains[persona].invoke({"input": prompt})["text"]
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return f"Agent failed: {str(e)}"

def run_agent(prompt, persona="Generic Assistant"):
    try:
        llm = ChatOllama(model="llama3")
        memory = ConversationBufferMemory(memory_key="history", return_messages=True)
        chain = LLMChain(llm=llm, prompt=prompt_template, memory=memory)
        return chain.invoke({"input": prompt})["text"]
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Agent failed: {str(e)}"
