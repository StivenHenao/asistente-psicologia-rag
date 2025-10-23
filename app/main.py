from fastapi import FastAPI
from app.routes import auth_routes, user_routes, context_routes

app = FastAPI(title="Voice Auth App")

app.include_router(user_routes.router, tags=["Users"])
app.include_router(auth_routes.router, tags=["Auth"])
app.include_router(context_routes.router,tags=["Context"])
