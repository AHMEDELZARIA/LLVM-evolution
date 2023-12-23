# All necessary imports for code to run
import networkx as nx
from networkx.drawing.nx_pydot import graphviz_layout
from pyvis.network import Network
import pygraphviz as pgv
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
import os
import subprocess
import time
import colorsys
import sys
from bs4 import BeautifulSoup


def generate_ir(directory, output_directory):
    """
    Traverses a directory with an arbitrary number of subdirectories. Extracts all .c clang compilable files and generates 
    the IR files and places them in desired output directory.

    Parameter:
    directory (string): Path to the root directory of interest
    output_directory (string): Path to the directory to store IR

    Return:
    Nothing, IR(s) is/are appended to output_directory.
    """
	
    # Iterate over each item in directory
    for item in os.listdir(directory):

        # Construct current item path 
        itempath = os.path.join(directory, item)
	
        # Check if current item is a .c file
        if os.path.isfile(itempath) and itempath.endswith(".c"):

			# Check if file is compilable with clang
            if is_compilable_clang(itempath) == True:

                # Generate the IR of .c file and store in output directory
                subprocess.run(["clang", "-S", "-emit-llvm", itempath, '-o', os.path.join(output_directory, item + ".ll"), '-O0', "-Xclang", "-disable-O0-optnone"])
                
            # Skip to next item
            else:
                continue

        # Check if current item is a sub-directory
        elif os.path.isdir(itempath):

            # Traverse subdirectory
            generate_ir(itempath, output_directory)
        
        # Skip to next item
        else:
             continue
        
        
def is_compilable_clang(filepath):
	"""
	Checks if .c file is compilable with clang

	Parameters:
	filepath (string): complete filepath to your .c file of interest

	Returns:
	True: if .c file passed through is compilable with clang
	False: if .c file passed through is not compilable with clang
	"""

	# Run command to check if file is compilable with clang
	outcome = subprocess.run(["clang", "-fsyntax-only", filepath], capture_output = True, text = True)

	# Check return code of the process
	if outcome.returncode == 0:
		return True # file is compilable with clang
	else:
		return False # file is not compilable with clang


def add_graph_node(program_path, queue, graph, parent_node = None, pass_applied = None):
    """
    Adds nodes to the given graph. Adds the program_path as a node and appeneds the node to the queue.
    For all nodes besides the root, it will add an edge with the new node and parent node.

    Arguments:
    program_path (string): Path to program to be added as a node
    queue (list: string): List that holds the programs to be visited
    graph (Graph): Graph to which nodes will be added to
    optional argument, parent_node (string): Path to the parent node program
    optional argument, pass_applied (string): Pass applied to make new program

    Returns:
    Nothing, adds nodes and/or edges.
    """

    # Add the node to the graph and enqueue
    graph.add_node(program_path)
    queue.append(program_path)

    # For all nodes besides root, add an edge with the parent node
    if parent_node:
        graph.add_edge(parent_node, program_path, relationship = pass_applied)


def apply_pass(program, optimized_path, opt_pass):
    """
    Applies the given pass on the given program and stores it in the given path.

    Arguments:
    program (string): Path to program to apply pass on
    optimized_path (string): Path to which optimized program will be stored
    opt_pass (string): Pass to apply on given program

    Returns:
    optimized_program_path (string): Path to optimized file
    """

    # Optimized program path
    optimized_program_path = os.path.join(optimized_path, program.split('/')[-1] + '_' + opt_pass + '.ll')

    # Apply pass via opt
    subprocess.run(['opt', '-S', '-passes=' + opt_pass, '-o', optimized_program_path, program])

    return optimized_program_path


def is_existing(optimized_program_path, graph, parent_node, pass_appled, queue):
    """
    Checks whether the optimized file already exists on the graph. If it does, then connects the 
    parent node to the existing node. If it doesn't, it will create a new node and connect it 
    accordingly.

    Arguments:
    optimized_program_path (string): Path to optimized file'
    graph (Graph): Graph you're working with
    parent_node (string): Path to the parent node program
    pass_applied (string): Pass applied to make new program
    queue (list: string): List that holds the programs to be visited

    Returns:
    graph.add_edge(): Adds an edge with existing node
    graph.add_node(): Adds a new node to the graph and connects it accordingly
    """

    for node in graph.nodes:

        # Run llvm-diff command and capture output
        llvm_diff_output = llvm_diff(optimized_program_path, node)

        # Analyze the llvm-diff output and record number of additions and deletions
        differences = analyze_differences(llvm_diff_output)

        # If there is an equivalent node in the graph, add an edge from parent node to equivalent node
        if differences['Num Additions'] == 0 and differences['Num Deletions'] == 0:
            if(graph.has_edge(parent_node, node)) :
                graph[parent_node][node]['relationship'] = graph[parent_node][node]['relationship'] + ',' + pass_appled
                return
            return graph.add_edge(parent_node, node, relationship = pass_appled)
        
    # If non of the nodes in the graph are equivalent to the new program, add new node
    return add_graph_node(optimized_program_path, queue, graph, parent_node = parent_node, pass_applied = pass_appled)


