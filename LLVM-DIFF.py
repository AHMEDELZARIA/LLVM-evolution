# run the llvm-diff command, comparing a non optimized LLVM IR file with
# its individual independent pass optimized file. Captures and parses the
# output, then transfers it to a csv file for further analysis

import os
import subprocess
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import time

# Start timer
start_time = time.time()

# dictionary to track all differences between files
differences = []

# Holds all passes in O1
O1_Passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg', 'always-inline', 'sroa', 'speculative-execution', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa', 'loop-rotate', 'licm', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memcpyopt', 'sccp', 'bdce', 'dse', 'adce', 'globaldce', 'float2int', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']


def traverse_files(original_dir, optimized_dir):
    """
    Traverses through the original directory (containing non optimized LLVM IR files) and
    optimized directory (containing optimized LLVM IR files) and runs the llvm-diff command
    on corresponding files and analyzes the differences. The differences are stored in a dictionary
    structure as well as outputted to a csv file

    Parameter:
    original_dir (string): Path to the directory of non optimized LLVM IR files
    optimized_dir (string): Path to the directory of optimized LLVM IR files
    csv_output_dir (string): Path to the directory to store csv output

    Return:
    Nothing, dicitionary containing differences is updated and csv file is outputted to output directory
    """

    # Holds the names of the original and optimized files, sorted to ensure they match correctly
    original_files = os.listdir(original_dir)

    # Iterate over each original file and optimized file in respective directory simultaniously
    for original_file in original_files:

        if original_file.endswith('.ll'):

            # Construct filepaths
            original_path = os.path.join(original_dir, original_file)
            optimized_path = os.path.join(optimized_dir, original_file)
            
            # Run llvm-diff command and store output as a string
            llvm_diff_output = llvm_diff(original_path, optimized_path)

            # Analyze differences and record them
            analyze_differences(original_file, original_file, llvm_diff_output)

        else:
            
            # Skip to next file
            continue


def llvm_diff(original_path, optimized_path):
    """
    Runs the llvm-diff command on 2 corresponding files

    Parameter:
    original_path (string): Path to the LLVM IR file that wasn't optimized
    optimized_path (string): Path to the LLVM IR file that was optimized

    Return:
    diff_output_string (string): String representation of contents from command
    """

    # Run llvm-diff command
    diff_output = subprocess.run(['llvm-diff', original_path, optimized_path], capture_output = True, text = True)

    # Convert output to a string
    diff_output = diff_output.stderr.splitlines()

    return diff_output


def analyze_differences(original_file, optimized_file, llvm_diff):
    """
    Analyzes the differences between a non optimized LLVM IR file and the optimized version.

    Parameter:
    original_file (string): name of non optimized LLVM IR file
    optimized_file (string): name of optimized LLVM IR file
    llvm_diff_string (string): string output of llvm-diff command run on original and optimized file

    Return:
    Nothing, differences structure is updated with differences between corresponding files
    """

    # differences entry
    differences_entry = {
        'Original File': original_file.split("/")[-1],
        'Optimized File': optimized_file.split("/")[-1],
        'Additions': [],
        'Num Additions': 0,
        'Deletions': [],
        'Num Deletions': 0,
        'Modifications': [],
        'Num Modifications': 0
    }

    # Iterate over all lines in output and note the additions, deletions, and modifications
    for line in llvm_diff:

        # Check if line is an addition or deletion or modification and append it
        if line.strip().startswith('>'):
            differences_entry['Additions'].append(line)
            differences_entry['Num Additions'] += 1
        elif line.strip().startswith('<'):
            differences_entry['Deletions'].append(line)
            differences_entry['Num Deletions'] += 1
    
    # Append the current comparison to main list/dictionary
    differences.append(differences_entry)


def to_csv(csv_output_dir, csv_name):
    """
    Takes the differences information and outputs it into a csv file.

    Parameter:
    csv_output_dir (string): path to which you want to store csv file
    csv_name (string): name of csv file

    Return:
    Nothing, generates the csv file and places it in desired path
    """

    # Make a new subdirectory that will hold the csv containing the metrics and the csv containing the clustering of programs
    if os.path.exists(csv_output_dir) == False:
        os.mkdir(csv_output_dir)

    # Path to csv file containing metrics
    csv_file = os.path.join(csv_output_dir, csv_name)

    # Define the field names for the csv columns
    field_names = ['Original File', 'Optimized File', 'Num Additions', 'Num Deletions']

    with open(csv_file, mode = 'w', newline = '') as file:
        
        # Create csv writer object
        writer = csv.DictWriter(file, fieldnames = field_names)

        # Write the header row with field names
        writer.writeheader()

        # Iterate all file comparison differences and print metrics to csv
        for entry in differences:
            writer.writerow({
                'Original File': entry['Original File'],
                'Optimized File': entry['Optimized File'],
                'Num Additions': entry['Num Additions'],
                'Num Deletions': entry['Num Deletions']
            })


