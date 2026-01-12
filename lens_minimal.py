"""
LENS Minimal - 
Learning, Evolution, and Natural Language Synthesis for Autonomous Algorithm Discovery

A self-improving meta-architecture that integrates:
- Reinforcement Learning for adaptive action selection
- LLM (GPT-4o) for creative algorithm generation
- Genetic Algorithm for systematic refinement

Author: Based on the LENS paper
License: MIT
"""

import numpy as np
from typing import Dict, List, Callable, Optional
from openai import OpenAI
import json


class Algorithm:
    """Single algorithm with executable code."""
    
    def __init__(self, name: str, code: str, description: str = ""):
        self.name = name
        self.code = code
        self.description = description
        self.fitness = 0.0
        self.execute_fn = None
        
        # Compile code
        try:
            namespace = {}
            exec(code, namespace)
            self.execute_fn = namespace.get('execute')
        except Exception as e:
            print(f"Failed to compile {name}: {e}")
    
    def run(self, context: Dict) -> Dict:
        """Execute algorithm with given context."""
        if not self.execute_fn:
            return {'success': False}
        
        try:
            return self.execute_fn({}, context)
        except Exception as e:
            return {'success': False, 'error': str(e)}


class QLearningAgent:
    """Q-Learning agent for meta-level action selection."""
    
    def __init__(self, alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.q_table = {}
        self.actions = ['generate_new', 'improve_best', 'ga_evolution']
        self.prev_state = None
        self.prev_action = None
        self.fitness_history = []
    
    def get_state(self, current_fitness: float, generation: int) -> tuple:
        """
        Discretize search state into (stagnation_level, progress_level).
        
        stagnation_level: 0=improving, 1=plateau, 2=stagnant
        progress_level: 0=early, 1=mid, 2=late
        """
        self.fitness_history.append(current_fitness)
        
        # Determine stagnation level
        if len(self.fitness_history) < 3:
            stagnation = 0
        else:
            recent = self.fitness_history[-3:]
            improvement = max(recent) - min(recent)
            stagnation = 0 if improvement > 0.01 else (1 if improvement > 0.001 else 2)
        
        # Determine progress level based on generation
        progress = 0 if generation <= 5 else (1 if generation <= 15 else 2)
        
        return (stagnation, progress)
    
    def select_action(self, state: tuple) -> str:
        """Epsilon-greedy action selection."""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        
        if np.random.random() < self.epsilon:
            return np.random.choice(self.actions)
        else:
            q_values = self.q_table[state]
            max_q = max(q_values.values())
            best = [a for a, q in q_values.items() if q == max_q]
            return np.random.choice(best)
    
    def update(self, state: tuple, action: str, reward: float, next_state: tuple):
        """Q-Learning update rule."""
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}
        
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state].values())
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def get_reward(self, improvement: float) -> float:
        """Calculate reward based on fitness improvement."""
        if improvement > 0.1:
            return 1.0
        elif improvement > 0.01:
            return 0.5
        elif improvement > 0:
            return 0.1
        else:
            return -0.1


