"""
Single Platform Evaluator

This module implements evaluation for single-platform tasks and agents.
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..metrics.accuracy import AccuracyMetrics
from ..metrics.efficiency import EfficiencyMetrics
from ..metrics.error_handling import ErrorHandlingMetrics

logger = logging.getLogger(__name__)


class SinglePlatformEvaluator:
    """
    Evaluator for single-platform tasks and agents.
    
    This class provides comprehensive evaluation capabilities for tasks that
    operate within a single enterprise software platform.
    """
    
    def __init__(self, model: str, provider: str = "openai"):
        """
        Initialize the single-platform evaluator.
        
        Args:
            model: LLM model to use for evaluation
            provider: LLM provider to use
        """
        self.model = model
        self.provider = provider
        
        # Initialize metric calculators
        self.accuracy_metrics = AccuracyMetrics()
        self.efficiency_metrics = EfficiencyMetrics()
        self.error_handling_metrics = ErrorHandlingMetrics()
        
        logger.info(f"Initialized single-platform evaluator with model {model}")
    
    def evaluate_task(self, task: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, float]:
        """
        Evaluate a single-platform task execution.
        
        Args:
            task: Task definition
            execution_result: Result of task execution
            
        Returns:
            Dict containing evaluation metrics
        """
        try:
            evaluation_start = datetime.now()
            
            # Calculate different types of metrics
            accuracy_score = self._calculate_completion_rate(task, execution_result)
            efficiency_score = self._calculate_efficiency(task, execution_result)
            error_handling_score = self._calculate_error_handling(task, execution_result)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                accuracy_score, efficiency_score, error_handling_score
            )
            
            evaluation_time = (datetime.now() - evaluation_start).total_seconds()
            
            metrics = {
                "accuracy": accuracy_score,
                "efficiency": efficiency_score,
                "error_handling": error_handling_score,
                "overall_score": overall_score,
                "evaluation_time": evaluation_time
            }
            
            logger.debug(f"Task evaluation completed in {evaluation_time:.2f}s")
            return metrics
            
        except Exception as e:
            logger.error(f"Task evaluation failed: {e}")
            return {
                "accuracy": 0.0,
                "efficiency": 0.0,
                "error_handling": 0.0,
                "overall_score": 0.0,
                "evaluation_time": 0.0,
                "error": str(e)
            }
    
    def _calculate_completion_rate(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Calculate task completion rate.
        
        Args:
            task: Task definition
            result: Execution result
            
        Returns:
            float: Completion rate (0.0 to 1.0)
        """
        try:
            # Check if task was completed successfully
            if not result.get("success", False):
                return 0.0
            
            # Get expected answer
            expected_answer = task.get("answer")
            if not expected_answer:
                # If no expected answer, check if any data was returned
                return 1.0 if result.get("data") else 0.0
            
            # Get actual result data
            actual_data = result.get("data", [])
            
            # Calculate accuracy based on reward metric
            reward_metric = task.get("reward_metric", "exact_match")
            
            if reward_metric == "exact_match":
                return self.accuracy_metrics.calculate_exact_match(expected_answer, actual_data)
            elif reward_metric == "partial_match":
                return self.accuracy_metrics.calculate_partial_match(expected_answer, actual_data)
            elif reward_metric == "contains":
                return self.accuracy_metrics.calculate_contains(expected_answer, actual_data)
            elif reward_metric == "fuzzy_match":
                return self.accuracy_metrics.calculate_fuzzy_match(expected_answer, actual_data)
            else:
                # Default to exact match
                return self.accuracy_metrics.calculate_exact_match(expected_answer, actual_data)
                
        except Exception as e:
            logger.error(f"Completion rate calculation failed: {e}")
            return 0.0
    
    def _calculate_efficiency(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Calculate task execution efficiency.
        
        Args:
            task: Task definition
            result: Execution result
            
        Returns:
            float: Efficiency score (0.0 to 1.0)
        """
        try:
            execution_time = result.get("execution_time", 0.0)
            steps_taken = result.get("steps_taken", 0)
            
            # Calculate time efficiency
            time_efficiency = self.efficiency_metrics.calculate_time_efficiency(
                execution_time, task.get("timeout_seconds", 300)
            )
            
            # Calculate step efficiency
            step_efficiency = self.efficiency_metrics.calculate_step_efficiency(
                steps_taken, task.get("max_steps", 20)
            )
            
            # Calculate resource efficiency
            resource_efficiency = self.efficiency_metrics.calculate_resource_efficiency(
                result.get("resource_usage", {})
            )
            
            # Combine efficiency metrics
            overall_efficiency = (time_efficiency + step_efficiency + resource_efficiency) / 3.0
            
            return min(1.0, max(0.0, overall_efficiency))
            
        except Exception as e:
            logger.error(f"Efficiency calculation failed: {e}")
            return 0.0
    
    def _calculate_error_handling(self, task: Dict[str, Any], result: Dict[str, Any]) -> float:
        """
        Calculate error handling score.
        
        Args:
            task: Task definition
            result: Execution result
            
        Returns:
            float: Error handling score (0.0 to 1.0)
        """
        try:
            # Check for errors
            has_errors = not result.get("success", False)
            error_message = result.get("error_message", "")
            
            if not has_errors:
                return 1.0  # No errors, perfect score
            
            # Calculate error recovery score
            recovery_score = self.error_handling_metrics.calculate_recovery_score(
                error_message, result.get("recovery_attempts", 0)
            )
            
            # Calculate graceful degradation score
            degradation_score = self.error_handling_metrics.calculate_graceful_degradation(
                result.get("partial_results", [])
            )
            
            # Calculate error communication score
            communication_score = self.error_handling_metrics.calculate_error_communication(
                error_message
            )
            
            # Combine error handling metrics
            overall_error_handling = (recovery_score + degradation_score + communication_score) / 3.0
            
            return min(1.0, max(0.0, overall_error_handling))
            
        except Exception as e:
            logger.error(f"Error handling calculation failed: {e}")
            return 0.0
    
    def _calculate_overall_score(self, accuracy: float, efficiency: float, error_handling: float) -> float:
        """
        Calculate overall evaluation score.
        
        Args:
            accuracy: Accuracy score
            efficiency: Efficiency score
            error_handling: Error handling score
            
        Returns:
            float: Overall score (0.0 to 1.0)
        """
        # Weighted combination of metrics
        weights = {
            "accuracy": 0.5,      # 50% weight on accuracy
            "efficiency": 0.3,    # 30% weight on efficiency
            "error_handling": 0.2  # 20% weight on error handling
        }
        
        overall_score = (
            accuracy * weights["accuracy"] +
            efficiency * weights["efficiency"] +
            error_handling * weights["error_handling"]
        )
        
        return min(1.0, max(0.0, overall_score))
    
    def evaluate_agent_performance(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate overall agent performance across multiple tasks.
        
        Args:
            agent_results: List of agent execution results
            
        Returns:
            Dict containing performance metrics
        """
        try:
            if not agent_results:
                return {
                    "total_tasks": 0,
                    "success_rate": 0.0,
                    "average_accuracy": 0.0,
                    "average_efficiency": 0.0,
                    "average_error_handling": 0.0,
                    "average_overall_score": 0.0
                }
            
            # Calculate aggregate metrics
            total_tasks = len(agent_results)
            successful_tasks = sum(1 for result in agent_results if result.get("success", False))
            success_rate = successful_tasks / total_tasks
            
            # Calculate average scores
            accuracy_scores = [result.get("accuracy", 0.0) for result in agent_results]
            efficiency_scores = [result.get("efficiency", 0.0) for result in agent_results]
            error_handling_scores = [result.get("error_handling", 0.0) for result in agent_results]
            overall_scores = [result.get("overall_score", 0.0) for result in agent_results]
            
            average_accuracy = sum(accuracy_scores) / len(accuracy_scores)
            average_efficiency = sum(efficiency_scores) / len(efficiency_scores)
            average_error_handling = sum(error_handling_scores) / len(error_handling_scores)
            average_overall_score = sum(overall_scores) / len(overall_scores)
            
            # Calculate additional metrics
            execution_times = [result.get("execution_time", 0.0) for result in agent_results]
            average_execution_time = sum(execution_times) / len(execution_times)
            
            steps_taken = [result.get("steps_taken", 0) for result in agent_results]
            average_steps = sum(steps_taken) / len(steps_taken)
            
            return {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": success_rate,
                "average_accuracy": average_accuracy,
                "average_efficiency": average_efficiency,
                "average_error_handling": average_error_handling,
                "average_overall_score": average_overall_score,
                "average_execution_time": average_execution_time,
                "average_steps": average_steps,
                "performance_grade": self._calculate_performance_grade(average_overall_score)
            }
            
        except Exception as e:
            logger.error(f"Agent performance evaluation failed: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_grade(self, overall_score: float) -> str:
        """
        Calculate performance grade based on overall score.
        
        Args:
            overall_score: Overall evaluation score
            
        Returns:
            str: Performance grade (A, B, C, D, F)
        """
        if overall_score >= 0.9:
            return "A"
        elif overall_score >= 0.8:
            return "B"
        elif overall_score >= 0.7:
            return "C"
        elif overall_score >= 0.6:
            return "D"
        else:
            return "F"
    
    def compare_agents(self, agent_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Compare performance of multiple agents.
        
        Args:
            agent_results: Dictionary mapping agent names to their results
            
        Returns:
            Dict containing comparison metrics
        """
        try:
            comparison = {}
            
            for agent_name, results in agent_results.items():
                performance = self.evaluate_agent_performance(results)
                comparison[agent_name] = performance
            
            # Find best performing agent
            best_agent = max(comparison.keys(), key=lambda k: comparison[k]["average_overall_score"])
            
            comparison["best_agent"] = best_agent
            comparison["best_score"] = comparison[best_agent]["average_overall_score"]
            
            return comparison
            
        except Exception as e:
            logger.error(f"Agent comparison failed: {e}")
            return {"error": str(e)}
    
    def generate_evaluation_report(self, evaluation_results: List[Dict[str, Any]], 
                                 output_file: str = None) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report.
        
        Args:
            evaluation_results: List of evaluation results
            output_file: Optional output file path
            
        Returns:
            Dict containing evaluation report
        """
        try:
            # Calculate summary statistics
            total_evaluations = len(evaluation_results)
            successful_evaluations = sum(1 for r in evaluation_results if r.get("success", False))
            
            # Calculate average metrics
            metrics = ["accuracy", "efficiency", "error_handling", "overall_score"]
            averages = {}
            for metric in metrics:
                values = [r.get(metric, 0.0) for r in evaluation_results]
                averages[metric] = sum(values) / len(values) if values else 0.0
            
            # Generate report
            report = {
                "evaluation_summary": {
                    "total_evaluations": total_evaluations,
                    "successful_evaluations": successful_evaluations,
                    "success_rate": successful_evaluations / total_evaluations if total_evaluations > 0 else 0.0,
                    "average_metrics": averages
                },
                "detailed_results": evaluation_results,
                "generated_at": datetime.now().isoformat()
            }
            
            # Save to file if specified
            if output_file:
                import json
                with open(output_file, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                logger.info(f"Evaluation report saved to {output_file}")
            
            return report
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e)}
