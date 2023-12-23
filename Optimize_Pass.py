# Takes LLVM IR files of any amount of .c files, applies an individual independent pass
# to them and outputs the new IR files into a new directory
# Best used after IR.py 

import os
import subprocess
import time
import csv

# Start timer
start_time = time.time()

# Holds all passes in O1
O1_Passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg', 'always-inline', 'sroa', 'speculative-execution', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa', 'loop-rotate', 'licm', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memcpyopt', 'sccp', 'bdce', 'dse', 'adce', 'globaldce', 'float2int', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']

def traverse_files(directory):
    """
    Traverses a directory containing only LLVM IR files and applies a pass
    to them. Generates the newly optimized files and places them in a new
    directory. Additionally, times how long each pass takes on each file and
    outputs a csv with these results in the same directory that stores that passes
    optimized files. Additionally, times total time elapsed by applying the pass on all
    files and stores those results in a csv in the main directory that contains the subdirectories
    of optimized files.

    Parameter:
    directory (string): Path to the directory of interest containing LLVMN IR files
    output_directory (string): Path to the directory to store optimized LLVM IR files.

    Return:
    Nothing, optimized LLVM IR files are appended to output_directory and csv's are outputted to respective
    subdirectories.
    """   

    # Loop through each pass
    for O1_Pass in O1_Passes:

        # Create a new directory to store new optimized files
        output_directory_path = os.path.join("/Users/ahmedelzaria/Documents/LLVM/Optimized_Files", O1_Pass)

        # Check if directory exits, if not, make it
        if os.path.exists(output_directory_path) == False:
            os.makedirs(output_directory_path, exist_ok = True) # Make directory at new path

        # csv file path
        csv_file = os.path.join(output_directory_path, 'Pass_Time_Results.csv')

        with open(csv_file, mode = 'w', newline = '') as file:

            # Create write object
            writer = csv.writer(file)

            # Write header to csv
            writer.writerow(['Program Name', 'Elapsed Time'])

            # Start timer for total pass time
            total_start_time = time.time()

            # Iterates through each file in directory
            for file in os.listdir(directory):

                if file.endswith(".ll"):

                    # Construct filepath
                    filepath = os.path.join(directory, file)

                    # Start the timer to time how long the pass takes on current file
                    start_time = time.time()

                    # Run pass command
                    subprocess.run(['opt', '-S', '-passes=' + O1_Pass, '-o', os.path.join(output_directory_path, file), filepath])

                    # End the timer
                    end_time = time.time()

                    # Elapsed time
                    elapsed_time = end_time - start_time

                    # Data to be written to current row of csv
                    row_data = [file, elapsed_time]

                    # Write to csv
                    writer.writerow(row_data)

                else:

                    # Skip to next file
                    continue

        # End timer for total pass time
        total_end_time = time.time()
        
        # Total elapsed time
        total_elapsed_time = total_end_time - total_start_time

        # Csv path to store total pass time results
        csv_file = os.path.join('/Users/ahmedelzaria/Documents/LLVM/Optimized_Files', 'Total_Pass_Time_Results.csv')

        # Write the time taken for pass to run all files in separate csv
        with open(csv_file, mode = 'a', newline = '') as file:

            # Create write object
            writer = csv.writer(file)

            # If first iteration, write header to csv
            if O1_Pass == 'forceattrs':

                # Write header to csv
                writer.writerow(['Pass', 'Total Elapsed Time'])

            # Row data
            row_data = [O1_Pass, total_elapsed_time]

            # Write data to csv
            writer.writerow(row_data)


# Path to directory containing LLVM IR files
input_directory = "/Users/ahmedelzaria/Documents/LLVM/Ir_Files"
traverse_files(input_directory)

# Stop the timer
end_time = time.time()

# Calculate total time
elapsed_time = end_time - start_time

print("Elapsed time:", elapsed_time)



introduction = "Hello! I will be talking about my research today!"
print(introduction)