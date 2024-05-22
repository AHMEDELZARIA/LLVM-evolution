# LLVM Pass Microscope Tool Documentation
## *Background*
>A tool that allows us to visualize the evolution of pass interactions throughout the fate of a computer program. Maps out how different LLVM optimization passes interact with one another helping us visualize the fate of a computer program during the compilation process.


Code is a set of instruction humans write to the computer to follow. We can write this code in multiple different languages such as Python, C, C++, Java, Javascript, etc. The same way we can give verbal instructions to one another in multiple different languages like Arabic, English, French, Spanish, etc. However, when programmers hit that run button in hopes of our code running successfully... and as intended, the computer doesn't understand our code right away.

There are two main levels of code, high and low level. High level is simple for humans to read and write (ex. Python, Java, etc.). These languages were designed for human use, hence why the syntax is fairly simple for a human to learn. However, computers don't understand this high level code. The computer's language is low level machine code which is a bunch of 0's and 1's.

So how does a computer take our high level code and translate it to the 0's and 1's it understands?

Looking at the big picture, it's a 3 step process. Step #1, the user writes their high level code and runs the program. Step #2, the computer then passes the user code into a set of complex programs called the compiler. The compiler's job is to translate your high level code to low level machine code. Step #3, the computer exits the compiler and gives the user an executable file (assuming compilation was successful) which can be run, revealing the results of the computer program. 

My main focus is the middle stage of this process, the compiler. As mentioned, the compiler is a set of complex programs and hence, a lot of software engineers have no idea what really happens during this stage of the process.
<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/ccbb9484-b8ab-40d2-accb-b6b8183af5f8" alt="Example Image" width="500" height="185">
<p>3 step process described above</p>
</div>

### Complitation Process
An analogy that will help us understand this process is writing an essay. The compilation process consists of 6 stages. Stage #1 is called Lexical Analysis. Think of this as separating the words from a sentence. Stage #2 is called Syntax Analysis, think of this as making sure your sentance has proper grammar. Stage #3 is called Semantic Analysis, now you are making sure that your sentance has meaning and is not pointless. Stage #4 is called Intermediate Code Generation and this is the area of our research. Think of this as a representation of your code which is not completely low level, but it isn't also high level, somewhere in the middle. Now that we have access to this representation, we can start treating it like a rough draft of an essay. When you have a rough draft, you will likely start proofreading it and making it better. It's the same case with this intermediate representation which leads me to stage #5, which is called Code Optimization. During this stage, the compiler is optimizing your code through this representation which will ultimately lead to more efficient machine code. More efficient machine code means smoother programs, less power consumption, less resource consumption, and a bunch more useful benefits. The final stage, stage #6, is linking (for multiple files). Imagine you've perfected all your sentences and now you have to combine them to get the full story.

<div align="center">
<img src="https://github.com/AHMEDELZARIA/LLVM-evolution/assets/93144563/4748cf1b-9121-43dc-a56f-5ef67afae868" alt="Example Image" width="1158" height="358">
<p>General overview of LLVM compiler infrastructure with a focus on the middle-end stage where optimizations take place</p>
</div>

### So What is LLVM?
LLVM is a set of tools and libraries to build compilers, it is a compiler infrastructure. Imagine you are building a toy factory, instead of designing each toy from scratch, you will likely want to set yourself some building blocks which you can reuse to build all the other toys. Once you are done building the toys, you will also likely want to hire an inspector to run some tests like checking the colour, the fit of the components, etc. They will also let you know what improvements can be made to the design process. It is very similar for LLVM. LLVM provides us with passes, each having a specific aspect of your program that it targets and aims to optimize. When you combine these passes, you end up with a much more optimized version of your code that most programmers would not have been able to produce in the first place. So not only does the user end up with more efficient machine code (without any effort), but the computer can save some of its energy over time by optimizing your code during the compilation process. For example, if we consider the pass "loop-unroll", the basic idea behind it is to reduce loop overhead by executing multiple iterations of the loop in parallel, which can lead to better utilization of CPU resources and potentially fewer branching instructions.

### Ever Used an Apple Device?
Everytime an iPhone, MacBook, iMac, iPad, and most other apple devices are turned on, they are compiled by a compiler called Clang. Apple's default compiler is Clang which utilizes LLVM. 

