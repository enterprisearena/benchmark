"""
Agent Utilities

This module provides utility functions and classes for agent implementations.
"""

import logging
import re
import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class AgentUtils:
    """Utility class for agent operations."""
    
    @staticmethod
    def parse_action_from_message(message: str) -> Optional[Dict[str, Any]]:
        """
        Parse action information from agent message.
        
        Args:
            message: Agent message to parse
            
        Returns:
            Parsed action dictionary if found, None otherwise
        """
        try:
            # Look for action patterns
            action_patterns = [
                r"Action:\s*(.+)",
                r"ACTION:\s*(.+)",
                r"action:\s*(.+)",
                r"```json\s*(\{.*?\})\s*```",
                r"```\s*(\{.*?\})\s*```"
            ]
            
            for pattern in action_patterns:
                match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
                if match:
                    action_text = match.group(1).strip()
                    
                    # Try to parse as JSON
                    try:
                        return json.loads(action_text)
                    except json.JSONDecodeError:
                        # If not JSON, treat as simple action
                        return {"action": action_text}
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse action from message: {e}")
            return None
    
    @staticmethod
    def extract_thought_from_message(message: str) -> Optional[str]:
        """
        Extract thought/reasoning from agent message.
        
        Args:
            message: Agent message to parse
            
        Returns:
            Extracted thought if found, None otherwise
        """
        try:
            # Look for thought patterns
            thought_patterns = [
                r"Thought:\s*(.+?)(?=Action:|$)",
                r"THOUGHT:\s*(.+?)(?=ACTION:|$)",
                r"thought:\s*(.+?)(?=action:|$)",
                r"Reasoning:\s*(.+?)(?=Action:|$)",
                r"REASONING:\s*(.+?)(?=ACTION:|$)"
            ]
            
            for pattern in thought_patterns:
                match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract thought from message: {e}")
            return None
    
    @staticmethod
    def extract_observation_from_message(message: str) -> Optional[str]:
        """
        Extract observation from agent message.
        
        Args:
            message: Agent message to parse
            
        Returns:
            Extracted observation if found, None otherwise
        """
        try:
            # Look for observation patterns
            observation_patterns = [
                r"Observation:\s*(.+?)(?=Thought:|Action:|$)",
                r"OBSERVATION:\s*(.+?)(?=THOUGHT:|ACTION:|$)",
                r"observation:\s*(.+?)(?=thought:|action:|$)",
                r"Result:\s*(.+?)(?=Thought:|Action:|$)",
                r"RESULT:\s*(.+?)(?=THOUGHT:|ACTION:|$)"
            ]
            
            for pattern in observation_patterns:
                match = re.search(pattern, message, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to extract observation from message: {e}")
            return None
    
    @staticmethod
    def format_reward_calculation(reward: float, details: Dict[str, Any] = None) -> str:
        """
        Format reward calculation for display.
        
        Args:
            reward: Calculated reward
            details: Optional reward calculation details
            
        Returns:
            Formatted reward string
        """
        if details:
            components = []
            for key, value in details.items():
                if isinstance(value, (int, float)):
                    components.append(f"{key}: {value:.2f}")
                else:
                    components.append(f"{key}: {value}")
            
            return f"Reward: {reward:.2f} ({', '.join(components)})"
        else:
            return f"Reward: {reward:.2f}"
    
    @staticmethod
    def validate_agent_response(response: str, max_length: int = 4000) -> Dict[str, Any]:
        """
        Validate agent response.
        
        Args:
            response: Agent response to validate
            max_length: Maximum allowed response length
            
        Returns:
            Validation result dictionary
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "length": len(response)
        }
        
        if not response or not response.strip():
            result["valid"] = False
            result["errors"].append("Empty response")
        
        if len(response) > max_length:
            result["valid"] = False
            result["errors"].append(f"Response too long: {len(response)} > {max_length}")
        
        # Check for potential issues
        if len(response) > max_length * 0.8:
            result["warnings"].append("Response approaching length limit")
        
        # Check for common issues
        if "error" in response.lower() and "success" not in response.lower():
            result["warnings"].append("Response may contain error information")
        
        return result
    
    @staticmethod
    def calculate_conversation_metrics(messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Calculate conversation metrics.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Dictionary containing conversation metrics
        """
        if not messages:
            return {
                "total_messages": 0,
                "user_messages": 0,
                "assistant_messages": 0,
                "total_characters": 0,
                "average_message_length": 0,
                "conversation_duration": 0
            }
        
        user_messages = sum(1 for msg in messages if msg.get("role") == "user")
        assistant_messages = sum(1 for msg in messages if msg.get("role") == "assistant")
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        
        return {
            "total_messages": len(messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_characters": total_chars,
            "average_message_length": total_chars / len(messages) if messages else 0,
            "conversation_duration": 0  # Would need timestamps to calculate
        }
    
    @staticmethod
    def generate_conversation_id(messages: List[Dict[str, str]]) -> str:
        """
        Generate a unique ID for a conversation.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Unique conversation ID
        """
        # Create a hash of the conversation content
        content = json.dumps(messages, sort_keys=True)
        conversation_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"conv_{timestamp}_{conversation_hash}"
    
    @staticmethod
    def extract_keywords(text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            min_length: Minimum keyword length
            
        Returns:
            List of keywords
        """
        # Simple keyword extraction - can be enhanced
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if len(word) >= min_length]
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'
        }
        
        keywords = [word for word in keywords if word not in stop_words]
        
        return list(set(keywords))  # Remove duplicates
    
    @staticmethod
    def calculate_response_quality(response: str, expected_keywords: List[str] = None) -> Dict[str, Any]:
        """
        Calculate response quality metrics.
        
        Args:
            response: Agent response
            expected_keywords: Optional list of expected keywords
            
        Returns:
            Dictionary containing quality metrics
        """
        metrics = {
            "length": len(response),
            "word_count": len(response.split()),
            "sentence_count": len(re.split(r'[.!?]+', response)),
            "has_question": '?' in response,
            "has_exclamation": '!' in response,
            "keyword_coverage": 0.0
        }
        
        if expected_keywords:
            response_keywords = AgentUtils.extract_keywords(response)
            matched_keywords = set(response_keywords) & set(expected_keywords)
            metrics["keyword_coverage"] = len(matched_keywords) / len(expected_keywords) if expected_keywords else 0.0
        
        return metrics
    
    @staticmethod
    def format_agent_log(agent_info: Dict[str, Any], action: str, details: Dict[str, Any] = None) -> str:
        """
        Format agent log entry.
        
        Args:
            agent_info: Agent information dictionary
            action: Action being logged
            details: Optional action details
            
        Returns:
            Formatted log string
        """
        log_parts = [
            f"Agent({agent_info.get('agent_type', 'unknown')})",
            f"Model({agent_info.get('model', 'unknown')})",
            f"Turn({agent_info.get('current_turn', 0)})",
            f"Action({action})"
        ]
        
        if details:
            detail_str = ", ".join(f"{k}={v}" for k, v in details.items())
            log_parts.append(f"Details({detail_str})")
        
        return " | ".join(log_parts)
    
    @staticmethod
    def sanitize_agent_input(text: str) -> str:
        """
        Sanitize agent input text.
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove potentially harmful content
        sanitized = text.strip()
        
        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove control characters
        sanitized = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', sanitized)
        
        return sanitized
    
    @staticmethod
    def create_agent_summary(agent_info: Dict[str, Any], execution_stats: Dict[str, Any]) -> str:
        """
        Create a summary of agent execution.
        
        Args:
            agent_info: Agent information
            execution_stats: Execution statistics
            
        Returns:
            Agent execution summary
        """
        summary_parts = [
            f"Agent Type: {agent_info.get('agent_type', 'unknown')}",
            f"Model: {agent_info.get('model', 'unknown')}",
            f"Strategy: {agent_info.get('strategy', 'unknown')}",
            f"Turns: {execution_stats.get('total_steps', 0)}/{agent_info.get('max_turns', 0)}",
            f"Execution Time: {execution_stats.get('total_execution_time', 0):.2f}s"
        ]
        
        if 'tool_calls' in execution_stats:
            summary_parts.append(f"Tool Calls: {execution_stats['tool_calls']}")
        
        if 'messages' in execution_stats:
            summary_parts.append(f"Messages: {execution_stats['messages']}")
        
        return " | ".join(summary_parts)
