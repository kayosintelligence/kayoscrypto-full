"""
Enterprise FastAPI Application - Kayos Cloud Licensing
Main API entry point with enterprise features - LOCAL DEVELOPMENT VERSION
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import os
import logging
from datetime import datetime, timezone

from app.core.security_engine import crypto_engine, license_generator
from app.models.schemas import *
from app.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security scheme
security_scheme = HTTPBearer()

def create_application() -> FastAPI:
    """Create and configure FastAPI application for local development"""
    
    app = FastAPI(
        title="Kayos Cloud Licensing Enterprise API",
        description="Enterprise-grade software licensing as a service - DEVELOPMENT",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc", 
        openapi_url="/openapi.json"
    )
    
    # Security middleware - relaxed for development
    if os.getenv("ENVIRONMENT") == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.kayos.io", "localhost", "127.0.0.1"]
        )
    
    # CORS middleware - permissive for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this!
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    return app

# Create app instance
app = create_application()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Kayos Cloud Licensing Enterprise API - DEVELOPMENT",
        "version": "2.0.0", 
        "status": "operational",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check crypto engine
        test_payload = {"test": "health_check"}
        encoded, signature = crypto_engine.sign_license(test_payload)
        is_valid, _ = crypto_engine.verify_license(encoded, signature)
        
        if not is_valid:
            raise Exception("Crypto engine health check failed")
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "services": {
                "crypto_engine": "operational",
                "license_generator": "operational",
                "api": "operational"
            },
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}"
        )

@app.post("/v1/licenses/generate", response_model=LicenseResponse)
async def generate_license(
    request: LicenseRequest,
    # credentials: HTTPAuthorizationCredentials = Depends(security_scheme)  # Disabled for development
):
    """Generate new enterprise license"""
    try:
        # TODO: Enable in production
        # await verify_api_key(credentials.credentials)
        # await rate_limiter.check_limit(credentials.credentials, "generate_license")
        
        logger.info(f"Generating license for customer: {request.customer_info['name']}")
        
        # Generate license
        result = license_generator.generate_enterprise_license(
            customer_info=request.customer_info,
            product_config=request.product_config,
            license_tier=request.license_tier
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "License generation failed")
            )
        
        # Log generation
        logger.info(f"License generated successfully: {result['metadata']['license_id']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"License generation failed: {str(e)}"
        )

@app.post("/v1/licenses/validate", response_model=ValidationResponse)
async def validate_license(request: ValidationRequest):
    """Validate enterprise license"""
    try:
        logger.info("Validating license")
        
        # Validate license
        is_valid, payload = crypto_engine.verify_license(
            request.license_payload,
            request.signature
        )
        
        if is_valid:
            logger.info(f"License validation successful: {payload['license_id']}")
            return {
                "valid": True,
                "license": payload,
                "message": "License is valid and active"
            }
        else:
            logger.warning(f"License validation failed: {payload.get('error')}")
            return {
                "valid": False,
                "error": payload.get("error", "Validation failed"),
                "message": "License is invalid or expired"
            }
            
    except Exception as e:
        logger.error(f"License validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"License validation error: {str(e)}"
        )

@app.get("/v1/licenses/{license_id}")
async def get_license_info(
    license_id: str,
    # credentials: HTTPAuthorizationCredentials = Depends(security_scheme)  # Disabled for development
):
    """Get license information (admin only) - DEVELOPMENT VERSION"""
    try:
        # TODO: Enable admin verification in production
        # user = await get_current_user(credentials.credentials)
        # if not user.get("is_admin", False):
        #     raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        # Mock response for development
        return {
            "license_id": license_id,
            "status": "active",
            "environment": "development",
            "message": "License details endpoint - development mode",
            "note": "Admin authentication disabled in development"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"License info fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch license information: {str(e)}"
        )

@app.get("/v1/debug/public-key")
async def get_public_key():
    """Debug endpoint to get public key (for development only)"""
    if os.getenv("ENVIRONMENT") == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint is disabled in production"
        )
    
    return {
        "public_key": crypto_engine.get_public_key_pem(),
        "note": "Development only - disable in production"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "8000")),
        workers=int(os.getenv("API_WORKERS", "1")),
        log_level="info",
        reload=True  # Auto-reload in development
    )
