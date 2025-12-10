from langgraph.graph import END, StateGraph
from src.state import GraphState

class Workflow():
    def __init__(self):
        workflow = StateGraph(GraphState)
        