"""
Standard response schemas for the API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime

# Define a generic type for use with the paginated response
T = TypeVar('T')

class StandardResponse(BaseModel):
    """Standard success response format."""
    status: str = Field("success", description="Response status")
    message: str = Field(..., description="Response message")
    data: Optional[Any] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    """Standard error response format."""
    status: str = Field("error", description="Error status")
    message: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Any] = Field(None, description="Error details")

class PageMetadata(BaseModel):
    """Metadata for paginated responses."""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_prev: bool = Field(..., description="Whether there is a previous page")

class PageResponse(BaseModel, Generic[T]):
    """Paginated response format."""
    items: List[T] = Field(..., description="Page items")
    metadata: PageMetadata = Field(..., description="Page metadata")

class HealthCheckResponse(BaseModel):
    """Health check response format."""
    status: str = Field("ok", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current server time")
    database: str = Field(..., description="Database connection status")
    claude_api: str = Field(..., description="Claude API connection status")

class TaskResponse(BaseModel):
    """Asynchronous task response format."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status")
    message: str = Field(..., description="Task message")

class TaskStatusResponse(BaseModel):
    """Task status response format."""
    task_id: str = Field(..., description="Task ID")
    status: str = Field(..., description="Task status")
    created_at: datetime = Field(..., description="Task creation time")
    processing_started: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    result: Optional[Any] = Field(None, description="Task result")
    error: Optional[str] = Field(None, description="Error message if failed")

class UserAgentInteractionResponse(BaseModel):
    """Response format for user-agent interactions."""
    message: str = Field(..., description="Agent's response message")
    agent_type: str = Field(..., description="Type of agent that responded")
    interaction_id: int = Field(..., description="Interaction ID for reference")
    timestamp: datetime = Field(..., description="Interaction timestamp")

class LearningProgressSummary(BaseModel):
    """Summary of learning progress across subjects."""
    overall_progress: float = Field(..., description="Overall progress percentage")
    subjects_progress: List[Dict[str, Any]] = Field(..., description="Progress by subject")
    recent_activities: List[Dict[str, Any]] = Field(..., description="Recent learning activities")
    recommendations: List[Dict[str, Any]] = Field(..., description="Personalized recommendations")

class ContentSearchResponse(BaseModel):
    """Response format for content search results."""
    query: str = Field(..., description="Search query")
    results_count: int = Field(..., description="Number of results")
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    categories: List[str] = Field(..., description="Result categories")
    suggestion: Optional[str] = Field(None, description="Search suggestion if query had typos")