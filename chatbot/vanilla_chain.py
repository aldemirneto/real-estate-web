from datetime import datetime
from langchain import LLMChain

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory


def get_llm_chain(system_prompt: str, memory: ConversationBufferMemory) -> LLMChain:
    """Return a basic LLMChain with memory."""
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                system_prompt + "\nIt's currently {time}.",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    ).partial(time=lambda: str(datetime.now()))
    llm = ChatOpenAI(temperature=0.7)
    chain = LLMChain(prompt=prompt, llm=llm, memory=memory)
    return chain


