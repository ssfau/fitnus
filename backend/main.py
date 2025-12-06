from fastapi import FastAPI 
from backend.db import Base, engine
from backend.routers.nutrition import router as nutrition_router
from backend.routers.workout import router as workout_router
from backend.settings import router as settings_router

app = FastAPI(openapi_prefix="/api")

Base.metadata.create_all(bind=engine)

app.include_router(nutrition_router, prefix="/nutrition")
app.include_router(workout_router, prefix="/workouts")
app.include_router(settings_router, prefix="/settings")

# Local development run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

@app.get("/health")
def root_health():
    return {"Hello":"Health check positive"}

@app.get("/")
def homepage_quickreturn():
    return {"Hello":"Homepage quick return"}