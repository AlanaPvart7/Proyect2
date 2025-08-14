import uvicorn
import logging
from fastapi import FastAPI, Request

# Routers
from routes.catalogtypes import router as catalogtypes_router
from routes.catalogs import router as catalogs_router
from routes.order_statuses import router as order_statuses_router
from routes.orders import router as orders_router
from routes.order_details import router as order_details_router
from routes.inventory import router as inventory_router
from routes.artist import router as artist_router
from routes.reviews import router as reviews_router

# Controllers para usuarios
from controllers.users import create_user, login
from models.users import User
from models.login import Login
from utils.security import validateuser, validateadmin

# Inicializar app
app = FastAPI()

# Configuración CORS
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(catalogtypes_router)
app.include_router(catalogs_router)
app.include_router(order_statuses_router)
app.include_router(orders_router)
app.include_router(order_details_router)
app.include_router(inventory_router)
app.include_router(artist_router)
app.include_router(reviews_router)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rutas raíz y checks de salud
@app.get("/")
def read_root():
    return {"status": "healthy", "version": "0.0.0", "service": "tienda-api"}

@app.get("/health")
def health_check():
    try:
        return {
            "status": "healthy", 
            "timestamp": "2025-08-02", 
            "service": "tienda-api",
            "environment": "production"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/ready")
def readiness_check():
    try:
        from utils.mongodb import test_connection
        db_status = test_connection()
        return {
            "status": "ready" if db_status else "not_ready",
            "database": "connected" if db_status else "disconnected",
            "service": "tienda-api"
        }
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}

# Endpoints de usuarios
@app.post("/users")
async def create_user_endpoint(user: User) -> User:
    return await create_user(user)

@app.post("/login")
async def login_access(l: Login) -> dict:
    return await login(l)

# Ejemplo de endpoint que requiere admin
@app.get("/exampleadmin")
@validateadmin
async def example_admin(request: Request):
    return {
        "message": "This is an example admin endpoint.",
        "admin": request.state.admin
    }

# Ejemplo de endpoint que requiere usuario autenticado
@app.get("/exampleuser")
@validateuser
async def example_user(request: Request):
    return {
        "message": "This is an example user endpoint.",
        "email": request.state.email
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
