import subprocess
import time
import os

# Start timer
start_time = time.time()

# List of O1 Passes (from 2013)
O1_passes = ['targetlibinfo', 'tti', 'tbaa', 'scoped-noalias', 'assumption-cache-tracker', 'profile-summary-info', 'forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'domtree', 'mem2reg', 'deadargelim', 'basic-aa', 'aa', 'loops', 'lazy-branch-prob', 'lazy-block-freq', 'opt-remark-emitter', 'instcombine', 'simplifycfg', 'basiccg', 'globals-aa', 'prune-eh', 'always-inline', 'functionattrs', 'sroa', 'memoryssa', 'early-cse-memssa', 'speculative-execution', 'lazy-value-info', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'branch-prob', 'block-freq', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa-verification', 'lcssa', 'scalar-evolution', 'loop-rotate', 'licm', 'loop-unswitch', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memdep', 'memcpyopt', 'sccp', 'demanded-bits', 'bdce', 'dse', 'postdomtree', 'adce', 'barrier', 'rpo-functionattrs', 'globaldce', 'float2int', 'loop-accesses', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']

# Test files
output_filename = 'test-'
output_directory_path = '/Users/ahmedelzaria/Documents/LLVM/Test_Passes'
input_filepath = '/Users/ahmedelzaria/Documents/LLVM/extr_tau32-ddk.c_Pp5_4.c.ll'

# List to hold removed passes
valid_passes = []

# Loop through passes, run the pass on 2 files and see if it returns an error, if it does, than the pass doesn't exist in 2023, so remove from O1_Passes list
for O1_pass in O1_passes:

    try:
        subprocess.run(['opt', '-S', '-passes=' + O1_pass, '-o', os.path.join(output_directory_path, output_filename + O1_pass), input_filepath], check = True)
        valid_passes.append(O1_pass)
    except subprocess.CalledProcessError:
        pass
 
print(valid_passes)

# Stop the timer
end_time = time.time()

# Calculate total time
elapsed_time = end_time - start_time

print("Elapsed time:", elapsed_time)