def llvm_diff(optimized_program_path, node_program):
    """
    Runs the llvm-diff command on two passed in programs.

    Arguments:
    optimized_program_path (string): Path to optimized file
    node_program (string): Program path of a node on the graph

    Returns:
    diff_output (list: string): llvm-diff command captured and split into lines
    """

    # Run llvm-diff command
    diff_output = subprocess.run(['llvm-diff', optimized_program_path, node_program], capture_output = True, text = True)

    # Convert output to a string
    diff_output = diff_output.stderr.splitlines()

    return diff_output


def analyze_differences(llvm_diff):
    """
    Analyzes the llvm-diff output captured and records the number of additions and deletions that were
    made.

    Arguments:
    llvm-diff (list: string): llvm-diff output captured and split into lines

    Returns:
    differences (dict: int): Holds the number of additions and deletions from llvm-diff command
    """

    # Holds the number of additions and deletions from llvm-diff output
    differences = {
        'Num Additions': 0,
        'Num Deletions': 0,
    }

    # Iterate over all lines in output and note the additions, deletions, and modifications
    for line in llvm_diff:

        # Check if line is an addition or deletion or modification and append it
        if line.strip().startswith('>'):
            differences['Num Additions'] += 1
        elif line.strip().startswith('<'):
            differences['Num Deletions'] += 1

    return differences
    

def output_graph(graph, html_path, gml_path, graph_count):
    """
    Outputs the completed graph in two ways, as a pop up window during execution and as a html graph.

    Arguments:
    graph (Graph): graph to which you want to be outputted
    program_name (string): Name of the program that the graph is based off of

    Returns:
    Nothing, outputs graphs.
    """

    # In cases of an empty graph
    if graph.number_of_nodes() == 0:

        # Message
        print("Graph is empty. No nodes to visualize.")
        return

    # Write the gml representation of graph
    nx.write_gml(graph, gml_path)

    # Detect strongly connected components
    strongly_connected = [comp for comp in nx.strongly_connected_components(graph) if len(comp) > 1]
    print(strongly_connected)

    # Detect strongly connected components
    weakly_connected = [comp for comp in nx.weakly_connected_components(graph) if len(comp) > 1]
    print(weakly_connected)

    strong_connected_highlighted = True
    components = strongly_connected if strong_connected_highlighted else weakly_connected

    # Create a Network object with desired properties
    net = Network(notebook=True, directed=True, height="750px")

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

    for edge in net.edges:
        print(edge)
    
    # Show the Network object
    net.show_buttons()

    # Show the Network object
    net.show(html_path)

    # Read the html file
    with open(html_path, 'r') as html_file:
        html_content = html_file.read()

    # Parse the html file
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the body and head tag
    body_tag = soup.body
    head_tag = soup.head

    # Create a new <div> and <style> tag
    legend_div = soup.new_tag('div', id='legend')
    style_tag = soup.new_tag('style')

    # Styling content
    style_tag.string = """
    /* Additional styles for the legend */
    #legend {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: white;
        border: 1px solid gray;
        padding: 10px;
    }
    """

    # Legend content
    legend_html = """
        <h3>LEGEND</h3>
        <ul>
            <li><svg width="15" height="15"><circle cx="7" cy="7" r="5" fill="gray" /></svg> Node (Program State)</li>
            <li><span style="color: black;">&#x2192;</span> Pass Applied</li>
            <li><span style="color: darkgray;">Gray Nodes</span>: Weakly Connected Components</li>
            <li><span style="color: coral;">Coloured Nodes</span>: Strongly Connected Components</li>
        </ul>
    """
    legend_div.append(BeautifulSoup(legend_html, 'html.parser'))

    # Insert the new <div> and <style? tags
    body_tag.append(legend_div)
    head_tag.append(style_tag)

    # Save the modified html
    with open(html_path, 'w') as modified_html_file:
        modified_html_file.write(soup.prettify())


