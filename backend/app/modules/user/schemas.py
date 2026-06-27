from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


class PermissionBase(BaseModel):
    """Base permission schema."""

    name: str
    description: Optional[str] = None
    module: str
    action: str
    is_active: bool = True


class PermissionCreate(PermissionBase):
    """Create permission schema."""

    pass


class PermissionUpdate(BaseModel):
    """Update permission schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    module: Optional[str] = None
    action: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionResponse(PermissionBase):
    """Permission response schema."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role schema."""

    name: str
    description: Optional[str] = None
    is_active: bool = True


class RoleCreate(RoleBase):
    """Create role schema."""

    permission_ids: Optional[List[str]] = None


class RoleUpdate(BaseModel):
    """Update role schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """Role response schema."""

    id: str
    is_system_role: bool
    permissions: List[PermissionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None

    @field_validator("username")
    def validate_username(cls, v):
        if not v.isalnum() and "_" not in v and "-" not in v:
            raise ValueError("Username can only contain alphanumeric, underscore, and dash")
        return v


class UserCreate(UserBase):
    """Create user schema."""

    password: str = Field(..., min_length=8, max_length=100)
    role_ids: Optional[List[str]] = None

    @field_validator("password")
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "!@#$%^&*()-_=+" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserUpdate(BaseModel):
    """Update user schema."""

    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    role_ids: Optional[List[str]] = None


class UserProfileUpdate(BaseModel):
    """Update user profile schema."""

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPasswordChange(BaseModel):
    """Change password schema."""

    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "!@#$%^&*()-_=+" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserResponse(UserBase):
    """User response schema."""

    id: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    avatar_url: Optional[str]
    last_login_at: Optional[datetime]
    roles: List[RoleResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """User detail response schema."""

    password_changed_at: Optional[datetime]
    is_locked: bool

    class Config:
        from_attributes = True


class AuthRequest(BaseModel):
    """Authentication request schema."""

    username: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class AuthResponse(BaseModel):
    """Authentication response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str

    @field_validator("new_password")
    def validate_password(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char in "!@#$%^&*()-_=+" for char in v):
            raise ValueError("Password must contain at least one special character")
        return v


class AuditLogResponse(BaseModel):
    """Audit log response schema."""

    id: str
    user_id: Optional[str]
    action: str
    entity_type: str
    entity_id: str
    old_values: Optional[str]
    new_values: Optional[str]
    ip_address: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"


class PaginatedResponse(BaseModel):
    """Paginated response schema."""

    total: int
    page: int
    page_size: int
    total_pages: int
    items: List
