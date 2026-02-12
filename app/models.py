"""Pydantic models for request/response validation."""

from pydantic import BaseModel
from typing import List, Dict


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str


class StyleInfo(BaseModel):
    """Docstring style information."""
    name: str
    description: str


class StylesResponse(BaseModel):
    """Available docstring styles response."""
    styles: List[StyleInfo]
