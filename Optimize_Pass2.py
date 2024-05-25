import os 
import subprocess
import csv
import time
# import pandas as pd
# import matplotlib.pyplot as plt
# import hdbscan

# Holds the passes in opt O1, 45 passes
o1_passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg', 'always-inline', 'sroa', 'speculative-execution', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa', 'loop-rotate', 'licm', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memcpyopt', 'sccp', 'bdce', 'dse', 'adce', 'globaldce', 'float2int', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']

# Dictionary that holds differences between program from llvm-diff command
differences = []


def create_directory(directory_path):

    # Check if directory exits, if not, make it
    if os.path.exists(directory_path) == False:

        # Make directory at new path
        os.makedirs(directory_path, exist_ok = True)



def apply_passes(program_path, program_directory_path, round):

    """
    Applies each pass on a program, generating 45 optimized versions of that program and storing each version in its own subdirectory named
    after the pass that was applied on it. 

    Parameter:
    original_filepath (string): path to file which you would like to compare other files with
    program_directory_path (string): path to directory holding the programs contents
    round (int): indicates which stage you are on

    Return:
    pass_subdirectory_paths (list: string): paths to all the subdirectories generated
    """

    # List to hold all paths to pass subdirectories of current program
    pass_subdirectory_paths = []

    # Apply the passes on program, result is n (number of O1 passes in o1_passes) versions of program
    for o1_pass in o1_passes:

        # Path to subdirectory within that programs directory, this will hold the pass optimized file version of that program. Name the file the pass name
        pass_directory_path = os.path.join(program_directory_path, o1_pass)

        # Create a subdirectory within the program's directory to store that pass's optimized file
        create_directory(pass_directory_path)

        # Append subdirectory path to list
        pass_subdirectory_paths.append(pass_directory_path)

        if round == 1:
            # Optimized file name 
            optimized_filename = program_path.split('/')[-1] + "_" + o1_pass + ".ll" 
        else:
            optimized_filename = program_path.split('/')[-1] + o1_pass + ".ll"

        # Run opt command to apply current pass on the current program
        subprocess.run(['opt', '-S', '-passes=' + o1_pass, '-o', os.path.join(pass_directory_path, optimized_filename), program_path])

    
    return pass_subdirectory_paths
    

def traverse_files(original_filepath, program_subdirectory_path, pass_subdirectory_paths):
    """
    Traverses through subdirectories and applies the llvm-diff command on the files of interest. Then analyzes those differences 
    outputting them to a csv file in the subdirectory.

    Parameter:
    original_filepath (string): path to file which you would like to compare other files with
    program_subdirectory_path (string): path to directory holding the programs contents
    pass_subdirectory_paths (list: string): all paths to the subdirectories that hold the pass optimized versions of the program

    Return:
    Nothing, generates the csv file and places it in desired path
    """

    # Loop through each subdirectory under the program
    for pass_subdirectory in pass_subdirectory_paths:

        # Loop through subdirectory contents, should just be one file
        for item in os.listdir(pass_subdirectory):

            # Construct itempath
            itempath = os.path.join(pass_subdirectory, item)

            # Make sure the file is a path to a .ll file
            if item.endswith('.ll'):

                # Run llvm-diff command and store output as a string
                llvm_diff_output = llvm_diff(original_filepath, itempath)

                # Analyze differences and record them
                analyze_differences(pass_subdirectory, llvm_diff_output)

        # If not skip to next pass subdirectory
        else:

            continue
    
    # Output differences to a csv
    llvm_diff_csv_name = original_filepath.split("/")[-1] + '-llvm-diff-Results.csv'
    to_csv(program_subdirectory_path, llvm_diff_csv_name)




def llvm_diff(original_path, optimized_path):
    """
    Runs the llvm-diff command on 2 corresponding files

    Parameter:
    original_path (string): Path to the LLVM IR file that wasn't optimized
    optimized_path (string): Path to the LLVM IR file that was optimized

    Return:
    diff_output (string): String representation of contents from command
    """

    # Run llvm-diff command
    diff_output = subprocess.run(['llvm-diff', original_path, optimized_path], capture_output = True, text = True)

    # Convert output to a string
    diff_output = diff_output.stderr.splitlines()

    return diff_output


def analyze_differences(pass_subdirectory, llvm_diff):
    """
    Analyzes the differences between a non optimized LLVM IR file and the optimized version.

    Parameter:
    pass_subdirectory (string): Path to subdirectory holding the desired file
    llvm_diff (string): string output of llvm-diff command run on original and optimized file

    Return:
    Nothing, differences structure is updated with differences between corresponding files
    """

    # differences entry
    differences_entry = {
        'Pass': pass_subdirectory.split("/")[-1],
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

    # Path to csv file containing metrics
    csv_file = os.path.join(csv_output_dir, csv_name)

    # Define the field names for the csv columns
    field_names = ['Pass', 'Num Additions', 'Num Deletions']

    with open(csv_file, mode = 'w', newline = '') as file:
        
        # Create csv writer object
        writer = csv.DictWriter(file, fieldnames = field_names)

        # Write the header row with field names
        writer.writeheader()

        # Iterate all file comparison differences and print metrics to csv
        for entry in differences:
            writer.writerow({
                'Pass': entry['Pass'],
                'Num Additions': entry['Num Additions'],
                'Num Deletions': entry['Num Deletions']
            })


def main():

    global differences

    # Path to the directory containing the unoptimized files
    directory_path = '/Users/ahmedelzaria/Documents/LLVM/Test_Programs'

    # Create a new root directory that will hold all of the optimized files
    optimized_directory_path = '/Users/ahmedelzaria/Documents/LLVM/Optimized_Files_2'

    create_directory(optimized_directory_path)

    # Iterate over the programs in directory containing the unoptimized files
    for item in os.listdir(directory_path):
        
        # Construct item path
        itempath = os.path.join(directory_path, item)

        # Check if item is a file and a .ll file, if not skip to next item in directory
        if os.path.isfile(itempath) and item.endswith('.ll'):

            # Path to subdirectory within optimized_directory_path holding the optimized versions of the current program. Name it after the program
            program_subdirectory_path = os.path.join(optimized_directory_path, item)

            # Create directory if it doesn't exist
            create_directory(program_subdirectory_path)

            # First set of passes, result is 45 versions of current item each optimized with a different pass. Also holds the paths to all pass subdirectories of current program
            pass_subdirectories = apply_passes(itempath, program_subdirectory_path, round = 1)
            
            # Traverse the subdirectories and compare the optimized versions with the unoptimized versions, output the llvm-diff result of all passes on this program in a csv file
            # which will be stored in the program's subdirectory
            traverse_files(itempath, program_subdirectory_path, pass_subdirectories)

            # Reset differences list
            differences = []

            # Loop through each subdirectory and apply 45 pass version on the 1 optimized file in there
            for pass_subdirectory in pass_subdirectories:
                
                for file in os.listdir(pass_subdirectory):

                    # Construct filepath
                    filepath = os.path.join(pass_subdirectory, file)

                    # Check if file is correct one
                    if os.path.isfile(filepath) and filepath.endswith('.ll'):
                        
                        # apply passes
                        round2_pass_subdirectories = apply_passes(filepath, pass_subdirectory, round = 2)

                        # traverse the subdirectories and compare as before
                        traverse_files(filepath, pass_subdirectory, round2_pass_subdirectories)

                    else:

                        continue
            
            # Reset differences list
            differences = []

        else:

            # Skip to next item in directory
            continue


main()
