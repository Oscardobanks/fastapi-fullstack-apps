from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import create_db_and_tables
from .routers import products, cart, users
from .middleware import ResponseTimeMiddleware

# Create FastAPI app
app = FastAPI(title="Online Store API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for this project
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom response time middleware
app.add_middleware(ResponseTimeMiddleware)

# Include routers
app.include_router(products.router, prefix="/products", tags=["products"])
app.include_router(products.admin_router, prefix="/admin", tags=["admin"])
app.include_router(cart.router, prefix="/cart", tags=["cart"])
app.include_router(users.router, prefix="/auth", tags=["authentication"])

# Create database tables on startup


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Health check endpoint


@app.get("/")
def root():
    return {"message": "Online Store API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
