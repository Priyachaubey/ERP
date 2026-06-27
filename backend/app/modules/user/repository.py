from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.modules.user.models import User, Role, Permission, Session as SessionModel, AuditLog, PasswordReset


class UserRepository:
    """User repository for database operations."""

    @staticmethod
    def create(db: Session, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        user = User(**user_data)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id, User.is_deleted == False).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email, User.is_deleted == False).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username, User.is_deleted == False).first()

    @staticmethod
    def get_by_phone(db: Session, phone: str) -> Optional[User]:
        """Get user by phone."""
        return db.query(User).filter(User.phone == phone, User.is_deleted == False).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """List users with pagination and filtering."""
        query = db.query(User).filter(User.is_deleted == False)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                )
            )

        total = query.count()

        if sort_order == "desc":
            query = query.order_by(getattr(User, sort_by).desc())
        else:
            query = query.order_by(getattr(User, sort_by).asc())

        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, user_id: UUID, user_data: Dict[str, Any]) -> Optional[User]:
        """Update user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        for key, value in user_data.items():
            if value is not None:
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: UUID) -> bool:
        """Soft delete user."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            return False
        user.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def restore(db: Session, user_id: UUID) -> Optional[User]:
        """Restore soft deleted user."""
        user = db.query(User).filter(User.id == user_id, User.is_deleted == True).first()
        if not user:
            return None
        user.is_deleted = False
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def assign_role(db: Session, user_id: UUID, role_id: UUID) -> Optional[User]:
        """Assign role to user."""
        user = UserRepository.get_by_id(db, user_id)
        role = db.query(Role).filter(Role.id == role_id).first()
        if not user or not role:
            return None
        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)
        return user

    @staticmethod
    def remove_role(db: Session, user_id: UUID, role_id: UUID) -> Optional[User]:
        """Remove role from user."""
        user = UserRepository.get_by_id(db, user_id)
        role = db.query(Role).filter(Role.id == role_id).first()
        if not user or not role:
            return None
        if role in user.roles:
            user.roles.remove(role)
            db.commit()
            db.refresh(user)
        return user


