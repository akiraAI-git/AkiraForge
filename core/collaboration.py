#!/usr/bin/env python3
"""
Collaborative Workspace Manager for Akira Forge

Enable team collaboration with shared workspaces, permissions,
real-time collaboration, and activity tracking.
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Workspace permissions."""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    COMMENTER = "commenter"


class ActivityType(Enum):
    """Activity types."""
    CREATED = "created"
    EDITED = "edited"
    COMMENTED = "commented"
    SHARED = "shared"
    DELETED = "deleted"
    PERMISSION_CHANGED = "permission_changed"


@dataclass
class TeamMember:
    """Team member with role and permissions."""
    user_id: str
    name: str
    email: str
    permission: Permission
    joined_at: datetime = field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    
    def can_edit(self) -> bool:
        """Check if member can edit."""
        return self.permission in [Permission.OWNER, Permission.ADMIN, Permission.EDITOR]
    
    def can_comment(self) -> bool:
        """Check if member can comment."""
        return self.permission in [Permission.OWNER, Permission.ADMIN, Permission.EDITOR, Permission.COMMENTER]


@dataclass
class WorkspaceActivity:
    """Activity log entry."""
    activity_id: str
    activity_type: ActivityType
    user_id: str
    user_name: str
    description: str
    resource_type: str  # 'project', 'note', 'file', etc.
    resource_id: str
    resource_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SharedResource:
    """Shared resource in workspace."""
    resource_id: str
    resource_type: str
    name: str
    owner_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    editors_count: int = 0
    comments_count: int = 0
    version: int = 1


@dataclass
class Workspace:
    """Collaborative workspace."""
    workspace_id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime = field(default_factory=datetime.now)
    members: Dict[str, TeamMember] = field(default_factory=dict)
    shared_resources: Dict[str, SharedResource] = field(default_factory=dict)
    activity_log: List[WorkspaceActivity] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True


