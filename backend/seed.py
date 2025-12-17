"""
Seed the database with demo LLM call logs for charts.
Run: <venv_python> seed.py (use your venv's python executable)
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Ensure relative imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from models import LLMCallLog, CostLog, LLMModel, User

DAYS = int(os.getenv("SEED_DAYS", "30"))
PER_DAY = int(os.getenv("SEED_PER_DAY", "40"))
USER_EMAIL = os.getenv("SEED_USER", "admin@example.com")


def main():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == USER_EMAIL).first()
        if not user:
            print(f"User {USER_EMAIL} not found")
            return

        models = db.query(LLMModel).all()
        if not models:
            print("No LLM models found. Seed models first from main.py startup.")
            return

        total_created = 0
        now = datetime.utcnow()

        for d in range(DAYS):
            day_dt = now - timedelta(days=d)
            for _ in range(PER_DAY):
                model = random.choice(models)
                prompt_tokens = random.randint(50, 800)
                completion_tokens = random.randint(20, 1200)
                total_tokens = prompt_tokens + completion_tokens
                latency_ms = max(20, int(random.gauss(250, 120)))
                status = "success" if random.random() > 0.08 else "error"
                error_message = None if status == "success" else random.choice([
                    "timeout", "rate_limit", "invalid_request", "provider_error"
                ])

                log_entry = LLMCallLog(
                    user_id=user.id,
                    model_id=model.id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    total_tokens=total_tokens,
                    latency_ms=float(latency_ms),
                    status=status,
                    error_message=error_message,
                    prompt_preview="Explain quantum computing",
                    response_preview="Quantum computing uses qubits...",
                    created_at=day_dt,
                )
                db.add(log_entry)
                db.flush()

                estimated_cost = (total_tokens / 1000.0) * float(model.cost_per_1k_tokens)
                db.add(CostLog(
                    llm_call_id=log_entry.id,
                    estimated_cost=estimated_cost,
                    created_at=day_dt,
                ))
                total_created += 1

            db.commit()
            print(f"Created {PER_DAY} logs for {day_dt.date()}")

        print(f"\nSeed complete: {total_created} logs across {DAYS} days for {USER_EMAIL}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