## *Problem and Objectives*
### Passes Sound Great! But... What's the Catch?
**LLVM provides us with over 70 passes**. After doing some combinatorial analysis, **that's over 70! pass combinations which the compiler may apply on the intermediate representation.** The number of atoms in the universe is around 10^80. **Over 70! is over 10^100 possible pass combinations out there.** That's an enormous amount of interactions. To put this in perspective, it would be more ridiculous to study all these interactions than it is to go out in space and visit each atom in the universe and note down how it interacts with the other atoms. 

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/5039a79d-85eb-4cf9-ada0-d783b51465fb" alt="Example Image" width="550" height="300">
<p>There are more possible pass combinations out there than the number of atoms in the universe...</p>
</div>

### What's the Problem?
Theoretically, it would be awesome to analyze all these interactions and influences, but in reality it is impossible. French computer scientics Jean-Marc Jezequel once said, "If you are an astrophysicist, you are dealing with objects way smaller than the ones used by software engineers on a daily bases." That could not be any more true with LLVM pass interactions. So the issue that arises is that there is so much information about how these passes interact, influence one another, and how they impact the fate of a computer program that is left undiscovered. If we can find an effective approach to discover such information, we can learn a lot more on how to efficiently apply these passes to generate, in the quickest and most efficient manner, the best possible machine code during the compilation process. This information is crucial for companies such as Apple which are constantly looking for ways to achieve smoother devices and applications.

### Objectives
There are 3 main objectives:
1. Look at the passes and their dependencies. 
   - This will help us understand how the passes depend on eachother. By studying the relationshops between passes, I can gain insights into how different optimizations are interconnected and how they influence one another.
2. Analyze the evolution of the passes and their dependencies.
   - Focus on how the passes and their dependencies have changes over time. As LLVM evolves, new passes may be added, some may be modified, and others could be removed or combined. Analyzing this evolution helps us understand how LLVM's optimization infrastructure was developed, what improvements have been made, and how the design choices have evolved to achieve better performance and efficiency.
3. Visualize this evolution 
   - Present the analysis of pass evolution and dependencies in a visual and understandable manner. Visualization can help us and others better grasp the complex relationships and patterns among passes.

### Approach
Back to the universe example, you can imagine if you were tasked to discover and analyze how all the different components within our universe interact with one another, you would feel defeated as this is simply, in reality and practicality, impossible. So how about we zoom into multiple different sections within this huge canvas, analyze these sections and extract as much information as possible, then compare our observations with the observations from other sections we zoomed into and look for consistent and inconsistent patterns which we then can draw some conclusions from. ***The microscope effect.*** A microscope can help scientists zoom into a specific section within a relatively large canvas and helps them draw conclusions about the behaviour of the complete canvas. Same thing goes on here with my approach, I want to build a "pass microscope" that will help us zoom into any area within this large canvas and analyze the behavuour of the passes. After doing this for several different sections, we can then compare observations to draw some important conclusions. 

## *Methodology*

We utilize the "Angha Project" benchmark consisting of 1 million clang compilable .c programs. After parsing each program and extracting structural metrics (number of variables, functions, control flows, etc.), it was evident that the benchmark could be downsized to 3600 random programs without bias since metrics revealed signs of a homogenous benchmark. This left us with a more practical amount of programs to work with.

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/f6faff9c-ae4d-4d12-adc2-c95870657c5a" alt="Example Image" width="600" height="500">
</div>

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/56565086-c31c-435d-ad24-ff0b4aa63a61" alt="Example Image" width="600" height="500">
<p>Graphs of metrics revealed similar results, indicating a homogenous benchmark</p>
</div>

A **4-step process** is executed on each program:
1. Passes are selected (ex. loop-unroll, mem2reg, etc.).
2. LLVM-IR is generated.
3. Passes are applied on the IR.
   - Using "llvm-diff", determine if post-pass applied version of the program is identical to any other versions generated
   - If unique, add a new node to the graph representing new program state
   - Else, add an edge from parent node to identical node
   - Keep track of newly genereated nodes to visit in queue
4. Repeat for all nodes in queue until empty

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/3d7094ed-eabe-4045-8c77-639dedc62dee" alt="Example Image" width="1000" height="300">
<p>Demonstration of how transition graphs are built</p>
</div>


