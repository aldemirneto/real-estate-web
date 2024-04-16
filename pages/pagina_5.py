import os

from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_models import ChatOpenAI
import streamlit as st
import pandas as pd
import uuid
from datetime import datetime

from helpers.page5 import insert_interaction

st.set_page_config(page_title="LangChain: Chat with pandas DataFrame", page_icon="🦜")
st.title("🦜 LangChain: Chat with pandas DataFrame")


def get_exploration_prompt(df):
    """
  Generates a data exploration prompt based on the DataFrame columns.
  """
    categorical_cols = df.select_dtypes(include=[pd.api.types.is_categorical_dtype])
    if not categorical_cols.empty:
        col_name = categorical_cols.columns[0]
        return f"What are the different values in the '{col_name}' column?"
    else:
        # Add other logic for different data types or pre-defined prompts here
        return "What would you like to know about this data?"


def generate_session_id():
    return str(uuid.uuid4())


if "session_id" not in st.session_state:
    st.session_state["session_id"] = generate_session_id()
if "messages" not in st.session_state or st.sidebar.button("Clear conversation history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "como posso te ajudar??", "feedback": "neutral"}]

# Criar dicionário para armazenar dados da sessão
session_data = {
    "session_id": st.session_state["session_id"],
    "start_time": datetime.now(),
    "feedback": {},
    "messages": st.session_state["messages"],
}

if "session_data" not in st.session_state:
    st.session_state["session_data"] = session_data


def get_user_feedback():
    """Obtém o feedback do usuário para uma resposta específica."""
    col1, col2, col3 = st.columns(3)
    with col1:
        thumbs_up = st.button("Útil")
    with col2:
        thumbs_neutral = st.button("Neutro")
    with col3:
        thumbs_down = st.button("Não Útil")

    if thumbs_up:
        feedback = "positive"
        st.session_state.messages.append({"role": "assistant", "content": response, "feedback": feedback})
    elif thumbs_down:
        feedback = "negative"
        st.session_state.messages.append({"role": "assistant", "content": response, "feedback": feedback})
    elif thumbs_neutral:
        feedback = "neutral"
        st.session_state.messages.append({"role": "assistant", "content": response, "feedback": feedback})


df = pd.read_parquet('lineitem.parquet')

llm = ChatOpenAI(api_key= os.environ['OPENAI_API_KEY'], temperature=0, streaming=True)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="como posso te ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

pandas_df_agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=False,
    agent_type="openai-tools",
    handle_parsing_errors=True,
)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response = pandas_df_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.write(response)
        get_user_feedback()

conversation_duration = datetime.now() - session_data["start_time"]

# Calcular pontuação média
if len([f['feedback'] for f in st.session_state.messages if 'feedback' in f]):
    num_positive_feedback = sum(
        feedback["feedback"] == "positive" for feedback in st.session_state.messages if
        'feedback' in feedback and feedback["role"] == "assistant")
    total_feedback = len([message for message in st.session_state.messages if message["role"] == "assistant"])
    average_score = (num_positive_feedback / total_feedback) * 100
    if 'metrics' not in st.session_state:
        id = st.session_state["session_id"]
        st.session_state['metrics'] = {"id": id, "average_score": average_score, "duration": conversation_duration}
    else:

        st.session_state.metrics["average_score"] = average_score
        st.session_state.metrics["duration"] = conversation_duration

if len([message for message in st.session_state.messages if message["role"] == "assistant"]) % 3 == 0:
    id = st.session_state["session_id"]
    average_score = st.session_state.metrics["average_score"]
    interaction_time = st.session_state.metrics["duration"]
    insert_interaction(interaction_time, average_score, id)