class RoleRepository:
    """Role repository for database operations."""

    @staticmethod
    def create(db: Session, role_data: Dict[str, Any]) -> Role:
        """Create a new role."""
        role = Role(**role_data)
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def get_by_id(db: Session, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        return db.query(Role).filter(Role.id == role_id, Role.is_deleted == False).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Role]:
        """Get role by name."""
        return db.query(Role).filter(Role.name == name, Role.is_deleted == False).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Role], int]:
        """List roles with pagination."""
        query = db.query(Role).filter(Role.is_deleted == False)

        if is_active is not None:
            query = query.filter(Role.is_active == is_active)

        if search:
            query = query.filter(Role.name.ilike(f"%{search}%"))

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, role_id: UUID, role_data: Dict[str, Any]) -> Optional[Role]:
        """Update role."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            return None
        for key, value in role_data.items():
            if value is not None:
                setattr(role, key, value)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def delete(db: Session, role_id: UUID) -> bool:
        """Soft delete role."""
        role = RoleRepository.get_by_id(db, role_id)
        if not role:
            return False
        role.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def assign_permission(db: Session, role_id: UUID, permission_id: UUID) -> Optional[Role]:
        """Assign permission to role."""
        role = RoleRepository.get_by_id(db, role_id)
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not role or not permission:
            return None
        if permission not in role.permissions:
            role.permissions.append(permission)
            db.commit()
            db.refresh(role)
        return role

    @staticmethod
    def remove_permission(db: Session, role_id: UUID, permission_id: UUID) -> Optional[Role]:
        """Remove permission from role."""
        role = RoleRepository.get_by_id(db, role_id)
        permission = db.query(Permission).filter(Permission.id == permission_id).first()
        if not role or not permission:
            return None
        if permission in role.permissions:
            role.permissions.remove(permission)
            db.commit()
            db.refresh(role)
        return role


class PermissionRepository:
    """Permission repository for database operations."""

    @staticmethod
    def create(db: Session, permission_data: Dict[str, Any]) -> Permission:
        """Create a new permission."""
        permission = Permission(**permission_data)
        db.add(permission)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def get_by_id(db: Session, permission_id: UUID) -> Optional[Permission]:
        """Get permission by ID."""
        return db.query(Permission).filter(Permission.id == permission_id, Permission.is_deleted == False).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Permission]:
        """Get permission by name."""
        return db.query(Permission).filter(Permission.name == name, Permission.is_deleted == False).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        module: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Permission], int]:
        """List permissions with pagination."""
        query = db.query(Permission).filter(Permission.is_deleted == False)

        if module:
            query = query.filter(Permission.module == module)

        if is_active is not None:
            query = query.filter(Permission.is_active == is_active)

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, permission_id: UUID, permission_data: Dict[str, Any]) -> Optional[Permission]:
        """Update permission."""
        permission = PermissionRepository.get_by_id(db, permission_id)
        if not permission:
            return None
        for key, value in permission_data.items():
            if value is not None:
                setattr(permission, key, value)
        db.commit()
        db.refresh(permission)
        return permission

    @staticmethod
    def delete(db: Session, permission_id: UUID) -> bool:
        """Soft delete permission."""
        permission = PermissionRepository.get_by_id(db, permission_id)
        if not permission:
            return False
        permission.is_deleted = True
        db.commit()
        return True


class SessionRepository:
    """Session repository for database operations."""

    @staticmethod
    def create(db: Session, session_data: Dict[str, Any]) -> SessionModel:
        """Create a new session."""
        session = SessionModel(**session_data)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def get_by_id(db: Session, session_id: UUID) -> Optional[SessionModel]:
        """Get session by ID."""
        return db.query(SessionModel).filter(
            SessionModel.id == session_id,
            SessionModel.is_revoked == False
        ).first()

    @staticmethod
    def get_by_user_id(db: Session, user_id: UUID) -> List[SessionModel]:
        """Get all active sessions for a user."""
        return db.query(SessionModel).filter(
            SessionModel.user_id == user_id,
            SessionModel.is_revoked == False
        ).all()

    @staticmethod
    def revoke(db: Session, session_id: UUID) -> bool:
        """Revoke a session."""
        from datetime import datetime
        session = SessionRepository.get_by_id(db, session_id)
        if not session:
            return False
        session.is_revoked = True
        session.revoked_at = datetime.utcnow()
        db.commit()
        return True

    @staticmethod
    def revoke_all_user_sessions(db: Session, user_id: UUID) -> bool:
        """Revoke all sessions for a user."""
        from datetime import datetime
        sessions = SessionRepository.get_by_user_id(db, user_id)
        for session in sessions:
            session.is_revoked = True
            session.revoked_at = datetime.utcnow()
        db.commit()
        return True


class AuditLogRepository:
    """Audit log repository for database operations."""

    @staticmethod
    def create(db: Session, audit_data: Dict[str, Any]) -> AuditLog:
        """Create audit log entry."""
        audit = AuditLog(**audit_data)
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit

    @staticmethod
    def get_by_id(db: Session, audit_id: UUID) -> Optional[AuditLog]:
        """Get audit log by ID."""
        return db.query(AuditLog).filter(AuditLog.id == audit_id).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        entity_type: Optional[str] = None,
        entity_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        action: Optional[str] = None,
    ) -> tuple[List[AuditLog], int]:
        """List audit logs with filtering."""
        query = db.query(AuditLog)

        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)

        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        if action:
            query = query.filter(AuditLog.action == action)

        total = query.count()
        items = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        return items, total


class PasswordResetRepository:
    """Password reset repository for database operations."""

    @staticmethod
    def create(db: Session, reset_data: Dict[str, Any]) -> PasswordReset:
        """Create password reset token."""
        reset = PasswordReset(**reset_data)
        db.add(reset)
        db.commit()
        db.refresh(reset)
        return reset

    @staticmethod
    def get_by_token(db: Session, token: str) -> Optional[PasswordReset]:
        """Get password reset by token."""
        return db.query(PasswordReset).filter(
            PasswordReset.token == token,
            PasswordReset.is_used == False
        ).first()

    @staticmethod
    def mark_as_used(db: Session, reset_id: UUID) -> bool:
        """Mark password reset as used."""
        reset = db.query(PasswordReset).filter(PasswordReset.id == reset_id).first()
        if not reset:
            return False
        reset.is_used = True
        db.commit()
        return True
