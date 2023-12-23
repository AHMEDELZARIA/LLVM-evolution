import networkx as nx
import colorsys
from pyvis.network import Network

# Create a directed graph
graph = nx.DiGraph()
#graph.add_edges_from([(1, 2), (2, 3), (3, 1), (4, 5), (5, 6), (6, 4), (7, 8), (8, 9), (9, 7), (9, 3), (7, 4), (10, 11)])

graph.add_edge(1, 2, relationship = "pass1")
graph.add_edge(2, 3, relationship = "pass2")
graph.add_edge(3, 1, relationship = "pass3")
graph.add_edge(3, 4, relationship = "pass4")
graph.add_edge(4, 5, relationship = "pass5")
graph.add_edge(5, 6, relationship = "pass6")
graph.add_edge(6, 4, relationship = "pass7")


# Detect strongly connected components
strongly_connected = [comp for comp in nx.strongly_connected_components(graph) if len(comp) > 1]
print(strongly_connected)

# Detect strongly connected components
weakly_connected = [comp for comp in nx.weakly_connected_components(graph) if len(comp) > 1]
print(weakly_connected)

strong_connected_highlighted = True
components = strongly_connected if strong_connected_highlighted else weakly_connected

# Create a Network object with desired properties
net = Network(notebook=True, directed=True, height="750px", heading='<link rel="stylesheet" href="style.css">')

# Generate unique colors for each component using HSV color space
component_colors = [colorsys.hsv_to_rgb(i / len(components), 1.0, 1.0) for i in range(len(components))]

# Convert the generated RGB colors to hexadecimal format
component_colors_hex = ['#%02x%02x%02x' % tuple(int(c * 255) for c in color) for color in component_colors]

# Create a dictionary to map component IDs to colors
node_colors = {f'component_{i}': color for i, color in enumerate(component_colors_hex)}

# Add nodes and edges to the Network object
for node in graph.nodes():
    # Get the connected component to which the node belongs
    connected_component = None
    for component in components:
        if node in component:
            connected_component = component
            break
    
    # Determine the color of the node based on its connected component
    if connected_component is not None:
        component_id = "component_" + str(components.index(connected_component))
        node_color = node_colors.get(component_id, 'gray')  # Default to gray if not found
    else:
        node_color = 'gray'  # Default color for nodes not in any connected component
    
    # Add the node with specified color
    net.add_node(node, color=node_color)

for source, target, data in graph.edges(data=True):
    relationship = data.get("relationship", "")
    net.add_edge(source, target, title=relationship)

net.show_buttons()

# Add the control to toggle cluster colors
net.show("/Users/ahmedelzaria/Documents/LLVM/graph.html")





