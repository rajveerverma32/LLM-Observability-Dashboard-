"""
LLM Call Observability Wrapper - Measures and persists LLM call metrics
This wrapper is the core of the observability system
"""
import time
from datetime import datetime
from typing import Optional, Callable, Any, Dict
from sqlalchemy.orm import Session
from models import LLMCallLog, CostLog, LLMModel, User
import logging

logger = logging.getLogger(__name__)


class LLMObservabilityWrapper:
    """
    Wraps LLM API calls to measure performance metrics and persist them to database
    
    Example usage:
        wrapper = LLMObservabilityWrapper(db, user_id, model_id)
        result = wrapper.call_llm(llm_api_function, prompt)
    """
    
    def __init__(self, db: Session, user_id: int, model_id: int):
        self.db = db
        self.user_id = user_id
        self.model_id = model_id
        self.start_time = None
        self.end_time = None
        
    def call_llm(
        self,
        llm_function: Callable,
        prompt: str,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute LLM function with observability metrics
        
        Args:
            llm_function: The LLM API function to call (e.g., OpenAI, Anthropic, etc.)
            prompt: The input prompt
            *args, **kwargs: Additional arguments for the LLM function
        
        Returns:
            Dictionary containing the LLM response and metrics
        """
        self.start_time = time.time()
        
        try:
            # Call the LLM function
            response = llm_function(prompt, *args, **kwargs)
            
            self.end_time = time.time()
            
            # Extract metrics from response
            latency_ms = (self.end_time - self.start_time) * 1000
            prompt_tokens = response.get("prompt_tokens", 0)
            completion_tokens = response.get("completion_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens
            
            # Persist to database
            log_entry = self._log_successful_call(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                prompt_preview=prompt[:500],
                response_preview=response.get("response", "")[:500]
            )
            
            # Calculate and log cost
            self._log_cost(log_entry, total_tokens)
            
            return {
                "success": True,
                "response": response.get("response"),
                "metrics": {
                    "latency_ms": latency_ms,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "estimated_cost": self._calculate_cost(total_tokens)
                },
                "log_id": log_entry.id
            }
            
        except Exception as e:
            self.end_time = time.time()
            latency_ms = (self.end_time - self.start_time) * 1000
            
            # Log error
            self._log_error(
                latency_ms=latency_ms,
                error_message=str(e)
            )
            
            logger.error(f"LLM call failed: {str(e)}")
            
            return {
                "success": False,
                "error": str(e),
                "metrics": {
                    "latency_ms": latency_ms,
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0.0
                }
            }
    
    def _log_successful_call(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        latency_ms: float,
        prompt_preview: str,
        response_preview: str
    ) -> LLMCallLog:
        """Log successful LLM call to database"""
        
        log_entry = LLMCallLog(
            user_id=self.user_id,
            model_id=self.model_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_ms=latency_ms,
            status="success",
            prompt_preview=prompt_preview,
            response_preview=response_preview,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def _log_error(
        self,
        latency_ms: float,
        error_message: str
    ) -> LLMCallLog:
        """Log failed LLM call to database"""
        
        log_entry = LLMCallLog(
            user_id=self.user_id,
            model_id=self.model_id,
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            latency_ms=latency_ms,
            status="error",
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        
        return log_entry
    
    def _calculate_cost(self, total_tokens: int) -> float:
        """Calculate estimated cost for the LLM call"""
        model = self.db.query(LLMModel).filter(LLMModel.id == self.model_id).first()
        if not model:
            return 0.0
        
        # Cost = (tokens / 1000) * cost_per_1k_tokens
        return (total_tokens / 1000) * model.cost_per_1k_tokens
    
    def _log_cost(self, log_entry: LLMCallLog, total_tokens: int) -> None:
        """Log cost information to database"""
        estimated_cost = self._calculate_cost(total_tokens)
        
        cost_log = CostLog(
            llm_call_id=log_entry.id,
            estimated_cost=estimated_cost,
            created_at=datetime.utcnow()
        )
        
        self.db.add(cost_log)
        self.db.commit()


def create_observability_wrapper(
    db: Session,
    user_id: int,
    model_id: int
) -> LLMObservabilityWrapper:
    """Factory function to create observability wrapper"""
    return LLMObservabilityWrapper(db, user_id, model_id)
