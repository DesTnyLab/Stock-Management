from langgraph.graph import StateGraph, END
from inventory_ai.graph.nodes import predict_demand, get_stock, compare

def create_alert_graph():
    g = StateGraph(dict)

    g.add_node("predict", predict_demand)
    g.add_node("stock", get_stock)
    g.add_node("compare", compare)

    g.set_entry_point("predict")
    g.add_edge("predict", "stock")
    g.add_edge("stock", "compare")
    g.add_edge("compare", END)

    return g.compile()
