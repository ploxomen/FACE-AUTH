from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routers import register, login

app = FastAPI(
    title="Facial Authentication API",
    description="Sistema de autenticación facial con pgvector",
    version="1.0.0"
)

# Configuración de templates
templates = Jinja2Templates(directory="app/templates")

# Ruta para el formulario de registro
@app.get("/register-page", response_class=HTMLResponse)
async def show_register_form(request: Request):
    return templates.TemplateResponse(request=request, name="register.html", context={"request": request})

@app.get("/")
def read_root():
    return {"message": "Facial Authentication API is running"}

# Incluir routers
app.include_router(register.router)
app.include_router(login.router)