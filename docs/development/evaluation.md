# Evaluation Guide

This guide covers how to run evaluations, interpret results, and analyze agent performance in EnterpriseArena.

## Running Evaluations

### Basic Usage

#### Single-Platform Evaluation
```bash
python scripts/run_enterprise_arena.py \
    --task_type single_platform \
    --platform salesforce \
    --model gpt-4o \
    --agent_strategy react
```

#### Cross-Platform Evaluation
```bash
python scripts/run_enterprise_arena.py \
    --task_type cross_platform \
    --category financial_integration \
    --model gpt-4o \
    --agent_strategy orchestration
```

#### All Tasks
```bash
python scripts/run_enterprise_arena.py \
    --task_type all \
    --model gpt-4o \
    --agent_strategy react
```

### Advanced Options

#### Interactive Tasks
```bash
python scripts/run_enterprise_arena.py \
    --task_type single_platform \
    --platform salesforce \
    --interactive \
    --max_user_turns 10
```

#### Specific Task
```bash
python scripts/run_enterprise_arena.py \
    --task_type single_platform \
    --platform salesforce \
    --task_name lead_management
```

#### Custom Configuration
```bash
python scripts/run_enterprise_arena.py \
    --task_type all \
    --model gpt-4o \
    --agent_strategy react \
    --max_turns 30 \
    --log_dir results/experiment_1 \
    --reuse_results
```

## Command Line Arguments

### Task Selection
- `--task_type`: Type of tasks to run (`single_platform`, `cross_platform`, `all`)
- `--platform`: Platform for single-platform tasks (`salesforce`, `servicenow`, `netsuite`, `quickbooks`)
- `--category`: Category for cross-platform tasks (`financial_integration`, `customer_service`, `sales_support`, `data_sync`)
- `--task_name`: Specific task name to run
- `--interactive`: Use interactive tasks (multi-turn conversations)

### Agent Configuration
- `--model`: LLM model to use (`gpt-4o`, `gpt-4-turbo`, `claude-3-opus`, etc.)
- `--agent_strategy`: Agent strategy (`react`, `act`, `tool_call`, `orchestration`)
- `--max_turns`: Maximum number of turns per task
- `--max_user_turns`: Maximum user turns for interactive tasks

### Evaluation Settings
- `--log_dir`: Directory to save logs and results
- `--reuse_results`: Reuse results from previous runs
- `--timeout`: Timeout for task execution (seconds)

## Understanding Results

### Result Structure

Each task execution produces a result with the following structure:

```json
{
    "task_id": 1,
    "task_type": "lead_management",
    "platform": "salesforce",
    "query": "Find all leads created in the last 30 days...",
    "gt_answer": ["John Smith, john.smith@email.com"],
    "reward": 1,
    "agent_info": {
        "model": "gpt-4o",
        "strategy": "react",
        "platform": "salesforce",
        "total_cost": 0.05,
        "num_turns": 3
    },
    "traj": [
        {"role": "assistant", "content": "<thought>I need to query leads...</thought>"},
        {"role": "assistant", "content": "<execute>SELECT Name, Email FROM Lead...</execute>"},
        {"role": "assistant", "content": "<respond>John Smith, john.smith@email.com</respond>"}
    ],
    "execution_time": 2.5,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Key Metrics

#### Success Rate
```python
def calculate_success_rate(results: List[Dict]) -> float:
    successful_tasks = sum(1 for r in results if r["reward"] == 1)
    return successful_tasks / len(results)
```

#### Average Execution Time
```python
def calculate_avg_execution_time(results: List[Dict]) -> float:
    total_time = sum(r["execution_time"] for r in results)
    return total_time / len(results)
```

#### Cost Analysis
```python
def calculate_total_cost(results: List[Dict]) -> float:
    return sum(r["agent_info"].get("total_cost", 0) for r in results)
```

## Analyzing Results

### Loading Results

```python
import json
import pandas as pd

def load_results(log_dir: str, experiment_name: str) -> pd.DataFrame:
    """Load results from JSON files"""
    results = []
    
    # Load all result files
    for file in glob.glob(f"{log_dir}/results_{experiment_name}_*.json"):
        with open(file, 'r') as f:
            results.extend(json.load(f))
    
    return pd.DataFrame(results)
```

### Performance Analysis

```python
def analyze_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze agent performance across tasks"""
    analysis = {
        "overall_success_rate": df["reward"].mean(),
        "avg_execution_time": df["execution_time"].mean(),
        "total_cost": df["agent_info"].apply(lambda x: x.get("total_cost", 0)).sum(),
        "tasks_by_platform": df.groupby("platform")["reward"].agg(["count", "mean"]),
        "tasks_by_type": df.groupby("task_type")["reward"].agg(["count", "mean"]),
        "error_analysis": df[df["reward"] == 0]["agent_info"].apply(lambda x: x.get("error", "Unknown"))
    }
    
    return analysis
```

### Cross-Platform Analysis

```python
def analyze_cross_platform_performance(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze cross-platform task performance"""
    cross_platform_tasks = df[df["task_type"].str.contains("cross_platform", na=False)]
    
    analysis = {
        "cross_platform_success_rate": cross_platform_tasks["reward"].mean(),
        "platform_coordination_success": cross_platform_tasks.groupby("platforms")["reward"].mean(),
        "workflow_completion_rate": cross_platform_tasks["reward"].mean(),
        "step_success_analysis": analyze_step_success(cross_platform_tasks)
    }
    
    return analysis
