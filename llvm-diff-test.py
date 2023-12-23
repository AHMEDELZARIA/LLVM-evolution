import subprocess

differences = []

original_path = "/Users/ahmedelzaria/Documents/LLVM/Ir_Files/extr_async_xor.c_do_sync_xor.c.ll"
optimized_path = "/Users/ahmedelzaria/Documents/LLVM/Optimized_Files/O1/extr_async_xor.c_do_sync_xor.c.ll"

# Run llvm-diff command
diff_output = subprocess.run(['llvm-diff', original_path, optimized_path], capture_output=True, text=True)

diff_output = diff_output.stderr.splitlines()

# differences entry
differences_entry = {
    'Original File': original_path,
    'Optimized File': optimized_path,
    'Additions': [],
    'Num Additions': 0,
    'Deletions': [],
    'Num Deletions': 0,
    'Modifications': [],
    'Num Modifications': 0
}

# Iterate over all lines in output and note the additions, deletions, and modifications
for line in diff_output:

    # Check if line is an addition or deletion or modification and append it
    if line.strip().startswith('>'):
        differences_entry['Additions'].append(line)
        differences_entry['Num Additions'] += 1
    elif line.strip().startswith('<'):
        differences_entry['Deletions'].append(line)
        differences_entry['Num Deletions'] += 1

# Append the current comparison to main list/dictionary
differences.append(differences_entry)

print(differences['Num Additions'])

