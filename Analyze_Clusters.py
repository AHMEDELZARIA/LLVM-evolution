import csv
import os
import sys

def read_csv(csv_files_root_directory):

    # Csv names list
    csv_paths = []

    # Iterate through each item in root directory
    for item in os.listdir(csv_files_root_directory):

        # Construct current item path
        item_path = os.path.join(csv_files_root_directory, item)

        # If current item is a file skip
        if os.path.isdir(item_path):

            # Recursively traverse subdirectories
            subdirectory_csv_names = read_csv(item_path)
            csv_paths.extend(subdirectory_csv_names)

        # Else if path is a file of type .csv and contains 'clusters-data' in name, record name of file in csv_names list
        elif os.path.isfile(item_path) and item.endswith('.csv') and ('clusters-data' in item):

            # Append name of file to csv names list
            csv_paths.append(item_path)

        # If anything else, skip
        else:
            
            continue

    # Dictioanry to store csv data
    csv_data = {}

    # Loop through each csv in csv_names list
    for csv_file in csv_paths:

        # Initialize an empty list for the current csv's entry in the dictionary
        csv_data[csv_file] = []

        # Open the current csv for reading
        with open(csv_file, 'r') as file:
            
            # Read the csv into reader
            reader = csv.DictReader(file)

            # Append each row of csv to list stored in dictionary
            for row in reader:

                csv_data[csv_file].append(row)


    return csv_data
        
def store_clusters(csv_pass_data):

    # Dictionary to store each programs cluster
    program_clusters = {}

    # Iterate over each item in csv_pass_data, which contains the csv data for each pass
    for csv_file, data in csv_pass_data.items():

        # For each csv_file and its corresponding data, iterate over each row in the data
        for row in data:

            # Extract the program name and cluster information from the current row
            program_name = row['Program Name']
            cluster = row['Cluster']

            # Check if current program name already exists as a key in program_clusters
            if program_name not in program_clusters:

                # If not add the program name as a new key with an empty list as its value
                program_clusters[program_name] = []
            
            # If program name already exists, append the cluster value to the list associated with that program name
            program_clusters[program_name].append(cluster)

    return program_clusters

def compare_cluster_lists(program_clusters):

    # List to store list of consistent clusters
    consistent_clusters = []

    # Iterate over each program in program_clusters
    for program_name, clusters in program_clusters.items():

        # Tracks if a program is repeated in the main list
        repeats = False

        # To ensure no repetitions, check if current_program name is not in main list already
        for sub_list in consistent_clusters:
            
            # If it is in one of the sublist, update state of repeats to True and break out
            if program_name in sub_list:

                repeats = True
                break

        # If no repeats, start checking for consistency
        if repeats == False:

            # Sublist to store programs that are consistent with current program
            current_matches = [program_name]

            # Iterate over all other programs
            for other_program, other_clusters in program_clusters.items():

                # As long as it's not the same program
                if program_name != other_program:

                    # If the set of clusters is the same, note down consistency
                    if set(clusters) == set(other_clusters):
                        
                        current_matches.append(other_program)

            # If matches were found, append, else don't
            if len(current_matches) > 1:
                # Append current matches to main list
                consistent_clusters.append(current_matches)

        # Else skip to next program as current program already in a consistency list
        else:

            continue

    return consistent_clusters


def main():

    # Save execution into a text file
    with open('/Users/ahmedelzaria/Documents/LLVM/Same_Clusters.txt', 'w') as file:

        # Redirect the standard output to the file
        original_stdout = sys.stdout
        sys.stdout = file # Ensures any prints moving forward are to the file not terminal

        # Step 1: Read csv files for each pass
        csv_pass_data = read_csv(csv_files_root_directory = '/Users/ahmedelzaria/Documents/LLVM/llvm-diff-csv')

        # Step 2: Create a dictionary to store clusters for each program
        program_clusters = store_clusters(csv_pass_data)

        # Step 3: Compare cluster lists for each program
        consistent_clusters = compare_cluster_lists(program_clusters)

        # Print results
        print(consistent_clusters)

        # Restore the standard output
        sys.stdout = original_stdout


main()
