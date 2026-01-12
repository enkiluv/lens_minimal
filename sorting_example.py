"""
sorting_example.py

LENS Sorting Experiment - Autonomous algorithm discovery demonstration.

This script uses LENS to evolve sorting algorithms starting from O(n^2) baselines
(Bubble Sort, Selection Sort, Insertion Sort) with the goal of discovering more
efficient algorithms that minimize comparison operations.

Usage:
    export OPENAI_API_KEY="your-api-key"
    python sorting_example.py

*** HARD MODE ***
Forbidden algorithm names: 'merge', 'quick', 'heap', 'shell', 'tim', etc.
The AI must implement the LOGIC without using standard textbook names.
"""

import os
import sys
import numpy as np

from lens_minimal import LENS


# ============================================================
# PROBLEM DEFINITION
# ============================================================

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


# ============================================================
# INITIAL ALGORITHMS (O(n^2) Baselines)
# ============================================================

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

INITIAL_ALGORITHMS = [
    {"name": "Bubble-Sort", "code": BUBBLE_SORT_CODE, "description": "Basic swapping sort O(n^2)"},
    {"name": "Selection-Sort", "code": SELECTION_SORT_CODE, "description": "Min-finding sort O(n^2)"},
    {"name": "Insertion-Sort", "code": INSERTION_SORT_CODE, "description": "Insert-into-sorted sort O(n^2)"}
]


# ============================================================
# EVALUATION FUNCTIONS
# ============================================================

def create_context_generator(size: int):
    """Create a context generator that produces random arrays."""
    def generator():
        return {'array': np.random.randint(0, 1000, size).tolist()}
    return generator


def evaluate_sorting(result, algorithm):
    """Evaluate a sorting algorithm based on correctness and efficiency."""
    # 1. Check basic success
    if not isinstance(result, dict) or not result.get('success'):
        return 0.0001

    # 2. Anti-Cheating: Check code for forbidden patterns
    if hasattr(algorithm, 'code'):
        code_lower = algorithm.code.lower()
        
        forbidden_patterns = ['sorted(', '.sort(', 'heapq', 'bisect', 'numpy', 'pandas']
        forbidden_names = ['merge', 'quick', 'heap', 'shell', 'tim', 'intro', 'radix', 'pivot', 'partition']
        
        for pattern in forbidden_patterns:
            if pattern in code_lower:
                return 0.0001

        for name in forbidden_names:
            if name in code_lower:
                return 0.0001

    # 3. Check correctness
    sorted_arr = result.get('sorted', [])
    if sorted_arr != sorted(sorted_arr):
        return 0.0001
    
    # 4. Check comparison count validity
    comparisons = result.get('comparisons', 0)
    if comparisons == 0 and len(sorted_arr) > 1:
        return 0.0001

    # 5. Calculate fitness (fewer comparisons = higher fitness)
    return 10000.0 / (1.0 + comparisons)


# ============================================================
# MAIN
# ============================================================

def main():
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set")
        print("Please set it: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    # Configuration
    print("\n" + "=" * 70)
    print("LENS: Dynamic Algorithm Discovery System")
    print("Target Problem: Sorting Problem")
    print("=" * 70)
    
    generations = int(input("Generations [20]: ").strip() or "20")
    trials = int(input("Trials per generation [5]: ").strip() or "5")
    problem_size = int(input("Array size [50]: ").strip() or "50")
    
    print(f"\nConfiguration: {generations} generations, {trials} trials, size {problem_size}")
    print("=" * 70)
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Initialize LENS
    lens = LENS(
        api_key=api_key,
        problem=PROBLEM_DESCRIPTION,
        max_population=8
    )
    
    # Add initial algorithms
    for algo in INITIAL_ALGORITHMS:
        lens.add_algorithm(
            name=algo['name'],
            code=algo['code'],
            description=algo['description']
        )
    
    # Run evolution
    context_gen = create_context_generator(problem_size)
    
    lens.evolve(
        generations=generations,
        eval_fn=evaluate_sorting,
        context_gen=context_gen,
        n_trials=trials
    )
    
    # Save results
    lens.save("lens_sorting_results.json")
    
    print(f"\nCompleted: Best={lens.get_best().name}, Fitness={lens.get_best().fitness:.4f}")


if __name__ == "__main__":
    main()
