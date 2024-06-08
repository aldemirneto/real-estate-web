
import streamlit as st
from langchain.callbacks.tracers.langchain import wait_for_all_tracers
from langchain.callbacks.tracers.run_collector import RunCollectorCallbackHandler
from langchain.memory import ConversationBufferMemory, StreamlitChatMessageHistory
from langchain.schema.runnable import RunnableConfig
from langchain_core.messages import HumanMessage
from agent.graph import build_graph
from streamlit_feedback import streamlit_feedback

from helpers.page5 import insert_interaction



st.set_page_config(
    page_title="Encontre seu imóvel perfeito!",
    page_icon="🦜",
)

if "last_run" not in st.session_state:
    st.session_state["last_run"] = "some_initial_value"

col1, col2, col3 = st.columns([0.6, 3, 1])

st.markdown("___")

if "run_id" not in st.session_state:
    st.session_state.run_id = None

_DEFAULT_SYSTEM_PROMPT = ""
system_prompt = _DEFAULT_SYSTEM_PROMPT = ""
system_prompt = system_prompt.strip().replace("{", "{{").replace("}", "}}")


memory = ConversationBufferMemory(
    chat_memory=StreamlitChatMessageHistory(key="langchain_messages"),
    return_messages=True,
    memory_key="chat_history",
)


chain = build_graph()
if st.sidebar.button("Limpar Historico de Mensagens"):
    memory.clear()
    st.session_state.run_id = None


def _get_openai_type(msg):
    if msg.type == "human":
        return "user"
    if msg.type == "ai":
        return "assistant"
    if msg.type == "chat":
        return msg.role
    return msg.type


for msg in st.session_state.langchain_messages:
    streamlit_type = _get_openai_type(msg)
    avatar = "🦜" if streamlit_type == "assistant" else None
    with st.chat_message(streamlit_type, avatar=avatar):
        st.markdown(msg.content)

run_collector = RunCollectorCallbackHandler()
runnable_config = RunnableConfig(
    callbacks=[run_collector],
    tags=["Streamlit Chat"],
    configurable={"thread_id": "1", "recursion_limit": 5}
)


def _reset_feedback():
    st.session_state.feedback = []


MAX_CHAR_LIMIT = 500  # Adjust this value as needed

if prompt := st.chat_input(placeholder="Faça uma pergunta sobre imóveis!"):

    if len(prompt) > MAX_CHAR_LIMIT:
        st.warning(f"⚠️ Your input is too long! Please limit your input to {MAX_CHAR_LIMIT} characters.")
        prompt = None  # Reset the prompt so it doesn't get processed further
    else:
        st.chat_message("user").write(prompt)

        with st.chat_message("assistant", avatar="🦜"):
            message_placeholder = st.empty()
            full_response = ""

            input_structure = {
                "messages": [
                    HumanMessage(
                        content=prompt
                    )
                ],
            },
            question_structure = {"question": prompt}


            for chunk in chain.stream({
                        "messages": [
                            HumanMessage(
                                content=prompt
                            )
                        ],
                    }, runnable_config):
                print('-------------------')
                print(chunk)
                print('-------------------')
                if "__end__" not in chunk:
                    item = next(iter(chunk.values()))
                    if "messages" in item:
                        result = item["messages"][-1].content

            memory.save_context({"input": prompt}, {"output": result})

            message_placeholder.markdown(result)

            run = run_collector.traced_runs[0]
            run_collector.traced_runs = []
            st.session_state.run_id = run.id
            wait_for_all_tracers()

has_chat_messages = len(st.session_state.get("langchain_messages", [])) > 0

# Only show the feedback toggle if there are chat messages
if has_chat_messages:
    feedback_option = (
        "faces" if st.toggle(label="`Thumbs` ⇄ `Faces`", value=False) else "thumbs"
    )
else:
    pass

if st.session_state.get("run_id"):
    feedback = streamlit_feedback(
        feedback_type=feedback_option,  # Use the selected feedback option
        key=f"feedback_{st.session_state.run_id}",
    )

    # Define score mappings for both "thumbs" and "faces" feedback systems
    score_mappings = {
        "thumbs": {"👍": 1, "👎": 0},
        "faces": {"😀": 1, "🙂": 0.75, "😐": 0.5, "🙁": 0.25, "😞": 0},
    }

    # Get the score mapping based on the selected feedback option
    scores = score_mappings[feedback_option]

    if feedback:
        # Get the score from the selected feedback option's score mapping
        score = scores.get(feedback["score"])

        if score is not None:
            # Formulate feedback type string incorporating the feedback option and score value
            feedback_type_str = f"{feedback_option} {feedback['score']}"

            if 'feedback' not in st.session_state:
                _reset_feedback()
            st.session_state.feedback.append({
                "feedback_id": str(st.session_state.run_id),
                "score": score,
            })
            insert_interaction(str(st.session_state.run_id), score)
        else:
            st.warning("Invalid feedback score.")
