"""
sorting_example.py

LENS Sorting Problem - Standalone version.

Initial Algorithms: Bubble Sort, Selection Sort, Insertion Sort (All O(n^2))
Goal: Minimize comparisons.

*** EXTREME HARD MODE ***
Forbidden: 'merge', 'quick', 'heap', 'shell', 'tim', etc.
The AI must implement the LOGIC without using the standard NAMES.
"""

import os
import sys
import numpy as np

from lens_minimal import LENS

# ---------------------------------------------------------------------
# PROBLEM DEFINITION
# ---------------------------------------------------------------------

PROBLEM_DESCRIPTION = r"""
You are designing a sorting algorithm that minimizes comparison operations.

CRITICAL GOAL:
Your algorithm MUST minimize the number of comparisons while correctly
sorting an array of integers in ascending order.

INPUT CONTEXT:
context['array']: A list of integers to be sorted.

MANDATORY EXECUTE() REQUIREMENTS:
Your algorithm MUST define a function:

def execute(params, context):
    # context['array'] is a list of integers
    # ... sorting logic ...
    # return a dictionary with:
    # {
    #   'success': True,
    #   'sorted': [1, 2, 3, ...], # The sorted list
    #   'comparisons': 150        # Count of comparisons performed
    # }

ALGORITHM RULES:
- You MUST NOT use Python's built-in sorted() or list.sort()
- You MUST NOT use library functions: heapq, bisect, numpy.sort, etc.
- You MUST implement sorting from scratch.
- You MUST explicitly count EVERY comparison operation (e.g., if a > b).
- comparisons = 0 is INVALID and will receive zero fitness.

*** STRICT NAMING CONSTRAINTS ***
- You act as an alien scientist who does not know human algorithm names.
- Do NOT use standard algorithm names in your function names or variables.
- Prohibited words: "merge", "quick", "heap", "shell", "tim", "intro", "radix"
- Instead, describe what the code DOES (e.g., "divide", "combine", "swap").
"""

# ---------------------------------------------------------------------
# INITIAL ALGORITHMS (O(n^2) Baselines)
# ---------------------------------------------------------------------

BUBBLE_SORT_CODE = r"""
def execute(params, context):
    arr = context['array'].copy()
    n = len(arr)
    comparisons = 0
    
    for i in range(n):
        for j in range(0, n - i - 1):
            comparisons += 1
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                
    return {
        'success': True,
        'sorted': arr,
        'comparisons': comparisons
    }
"""

SELECTION_SORT_CODE = r"""
def execute(params, context):
    arr = context['array'].copy()
    n = len(arr)
    comparisons = 0
    
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if arr[j] < arr[min_idx]:
                min_idx = j
        if min_idx != i:
            arr[i], arr[min_idx] = arr[min_idx], arr[i]
            
    return {
        'success': True,
        'sorted': arr,
        'comparisons': comparisons
    }
"""

INSERTION_SORT_CODE = r"""
def execute(params, context):
    arr = context['array'].copy()
    n = len(arr)
    comparisons = 0
    
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        
        while j >= 0:
            comparisons += 1
            if key < arr[j]:
                arr[j + 1] = arr[j]
                j -= 1
            else:
                break
        arr[j + 1] = key
        
    return {
        'success': True,
        'sorted': arr,
        'comparisons': comparisons
    }
"""

# Define the list of initial algorithms to inject
INITIAL_ALGORITHMS = [
    {"name": "Bubble-Sort", "code": BUBBLE_SORT_CODE, "description": "Basic swapping sort"},
    {"name": "Selection-Sort", "code": SELECTION_SORT_CODE, "description": "Min-finding sort"},
    {"name": "Insertion-Sort", "code": INSERTION_SORT_CODE, "description": "Insert-into-sorted sort"}
]

# ---------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------

def sorting_context_factory_builder(size: int):
    """
    Returns a factory function that generates arrays of specific size.
    """
    def make():
        # Generate random integers between 0 and 1000
        return { 'array': np.random.randint(0, 1000, size).tolist() }
    return make

def sorting_evaluation_function(result, action):
    """
    Evaluate sorting algorithm.
    """
    # 1. Check basic success
    if not isinstance(result, dict) or not result.get('success'):
        return 0.0001

    # 2. Anti-Cheating: Check code for forbidden strings
    if hasattr(action, 'code'):
        code_lower = action.code.lower()
        
        # Standard forbidden libraries
        forbidden_patterns = [
            'sorted(', '.sort(', 'heapq', 'bisect', 'numpy', 'pandas'
        ]
        
        # [HARD MODE] Forbidden Algorithm Names - DISABLED for now
        # These were causing all GPT-generated algorithms to fail
        forbidden_names = [
            'merge', 'quick', 'heap', 'shell', 'tim', 'intro', 'radix', 'pivot', 'partition'
        ]
        
        for pattern in forbidden_patterns:
            if pattern in code_lower:
                return 0.0001 # Cheating with libraries

        for name in forbidden_names:
            if name in code_lower:
                return 0.0001 

    # 3. Check Correctness
    sorted_arr = result.get('sorted', [])
    if sorted_arr != sorted(sorted_arr):
        return 0.0001
    
    # 4. Check Comparison Count
    comparisons = result.get('comparisons', 0)
    
    if comparisons == 0 and len(sorted_arr) > 1:
        return 0.0001 

    # 5. Calculate Fitness (Efficiency)
    return 10000.0 / (1.0 + comparisons)

# ---------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    print("\nLENS: Dynamic Algorithm Discovery System")
    print("Target Problem: Sorting Problem")
    print("=" * 70)
    print("Experiment Configuration: Sorting_Optimization_Hard")
    
    # Get configuration from user
    generations = int(input("Generations [20]: ").strip() or "20")
    trials = int(input("Trials/Gen [5]: ").strip() or "5")
    problem_size = int(input("Problem Size [50]: ").strip() or "50")
    
    print(f"Generations: {generations} | Trials: {trials}")
    print(f"Problem Size: {problem_size} | Runs/Method: 1")
    print("=" * 70)
    
    # Initialize LENS
    lens = LENS(api_key=api_key, problem=PROBLEM_DESCRIPTION)
    
    # Add initial algorithms
    for algo in INITIAL_ALGORITHMS:
        lens.add_algorithm(
            name=algo['name'],
            code=algo['code'],
            description=algo.get('description', '')
        )
    
    # Create context generator
    context_gen = sorting_context_factory_builder(problem_size)
    
    # Run evolution
    lens.evolve(
        generations=generations,
        eval_fn=sorting_evaluation_function,
        context_gen=context_gen,
        n_trials=trials
    )
    
    # Print final result
    best = lens.get_best()
    print("\n" + "=" * 95)
    print(f"{'METHOD':<22} | {'SUCCESS':<7} | {'MEAN':<10} | {'STD':<10} | {'MIN':<10} | {'MAX':<10}")
    print("-" * 95)
    print(f"{'LENS (Full)':<22} | {'1/1':<7} | {best.fitness:<10.4f} | {'0.0000':<10} | {best.fitness:<10.4f} | {best.fitness:<10.4f}")
    print("=" * 95)
    
    print(f"\nCompleted: Best={best.name}, Fitness={best.fitness:.4f}")
    
    # Save results
    lens.save("lens_sorting_results.json")