class LENS:
    """
    LENS: Learning, Evolution, and Natural Language Synthesis
    
    A self-improving meta-architecture for autonomous algorithm discovery.
    
    Usage:
        lens = LENS(api_key="your-openai-key", problem="problem description")
        lens.add_algorithm("baseline", code, "description")
        lens.evolve(generations=20, eval_fn=evaluate, context_gen=generator)
    """
    
    def __init__(self, api_key: str, problem: str, max_population: int = 8,
                 alpha: float = 0.1, gamma: float = 0.9, epsilon: float = 0.2):
        """
        Initialize LENS framework.
        
        Args:
            api_key: OpenAI API key
            problem: Natural language problem description
            max_population: Maximum algorithms to keep
            alpha: RL learning rate
            gamma: RL discount factor
            epsilon: RL exploration rate
        """
        self.client = OpenAI(api_key=api_key)
        self.problem = problem
        self.max_pop = max_population
        self.algorithms: List[Algorithm] = []
        self.generation = 0
        self.ga_counter = 0
        
        # Initialize RL agent
        self.rl_agent = QLearningAgent(alpha, gamma, epsilon)
        self.prev_fitness = 0.0
        
        print("LENS initialized")
        print(f"RL params: alpha={alpha}, gamma={gamma}, epsilon={epsilon}")
    
    def add_algorithm(self, name: str, code: str, description: str = ""):
        """Add an algorithm to the population."""
        algo = Algorithm(name, code, description)
        if algo.execute_fn:
            self.algorithms.append(algo)
            print(f"Added: {name}")
    
    def evaluate(self, eval_fn: Callable, context_gen: Callable, n_trials: int = 5):
        """Evaluate all algorithms over multiple trials."""
        for algo in self.algorithms:
            scores = []
            for _ in range(n_trials):
                result = algo.run(context_gen())
                scores.append(eval_fn(result, algo))
            algo.fitness = np.mean(scores) if scores else 0.0
    
    def get_best(self) -> Optional[Algorithm]:
        """Get the best algorithm by fitness."""
        return max(self.algorithms, key=lambda a: a.fitness) if self.algorithms else None
    
    def genetic_crossover(self) -> Optional[Algorithm]:
        """Create offspring through genetic crossover."""
        if len(self.algorithms) < 2:
            return None
        
        sorted_algos = sorted(self.algorithms, key=lambda a: a.fitness, reverse=True)
        parent1, parent2 = sorted_algos[0], sorted_algos[1]
        
        self.ga_counter += 1
        name = f"GA-{self.ga_counter}"
        code = parent1.code  # Simple crossover: inherit best parent's code
        desc = f"GA offspring #{self.ga_counter} from {parent1.name[:15]} x {parent2.name[:15]}"
        
        return Algorithm(name, code, desc)
    
    def generate_new_algorithm(self) -> Optional[Algorithm]:
        """Use LLM to generate a completely new algorithm."""
        best = self.get_best()
        best_info = f"Current best: {best.name} (fitness={best.fitness:.4f})" if best else "No algorithms yet"
        
        prompt = f"""Generate a new algorithm for this problem:

{self.problem}

{best_info}

Create a better algorithm. Return JSON:
{{
  "name": "algorithm-name",
  "description": "brief description",
  "code": "complete Python code with execute(params, context) function"
}}

The execute function must:
- Take params (dict) and context (dict)
- Return dict with at least 'success' key
- Handle all errors

Code only, no markdown.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert algorithm designer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            name = data.get('name', f'GPT-Gen-{self.generation}')
            code = data.get('code', '')
            desc = data.get('description', 'GPT-generated')
            
            # Clean code if wrapped in markdown
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            print(f"GPT-4o generated: {name}")
            return Algorithm(name, code, desc)
            
        except Exception as e:
            print(f"GPT-4o generation failed: {e}")
            return None
    
    def improve_best_algorithm(self) -> Optional[Algorithm]:
        """Use LLM to improve the current best algorithm."""
        best = self.get_best()
        if not best:
            return None
        
        prompt = f"""Improve this algorithm:

Name: {best.name}
Fitness: {best.fitness:.4f}

Code:
{best.code}

Problem: {self.problem}

