"""
Mock LLM implementations for testing/demo purposes
"""
from typing import Dict, Any
import random
import time


def mock_llm_api_call(prompt: str, model_name: str = "gpt-4") -> Dict[str, Any]:
    """
    Mock LLM API call for testing/demo
    Simulates realistic token counts and latency
    """
    # Simulate latency (50-500ms)
    latency = random.uniform(0.05, 0.5)
    time.sleep(latency)
    
    # Simulate token counts based on prompt length
    prompt_tokens = max(5, len(prompt.split()) // 2)
    completion_tokens = random.randint(50, 200)
    
    # Mock response
    response_text = f"This is a mock response from {model_name} to: {prompt[:50]}..."
    
    return {
        "response": response_text,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "model": model_name,
    }


def mock_claude_api_call(prompt: str) -> Dict[str, Any]:
    """Mock Claude API call"""
    return mock_llm_api_call(prompt, model_name="claude-3-sonnet")


def mock_gpt4_api_call(prompt: str) -> Dict[str, Any]:
    """Mock GPT-4 API call"""
    return mock_llm_api_call(prompt, model_name="gpt-4")


def mock_haiku_api_call(prompt: str) -> Dict[str, Any]:
    """Mock Claude Haiku API call"""
    return mock_llm_api_call(prompt, model_name="claude-3-haiku")
