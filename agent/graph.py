import functools
import sqlite3

from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, BaseMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from agent.agent import build_openai_sql
from agent.multi_agent import agent_node, create_agent, create_team_supervisor
from chatbot.conversational_chain import initialize_chain
from tools.sql_tool import SQLTool
from tools.tools import build_search_tools
from utils.prompt import TEAM_SUPERVISOR_PROMPT
import operator
from typing import Annotated, Sequence, List
from langchain_experimental.utilities import PythonREPL
from typing_extensions import TypedDict
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
def build_graph():
    llm = ChatOpenAI(model="gpt-3.5-turbo", max_tokens=512, temperature=0, streaming=True)

    searcher = initialize_chain()
    memory = SqliteSaver.from_conn_string("checkpoints.sqlite")
    runnable_sql = build_openai_sql(llm)
    sql_tool = SQLTool(sql_chain=runnable_sql, handle_tool_error=True)
    sql_agent = create_agent(
        llm,
        [sql_tool] + build_search_tools(),
        "You are an useful data assistant. "
        "You are responsible for requests of retrieving user or system data from the database by using provided tools or just talking with the person"
    )
    analytical = sql_agent

    repl = PythonREPL()

    @tool
    def python_repl(
        code: Annotated[str, "The python code to execute to generate your chart."]
    ):
        """Use this to execute python code. If you want to see the output of a value,
        you should print it out with `print(...)`. This is visible to the user."""
        try:
            result = repl.run(code)
        except BaseException as e:
            return f"Failed to execute. Error: {repr(e)}"
        result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
        return (
            result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
        )
    # This defines the object that is passed between each node
    # in the graph. We will create different nodes for each agent and tool
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        team_members: List[str]
        next: str


    def should_continue(state):
        messages = state["messages"]
        last_message = messages[-1]

        if "FINISH" in last_message.content:
            return "FINISH"
        else:
            return state["next"]
    searcher_node = functools.partial(agent_node, agent=searcher, name="RAG")
    analytical_node = functools.partial(agent_node, agent=analytical, name="SQL")



    supervisor_agent = create_team_supervisor(
            llm,
            TEAM_SUPERVISOR_PROMPT,
            ["SQL", "RAG"],
        )
    workflow = StateGraph(AgentState)

    workflow.add_node("SQL", analytical_node)
    workflow.add_node("RAG", searcher_node)
    workflow.add_node("supervisor", supervisor_agent)

    # control flow
    workflow.add_edge("SQL", "supervisor")
    workflow.add_edge("RAG", "supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "SQL": "SQL",
            "RAG": "RAG",
            "FINISH": END
        },
    )

    workflow.set_entry_point("supervisor")
    chain = workflow.compile(checkpointer=memory)

    return chain
