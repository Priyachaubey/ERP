from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.modules.user.models import User, Role, Permission, PasswordReset
from app.modules.user.repository import (
    UserRepository,
    RoleRepository,
    PermissionRepository,
    SessionRepository,
    AuditLogRepository,
    PasswordResetRepository,
)
import secrets
import json


class AuthService:
    """Authentication service."""

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = UserRepository.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def login(
        db: Session,
        username: str,
        password: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        remember_me: bool = False,
    ) -> Dict[str, Any]:
        """Login user and create session."""
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )

        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is locked",
            )

        # Create tokens
        access_token = create_access_token(str(user.id))
        refresh_token = create_refresh_token(str(user.id))

        # Create session
        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        SessionRepository.create(
            db,
            {
                "user_id": user.id,
                "refresh_token": refresh_token,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "expires_at": expires_at,
            },
        )

        # Update last login
        user.last_login_at = datetime.utcnow()
        db.commit()

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "user_id": user.id,
                "action": "LOGIN",
                "entity_type": "User",
                "entity_id": user.id,
                "ip_address": ip_address,
                "user_agent": user_agent,
            },
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    @staticmethod
    def logout(
        db: Session,
        user_id: UUID,
        refresh_token: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> bool:
        """Logout user and revoke session."""
        if refresh_token:
            # Find and revoke specific session
            sessions = SessionRepository.get_by_user_id(db, user_id)
            for session in sessions:
                if session.refresh_token == refresh_token:
                    SessionRepository.revoke(db, session.id)
        else:
            # Revoke all sessions
            SessionRepository.revoke_all_user_sessions(db, user_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "user_id": user_id,
                "action": "LOGOUT",
                "entity_type": "User",
                "entity_id": user_id,
                "ip_address": ip_address,
            },
        )

        return True

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        user_id = payload.get("sub")
        user = UserRepository.get_by_id(db, UUID(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        new_access_token = create_access_token(str(user.id))
        new_refresh_token = create_refresh_token(str(user.id))

        # Create new session
        expires_at = datetime.utcnow() + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        SessionRepository.create(
            db,
            {
                "user_id": user.id,
                "refresh_token": new_refresh_token,
                "expires_at": expires_at,
            },
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    @staticmethod
    def forgot_password(db: Session, email: str) -> bool:
        """Generate password reset token."""
        user = UserRepository.get_by_email(db, email)
        if not user:
            # Don't reveal if email exists
            return True

        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=24)

        PasswordResetRepository.create(
            db,
            {
                "user_id": user.id,
                "token": token,
                "expires_at": expires_at,
            },
        )

        # TODO: Send email with reset link
        return True

    @staticmethod
    def reset_password(
        db: Session, token: str, new_password: str
    ) -> Optional[User]:
        """Reset password using token."""
        reset = PasswordResetRepository.get_by_token(db, token)
        if not reset:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token",
            )

        if reset.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired",
            )

        user = UserRepository.get_by_id(db, reset.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        password_hash = get_password_hash(new_password)
        user = UserRepository.update(
            db,
            user.id,
            {
                "password_hash": password_hash,
                "password_changed_at": datetime.utcnow(),
            },
        )

        PasswordResetRepository.mark_as_used(db, reset.id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "user_id": user.id,
                "action": "PASSWORD_RESET",
                "entity_type": "User",
                "entity_id": user.id,
            },
        )

        return user


