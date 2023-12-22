# LLVM Pass Microscope Tool Documentation
## *Background*
>A tool that allows us to visualize the evolution of pass interactions throughout the fate of a computer program. Maps out how different LLVM optimization passes interact with one another helping us visualize the fate of a computer program during the compilation process.


Code is a set of instruction us humans write to the computer to follow. We can write this code in multiple different languages such as Python, C, C++, Java, Javascript, etc. The same way we can give verbal instructions to one another in multiple different languages like Arabic, English, French, Spanish, etc. However, when programmers hit that run button in hopes of our code running successfully and as intended, the computer doesn't understand what you wrote right away.

There are two main levels of code, high and low level. High level is simple for humans to read and write (ex. Python, Java, etc.). These languages were designed for human use, hence why the syntax is fairly simple for a human to learn. However, computers don't understand this high level code. The computer's language is low level machine code which is a bunch of 0's and 1's.

So how does a computer take our English looking code and translate it to 0's and 1's it understands?

Looking at the big picture, it's a 3 step process. Step #1, the user writes there high level code and runs the program. Step #2, the computer then passes the user code into a set of complex programs called the compiler. The compiler's job is to translate your high level code to low level machine code. Step #3, the computer exits the compiler and gives the user an executable file which can be run to see the results of the computer program. 

My main focus is the middle stage of this process, the compiler. As mentioned, the compiler is a set of complex programs and hence, a lot of software engineers have no idea what really happens during this stage.

### Complitation Process
An analogy that will help us understand this process is writing an essay. The compilation process consists of 6 stages. Stage #1 is called Lexical Analysis. Think of this as separating the words from a sentence. Stage #2 is called Syntax Analysis, think of this as making sure your sentance has proper grammar. Stage #3 is called Semantic Analysis, now you are making sure that your sentance has meaning and is not pointless. Stage #4 is called Intermediate Code Generation and this is a huge area of our research. Think of this as a representation of your code which is not completely low level, but it isn't also high level, somewhere in the middle. Now that we have access to this representation, we can start treating it like a rough draft of an essay. When you have a rough draft, you will likely start proofreading it and making it better. It's the same case with this intermediate representation which leads me to stage #5, which is called Code Optimization. During this stage, the compiler is optimizing your code through this representation which will ultimately lead to more efficient machine code. More efficient machine code means smoother programs, less power consumption, less resource consumption, and a bunch more useful benefits. The final stage, stage #6, is linking (for multiple files). Imagine you've perfected all your sentences and now you have to combine them to get the full story.


### So What is LLVM?
LLVM is a set of tools and libraries to build compilers, it's a compiler infrastructure. Imagine you are building a toy factory, instead of designing each toy from scratch, you will likely want to set yourself some building blocks which you can reuse to build all the toys. Once you are done building the toys, you will also likely want to hire an inspector to run some tests like checking the colour, the fit of the components, etc. They will also let you know what improvements can be made to the design process. It's very similar for LLVM. LLVM provides us with passes, each having a specific aspect of your program that it targers and looks to optimize. When you combine these passes, you end up with a much more optimized version of your code that most programmers would not have been able to produce in the first place. So not only does the user end up with more efficient machine code (without any effort), but the computer can save some of its energy over time by optimizing your code during the compilation process. For example, if we consider the pass "loop-unroll", the basic idea behind it is to reduce loop overhead by executing multiple iterations of the loop in parallel, which can lead to better utilization of CPU resources and potentially fewer branching instructions.

### Ever Used an Apple Device?
Everytime an iPhone, MacBook, iMac, iPad, and most other apple devices are turned on, they are compiled by a compiler called Clang. Apple's default compiler is Clang which utilizes LLVM. 

## *Problem and Objectives*
### Passes Sound Great! But... What's the Catch?
LLVM provides us with over 70 passes. After doing the math, that's over 70! pass combinations which the compiler may apply on the intermediate representation (analagous to the rough draft mentioned). The number of atoms in the universe is around 10^80. Over 70! is over 10^100 possible pass combinations out there. That's an enormous amound of interactions. To put this in perspective, it would be more ridiculous to study all these interactions that it is to go out in space and visit each atom in the universe and note down how it interacts with the other atoms. 

### What's the Problem?
Theoretically, it would be awesome to analyze all these interactions and influences, but in reality it is impossible. French computer scientics Jean-Marc Jezequel once said, "If you are an astrophysicist, you are dealing with objects way smaller than the ones used by software engineers on a daily bases." That couldn't be any more true with LLVM pass interactions. So the issue that arises is that there is so much information about how these passes interact, influence one another, and how they impact the fate of a computer program that is left undiscovered. If we can find an effective approach to discover such information, we can learn a lot more on how to efficiently apply these passes to generate, in the quickest and most efficient manner, the best possible machine code during the compilation process. This information is crucial for companies such as Apple which are constantly looking for ways to achieve smoother devices and applications.

### Objectives
There are 3 main objectives to which I want the solution to solve.
1. Look at the passes and their dependencies. 
   - This will help us understand how the passes depend on eachother. By studying the relationshops between passes, I can gain insights into how different optimizations are interconnected and how they influence one another.
2. Analyze the evolution of the passes and their dependencies.
   - Focus on how the passes and their dependencies have changes over time. As LLVM evolves, new passes may be added, some may be modifies, and others could be removed or combined. Analyzing this evolution helps us understand how LLVM's optimization infrastructure was developed, what improvements have been made, and how the design choices have evolved to achieve better performance and efficiency.
3. Visualize this evolution 
   - Present the analysis of pass evolution and dependencies in a visual and understandable manner. Visualization can help us and others better grasp the complex relationships and patterns among passes.

### Approach
Back to the universe example, you can imagine if you were tasked to discover and analyze how all the different components within our universe interact with one another, you would feel defeated as this is simply, in reality and practicality, impossible to iterate over all possible interactions. So how about we zoom into multiple different sections within this huge canvas, analyze these sections and extract as much information as possible, then compare our observations with the observations from other sections we zoomed into and look for consistent and inconsistent patterns which we then can draw some conclusions from. The microscope effect. A microscope can help scientists zoom into a specific section within a relatively large canvas and helps them draw conclusions about the behaviour of the complete canvas. Same thing goes with my approach, I want to build a "pass microscope" that will help us zoom into any area within this large canvas and analyze the behavuour of the passes. After doing this for several different sections, we can then compare observations to draw some important conclusions. 

### Methodology

A 4-step process is executed on each program:
1. Passes are selected (ex. loop-unroll, mem2reg, etc.)
2. LLVM-IR is generated
3. Passes are applied on the IR
   - Using "llvm-diff", determine if post-pass applied version of the program is identical to any other versions generated
   - If unique, add a new node to the graph
   - Else, add an edge from parent node to identical node
   - Keep track of newly genereated nodes to visit in queue
4. Repeat for all nodes in queue until empty