def main():

    input("") # Ignore, /Users/ahmedelzaria/Documents/LLVM/c_benchmark

    # Get the benchmark path that holds the .c files
    benchmark_path = input("Enter the directory path containing the .c files: ").strip()
    while os.path.exists(benchmark_path) == False:
        print("Error: Directory does not exist.")
        benchmark_path = input("Please enter a valid directory path (Q for Quit): ")

        if benchmark_path == 'Q':
            sys.exit(0)

    # Generate the path to the directory that will hold the generated non-optimized IR files. If it doesn't already exist, create it.
    ir_benchmark_path = os.path.join(os.path.split(benchmark_path)[0], "Test_Programs")
    if os.path.exists(ir_benchmark_path) == False:
        os.mkdir(ir_benchmark_path)

    # Generate the path to the directory that will hold the generated optimized IR files. If it doesn't already exist, create it.
    optimized_path = os.path.join(os.path.split(benchmark_path)[0], "Test_Optimized_Programs")
    if os.path.exists(optimized_path) == False:
        os.mkdir(optimized_path)

    # Generate the path to the directory that will hold the html visualizations. If it doesn't already exist, create it.
    graphs_dir_path = os.path.join(os.path.split(benchmark_path)[0], "Graph_Visualizations")
    if os.path.exists(graphs_dir_path) == False:
        os.mkdir(graphs_dir_path)

    # Generate the path to the directory that will hold the gml files. If it doesn't already exist, create it.
    gml_dir_path = os.path.join(os.path.split(benchmark_path)[0], "gml_files")
    if os.path.exists(gml_dir_path) == False:
        os.mkdir(gml_dir_path)

    # Generate the IR files and store them in the correct directory
    generate_ir(benchmark_path, ir_benchmark_path)

    # Keep track of how many graphs generated
    graph_count = 1

    # List of passes
    # passes = ['jump-threading', 'early-cse', 'mem2reg', 'forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt']
    # passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg']
    passes = ['loop-simplify', 'loop-rotate', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'loop-sink', ]
    # passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg', 'always-inline', 'sroa', 'speculative-execution', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa', 'loop-rotate', 'licm', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memcpyopt', 'sccp', 'bdce', 'dse', 'adce', 'globaldce', 'float2int', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']

    # Loop through each program in benchmark
    for program in os.listdir(ir_benchmark_path):

        # Construct current program path
        root_program_path = os.path.join(ir_benchmark_path, program)

        # Check if file is correct format
        if os.path.isfile(root_program_path) and root_program_path.endswith('.ll'):

            # Set the path the html and gml file of the graph will be placed. It will be placed all within the same main directory as the 2 benchmark directories
            html_path = os.path.join(graphs_dir_path, "graph" + str(graph_count) + ".html")
            gml_path = os.path.join(gml_dir_path, "graph" + str(graph_count) + ".gml")

            # Create an empty graph
            G = nx.DiGraph()

            # Declare and initialize an empty queue
            queue = []

            # Add current program as root node
            add_graph_node(root_program_path, queue, G)

            # Start timer
            start_time = time.time()

            # Loop through the queue
            while queue:

                # Get the front element from the queue
                node = queue.pop(0)

                # Loop through each pass
                for opt_pass in passes:

                    # Apply pass using opt and hold temporary program
                    optimized_program_path = apply_pass(node, optimized_path, opt_pass)

                    # Check if post-pass-applied program is the same as any other nodes on graph
                    is_existing(optimized_program_path, G, node, opt_pass, queue)

                # Check if time exceeds 25 seconds or if there are more than 100 nodes, break out of loop if any are met
                current_time = time.time()
                elapsed_time = current_time - start_time
                num_nodes = G.number_of_nodes()
                if elapsed_time > 10000 or num_nodes > 10000:
                    break

            # Rename the nodes 
            program_node_count = 0
            old_new_names = {}
            
            for node in G.nodes:
                old_new_names[node] = 'P' + str(program_node_count)
                program_node_count += 1

            renamed_graph = nx.relabel_nodes(G, old_new_names)

            # Output the graph visualization
            output_graph(renamed_graph, html_path, gml_path, graph_count)

            graph_count += 1

 
main()









# MATPLOTLIB VISUALIZATION CODE, UNCOMMENT EVERYTHING BELOW TO USE, PLACE IN OUTPUT_GRAPH() FUNCTION TO USE. MAY HAVE TO ADJUST SOME STUFF.
# # Generate the layout
#     pos = graphviz_layout(graph, prog='dot')

#     # Draw the graph
#     edge_labels = nx.get_edge_attributes(graph, 'relationship')
#     nx.draw(graph, pos, with_labels=True, node_color="lightblue", edge_color="gray", arrowsize=20, node_size=1000)
#     nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_color='red')

#     # Highlight components with a distinct color
#     num_colors = len(components)
#     colors = list(mcolors.TABLEAU_COLORS.values())[:num_colors]
#     padding_factor = 0.15

#     for idx, component in enumerate(components):
#         color = colors[idx]
#         nx.draw_networkx_nodes(graph, pos, nodelist=component, node_color=color, node_size=1000)
#         nx.draw_networkx_edges(graph, pos, edgelist=graph.subgraph(component).edges(), edge_color=color, width=2)

#         # Calculate the bounding box diagonal of the component nodes
#         node_positions = [pos[node] for node in component]
#         min_x, min_y = min(node_positions, key=lambda p: p[0])[0], min(node_positions, key=lambda p: p[1])[1]
#         max_x, max_y = max(node_positions, key=lambda p: p[0])[0], max(node_positions, key=lambda p: p[1])[1]
        
#         diagonal_length = ((max_x - min_x) ** 2 + (max_y - min_y) ** 2) ** 0.5
#         center_x = (min_x + max_x) / 2
#         center_y = (min_y + max_y) / 2
#         radius = diagonal_length / 2 + padding_factor * diagonal_length
        
#         circle = patches.Circle(
#             (center_x, center_y), 
#             radius=radius, 
#             edgecolor=color, 
#             facecolor=color,  
#             linewidth=2, 
#             alpha=0.3
#         )
        
#         # add the bounding circle to the plot
#         plt.gca().add_patch(circle)

#     # Add a title
#     plt.title("Runtime Analysis: " + program_name + " Pass Dependencies")

#     # Show the graph
#     plt.show()