```

## Visualization

### Success Rate by Platform

```python
import matplotlib.pyplot as plt
import seaborn as sns

def plot_success_by_platform(df: pd.DataFrame):
    """Plot success rate by platform"""
    platform_success = df.groupby("platform")["reward"].mean()
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=platform_success.index, y=platform_success.values)
    plt.title("Success Rate by Platform")
    plt.ylabel("Success Rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
```

### Execution Time Distribution

```python
def plot_execution_time_distribution(df: pd.DataFrame):
    """Plot execution time distribution"""
    plt.figure(figsize=(12, 6))
    
    plt.subplot(1, 2, 1)
    plt.hist(df["execution_time"], bins=30, alpha=0.7)
    plt.title("Execution Time Distribution")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Frequency")
    
    plt.subplot(1, 2, 2)
    sns.boxplot(data=df, x="platform", y="execution_time")
    plt.title("Execution Time by Platform")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
```

### Cost Analysis

```python
def plot_cost_analysis(df: pd.DataFrame):
    """Plot cost analysis"""
    df["cost"] = df["agent_info"].apply(lambda x: x.get("total_cost", 0))
    
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 3, 1)
    plt.scatter(df["execution_time"], df["cost"], alpha=0.6)
    plt.xlabel("Execution Time (s)")
    plt.ylabel("Cost ($)")
    plt.title("Cost vs Execution Time")
    
    plt.subplot(1, 3, 2)
    cost_by_platform = df.groupby("platform")["cost"].sum()
    plt.pie(cost_by_platform.values, labels=cost_by_platform.index, autopct='%1.1f%%')
    plt.title("Cost Distribution by Platform")
    
    plt.subplot(1, 3, 3)
    sns.barplot(data=df, x="platform", y="cost")
    plt.title("Average Cost by Platform")
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.show()
```

## Benchmarking

### Model Comparison

```python
def compare_models(results_dir: str) -> pd.DataFrame:
    """Compare performance across different models"""
    model_results = []
    
    for model in ["gpt-4o", "gpt-4-turbo", "claude-3-opus"]:
        model_df = load_results(results_dir, f"*{model}*")
        if not model_df.empty:
            model_results.append({
                "model": model,
                "success_rate": model_df["reward"].mean(),
                "avg_time": model_df["execution_time"].mean(),
                "total_cost": model_df["agent_info"].apply(lambda x: x.get("total_cost", 0)).sum()
            })
    
    return pd.DataFrame(model_results)
```

### Strategy Comparison

```python
def compare_strategies(results_dir: str) -> pd.DataFrame:
    """Compare performance across different agent strategies"""
    strategy_results = []
    
    for strategy in ["react", "act", "tool_call", "orchestration"]:
        strategy_df = load_results(results_dir, f"*{strategy}*")
        if not strategy_df.empty:
            strategy_results.append({
                "strategy": strategy,
                "success_rate": strategy_df["reward"].mean(),
                "avg_turns": strategy_df["agent_info"].apply(lambda x: x.get("num_turns", 0)).mean(),
                "avg_time": strategy_df["execution_time"].mean()
            })
    
    return pd.DataFrame(strategy_results)
```

## Reporting

### Generate Report

```python
def generate_evaluation_report(results_dir: str, output_file: str):
    """Generate comprehensive evaluation report"""
    df = load_results(results_dir, "*")
    
    report = {
        "summary": {
            "total_tasks": len(df),
            "successful_tasks": df["reward"].sum(),
            "success_rate": df["reward"].mean(),
            "total_execution_time": df["execution_time"].sum(),
            "total_cost": df["agent_info"].apply(lambda x: x.get("total_cost", 0)).sum()
        },
        "by_platform": df.groupby("platform")["reward"].agg(["count", "mean"]).to_dict(),
        "by_task_type": df.groupby("task_type")["reward"].agg(["count", "mean"]).to_dict(),
        "performance_metrics": {
            "avg_execution_time": df["execution_time"].mean(),
            "median_execution_time": df["execution_time"].median(),
            "execution_time_std": df["execution_time"].std()
        }
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
```

### Export Results

```python
def export_results_to_csv(df: pd.DataFrame, output_file: str):
    """Export results to CSV for further analysis"""
    # Flatten agent_info for CSV export
    df_export = df.copy()
    df_export["model"] = df_export["agent_info"].apply(lambda x: x.get("model", ""))
    df_export["strategy"] = df_export["agent_info"].apply(lambda x: x.get("strategy", ""))
    df_export["cost"] = df_export["agent_info"].apply(lambda x: x.get("total_cost", 0))
    df_export["turns"] = df_export["agent_info"].apply(lambda x: x.get("num_turns", 0))
    
    # Drop the nested agent_info column
    df_export = df_export.drop("agent_info", axis=1)
    
    df_export.to_csv(output_file, index=False)
```

## Best Practices

### Experiment Design
- Use consistent evaluation parameters across experiments
- Run multiple trials for statistical significance
- Document experimental conditions and assumptions
- Compare against baseline models

### Result Interpretation
- Consider task difficulty and complexity
- Account for platform-specific limitations
- Analyze error patterns and failure modes
- Look for systematic biases or issues

### Performance Optimization
- Monitor resource usage and costs
- Optimize prompts and strategies
- Use appropriate model sizes for tasks
- Implement caching where beneficial

### Reproducibility
- Use version control for experiments
- Document all configuration parameters
- Save random seeds for reproducibility
- Archive results and analysis code