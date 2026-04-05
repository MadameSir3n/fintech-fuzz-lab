#!/usr/bin/env python3
"""
FinTech Fuzz Lab - Payment API for security testing

A FastAPI application designed to be fuzz-tested with various attack vectors
including malformed JSON, oversized payloads, and injection attempts.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import json
import logging
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="FinTech Fuzz Lab",
    description="Payment API for security testing and fuzzing demonstrations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payment request model
class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount must be positive")
    currency: str = Field(default="USD", description="Currency code")
    card_number: str = Field(..., min_length=13, max_length=19, description="Credit card number")
    expiry_date: str = Field(..., description="Expiry date in MM/YY format")
    cvv: str = Field(..., min_length=3, max_length=4, description="CVV code")
    merchant_id: str = Field(..., description="Merchant identifier")
    description: Optional[str] = Field(default=None, max_length=100, description="Payment description")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

    @validator('expiry_date')
    def validate_expiry_date(cls, v):
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', v):
            raise ValueError('Expiry date must be in MM/YY format')
        return v

    @validator('card_number')
    def validate_card_number(cls, v):
        # Basic Luhn algorithm check
        digits = [int(d) for d in v if d.isdigit()]
        if len(digits) < 13 or len(digits) > 19:
            raise ValueError('Invalid card number length')
        
        # Luhn algorithm
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        
        if total % 10 != 0:
            raise ValueError('Invalid card number')
        
        return v

    @validator('cvv')
    def validate_cvv(cls, v):
        if not v.isdigit():
            raise ValueError('CVV must contain only digits')
        return v

# Payment response model
class PaymentResponse(BaseModel):
    success: bool
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    errors: Optional[List[str]] = None
    timestamp: datetime
    amount: Optional[float] = None
    currency: Optional[str] = None

# In-memory storage for demo purposes (not for production!)
transactions = {}

def generate_transaction_id():
    """Generate a unique transaction ID."""
    return f"txn_{int(datetime.now().timestamp() * 1000)}"

@app.post("/payments", response_model=PaymentResponse)
async def process_payment(payment: PaymentRequest):
    """
    Process a payment transaction.
    
    This endpoint is designed to be fuzz-tested with various attack vectors
    including malformed JSON, oversized payloads, and injection attempts.
    """
    try:
        # Validate payment data
        transaction_id = generate_transaction_id()
        
        # Simulate payment processing
        # In a real implementation, this would integrate with payment gateways
        
        transaction_data = {
            "transaction_id": transaction_id,
            "amount": payment.amount,
            "currency": payment.currency,
            "merchant_id": payment.merchant_id,
            "timestamp": datetime.now(),
            "status": "completed"
        }
        
        # Store transaction (in-memory for demo)
        transactions[transaction_id] = transaction_data
        
        logger.info(f"Payment processed successfully: {transaction_id}")
        
        return PaymentResponse(
            success=True,
            transaction_id=transaction_id,
            message="Payment processed successfully",
            timestamp=datetime.now(),
            amount=payment.amount,
            currency=payment.currency
        )
        
    except Exception as e:
        logger.error(f"Payment processing failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/payments/{transaction_id}")
async def get_payment(transaction_id: str):
    """Get payment transaction details."""
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transactions[transaction_id]

@app.get("/payments")
async def list_payments(limit: int = 10, offset: int = 0):
    """List recent payment transactions."""
    transaction_list = list(transactions.values())
    return transaction_list[offset:offset + limit]

@app.delete("/payments/{transaction_id}")
async def delete_payment(transaction_id: str):
    """Delete a payment transaction (demo only - not production safe!)."""
    if transaction_id not in transactions:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    del transactions[transaction_id]
    return {"message": "Transaction deleted"}

# Additional vulnerable endpoints for fuzz testing

@app.post("/vulnerable/echo")
async def echo_endpoint(request: Request):
    """Echo endpoint that returns raw input - vulnerable to various attacks."""
    try:
        raw_data = await request.body()
        return {"echo": raw_data.decode('utf-8', errors='ignore')}
    except Exception as e:
        return {"error": str(e)}

@app.post("/vulnerable/json-parse")
async def json_parse_endpoint(request: Request):
    """JSON parsing endpoint vulnerable to malformed JSON attacks."""
    try:
        raw_data = await request.body()
        parsed_data = json.loads(raw_data)
        return {"parsed": parsed_data}
    except Exception as e:
        return {"error": str(e)}

@app.get("/vulnerable/reflect")
async def reflect_parameter(param: str = "test"):
    """Parameter reflection endpoint vulnerable to XSS and injection."""
    return {"reflected": param}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)