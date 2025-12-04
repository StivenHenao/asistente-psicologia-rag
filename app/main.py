from fastapi import FastAPI
from app.routes import auth_routes, context_routes, report_routes, user_routes, esp32_routes
from app.services.email.resend_email_service import ResendEmailService
import os

app = FastAPI(title="Voice Auth App")

email_service = ResendEmailService(
    api_key=os.getenv("RESEND_API_KEY"),
    sender=os.getenv("EMAIL_FROM")
)

#Guardar en app.state para acceder desde las rutas
app.state.email_service = email_service

app.include_router(user_routes.router, tags=["Users"])
app.include_router(auth_routes.router, tags=["Auth"])
app.include_router(context_routes.router, tags=["Context"])
app.include_router(report_routes.router, tags=["Reports"])
app.include_router(esp32_routes.router, tags=["ESP32"])
