"""
Background Task Queue for Akira Forge
Async task execution with retry logic, scheduling, and monitoring.
"""

import asyncio
import uuid
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque


class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class TaskResult:
    """Represents a task result."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    
    @property
    def duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class Task:
    """Represents a background task."""
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    max_retries: int = 3
    retry_delay: int = 5  # seconds
    timeout: Optional[int] = None  # seconds
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[TaskResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    async def execute(self) -> TaskResult:
        """Execute the task."""
        self.status = TaskStatus.RUNNING
        self.result = TaskResult(self.task_id, TaskStatus.RUNNING)
        self.result.started_at = datetime.now()
        self.result.attempts = 0
        
        last_error = None
        
        for attempt in range(self.max_retries):
            self.result.attempts = attempt + 1
            try:
                if asyncio.iscoroutinefunction(self.func):
                    result = await asyncio.wait_for(
                        self.func(*self.args, **self.kwargs),
                        timeout=self.timeout
                    )
                else:
                    result = self.func(*self.args, **self.kwargs)
                
                self.status = TaskStatus.COMPLETED
                self.result.status = TaskStatus.COMPLETED
                self.result.result = result
                self.result.completed_at = datetime.now()
                return self.result
                
            except asyncio.TimeoutError as e:
                last_error = f"Task timeout after {self.timeout}s"
            except Exception as e:
                last_error = str(e)
            
            # Retry if not last attempt
            if attempt < self.max_retries - 1:
                self.status = TaskStatus.RETRYING
                self.result.status = TaskStatus.RETRYING
                await asyncio.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
        
        # All retries failed
        self.status = TaskStatus.FAILED
        self.result.status = TaskStatus.FAILED
        self.result.error = last_error
        self.result.completed_at = datetime.now()
        return self.result


class BackgroundTaskQueue:
    """
    Async background task queue with retry logic.
    
    Features:
    - Task queuing and execution
    - Automatic retries with exponential backoff
    - Task timeout handling
    - Task history and monitoring
    - Task cancellation
    """
    
    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.queue: deque = deque()
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.workers: List[asyncio.Task] = []
    
    def enqueue(self, func: Callable, args: tuple = (), kwargs: dict = None,
                max_retries: int = 3, retry_delay: int = 5,
                timeout: Optional[int] = None) -> str:
        """Enqueue a task for execution."""
        if kwargs is None:
            kwargs = {}
        
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout
        )
        
        self.queue.append(task)
        return task.task_id
    
    def schedule_periodic(self, func: Callable, interval: int,
                         args: tuple = (), kwargs: dict = None) -> str:
        """Schedule a periodic task (every interval seconds)."""
        if kwargs is None:
            kwargs = {}
        
        async def periodic_wrapper():
            while True:
                try:
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
                except Exception as e:
                    print(f"❌ Periodic task error: {str(e)}")
                
                await asyncio.sleep(interval)
        
        return self.enqueue(periodic_wrapper, max_retries=1)
    
    async def start(self):
        """Start the task queue worker(s)."""
        for _ in range(self.max_workers):
            worker = asyncio.create_task(self._worker())
            self.workers.append(worker)
    
    async def _worker(self):
        """Worker coroutine that processes tasks."""
        while True:
            if not self.queue:
                await asyncio.sleep(0.1)
                continue
            
            task = self.queue.popleft()
            self.running_tasks[task.task_id] = task
            
            try:
                result = await task.execute()
                self.completed_tasks[task.task_id] = result
            finally:
                if task.task_id in self.running_tasks:
                    del self.running_tasks[task.task_id]
    
    def stop(self):
        """Stop the task queue."""
        for worker in self.workers:
            worker.cancel()
        self.workers.clear()
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get task status."""
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].status
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        return None
    
    def get_task_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result."""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].result
        return None
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task."""
        for i, task in enumerate(self.queue):
            if task.task_id == task_id:
                self.queue.remove(task)
                return True
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "queued": len(self.queue),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks),
            "total_processed": len(self.completed_tasks),
            "workers": self.max_workers
        }


# Global instance
_task_queue: Optional[BackgroundTaskQueue] = None


def get_task_queue(max_workers: int = 5) -> BackgroundTaskQueue:
    """Get or create global task queue."""
    global _task_queue
    if _task_queue is None:
        _task_queue = BackgroundTaskQueue(max_workers)
    return _task_queue


def enqueue_task(func: Callable, args: tuple = (), kwargs: dict = None,
                 max_retries: int = 3, retry_delay: int = 5) -> str:
    """Enqueue a task (convenience function)."""
    if kwargs is None:
        kwargs = {}
    return get_task_queue().enqueue(func, args, kwargs, max_retries, retry_delay)
