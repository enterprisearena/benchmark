#!/usr/bin/env python3
"""
EnterpriseArena Task Runner

Main script for running EnterpriseArena evaluations across single-platform
and cross-platform tasks.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional

# Add the parent directory to the path to import enterprise_sandbox
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from enterprise_sandbox.data.assets import (
    get_all_tasks,
    get_tasks_by_platform,
    get_tasks_by_category,
    ALL_SINGLE_PLATFORM_TASKS,
    ALL_CROSS_PLATFORM_TASKS,
    TASK_CATEGORIES
)

def setup_logging(log_dir: str) -> None:
    """Set up logging directory."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

def load_checkpoint(checkpoint_path: str) -> Dict[int, dict]:
    """Load completed tasks from checkpoint file."""
    completed_tasks = {}
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, 'r') as f:
                results = json.load(f)
                completed_tasks = {task['task_id']: task for task in results}
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not load checkpoint: {e}")
    return completed_tasks

def save_result(checkpoint_path: str, result: dict) -> None:
    """Save a single result to the checkpoint file."""
    results = []
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            results = json.load(f)
    
    results.append(result)
    
    with open(checkpoint_path, 'w') as f:
        json.dump(results, f, indent=2)

def run_single_platform_evaluation(
    platform: str,
    tasks: List[dict],
    model: str,
    agent_strategy: str,
    max_turns: int,
    log_dir: str,
    reuse_results: bool = False
) -> None:
    """Run evaluation for single-platform tasks."""
    print(f"Running {platform} single-platform evaluation...")
    print(f"Model: {model}, Strategy: {agent_strategy}")
    print(f"Tasks: {len(tasks)}")
    
    checkpoint_path = f"{log_dir}/results_{model}_{agent_strategy}_{platform}_single.json"
    
    # Load completed tasks
    completed_tasks = {}
    if reuse_results:
        completed_tasks = load_checkpoint(checkpoint_path)
    
    start_time = datetime.now()
    print(f"Starting evaluation at {start_time}")
    
    for task in tasks:
        task_id = task['idx']
        
        # Skip if already completed
        if task_id in completed_tasks:
            print(f"Skipping task {task_id} (already completed)")
            continue
        
        print(f"Running task {task_id}: {task['task']}")
        
        try:
            # TODO: Implement actual agent execution
            # For now, simulate a result
            result = {
                "task_id": task_id,
                "task_type": task['task'],
                "platform": platform,
                "query": task['query'],
                "gt_answer": task['answer'],
                "reward": 1,  # Simulate success
                "agent_info": {
                    "model": model,
                    "strategy": agent_strategy,
                    "platform": platform
                },
                "traj": [{"role": "assistant", "content": "Simulated response"}],
                "execution_time": 1.5,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Task {task_id} completed successfully")
            
        except Exception as e:
            print(f"❌ Task {task_id} failed: {e}")
            result = {
                "task_id": task_id,
                "task_type": task['task'],
                "platform": platform,
                "query": task['query'],
                "gt_answer": task['answer'],
                "reward": 0,
                "agent_info": {
                    "model": model,
                    "strategy": agent_strategy,
                    "platform": platform,
                    "error": str(e)
                },
                "traj": [],
                "execution_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Save result
        save_result(checkpoint_path, result)
        time.sleep(1)  # Rate limiting
    
    end_time = datetime.now()
    print(f"Finished evaluation at {end_time}")
    print(f"Total time: {end_time - start_time}")

def run_cross_platform_evaluation(
    category: str,
    tasks: List[dict],
    model: str,
    agent_strategy: str,
    max_turns: int,
    log_dir: str,
    reuse_results: bool = False
) -> None:
    """Run evaluation for cross-platform tasks."""
    print(f"Running {category} cross-platform evaluation...")
    print(f"Model: {model}, Strategy: {agent_strategy}")
    print(f"Tasks: {len(tasks)}")
    
    checkpoint_path = f"{log_dir}/results_{model}_{agent_strategy}_{category}_cross.json"
    
    # Load completed tasks
    completed_tasks = {}
    if reuse_results:
        completed_tasks = load_checkpoint(checkpoint_path)
    
    start_time = datetime.now()
    print(f"Starting evaluation at {start_time}")
    
    for task in tasks:
        task_id = task['idx']
        
        # Skip if already completed
        if task_id in completed_tasks:
            print(f"Skipping task {task_id} (already completed)")
            continue
        
        print(f"Running task {task_id}: {task['task']}")
        print(f"Platforms: {', '.join(task.get('platforms', []))}")
        
        try:
            # TODO: Implement actual cross-platform agent execution
            # For now, simulate a result
            result = {
                "task_id": task_id,
                "task_type": task['task'],
                "category": category,
                "platforms": task.get('platforms', []),
                "query": task['query'],
                "gt_answer": task['answer'],
                "reward": 1,  # Simulate success
                "agent_info": {
                    "model": model,
                    "strategy": agent_strategy,
                    "category": category,
                    "platforms": task.get('platforms', [])
                },
                "traj": [{"role": "assistant", "content": "Simulated cross-platform response"}],
                "execution_time": 3.2,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"✅ Task {task_id} completed successfully")
            
        except Exception as e:
            print(f"❌ Task {task_id} failed: {e}")
            result = {
                "task_id": task_id,
                "task_type": task['task'],
                "category": category,
                "platforms": task.get('platforms', []),
                "query": task['query'],
                "gt_answer": task['answer'],
                "reward": 0,
                "agent_info": {
                    "model": model,
                    "strategy": agent_strategy,
                    "category": category,
                    "platforms": task.get('platforms', []),
                    "error": str(e)
                },
                "traj": [],
                "execution_time": 0,
                "timestamp": datetime.now().isoformat()
            }
        
        # Save result
        save_result(checkpoint_path, result)
        time.sleep(1)  # Rate limiting
    
    end_time = datetime.now()
    print(f"Finished evaluation at {end_time}")
    print(f"Total time: {end_time - start_time}")

def main():
    parser = argparse.ArgumentParser(description="EnterpriseArena Task Runner")
    
    # Task selection
    parser.add_argument(
        "--task_type",
        type=str,
        choices=["single_platform", "cross_platform", "all"],
        default="all",
        help="Type of tasks to run"
    )
    
    parser.add_argument(
        "--platform",
        type=str,
        choices=["salesforce", "servicenow", "netsuite", "quickbooks"],
        help="Platform for single-platform tasks"
    )
    
    parser.add_argument(
        "--category",
        type=str,
        choices=["financial_integration", "customer_service", "sales_support", "data_sync"],
        help="Category for cross-platform tasks"
    )
    
    parser.add_argument(
        "--task_name",
        type=str,
        help="Specific task name to run"
    )
    
    # Agent configuration
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="LLM model to use"
    )
    
    parser.add_argument(
        "--agent_strategy",
        type=str,
        choices=["react", "act", "tool_call", "orchestration"],
        default="react",
        help="Agent strategy to use"
    )
    
    parser.add_argument(
        "--max_turns",
        type=int,
        default=20,
        help="Maximum number of turns per task"
    )
    
    # Evaluation settings
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Use interactive tasks"
    )
    
    parser.add_argument(
        "--reuse_results",
        action="store_true",
        help="Reuse results from previous runs"
    )
    
    parser.add_argument(
        "--log_dir",
        type=str,
        default="logs",
        help="Directory to save logs and results"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_dir)
    
    # Get tasks based on arguments
    tasks = []
    
    if args.task_type == "single_platform":
        if args.platform:
            tasks = get_tasks_by_platform(args.platform, args.interactive)
        else:
            tasks = ALL_SINGLE_PLATFORM_TASKS
    elif args.task_type == "cross_platform":
        if args.category:
            tasks = get_tasks_by_category(args.category, args.interactive)
        else:
            tasks = ALL_CROSS_PLATFORM_TASKS
    else:  # all
        tasks = get_all_tasks(interactive=args.interactive)
    
    # Filter by specific task name if provided
    if args.task_name:
        tasks = [task for task in tasks if task['task'] == args.task_name]
    
    if not tasks:
        print("No tasks found matching the criteria.")
        return
    
    print(f"Found {len(tasks)} tasks to run")
    
    # Run evaluation
    if args.task_type == "single_platform":
        platform = args.platform or "mixed"
        run_single_platform_evaluation(
            platform=platform,
            tasks=tasks,
            model=args.model,
            agent_strategy=args.agent_strategy,
            max_turns=args.max_turns,
            log_dir=args.log_dir,
            reuse_results=args.reuse_results
        )
    elif args.task_type == "cross_platform":
        category = args.category or "mixed"
        run_cross_platform_evaluation(
            category=category,
            tasks=tasks,
            model=args.model,
            agent_strategy=args.agent_strategy,
            max_turns=args.max_turns,
            log_dir=args.log_dir,
            reuse_results=args.reuse_results
        )
    else:  # all
        # Run both single-platform and cross-platform
        single_platform_tasks = [task for task in tasks if 'platforms' not in task]
        cross_platform_tasks = [task for task in tasks if 'platforms' in task]
        
        if single_platform_tasks:
            run_single_platform_evaluation(
                platform="mixed",
                tasks=single_platform_tasks,
                model=args.model,
                agent_strategy=args.agent_strategy,
                max_turns=args.max_turns,
                log_dir=args.log_dir,
                reuse_results=args.reuse_results
            )
        
        if cross_platform_tasks:
            run_cross_platform_evaluation(
                category="mixed",
                tasks=cross_platform_tasks,
                model=args.model,
                agent_strategy=args.agent_strategy,
                max_turns=args.max_turns,
                log_dir=args.log_dir,
                reuse_results=args.reuse_results
            )

if __name__ == "__main__":
    main()