def visualize(csv_output_dir, csv_name, store_plots, csv_clusters_name):
    """
    Plots every possible combination of the metrics stored in csv file passed in. Applies KMeans
    clustering algorithm to group data into visible clusters.

    Parameter:
    csv_output_dir (string): path to which you want to store csv file
    csv_name (string): name of csv file

    Return:
    Nothing, generates the plots in desired directory
    """

    # Make a new subdirectory to store plots
    if os.path.exists(store_plots) == False:
        os.mkdir(store_plots)

    # Indicate path to csv containing metrics
    csv_path = os.path.join(csv_output_dir, csv_name)

    # Load data into a DataFrame
    data = pd.read_csv(csv_path)
    
    # Set index as a combination of the original filename and optimized filename
    data.set_index(['Original File', 'Optimized File'], inplace = True)

    # Place metric names in an array
    metric_names = data.columns

    # Convert the DataFrame to a numpy array
    data_array = data.to_numpy()

    # Create an instance from the KMeans class and identify the number of clusters
    kmeans = KMeans(n_clusters = 4) 

    # Assigns a cluster to data points
    cluster_labels = kmeans.fit_predict(data_array)

    # Output the clusters to a csv file
    output_clusters(data, cluster_labels, csv_output_dir, csv_clusters_name)

    # Loop through each metric and ensure every possible combination of metrics is plotted
    for i in range(len(metric_names)):

        for j in range(i + 1, len(metric_names)):

            # Create a figure and axes
            figure, axes = plt.subplots()

            # Get metric names
            metric_1_name = metric_names[i]
            metric_2_name = metric_names[j]

            # Extract metrics data from DataFrame
            metric_1_data = data[metric_1_name]
            metric_2_data = data[metric_2_name]

            # Loop through each cluster in set of clusters
            for cluster_id in set(cluster_labels):

                # Get the indices of of all data points that fall in current cluster
                cluster_indices = cluster_labels == cluster_id
 
                # Get the metrics for current cluster
                cluster_data_x = metric_1_data[cluster_indices]
                cluster_data_y = metric_2_data[cluster_indices]

                # Plot the metrics for current cluster assigning a unqiue colour to current cluster
                axes.scatter(cluster_data_x, cluster_data_y, color='C{}'.format(cluster_id), s=15)

            # Style the graph
            axes.set_xlabel(metric_1_name)
            axes.set_ylabel(metric_2_name)
            plot_title = (store_plots.split('/')[-1]) + " " + metric_1_name + ' vs ' + metric_2_name
            axes.set_title(plot_title)
            axes.grid(True)

            # Save the current plot to the directory
            figure.savefig(os.path.join(store_plots, plot_title + '.png'), format='png')

            # Close the plot
            plt.close(figure)


def output_clusters(data, cluster_labels, csv_output_dir, cluster_csv_name):
    """
    Outputs the filename and cluster information to a new CSV file.

    Parameters:
    data (DataFrame): DataFrame containing the data
    cluster_labels (array-like): Array-like object containing the cluster labels
    csv_output_dir (string): Path to the directory to store the CSV file
    csv_name (string): Name of the CSV file

    Return:
    Nothing, generates the CSV file with the filename and cluster information
    """

    # Output path of csv
    csv_clusters_file = os.path.join(csv_output_dir, cluster_csv_name)

    with open(csv_clusters_file, mode = 'w', newline = '') as file:

        # Create write object
        writer = csv.writer(file)

        # Write header to csv
        writer.writerow(['Program Name', 'Cluster'])

        # Loop through each program and its clusterID
        for file, cluster_id in zip(data.index, cluster_labels):

            # Write program name and cluster ID to the csv
            writer.writerow([file, cluster_id])

        # Count the number of programs in each cluster
        cluster_counts = Counter(cluster_labels)

        # Output the cluster ID and program count
        writer.writerow([])
        writer.writerow(['Cluster', 'Program Count'])
        for cluster_id, count in cluster_counts.items():
            writer.writerow([cluster_id, count])


def main():

    for O1_Pass in O1_Passes:

        global differences

        # Empty the differences list if not first iteration
        if O1_Pass != 'forceattrs':
            differences = []

        # Paths to directories holding LLVM IR files
        original_dir = "/Users/ahmedelzaria/Documents/LLVM/Ir_Files"
        optimized_dir = os.path.join("/Users/ahmedelzaria/Documents/LLVM/Optimized_Files", O1_Pass)
        csv_output_dir = os.path.join("/Users/ahmedelzaria/Documents/LLVM/llvm-diff-csv", O1_Pass)
        csv_metrics_name = "llvm-diff-" + O1_Pass + "-Results.csv"
        csv_clusters_name = O1_Pass + "-clusters-data.csv"
        store_plots = os.path.join("/Users/ahmedelzaria/Documents/LLVM/Plots/llvm-diff_plots", O1_Pass)

        # Traverse all corresponding pair of files and analyze differences
        traverse_files(original_dir, optimized_dir)
        
        # for entry in differences:
        #     print(entry["Num Additions"], entry["Num Deletions"])

        # Print differences to csv file
        to_csv(csv_output_dir, csv_metrics_name)

        # Visualize differences through plots
        visualize(csv_output_dir, csv_metrics_name, store_plots, csv_clusters_name)


main()

# Stop the timer
end_time = time.time()

# Calculate total time
elapsed_time = end_time - start_time

print("Elapsed time:", elapsed_time)