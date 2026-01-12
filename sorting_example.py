"""
sorting_example.py

LENS Sorting Experiment - A complete example demonstrating autonomous algorithm discovery.

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
import json
import datetime
import numpy as np
from pathlib import Path

# Import LENS framework
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
    """
    Create a context generator that produces random arrays of given size.
    
    Args:
        size: Array size for sorting tests
        
    Returns:
        A function that generates context dictionaries
    """
    def generator():
        return {'array': np.random.randint(0, 1000, size).tolist()}
    return generator


def evaluate_sorting(result, algorithm):
    """
    Evaluate a sorting algorithm based on correctness and efficiency.
    
    Args:
        result: Dictionary returned by the algorithm's execute function
        algorithm: The Algorithm object (for code inspection)
        
    Returns:
        Fitness score (higher is better)
    """
    # 1. Check basic success
    if not isinstance(result, dict) or not result.get('success'):
        return 0.0001

    # 2. Anti-Cheating: Check code for forbidden patterns
    if hasattr(algorithm, 'code'):
        code_lower = algorithm.code.lower()
        
        # Forbidden library functions
        forbidden_patterns = [
            'sorted(', '.sort(', 'heapq', 'bisect', 'numpy', 'pandas'
        ]
        
        # Forbidden algorithm names (HARD MODE)
        forbidden_names = [
            'merge', 'quick', 'heap', 'shell', 'tim', 'intro', 'radix', 'pivot', 'partition'
        ]
        
        for pattern in forbidden_patterns:
            if pattern in code_lower:
                return 0.0001  # Cheating with libraries

        for name in forbidden_names:
            if name in code_lower:
                return 0.0001  # Using textbook names

    # 3. Check correctness
    sorted_arr = result.get('sorted', [])
    if sorted_arr != sorted(sorted_arr):
        return 0.0001  # Incorrect sorting
    
    # 4. Check comparison count validity
    comparisons = result.get('comparisons', 0)
    if comparisons == 0 and len(sorted_arr) > 1:
        return 0.0001  # Invalid: didn't count comparisons

    # 5. Calculate fitness (fewer comparisons = higher fitness)
    return 10000.0 / (1.0 + comparisons)


# ============================================================
# EXPERIMENT RUNNER
# ============================================================

class SortingExperiment:
    """Runner for LENS sorting experiments."""
    
    def __init__(self, output_dir: str = "lens_results"):
        self.output_dir = Path(output_dir)
        
    def run(self, config: dict) -> dict:
        """
        Run a single LENS experiment.
        
        Args:
            config: Dictionary with keys:
                - generations: Number of generations
                - trials: Trials per evaluation
                - problem_size: Array size
                - seed: Random seed
                
        Returns:
            Result dictionary with experiment outcomes
        """
        # Check API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("ERROR: OPENAI_API_KEY environment variable not set")
            print("Please set it: export OPENAI_API_KEY='your-key'")
            sys.exit(1)
        
        # Set random seed
        np.random.seed(config.get('seed', 42))
        
        # Create output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = self.output_dir / f"sorting_{timestamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        print("\n" + "=" * 70)
        print("LENS: Dynamic Algorithm Discovery System")
        print("Target Problem: Sorting Problem")
        print("=" * 70)
        print(f"Experiment Configuration:")
        print(f"  Generations: {config['generations']}")
        print(f"  Trials/Gen: {config['trials']}")
        print(f"  Problem Size: {config['problem_size']}")
        print(f"  Output: {run_dir}")
        print("=" * 70)
        
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
        
        # Create context generator
        context_gen = create_context_generator(config['problem_size'])
        
        # Run evolution
        lens.evolve(
            generations=config['generations'],
            eval_fn=evaluate_sorting,
            context_gen=context_gen,
            n_trials=config['trials']
        )
        
        # Get results
        best = lens.get_best()
        result = {
            'success': best is not None,
            'best_name': best.name if best else None,
            'best_fitness': float(best.fitness) if best else 0.0,
            'best_code': best.code if best else None,
            'config': config,
            'timestamp': timestamp
        }
        
        # Save results
        lens.save(str(run_dir / "lens_results.json"))
        
        with open(run_dir / "experiment_summary.json", 'w') as f:
            json.dump(result, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 95)
        print(f"{'METHOD':<22} | {'SUCCESS':<7} | {'MEAN':<10} | {'STD':<10} | {'MIN':<10} | {'MAX':<10}")
        print("-" * 95)
        print(f"{'LENS (Full)':<22} | {'1/1':<7} | {best.fitness:<10.4f} | {'0.0000':<10} | {best.fitness:<10.4f} | {best.fitness:<10.4f}")
        print("=" * 95)
        
        print(f"\nCompleted: Best={best.name}, Fitness={best.fitness:.4f}")
        print(f"Results saved to: {run_dir}")
        
        return result


def run_interactive():
    """Run interactive experiment configuration."""
    print("\n" + "=" * 70)
    print("LENS Sorting Experiment - Interactive Mode")
    print("=" * 70)
    
    print("\n--- Configuration ---")
    generations = int(input("Generations [20]: ").strip() or "20")
    trials = int(input("Trials per generation [5]: ").strip() or "5")
    problem_size = int(input("Array size [50]: ").strip() or "50")
    seed = int(input("Random seed [42]: ").strip() or "42")
    
    config = {
        'generations': generations,
        'trials': trials,
        'problem_size': problem_size,
        'seed': seed
    }
    
    experiment = SortingExperiment()
    experiment.run(config)


def run_default():
    """Run experiment with default configuration."""
    config = {
        'generations': 20,
        'trials': 5,
        'problem_size': 50,
        'seed': 42
    }
    
    experiment = SortingExperiment()
    experiment.run(config)


# ============================================================
# MAIN ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="LENS Sorting Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python sorting_example.py                    # Interactive mode
    python sorting_example.py --default          # Run with defaults
    python sorting_example.py -g 30 -t 10 -s 100 # Custom config
        """
    )
    
    parser.add_argument('--default', '-d', action='store_true',
                        help='Run with default configuration')
    parser.add_argument('--generations', '-g', type=int, default=20,
                        help='Number of generations (default: 20)')
    parser.add_argument('--trials', '-t', type=int, default=5,
                        help='Trials per evaluation (default: 5)')
    parser.add_argument('--size', '-s', type=int, default=50,
                        help='Array size for sorting (default: 50)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed (default: 42)')
    
    args = parser.parse_args()
    
    if args.default:
        run_default()
    elif len(sys.argv) > 1 and not args.default:
        # Custom configuration from command line
        config = {
            'generations': args.generations,
            'trials': args.trials,
            'problem_size': args.size,
            'seed': args.seed
        }
        experiment = SortingExperiment()
        experiment.run(config)
    else:
        # Interactive mode
        run_interactive()
