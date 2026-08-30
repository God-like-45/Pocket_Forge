from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.nodes import director_node, scriptwriter_node, reviewer_node

def route_from_reviewer(state: AgentState):
    """Determine whether to end or revise the script."""
    feedback = state.get("feedback")
    revision_count = state.get("revision_count", 0)
    
    if feedback == "PASS" or revision_count >= 3:
        return END
    return "scriptwriter"

# Initialize graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("director", director_node)
workflow.add_node("scriptwriter", scriptwriter_node)
workflow.add_node("reviewer", reviewer_node)

# Add edges
workflow.add_edge(START, "director")
workflow.add_edge("director", "scriptwriter")
workflow.add_edge("scriptwriter", "reviewer")
workflow.add_conditional_edges("reviewer", route_from_reviewer)

# Compile the graph
app = workflow.compile()
