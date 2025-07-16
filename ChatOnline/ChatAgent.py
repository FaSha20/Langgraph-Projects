from typing import TypedDict, List, Union
from langchain_core.messages import HumanMessage , AIMessage, BaseMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

load_dotenv()

class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage]

class ConfigSchema(TypedDict):
    llm: ChatOpenAI

def process(state: AgentState, config: ConfigSchema) -> AgentState:
    messages = state["messages"]
    llm = config["configurable"].get("llm", ChatOpenAI(model="gpt-4o-mini"))
    response = llm.invoke(messages)
    state["messages"].append(response)
    print("AI: ", response.content)
    return state 


graph = StateGraph(AgentState, config_schema=ConfigSchema)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

chatHistory: List[BaseMessage] = []

user_input = input("You: ")
while user_input != "exit":
    chatHistory.append(HumanMessage(content=user_input))
    state = agent.invoke(
        {"messages": chatHistory },
        # {"configurable": {"llm": ChatOpenAI(model="gpt-4o-mini")}}
    )
    chatHistory = state["messages"]
    user_input = input("You: ")
    