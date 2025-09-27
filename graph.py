# graph.py

class ConversationGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []
    
    def add_node(self, node):
        self.nodes.append(node)
    
    def add_edge(self, from_node, to_node):
        self.edges.append((from_node, to_node))
    
    def display(self):
        print("Nodes:", self.nodes)
        print("Edges:", self.edges)

# Example usage:
if __name__ == "__main__":
    graph = ConversationGraph()
    graph.add_node("User")
    graph.add_node("Bot")
    graph.add_edge("User", "Bot")
    graph.display()