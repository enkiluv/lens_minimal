# LENS Minimal

**Learning, Evolution, and Natural Language Synthesis for Autonomous Algorithm Discovery**

A self-improving meta-architecture that autonomously discovers, evaluates, and evolves algorithms through the integration of Reinforcement Learning, Large Language Models, and Genetic Algorithms.

## Overview

LENS decomposes algorithm discovery into three specialized components:

1. **RL Strategy Layer**: Q-learning agent that selects meta-level actions based on search progress
2. **LLM Synthesis Layer**: GPT-4o for creative algorithm generation and improvement
3. **Evolution Layer**: Genetic operators for systematic refinement

## Installation

```bash
pip install openai numpy
export OPENAI_API_KEY="your-api-key"
```

## Quick Start

```bash
python sorting_example.py
```

## Files

- `lens_minimal.py` - Core LENS framework
- `sorting_example.py` - Sorting experiment example

## Usage

```python
from lens_minimal import LENS

lens = LENS(api_key="...", problem="your problem description")
lens.add_algorithm("baseline", code, "description")
lens.evolve(generations=20, eval_fn=evaluate, context_gen=generator)

best = lens.get_best()
lens.save("results.json")
```

## License

MIT
