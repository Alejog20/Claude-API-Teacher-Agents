"""
Queue service for handling asynchronous tasks.
"""
import asyncio
from typing import Dict, Any, Callable, Awaitable, Optional, List
import json
from datetime import datetime
import uuid

from app.utils.logger import setup_logger
from app.utils.config import settings

logger = setup_logger("queue")

class MemoryQueue:
    """
    In-memory queue implementation for development and small deployments.
    """
    
    def __init__(self):
        self.tasks = asyncio.Queue()
        self.results = {}
        self._running = False
        self._worker_task = None
    
    async def enqueue(self, task_type: str, data: Dict[str, Any]) -> str:
        """
        Add a task to the queue.
        
        Args:
            task_type: Type of task
            data: Task data
            
        Returns:
            Task ID
        """
        task_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        task = {
            "id": task_id,
            "type": task_type,
            "data": data,
            "status": "pending",
            "created_at": timestamp
        }
        
        await self.tasks.put(task)
        
        self.results[task_id] = {
            "status": "pending",
            "result": None,
            "created_at": timestamp
        }
        
        logger.info(f"Task {task_id} ({task_type}) enqueued")
        return task_id
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """
        Get the result of a task.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task result
        """
        if task_id not in self.results:
            return {
                "status": "not_found",
                "result": None
            }
        
        return self.results[task_id]
    
    async def start_worker(self, process_func: Callable[[Dict[str, Any]], Awaitable[Any]]):
        """
        Start the worker process.
        
        Args:
            process_func: Function to process tasks
        """
        if self._running:
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._worker(process_func))
        logger.info("Queue worker started")
    
    async def stop_worker(self):
        """Stop the worker process."""
        if not self._running:
            return
        
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("Queue worker stopped")
    
    async def _worker(self, process_func: Callable[[Dict[str, Any]], Awaitable[Any]]):
        """
        Worker process to handle tasks.
        
        Args:
            process_func: Function to process tasks
        """
        while self._running:
            try:
                # Get a task from the queue with a timeout
                try:
                    task = await asyncio.wait_for(self.tasks.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                task_id = task["id"]
                logger.info(f"Processing task {task_id}")
                
                # Update status
                task["status"] = "processing"
                task["processing_started"] = datetime.now().isoformat()
                self.results[task_id]["status"] = "processing"
                self.results[task_id]["processing_started"] = task["processing_started"]
                
                try:
                    # Process the task
                    result = await process_func(task)
                    
                    # Update with result
                    completed_at = datetime.now().isoformat()
                    task["status"] = "completed"
                    task["completed_at"] = completed_at
                    self.results[task_id]["status"] = "completed"
                    self.results[task_id]["result"] = result
                    self.results[task_id]["completed_at"] = completed_at
                    
                    logger.info(f"Task {task_id} completed")
                    
                except Exception as e:
                    # Handle processing error
                    error_at = datetime.now().isoformat()
                    error_msg = str(e)
                    
                    task["status"] = "failed"
                    task["error"] = error_msg
                    task["error_at"] = error_at
                    self.results[task_id]["status"] = "failed"
                    self.results[task_id]["error"] = error_msg
                    self.results[task_id]["error_at"] = error_at
                    
                    logger.error(f"Task {task_id} failed: {error_msg}")
                
                finally:
                    # Mark the task as done in the queue
                    self.tasks.task_done()
                    
            except asyncio.CancelledError:
                logger.info("Worker cancelled")
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in worker: {str(e)}")


# Redis Queue implementation would go here for production use

def create_queue():
    """
    Create the appropriate queue based on settings.
    
    Returns:
        Queue instance
    """
    if settings.QUEUE_SYSTEM.lower() == "redis":
        # Redis queue would be used in production
        logger.warning("Redis queue not implemented, using memory queue")
        return MemoryQueue()
    else:
        logger.info("Using memory queue")
        return MemoryQueue()

# Create global queue instance
queue = create_queue()

async def start_queue_worker():
    """Start the queue worker."""
    from app.services.content_generator import process_task
    await queue.start_worker(process_task)

async def stop_queue_worker():
    """Stop the queue worker."""
    await queue.stop_worker()