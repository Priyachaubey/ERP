from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
    Index,
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid

# Association table for role-permission relationship
role_permission_association = Table(
    "role_permission_association",
    BaseModel.metadata,
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id")),
    Column("permission_id", UUID(as_uuid=True), ForeignKey("permission.id")),
)

# Association table for user-role relationship
user_role_association = Table(
    "user_role_association",
    BaseModel.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("user.id")),
    Column("role_id", UUID(as_uuid=True), ForeignKey("role.id")),
)


class Permission(BaseModel):
    """Permission model."""

    __tablename__ = "permission"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    module = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("idx_permission_module_action", "module", "action"),
        Index("idx_permission_is_active", "is_active"),
    )


class Role(BaseModel):
    """Role model."""

    __tablename__ = "role"

    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(String(500), nullable=True)
    is_system_role = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    permissions = relationship(
        "Permission",
        secondary=role_permission_association,
        backref="roles",
        lazy="joined",
    )
    users = relationship(
        "User", secondary=user_role_association, backref="roles", lazy="joined"
    )

    __table_args__ = (
        Index("idx_role_name", "name"),
        Index("idx_role_is_active", "is_active"),
    )


class User(BaseModel):
    """User model."""

    __tablename__ = "user"

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, nullable=True)
    login_attempts = Column(String(50), default="0", nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    locked_until = Column(DateTime, nullable=True)

    sessions = relationship("Session", backref="user", lazy="select")
    audit_logs = relationship("AuditLog", backref="user", lazy="select")

    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_username", "username"),
        Index("idx_user_is_active", "is_active"),
        CheckConstraint("email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}$'"),
    )


class Session(BaseModel):
    """User session model."""

    __tablename__ = "session"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    refresh_token = Column(String(500), nullable=False)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("idx_session_user_id", "user_id"),
        Index("idx_session_is_revoked", "is_revoked"),
        Index("idx_session_expires_at", "expires_at"),
    )


class AuditLog(BaseModel):
    """Audit log model."""

    __tablename__ = "audit_log"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    action = Column(String(50), nullable=False, index=True)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    old_values = Column(String(2000), nullable=True)
    new_values = Column(String(2000), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status = Column(String(20), default="success", nullable=False)
    error_message = Column(String(500), nullable=True)

    __table_args__ = (
        Index("idx_audit_log_action", "action"),
        Index("idx_audit_log_entity", "entity_type", "entity_id"),
        Index("idx_audit_log_user_id", "user_id"),
        Index("idx_audit_log_created_at", "created_at"),
    )


class PasswordReset(BaseModel):
    """Password reset token model."""

    __tablename__ = "password_reset"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    is_used = Column(Boolean, default=False, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index("idx_password_reset_user_id", "user_id"),
        Index("idx_password_reset_token", "token"),
        Index("idx_password_reset_is_used", "is_used"),
    )
