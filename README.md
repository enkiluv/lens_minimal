# LENS Minimal

**Learning, Evolution, and Natural Language Synthesis for Autonomous Algorithm Discovery**

A self-improving meta-architecture that autonomously discovers, evaluates, and evolves algorithms through the integration of Reinforcement Learning, Large Language Models, and Genetic Algorithms.

## Overview

LENS is a modular framework that decomposes algorithm discovery into three specialized components:

1. **RL Strategy Layer**: Q-learning agent that selects meta-level actions (generate new, improve best, or evolve) based on search progress
2. **LLM Synthesis Layer**: GPT-4o interface for creative algorithm generation and targeted improvement
3. **Evolution Layer**: Genetic operators for systematic refinement through crossover and selection

The key innovation is a **self-expanding action space** where newly discovered algorithms become available for future iterations, creating a persistent knowledge accumulation loop.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LENS Framework                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌───────────────┐      New/Improve      ┌─────────────────┐  │
│   │  RL Strategy  │ ──────────────────────▶ │  LLM Synthesis │  │
│   │  (Q-Learning) │                        │    (GPT-4o)     │  │
│   └───────┬───────┘                        └────────┬────────┘  │
│           │                                         │           │
│           │ Evolve                                  │ new algo  │
│           ▼                                         ▼           │
│   ┌───────────────┐                        ┌─────────────────┐  │
│   │   Evolution   │                        │    Evaluator    │  │
│   │ (Genetic Alg) │ ──────────────────────▶ │   (Sandbox)     │  │
│   └───────────────┘      refined algo      └────────┬────────┘  │
│                                                     │           │
│                          fitness scores             │           │
│   ┌─────────────────────────────────────────────────┘           │
│   │                                                             │
│   ▼                                                             │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              Algorithm Population (Persistent)          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

### Requirements

- Python 3.8+
- OpenAI API key

### Setup

```bash
# Clone or download the files
# Install dependencies
pip install openai numpy

# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Running the Sorting Example

```bash
# Interactive mode (prompts for configuration)
python sorting_example.py

# Default configuration (20 generations, 5 trials, 50 elements)
python sorting_example.py --default

# Custom configuration
python sorting_example.py -g 30 -t 10 -s 100
```

### Using LENS in Your Own Project

```python
from lens_minimal import LENS
import numpy as np

# Define your problem
PROBLEM = """
Your problem description here.
The algorithm must implement execute(params, context) function.
"""

# Define evaluation function
def evaluate(result, algorithm):
    if not result.get('success'):
        return 0.0
    # Your fitness calculation
    return result.get('score', 0.0)

# Define context generator
def context_generator():
    return {'data': np.random.rand(100).tolist()}

# Initialize LENS
lens = LENS(
    api_key="your-api-key",
    problem=PROBLEM,
    max_population=8
)

# Add baseline algorithms
lens.add_algorithm(
    name="baseline",
    code='''
def execute(params, context):
    # Your baseline implementation
    return {'success': True, 'score': 0.5}
''',
    description="Simple baseline"
)

# Run evolution
lens.evolve(
    generations=20,
    eval_fn=evaluate,
    context_gen=context_generator,
    n_trials=5
)

# Get best algorithm
best = lens.get_best()
print(f"Best: {best.name}, Fitness: {best.fitness}")

# Save results
lens.save("results.json")
```

## File Structure

```
lens_minimal/
├── lens_minimal.py      # Core LENS framework
├── sorting_example.py   # Complete sorting experiment
└── README.md           # This file
```

## Configuration Parameters

### LENS Initialization

| Parameter | Default | Description |
|-----------|---------|-------------|
| `api_key` | required | OpenAI API key |
| `problem` | required | Problem description for LLM |
| `max_population` | 8 | Maximum algorithms to maintain |
| `alpha` | 0.1 | RL learning rate |
| `gamma` | 0.9 | RL discount factor |
| `epsilon` | 0.2 | RL exploration rate |

### Evolution Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `generations` | - | Number of evolution cycles |
| `eval_fn` | - | Evaluation function |
| `context_gen` | - | Context generator function |
| `n_trials` | 5 | Trials per evaluation |

## Sorting Experiment Details

The sorting example demonstrates LENS evolving from O(n²) baseline algorithms toward more efficient solutions.

### Initial Algorithms
- Bubble Sort
- Selection Sort  
- Insertion Sort

### Fitness Function
```
fitness = 10000 / (1 + comparisons)
```
Higher fitness = fewer comparisons.

### Hard Mode Constraints
- Forbidden built-in functions: `sorted()`, `.sort()`, `heapq`, `bisect`
- Forbidden algorithm names: `merge`, `quick`, `heap`, `shell`, `tim`, `intro`, `radix`

This forces the LLM to implement efficient sorting logic without simply reproducing textbook algorithms.

## Expected Results

From the paper's experiments:

| Metric | Value |
|--------|-------|
| Baseline Fitness | ~15.77 (Insertion Sort) |
| Best Discovered | ~44-46 |
| Improvement | ~184% |

The system typically discovers divide-and-conquer structures similar to merge sort, but implemented without using standard algorithm names.

## Output

Results are saved to `lens_results/sorting_YYYYMMDD_HHMMSS/`:

- `lens_results.json`: Complete algorithm population with code
- `experiment_summary.json`: Experiment configuration and best result

### Sample Q-Table Output

```
Learned Q-Table:
------------------------------------------------------------
State (0, 0): generate=0.357 | improve_=0.000 | ga_evolu=0.000
State (0, 1): improve_=0.500 | generate=0.050 | ga_evolu=0.000
State (0, 2): improve_=0.236 | generate=0.000 | ga_evolu=0.000
------------------------------------------------------------
```

This shows the learned strategy:
- Early phase (0, 0): Prefer generating new algorithms
- Mid phase (0, 1): Prefer improving the best
- Late phase (0, 2): Continue refinement

## Extending LENS

### Adding New Problems

1. Define problem description (natural language)
2. Implement evaluation function
3. Create context generator
4. Add baseline algorithms
5. Run evolution

### Customizing the RL Agent

The `QLearningAgent` class can be modified for:
- Different state representations
- Custom reward functions
- Alternative action sets

## Citation

If you use LENS in your research, please cite:

```bibtex
@article{kim2025lens,
  title={LENS: A Self-Improving Meta-Architecture for Autonomous Algorithm Discovery 
         through Learning, Evolution, and Natural Language Synthesis},
  author={Kim, Myung Ho},
  journal={TechRxiv},
  year={2025}
}
```

## License

MIT License

## Acknowledgments

Based on the LENS paper demonstrating that intelligence can emerge from architectural composition rather than scale alone.