## *Results*
**A novel tool to visualize pass interactions in order to analyze how different LLVM passes affect code transformations and performance**. Nodes represent unique program states while edges indicate the relationships between different program states. This tool is able to generate the transition graph of any .c program with any set of valid LLVM passes. Simply indicate the location of test programs and the set of passes you want to run on them (see section *Usage* below).

**The graphs are also interactive!** Allowing you to easily navigate through complex structures and extract the information you need. There are also a bunch of customization tools available in order to suit your goals and style. 

Connected components are also highlighted in order to identify weakly connected and strongly connect program states. Here are some examples:

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/ce958494-5f82-4737-9bb0-e016e780f043" alt="Example Image" width="600" height="500">
<p>Fate of program depends on 2 passes in the middle, either trapping it in the left or right cluster which indicates significance in these passes</p>
</div>

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/c09180a6-08b8-4c27-93fd-e5da2e1b45a8" alt="Example Image" width="600" height="500">
<p>Small set of passes applied to a program</p>
</div>

<div align="center">
<img src="https://github.com/AHMEDELZARIA/Recover-JPEG/assets/93144563/a1af8c9c-464f-4f4a-a45a-9c2d051a3bb5" alt="Example Image" width="600" height="500">
<p>Large set of passes applied to a program</p>
</div>

## *Usage*
**In order to use the pass microscope for yourself, there are only a few simple steps required!**

1. Download the file **"Pass_Relations_Graph.py"**. **Each function used is documented!**
2. Select the passes of interest by navigating to the **main function (line 383)** and adding them to the list "passes".
```python
def main():
   # Main function code

   # Insert passes here
   passes = ['loop-simplify', 'loop-rotate', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'loop-sink']
   
   # Rest of main function
```
Here is the list of all passes I have tested, in order to validate that they are working till this date (2023):
```python
def main():
   # Valid passes as of 2023
   valid_O1_Passes = ['forceattrs', 'inferattrs', 'ipsccp', 'called-value-propagation', 'globalopt', 'mem2reg', 'deadargelim', 'instcombine', 'simplifycfg', 'always-inline', 'sroa', 'speculative-execution', 'jump-threading', 'correlated-propagation', 'libcalls-shrinkwrap', 'pgo-memop-opt', 'tailcallelim', 'reassociate', 'loop-simplify', 'lcssa', 'loop-rotate', 'licm', 'indvars', 'loop-idiom', 'loop-deletion', 'loop-unroll', 'memcpyopt', 'sccp', 'bdce', 'dse', 'adce', 'globaldce', 'float2int', 'loop-distribute', 'loop-vectorize', 'loop-load-elim', 'alignment-from-assumptions', 'strip-dead-prototypes', 'loop-sink', 'instsimplify', 'div-rem-pairs', 'verify', 'ee-instrument', 'early-cse', 'lower-expect']
```
3. **Optional:** By default, the program is set to run for a max of 3 hours or until more than 10000 nodes have been created. However, the program does automatically exit if the graph is finished generating before then. Depending on the program and set of passes used, this timing limit is reasonable. You can adjust this limit in the **main function (line 430)**, as seen below:
```python
def main():
   # Main function code

   # Change timning limit
   current_time = time.time()
   elapsed_time = current_time - start_time
   num_nodes = G.number_of_nodes()
   if elapsed_time > 10800 or num_nodes > 10000:
      break
   
   # Rest of main function
```
4. Run the program.
5. You will then be prompted for a path to the directory containing the .c file(s).
6. If all steps above were completed correctly, the program will now begin to generate your html file(s) containing the graph(s).
   - In general, the more complex the .c file is and the more passes you want to apply, the longer this process will take
7. Once done, a directory in the same path provided, called "Graph Visualizations", will contain the html file(s) which are the graph visualization(s). Additionally, a directory called "gml_files" will also be generated, containing the gml file(s) of the graph(s) generated.

## *Future Work*
1. Developing an algorithm to study patterns and identify traits from the graphs
   - Investigate methods to automate the extraction of meaningful patterns and dependencies, contributing to a deeper understanding of LLVM transformations and optimizations.
2. Scaling this process across an entire benchmark and using the algorithm in 1. to compare results and make some meaningful conclusions.

## Research Poster
This project was presented at the 2023 McMaster Undergraduate Research Fair. Here is the accompanying research poster.
[View PDF](./Ahmed_Elzaria_2023_Poster_FINAL.pdf)
