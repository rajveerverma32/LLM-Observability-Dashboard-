"""
Main FastAPI application - LLM Observability Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import database and models
from db import engine, Base
from models import User, LLMModel, LLMCallLog, CostLog, Feedback, SystemSettings

# Import routes
from routes import auth, llm, metrics, feedback, settings

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="LLM Observability Dashboard API",
    description="Enterprise-grade observability system for LLM applications",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(llm.router)
app.include_router(metrics.router)
app.include_router(feedback.router)
app.include_router(settings.router)


@app.get("/", tags=["health"])
async def root():
    """Root endpoint - API health check"""
    return {
        "status": "healthy",
        "service": "LLM Observability Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "LLM Observability Dashboard Backend"
    }


def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="LLM Observability Dashboard API",
        version="1.0.0",
        description="Enterprise-grade observability system for LLM applications",
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Database initialization function
def init_db():
    """Initialize database with seed data"""
    from db import SessionLocal
    from models import User, LLMModel, SystemSettings, RoleEnum
    from auth.jwt import hash_password
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        admin_user = db.query(User).filter(User.email == "admin@company.com").first()
        if not admin_user:
            admin_user = User(
                email="admin@company.com",
                password_hash=hash_password("admin123"),
                role=RoleEnum.ADMIN
            )
            db.add(admin_user)
            print("[OK] Created admin user: admin@company.com / admin123")
        
        # Check if user already exists
        user_user = db.query(User).filter(User.email == "user@company.com").first()
        if not user_user:
            user_user = User(
                email="user@company.com",
                password_hash=hash_password("user123"),
                role=RoleEnum.VIEWER
            )
            db.add(user_user)
            print("[OK] Created user: user@company.com / user123")
        
        # Add default LLM models
        models_to_add = [
            ("gpt-4", "OpenAI", 0.03),
            ("gpt-3.5-turbo", "OpenAI", 0.001),
            ("claude-3-sonnet", "Anthropic", 0.003),
            ("claude-3-haiku", "Anthropic", 0.00025),
            ("claude-3-opus", "Anthropic", 0.015),
        ]
        
        for name, provider, cost in models_to_add:
            existing = db.query(LLMModel).filter(LLMModel.name == name).first()
            if not existing:
                model = LLMModel(
                    name=name,
                    provider=provider,
                    cost_per_1k_tokens=cost
                )
                db.add(model)
                print(f"[OK] Added LLM model: {name} ({provider})")
        
        # Create default system settings
        settings = db.query(SystemSettings).first()
        if not settings:
            settings = SystemSettings(
                claude_haiku_45_enabled=False,
                max_tokens_per_request=4096,
                enable_caching=True
            )
            db.add(settings)
            print("[OK] Created default system settings")
        
        db.commit()
        
        # Seed demo LLM logs for both users if no logs exist
        from models import LLMCallLog, CostLog
        from datetime import datetime, timedelta
        import random
        
        # Check if demo data already seeded
        existing_logs = db.query(LLMCallLog).first()
        if not existing_logs:
            print("\n[SEED] Seeding demo LLM call logs...")
            
            # Get users and models
            admin_user = db.query(User).filter(User.email == "admin@company.com").first()
            user_user = db.query(User).filter(User.email == "user@company.com").first()
            models = db.query(LLMModel).all()
            
            if admin_user and user_user and models:
                total_created = 0
                now = datetime.utcnow()
                
                # Seed for both users
                for user in [admin_user, user_user]:
                    for d in range(30):
                        day_dt = now - timedelta(days=d)
                        for _ in range(25):  # 25 logs per day
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
                
                print(f"[OK] Seeded {total_created} demo logs for 2 users (admin & user)")
        
        print("\n[OK] Database initialization complete!")
        
    except Exception as e:
        print(f"[ERROR] Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    
    # Initialize database on startup
    init_db()
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