Return JSON:
{{
  "name": "improved-name",
  "description": "what you improved",
  "code": "improved Python code"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at algorithm optimization."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            name = data.get('name', f'Improved-{best.name}')
            code = data.get('code', '')
            desc = data.get('description', 'Improved version')
            
            # Clean code if wrapped in markdown
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            print(f"GPT-4o improved: {name}")
            return Algorithm(name, code, desc)
            
        except Exception as e:
            print(f"GPT-4o improvement failed: {e}")
            return None
    
    def evolve(self, generations: int, eval_fn: Callable, context_gen: Callable,
               n_trials: int = 5):
        """
        Main evolution loop with RL-guided action selection.
        
        Args:
            generations: Number of generations to run
            eval_fn: Evaluation function (result, algorithm) -> fitness
            context_gen: Context generator function () -> context dict
            n_trials: Number of trials per evaluation
        """
        print(f"\nStarting RL evolution: {generations} generations")
        print("=" * 60)
        
        for gen in range(generations):
            self.generation = gen + 1
            
            # Evaluate all algorithms
            self.evaluate(eval_fn, context_gen, n_trials)
            best = self.get_best()
            current_fitness = best.fitness if best else 0.0
            
            print(f"\nGeneration {self.generation}/{generations}")
            
            # Get state and select action via RL
            state = self.rl_agent.get_state(current_fitness, self.generation)
            action = self.rl_agent.select_action(state)
            
            print(f"State: {state} | Action: {action}")
            print(f"Best: {best.name if best else 'None'} (fitness={current_fitness:.4f})")
            
            # Execute selected action
            new_algo = None
            if action == 'generate_new':
                print("[RL->GPT] Generating new...")
                new_algo = self.generate_new_algorithm()
            elif action == 'improve_best':
                print("[RL->GPT] Improving best...")
                new_algo = self.improve_best_algorithm()
            elif action == 'ga_evolution':
                print("[RL->GA] Crossover...")
                new_algo = self.genetic_crossover()
            
            # Add new algorithm if valid
            if new_algo and new_algo.execute_fn:
                self.algorithms.append(new_algo)
            
            # Update RL agent
            improvement = current_fitness - self.prev_fitness
            reward = self.rl_agent.get_reward(improvement)
            
            if self.rl_agent.prev_state is not None:
                self.rl_agent.update(
                    self.rl_agent.prev_state, 
                    self.rl_agent.prev_action, 
                    reward, 
                    state
                )
            
            self.rl_agent.prev_state = state
            self.rl_agent.prev_action = action
            self.prev_fitness = current_fitness
            
            # Prune population if too large
            if len(self.algorithms) > self.max_pop:
                self.algorithms.sort(key=lambda a: a.fitness, reverse=True)
                self.algorithms = self.algorithms[:self.max_pop]
        
        # Print final results
        print("\n" + "=" * 60)
        print("Evolution complete!")
        
        if self.rl_agent.q_table:
            print("\nLearned Q-Table:")
            print("-" * 60)
            for state, actions in sorted(self.rl_agent.q_table.items()):
                print(f"State {state}: ", end="")
                sorted_actions = sorted(actions.items(), key=lambda x: x[1], reverse=True)
                print(" | ".join([f"{a[:8]}={q:.3f}" for a, q in sorted_actions]))
            print("-" * 60)
        
        best = self.get_best()
        if best:
            print(f"\nBest algorithm: {best.name}")
            print(f"Fitness: {best.fitness:.4f}")
            print(f"Description: {best.description}")
            
            print(f"\n{'=' * 60}")
            print(f"Code for {best.name}:")
            print("=" * 60)
            print(best.code)
            print("=" * 60)
    
    def save(self, filename: str):
        """Save results to JSON file."""
        data = {
            'generation': self.generation,
            'algorithms': [
                {
                    'name': a.name, 
                    'fitness': float(a.fitness), 
                    'description': a.description, 
                    'code': a.code
                }
                for a in sorted(self.algorithms, key=lambda x: x.fitness, reverse=True)
            ]
        }
        
        if self.rl_agent:
            data['q_table'] = {
                str(state): actions 
                for state, actions in self.rl_agent.q_table.items()
            }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Results saved to {filename}")


if __name__ == "__main__":
    print("LENS Minimal Framework")
    print("=" * 40)
    print("\nUsage:")
    print("  from lens_minimal import LENS")
    print("  lens = LENS(api_key='...', problem='...')")
    print("  lens.add_algorithm('Name', code, 'description')")
    print("  lens.evolve(generations=20, eval_fn=eval, context_gen=gen)")
    print("\nSee sorting_example.py for a complete example.")
