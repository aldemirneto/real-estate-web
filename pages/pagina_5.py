import os
import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI


llm = OpenAI(api_token=os.environ['OPENAI_API_KEY'])
df = pd.read_parquet('lineitem.parquet')
df = SmartDataframe(df, config={"llm": llm})

if "messages" not in st.session_state:
            st.session_state["messages"] = [
                {"role": "assistant", "content": "How can I help you?"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_response = ""

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        assistant_response = ""

        with st.spinner('CHAT-BOT is at Work ...'):
            assistant_response = output = df.chat(user_input, output_type="dataframe")
        message_placeholder.dataframe(assistant_response)
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
# llm = OpenAI(openai_api_key=, temperature=0)