"""
Enterprise Pydantic Schemas - Kayos Cloud Licensing
Data validation and serialization models
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class LicenseTier(str, Enum):
    """License tier enumeration"""
    STARTER = "starter"
    PROFESSIONAL = "professional" 
    ENTERPRISE = "enterprise"
    PREMIUM = "premium"


class FeatureType(str, Enum):
    """Feature type enumeration"""
    BOOLEAN = "boolean"
    NUMERIC = "numeric"
    TIERED = "tiered"
    TIME_LIMITED = "time_limited"


class LicenseRequest(BaseModel):
    """Request model for license generation"""
    
    customer_info: Dict[str, Any] = Field(
        ...,
        description="Customer information",
        example={
            "id": "cust_123",
            "name": "John Doe",
            "email": "john@company.com",
            "company": "Tech Corp",
            "metadata": {"plan": "annual"}
        }
    )
    
    product_config: Dict[str, Any] = Field(
        ...,
        description="Product configuration",
        example={
            "id": "prod_abc",
            "name": "Kayos Enterprise Suite",
            "version": "2.0.0",
            "features": {
                "api_access": True,
                "max_users": 100,
                "premium_support": True
            },
            "validity_days": 365,
            "max_activations": 5
        }
    )
    
    license_tier: LicenseTier = Field(
        default=LicenseTier.PROFESSIONAL,
        description="License tier level"
    )
    
    @validator('customer_info')
    def validate_customer_info(cls, v):
        required_fields = ['id', 'name', 'email']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required customer field: {field}")
        return v
    
    @validator('product_config') 
    def validate_product_config(cls, v):
        required_fields = ['id', 'name', 'version', 'features']
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required product field: {field}")
        return v


class ValidationRequest(BaseModel):
    """Request model for license validation"""
    
    license_payload: str = Field(
        ...,
        description="Base64 encoded license payload",
        example="eyJsaWNlbnNlX2lkIjoi...",
        min_length=10
    )
    
    signature: str = Field(
        ...,
        description="Base64 encoded RSA signature", 
        example="MEYCIQD...",
        min_length=10
    )
    
    activation_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional activation data"
    )


class LicenseResponse(BaseModel):
    """Response model for license generation"""
    
    success: bool = Field(..., description="Operation success status")
    
    license: Dict[str, Any] = Field(
        ...,
        description="Generated license data",
        example={
            "payload": "eyJsaWNlbnNlX2lkIjoi...",
            "signature": "MEYCIQD...",
            "format": "kayos_enterprise_v2"
        }
    )
    
    metadata: Dict[str, Any] = Field(
        ...,
        description="License metadata",
        example={
            "license_id": "kayos_abc123...",
            "issued_at": "2024-01-01T00:00:00Z",
            "expires_at": "2025-01-01T00:00:00Z", 
            "customer": "John Doe",
            "product": "Kayos Enterprise Suite"
        }
    )


class ValidationResponse(BaseModel):
    """Response model for license validation"""
    
    valid: bool = Field(..., description="License validity status")
    
    license: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Decoded license payload if valid"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error message if validation failed"
    )
    
    message: str = Field(..., description="Validation result message")


class CustomerCreate(BaseModel):
    """Model for customer creation"""
    
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    company: Optional[str] = Field(None, max_length=100)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ProductCreate(BaseModel):
    """Model for product creation"""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')
    features: Dict[str, Any] = Field(..., description="Product features configuration")
    
    default_validity_days: int = Field(default=365, ge=1, le=3650)
    default_max_activations: int = Field(default=1, ge=1, le=1000)


class APIKeyCreate(BaseModel):
    """Model for API key generation"""
    
    name: str = Field(..., min_length=1, max_length=50)
    permissions: List[str] = Field(
        default=["license:generate", "license:validate"],
        description="API key permissions"
    )
    
    expires_at: Optional[datetime] = Field(
        default=None,
        description="API key expiration date"
    )


class HealthResponse(BaseModel):
    """Health check response model"""
    
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Dependency status")


class ErrorResponse(BaseModel):
    """Standard error response model"""
    
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Error details")
    timestamp: str = Field(..., description="Error timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "ValidationError",
                "detail": "Invalid license format",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