class CollaborationManager:
    """Manage collaborative workspaces and team features."""
    
    def __init__(self):
        self.workspaces = {}
        self.user_workspaces = {}  # user_id -> [workspace_ids]
        self.real_time_sessions = {}  # workspace_id -> {user_id: session}
    
    def create_workspace(self, name: str, owner_id: str,
                        description: str = "") -> Workspace:
        """Create new collaborative workspace."""
        import uuid
        workspace_id = f"ws_{uuid.uuid4().hex[:8]}"
        
        workspace = Workspace(
            workspace_id=workspace_id,
            name=name,
            owner_id=owner_id,
            description=description
        )
        
        # Add owner as member
        workspace.members[owner_id] = TeamMember(
            user_id=owner_id,
            name="Owner",
            email="",
            permission=Permission.OWNER
        )
        
        self.workspaces[workspace_id] = workspace
        
        if owner_id not in self.user_workspaces:
            self.user_workspaces[owner_id] = []
        self.user_workspaces[owner_id].append(workspace_id)
        
        logger.info(f"✓ Created workspace: {name} ({workspace_id})")
        return workspace
    
    def add_member(self, workspace_id: str, user_id: str, name: str,
                  email: str, permission: Permission = Permission.VIEWER) -> bool:
        """Add team member to workspace."""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        workspace.members[user_id] = TeamMember(
            user_id=user_id,
            name=name,
            email=email,
            permission=permission
        )
        
        if user_id not in self.user_workspaces:
            self.user_workspaces[user_id] = []
        self.user_workspaces[user_id].append(workspace_id)
        
        # Log activity
        self._log_activity(
            workspace_id, user_id, "System",
            ActivityType.SHARED,
            "member", user_id,
            f"Added {name} with {permission.value} permission"
        )
        
        logger.info(f"✓ Added member {name} to workspace {workspace_id}")
        return True
    
    def share_resource(self, workspace_id: str, resource_id: str,
                      resource_type: str, name: str,
                      owner_id: str) -> Optional[SharedResource]:
        """Share resource in workspace."""
        if workspace_id not in self.workspaces:
            return None
        
        workspace = self.workspaces[workspace_id]
        resource = SharedResource(
            resource_id=resource_id,
            resource_type=resource_type,
            name=name,
            owner_id=owner_id
        )
        
        workspace.shared_resources[resource_id] = resource
        
        self._log_activity(
            workspace_id, owner_id, owner_id,
            ActivityType.SHARED,
            resource_type, resource_id, name
        )
        
        logger.info(f"✓ Shared resource: {name}")
        return resource
    
    def update_member_permission(self, workspace_id: str, user_id: str,
                                new_permission: Permission) -> bool:
        """Update team member permission."""
        if workspace_id not in self.workspaces:
            return False
        
        workspace = self.workspaces[workspace_id]
        if user_id not in workspace.members:
            return False
        
        old_permission = workspace.members[user_id].permission
        workspace.members[user_id].permission = new_permission
        
        self._log_activity(
            workspace_id, "System", "System",
            ActivityType.PERMISSION_CHANGED,
            "member", user_id,
            f"Changed from {old_permission.value} to {new_permission.value}"
        )
        
        logger.info(f"✓ Updated permission for {user_id}: {new_permission.value}")
        return True
    
    def start_real_time_session(self, workspace_id: str, user_id: str) -> bool:
        """Start real-time collaboration session."""
        if workspace_id not in self.workspaces:
            return False
        
        if workspace_id not in self.real_time_sessions:
            self.real_time_sessions[workspace_id] = {}
        
        self.real_time_sessions[workspace_id][user_id] = {
            'started_at': datetime.now().isoformat(),
            'cursor_position': None,
            'editing_resource': None
        }
        
        workspace = self.workspaces[workspace_id]
        if user_id in workspace.members:
            workspace.members[user_id].last_activity = datetime.now()
        
        logger.info(f"✓ Started session: {user_id} in {workspace_id}")
        return True
    
    def end_real_time_session(self, workspace_id: str, user_id: str) -> bool:
        """End real-time collaboration session."""
        if workspace_id in self.real_time_sessions:
            if user_id in self.real_time_sessions[workspace_id]:
                del self.real_time_sessions[workspace_id][user_id]
                logger.info(f"✓ Ended session: {user_id}")
                return True
        return False
    
    def get_active_members(self, workspace_id: str) -> List[TeamMember]:
        """Get list of members currently active in workspace."""
        if workspace_id not in self.real_time_sessions:
            return []
        
        workspace = self.workspaces[workspace_id]
        active_ids = set(self.real_time_sessions[workspace_id].keys())
        
        return [
            member for user_id, member in workspace.members.items()
            if user_id in active_ids
        ]
    
    def get_activity_log(self, workspace_id: str, 
                        limit: int = 50) -> List[WorkspaceActivity]:
        """Get workspace activity log."""
        if workspace_id not in self.workspaces:
            return []
        
        workspace = self.workspaces[workspace_id]
        return workspace.activity_log[-limit:]
    
    def _log_activity(self, workspace_id: str, user_id: str, user_name: str,
                     activity_type: ActivityType, resource_type: str,
                     resource_id: str, resource_name: str,
                     details: Dict[str, Any] = None):
        """Log activity in workspace."""
        if workspace_id not in self.workspaces:
            return
        
        import uuid
        activity = WorkspaceActivity(
            activity_id=f"act_{uuid.uuid4().hex[:8]}",
            activity_type=activity_type,
            user_id=user_id,
            user_name=user_name,
            description=f"{activity_type.value.capitalize()} {resource_type}",
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details or {}
        )
        
        workspace = self.workspaces[workspace_id]
        workspace.activity_log.append(activity)
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID."""
        return self.workspaces.get(workspace_id)
    
    def get_user_workspaces(self, user_id: str) -> List[Workspace]:
        """Get all workspaces for user."""
        workspace_ids = self.user_workspaces.get(user_id, [])
        return [self.workspaces[wid] for wid in workspace_ids 
                if wid in self.workspaces]
    
    def get_workspace_statistics(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace statistics."""
        if workspace_id not in self.workspaces:
            return {}
        
        workspace = self.workspaces[workspace_id]
        
        return {
            'workspace_id': workspace_id,
            'name': workspace.name,
            'members_count': len(workspace.members),
            'active_members': len(self.get_active_members(workspace_id)),
            'shared_resources': len(workspace.shared_resources),
            'activity_count': len(workspace.activity_log),
            'created_at': workspace.created_at.isoformat()
        }


# Global instance
_manager = None


def get_collaboration_manager() -> CollaborationManager:
    """Get or create collaboration manager."""
    global _manager
    if _manager is None:
        _manager = CollaborationManager()
    return _manager
