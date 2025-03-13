"""
Service modules for the learning assistant application.
"""
from app.services.claude_api import ClaudeClient
from app.services.content_generator import ContentGenerator, generate_content
from app.services.queue import queue, start_queue_worker, stop_queue_worker
from app.services.auth import (
    verify_password, get_password_hash, create_access_token, 
    decode_token, validate_email_password
)

__all__ = [
    'ClaudeClient',
    'ContentGenerator',
    'generate_content',
    'queue',
    'start_queue_worker',
    'stop_queue_worker',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'decode_token',
    'validate_email_password'
]