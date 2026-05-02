#!/usr/bin/env python3
"""
Workflow Automation Engine for Akira Forge

Create, manage, and execute automated workflows with triggers,
conditions, and actions for advanced task automation.
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """Workflow trigger types."""
    TIME_BASED = "time_based"
    EVENT_BASED = "event_based"
    MANUAL = "manual"
    WEBHOOK = "webhook"
    FILE_CHANGE = "file_change"


class ActionType(Enum):
    """Workflow action types."""
    EXECUTE_CODE = "execute_code"
    SEND_EMAIL = "send_email"
    HTTP_REQUEST = "http_request"
    DATABASE_QUERY = "database_query"
    FILE_OPERATION = "file_operation"
    NOTIFICATION = "notification"


@dataclass
class Trigger:
    """Workflow trigger definition."""
    type: TriggerType
    config: Dict[str, Any]
    enabled: bool = True
    last_triggered: Optional[datetime] = None


@dataclass
class Action:
    """Workflow action definition."""
    type: ActionType
    config: Dict[str, Any]
    enabled: bool = True
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Condition:
    """Workflow condition."""
    name: str
    expression: str  # Python expression to evaluate
    enabled: bool = True


@dataclass
class WorkflowStep:
    """Individual workflow execution step."""
    step_id: str
    action: Action
    conditions: List[Condition] = field(default_factory=list)
    on_success: Optional[str] = None  # Next step on success
    on_failure: Optional[str] = None  # Next step on failure
    timeout_seconds: int = 300


@dataclass
class Workflow:
    """Complete workflow definition."""
    id: str
    name: str
    description: str
    triggers: List[Trigger] = field(default_factory=list)
    steps: Dict[str, WorkflowStep] = field(default_factory=dict)
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)


class WorkflowEngine:
    """Execute workflows with state management."""
    
    def __init__(self):
        self.workflows = {}
        self.execution_history = []
        self.action_handlers = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self):
        """Register default action handlers."""
        self.register_action_handler(
            ActionType.NOTIFICATION,
            self._handle_notification
        )
        self.register_action_handler(
            ActionType.HTTP_REQUEST,
            self._handle_http_request
        )
    
    def register_action_handler(self, action_type: ActionType, handler: Callable):
        """Register custom action handler."""
        self.action_handlers[action_type] = handler
        logger.info(f"✓ Registered action handler: {action_type.value}")
    
    def create_workflow(self, name: str, description: str = "") -> Workflow:
        """Create new workflow."""
        import uuid
        workflow_id = str(uuid.uuid4())[:8]
        workflow = Workflow(
            id=workflow_id,
            name=name,
            description=description
        )
        self.workflows[workflow_id] = workflow
        logger.info(f"✓ Created workflow: {name} ({workflow_id})")
        return workflow
    
    def add_trigger(self, workflow_id: str, trigger: Trigger) -> bool:
        """Add trigger to workflow."""
        if workflow_id not in self.workflows:
            return False
        self.workflows[workflow_id].triggers.append(trigger)
        logger.info(f"✓ Added trigger to workflow: {workflow_id}")
        return True
    
    def add_step(self, workflow_id: str, step: WorkflowStep) -> bool:
        """Add step to workflow."""
        if workflow_id not in self.workflows:
            return False
        self.workflows[workflow_id].steps[step.step_id] = step
        logger.info(f"✓ Added step to workflow: {step.step_id}")
        return True
    
    def execute_workflow(self, workflow_id: str, 
                        context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow."""
        if workflow_id not in self.workflows:
            return {'error': 'Workflow not found', 'status': 'failed'}
        
        workflow = self.workflows[workflow_id]
        if not workflow.enabled:
            return {'error': 'Workflow is disabled', 'status': 'failed'}
        
        context = context or {}
        execution_id = self._generate_execution_id()
        execution_log = {
            'execution_id': execution_id,
            'workflow_id': workflow_id,
            'started_at': datetime.now().isoformat(),
            'steps_executed': [],
            'variables': context.copy()
        }
        
        try:
            # Start with first steps (steps with no predecessor)
            current_steps = [
                step for step in workflow.steps.values()
                if not any(s.on_success == step.step_id 
                          for s in workflow.steps.values())
            ]
            
            if not current_steps:
                current_steps = list(workflow.steps.values())[:1]
            
            while current_steps:
                next_steps = []
                
                for step in current_steps:
                    # Check conditions
                    if not self._evaluate_conditions(step.conditions, context):
                        continue
                    
                    # Execute action
                    result = self._execute_action(step.action, context)
                    
                    execution_log['steps_executed'].append({
                        'step_id': step.step_id,
                        'result': result,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Determine next step
                    next_step_id = step.on_success if result['success'] else step.on_failure
                    if next_step_id and next_step_id in workflow.steps:
                        next_steps.append(workflow.steps[next_step_id])
                
                current_steps = next_steps
        
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            execution_log['error'] = str(e)
        
        execution_log['completed_at'] = datetime.now().isoformat()
        execution_log['status'] = 'completed'
        
        workflow.execution_history.append(execution_log)
        self.execution_history.append(execution_log)
        
        logger.info(f"✓ Workflow executed: {workflow_id} ({execution_id})")
        return execution_log
    
    def _evaluate_conditions(self, conditions: List[Condition], 
                            context: Dict[str, Any]) -> bool:
        """Evaluate all conditions."""
        for condition in conditions:
            if not condition.enabled:
                continue
            
            try:
                result = eval(condition.expression, {"context": context})
                if not result:
                    return False
            except Exception as e:
                logger.error(f"Condition evaluation error: {e}")
                return False
        
        return True
    
    def _execute_action(self, action: Action, 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action."""
        if not action.enabled:
            return {'success': True, 'message': 'Action disabled'}
        
        handler = self.action_handlers.get(action.type)
        if not handler:
            return {'success': False, 'error': f'No handler for {action.type.value}'}
        
        try:
            result = handler(action.config, context)
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _handle_notification(self, config: Dict[str, Any], 
                           context: Dict[str, Any]) -> str:
        """Handle notification action."""
        message = config.get('message', 'Workflow notification')
        logger.info(f"📢 Notification: {message}")
        return "Notification sent"
    
    def _handle_http_request(self, config: Dict[str, Any], 
                            context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle HTTP request action."""
        import json
        url = config.get('url', '')
        method = config.get('method', 'POST')
        data = config.get('data', {})
        
        logger.info(f"📡 HTTP {method}: {url}")
        return {'url': url, 'method': method, 'queued': True}
    
    def _generate_execution_id(self) -> str:
        """Generate execution ID."""
        import uuid
        return f"exec_{uuid.uuid4().hex[:8]}"
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""
        return list(self.workflows.values())
    
    def get_execution_history(self, workflow_id: Optional[str] = None,
                             limit: int = 50) -> List[Dict[str, Any]]:
        """Get execution history."""
        if workflow_id:
            return self.execution_history[-limit:] if workflow_id else []
        return self.execution_history[-limit:]
    
    def enable_workflow(self, workflow_id: str) -> bool:
        """Enable workflow."""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = True
            return True
        return False
    
    def disable_workflow(self, workflow_id: str) -> bool:
        """Disable workflow."""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].enabled = False
            return True
        return False


class WorkflowBuilder:
    """Builder for constructing workflows fluently."""
    
    def __init__(self, name: str):
        self.engine = None
        self.workflow = Workflow(
            id='',
            name=name,
            description=''
        )
    
    def description(self, desc: str) -> 'WorkflowBuilder':
        """Set workflow description."""
        self.workflow.description = desc
        return self
    
    def add_trigger(self, trigger_type: TriggerType, 
                   config: Dict[str, Any]) -> 'WorkflowBuilder':
        """Add trigger to workflow."""
        trigger = Trigger(trigger_type, config)
        self.workflow.triggers.append(trigger)
        return self
    
    def add_step(self, step_id: str, action_type: ActionType,
                action_config: Dict[str, Any],
                conditions: List[Condition] = None) -> 'WorkflowBuilder':
        """Add step to workflow."""
        action = Action(action_type, action_config)
        step = WorkflowStep(step_id, action, conditions or [])
        self.workflow.steps[step_id] = step
        return self
    
    def link_steps(self, from_step: str, to_success: str = None,
                  to_failure: str = None) -> 'WorkflowBuilder':
        """Link workflow steps."""
        if from_step in self.workflow.steps:
            self.workflow.steps[from_step].on_success = to_success
            self.workflow.steps[from_step].on_failure = to_failure
        return self
    
    def build(self, engine: WorkflowEngine) -> Workflow:
        """Build and register workflow."""
        import uuid
        self.workflow.id = str(uuid.uuid4())[:8]
        engine.workflows[self.workflow.id] = self.workflow
        self.engine = engine
        return self.workflow


# Global instance
_engine = None


def get_workflow_engine() -> WorkflowEngine:
    """Get or create workflow engine."""
    global _engine
    if _engine is None:
        _engine = WorkflowEngine()
    return _engine
