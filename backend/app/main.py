from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.websockets import WebSocket
from typing import List, Optional
import logging

# Core Imports
from app.core.config import Settings, get_settings
from app.core.security import (
    setup_security,
    create_access_token,
    verify_token,
    get_current_user,
    verify_password,
    get_password_hash
)
from app.core.database import (
    setup_database,
    get_db,
    SessionLocal,
    engine
)
from app.core.risk import (
    RiskManager,
    calculate_position_size,
    validate_trade_risk
)

# API Routes Imports
from app.api.v1.auth.routes import auth_router
from app.api.v1.trading.routes import (
    orders_router,
    positions_router,
    portfolio_router
)
from app.api.v1.signals.routes import signals_router

# Exchange Imports
from app.exchanges.binance.spot.client import BinanceSpotClient
from app.exchanges.binance.futures.client import BinanceFuturesClient
from app.exchanges.binance.utils.auth import validate_api_keys

# WebSocket Handlers
from app.websockets.market_data.binance_stream import BinanceWebsocketManager
from app.websockets.market_data.price_feed import setup_price_feeds

# Services
from app.services.trading.order_manager import OrderManager
from app.services.trading.position_manager import PositionManager
from app.services.trading.portfolio_manager import PortfolioManager

# Models
from app.models.order import Order, OrderCreate
from app.models.position import Position, PositionCreate
from app.models.trade import Trade, TradeCreate

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Settings
settings = get_settings()

# Initialize FastAPI App
app = FastAPI(
    title="Trading Bot API",
    description="Automated Trading Platform with Signal Integration",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = setup_security(app)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.price_feeds = {}
        self.binance_ws_manager = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                await self.disconnect(connection)

manager = ConnectionManager()

# Startup Events
@app.on_event("startup")
async def startup_event():
    try:
        # Initialize Database
        await setup_database()
        
        # Initialize Exchange Clients
        app.state.spot_client = BinanceSpotClient(
            api_key=settings.BINANCE_API_KEY,
            api_secret=settings.BINANCE_API_SECRET,
            testnet=settings.USE_TESTNET
        )
        
        app.state.futures_client = BinanceFuturesClient(
            api_key=settings.BINANCE_API_KEY,
            api_secret=settings.BINANCE_API_SECRET,
            testnet=settings.USE_TESTNET
        )

        # Initialize WebSocket Manager
        manager.binance_ws_manager = BinanceWebsocketManager(
            spot_client=app.state.spot_client,
            futures_client=app.state.futures_client
        )
        await manager.binance_ws_manager.start()

        # Initialize Trading Services
        app.state.order_manager = OrderManager(
            spot_client=app.state.spot_client,
            futures_client=app.state.futures_client,
            db=SessionLocal()
        )
        
        app.state.position_manager = PositionManager(
            order_manager=app.state.order_manager,
            risk_manager=RiskManager(),
            db=SessionLocal()
        )
        
        app.state.portfolio_manager = PortfolioManager(
            position_manager=app.state.position_manager,
            db=SessionLocal()
        )

        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

# Shutdown Events
@app.on_event("shutdown")
async def shutdown_event():
    try:
        # Close WebSocket Connections
        if manager.binance_ws_manager:
            await manager.binance_ws_manager.close()

        # Close Database Connections
        await engine.dispose()

        logger.info("Application shutdown completed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Include Routers
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    orders_router,
    prefix="/api/v1/trading/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    positions_router,
    prefix="/api/v1/trading/positions",
    tags=["Positions"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    portfolio_router,
    prefix="/api/v1/trading/portfolio",
    tags=["Portfolio"],
    dependencies=[Depends(get_current_user)]
)

app.include_router(
    signals_router,
    prefix="/api/v1/signals",
    tags=["Signals"],
    dependencies=[Depends(get_current_user)]
)

# WebSocket Endpoints
@app.websocket("/ws/market/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    await manager.connect(websocket)
    try:
        await manager.binance_ws_manager.subscribe_symbol(symbol)
        
        while True:
            try:
                data = await websocket.receive_json()
                # Handle incoming WebSocket messages
                if data.get("type") == "subscribe":
                    # Handle subscription requests
                    pass
                elif data.get("type") == "unsubscribe":
                    # Handle unsubscription requests
                    pass
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
    finally:
        await manager.disconnect(websocket)
        await manager.binance_ws_manager.unsubscribe_symbol(symbol)

# Error Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": exc.detail,
            "code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "Internal server error",
            "code": 500
        }
    )

# Health Check Endpoint
@app.get("/health", tags=["System"])
async def health_check():
    try:
        # Check Database Connection
        db = SessionLocal()
        await db.execute("SELECT 1")
        
        # Check Exchange Connection
        spot_status = await app.state.spot_client.get_system_status()
        futures_status = await app.state.futures_client.get_system_status()
        
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": app.version,
            "database": "connected",
            "exchange": {
                "spot": spot_status,
                "futures": futures_status
            },
            "websocket_connections": len(manager.active_connections)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service health check failed"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        workers=settings.WORKERS_COUNT,
        log_level=settings.LOG_LEVEL.lower()
    )