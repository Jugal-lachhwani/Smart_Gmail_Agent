from langgraph.graph import END, StateGraph
from src.state import GraphState
from src.nodes import Nodes

class Workflow():
    def __init__(self):
        workflow = StateGraph(GraphState)
        nodes = Nodes()
        
        workflow.add_node("")