class UserService:
    """User service."""

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
        phone: Optional[str] = None,
        role_ids: Optional[List[UUID]] = None,
    ) -> User:
        """Create a new user."""
        # Check if email exists
        if UserRepository.get_by_email(db, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username exists
        if UserRepository.get_by_username(db, username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Check if phone exists
        if phone and UserRepository.get_by_phone(db, phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

        password_hash = get_password_hash(password)
        full_name = f"{first_name} {last_name}"

        user = UserRepository.create(
            db,
            {
                "email": email,
                "username": username,
                "password_hash": password_hash,
                "first_name": first_name,
                "last_name": last_name,
                "full_name": full_name,
                "phone": phone,
            },
        )

        # Assign roles
        if role_ids:
            for role_id in role_ids:
                UserRepository.assign_role(db, user.id, role_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "CREATE",
                "entity_type": "User",
                "entity_id": user.id,
                "new_values": json.dumps(
                    {
                        "email": user.email,
                        "username": user.username,
                        "first_name": user.first_name,
                    }
                ),
            },
        )

        return user

    @staticmethod
    def update_user(
        db: Session,
        user_id: UUID,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: Optional[bool] = None,
        role_ids: Optional[List[UUID]] = None,
    ) -> Optional[User]:
        """Update user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        old_values = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
        }

        update_data = {}
        if email and email != user.email:
            if UserRepository.get_by_email(db, email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            update_data["email"] = email

        if phone and phone != user.phone:
            if UserRepository.get_by_phone(db, phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number already registered",
                )
            update_data["phone"] = phone

        if first_name:
            update_data["first_name"] = first_name
        if last_name:
            update_data["last_name"] = last_name
        if is_active is not None:
            update_data["is_active"] = is_active

        if first_name or last_name:
            fname = first_name or user.first_name
            lname = last_name or user.last_name
            update_data["full_name"] = f"{fname} {lname}"

        user = UserRepository.update(db, user_id, update_data)

        # Update roles
        if role_ids is not None:
            # Remove all existing roles
            current_roles = user.roles.copy()
            for role in current_roles:
                UserRepository.remove_role(db, user_id, role.id)

            # Assign new roles
            for role_id in role_ids:
                UserRepository.assign_role(db, user_id, role_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "UPDATE",
                "entity_type": "User",
                "entity_id": user.id,
                "old_values": json.dumps(old_values),
                "new_values": json.dumps(update_data),
            },
        )

        return user

    @staticmethod
    def change_password(
        db: Session, user_id: UUID, old_password: str, new_password: str
    ) -> User:
        """Change user password."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if not verify_password(old_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid current password",
            )

        password_hash = get_password_hash(new_password)
        user = UserRepository.update(
            db,
            user_id,
            {
                "password_hash": password_hash,
                "password_changed_at": datetime.utcnow(),
            },
        )

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "user_id": user_id,
                "action": "PASSWORD_CHANGE",
                "entity_type": "User",
                "entity_id": user_id,
            },
        )

        return user

    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Soft delete user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        UserRepository.delete(db, user_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "DELETE",
                "entity_type": "User",
                "entity_id": user_id,
            },
        )

        return True

    @staticmethod
    def restore_user(db: Session, user_id: UUID) -> Optional[User]:
        """Restore soft deleted user."""
        user = UserRepository.restore(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "RESTORE",
                "entity_type": "User",
                "entity_id": user_id,
            },
        )

        return user

    @staticmethod
    def list_users(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """List users."""
        return UserRepository.list(
            db, skip=skip, limit=limit, search=search, is_active=is_active
        )

    @staticmethod
    def get_user(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user


class RoleService:
    """Role service."""

    @staticmethod
    def create_role(
        db: Session,
        name: str,
        description: Optional[str] = None,
        permission_ids: Optional[List[UUID]] = None,
    ) -> Role:
        """Create a new role."""
        if RoleRepository.get_by_name(db, name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already exists",
            )

        role = RoleRepository.create(
            db, {"name": name, "description": description}
        )

        if permission_ids:
            for permission_id in permission_ids:
                RoleRepository.assign_permission(db, role.id, permission_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "CREATE",
                "entity_type": "Role",
                "entity_id": role.id,
                "new_values": json.dumps({"name": role.name}),
            },
        )

        return role

    @staticmethod
    def update_role(
        db: Session,
        role_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_ids: Optional[List[UUID]] = None,
    ) -> Optional[Role]:
        """Update role."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update system roles",
            )

        update_data = {}
        if name and name != role.name:
            if RoleRepository.get_by_name(db, name):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role name already exists",
                )
            update_data["name"] = name

        if description is not None:
            update_data["description"] = description

        role = RoleRepository.update(db, role_id, update_data)

        if permission_ids is not None:
            current_permissions = role.permissions.copy()
            for permission in current_permissions:
                RoleRepository.remove_permission(db, role_id, permission.id)

            for permission_id in permission_ids:
                RoleRepository.assign_permission(db, role_id, permission_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "UPDATE",
                "entity_type": "Role",
                "entity_id": role_id,
                "new_values": json.dumps(update_data),
            },
        )

        return role

    @staticmethod
    def delete_role(db: Session, role_id: UUID) -> bool:
        """Delete role."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )

        if role.is_system_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system roles",
            )

        RoleRepository.delete(db, role_id)

        # Log audit
        AuditLogRepository.create(
            db,
            {
                "action": "DELETE",
                "entity_type": "Role",
                "entity_id": role_id,
            },
        )

        return True

    @staticmethod
    def list_roles(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
    ) -> tuple[List[Role], int]:
        """List roles."""
        return RoleRepository.list(db, skip=skip, limit=limit, search=search)

    @staticmethod
    def get_role(db: Session, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found",
            )
        return role
