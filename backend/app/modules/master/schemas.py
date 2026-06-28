from datetime import datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class DepartmentBase(BaseModel):
    """Base department schema."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    manager_id: Optional[str] = None
    status: str = "Active"
    display_order: int = 0


class DepartmentCreate(DepartmentBase):
    """Create department schema."""

    pass


class DepartmentUpdate(BaseModel):
    """Update department schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[str] = None
    status: Optional[str] = None
    display_order: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    """Department response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DesignationBase(BaseModel):
    """Base designation schema."""

    name: str = Field(..., min_length=1, max_length=200)
    department_id: str
    hierarchy_level: Optional[int] = None
    salary_grade: Optional[str] = None
    description: Optional[str] = None
    status: str = "Active"


class DesignationCreate(DesignationBase):
    """Create designation schema."""

    pass


class DesignationUpdate(BaseModel):
    """Update designation schema."""

    name: Optional[str] = None
    department_id: Optional[str] = None
    hierarchy_level: Optional[int] = None
    salary_grade: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class DesignationResponse(DesignationBase):
    """Designation response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShiftBase(BaseModel):
    """Base shift schema."""

    name: str = Field(..., min_length=1, max_length=200)
    shift_type: str  # Morning, Evening, Night, General, Custom
    start_time: time
    end_time: time
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    grace_time: int = 0
    working_hours: float
    weekly_off: Optional[str] = None
    status: str = "Active"


class ShiftCreate(ShiftBase):
    """Create shift schema."""

    pass


class ShiftUpdate(BaseModel):
    """Update shift schema."""

    name: Optional[str] = None
    shift_type: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    break_start: Optional[time] = None
    break_end: Optional[time] = None
    grace_time: Optional[int] = None
    working_hours: Optional[float] = None
    weekly_off: Optional[str] = None
    status: Optional[str] = None


class ShiftResponse(ShiftBase):
    """Shift response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MachineCategoryBase(BaseModel):
    """Base machine category schema."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = "Active"


class MachineCategoryCreate(MachineCategoryBase):
    """Create machine category schema."""

    pass


class MachineCategoryUpdate(BaseModel):
    """Update machine category schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


class MachineCategoryResponse(MachineCategoryBase):
    """Machine category response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MachineBase(BaseModel):
    """Base machine schema."""

    name: str = Field(..., min_length=1, max_length=200)
    category_id: str
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    capacity: Optional[float] = None
    speed: Optional[float] = None
    power_consumption: Optional[float] = None
    department_id: str
    production_line_id: Optional[str] = None
    current_operator_id: Optional[str] = None
    status: str = "Available"
    maintenance_status: str = "Good"
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    image_url: Optional[str] = None
    remarks: Optional[str] = None


class MachineCreate(MachineBase):
    """Create machine schema."""

    pass


class MachineUpdate(BaseModel):
    """Update machine schema."""

    name: Optional[str] = None
    category_id: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[datetime] = None
    warranty_expiry: Optional[datetime] = None
    capacity: Optional[float] = None
    speed: Optional[float] = None
    power_consumption: Optional[float] = None
    department_id: Optional[str] = None
    production_line_id: Optional[str] = None
    current_operator_id: Optional[str] = None
    status: Optional[str] = None
    maintenance_status: Optional[str] = None
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    image_url: Optional[str] = None
    remarks: Optional[str] = None


class MachineResponse(MachineBase):
    """Machine response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MachineMaintenanceBase(BaseModel):
    """Base machine maintenance schema."""

    machine_id: str
    maintenance_type: str  # Preventive, Corrective
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    technician_id: Optional[str] = None
    cost: Optional[float] = None
    remarks: Optional[str] = None
    attachment_url: Optional[str] = None
    status: str = "Scheduled"


class MachineMaintenanceCreate(MachineMaintenanceBase):
    """Create machine maintenance schema."""

    pass


class MachineMaintenanceUpdate(BaseModel):
    """Update machine maintenance schema."""

    machine_id: Optional[str] = None
    maintenance_type: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    technician_id: Optional[str] = None
    cost: Optional[float] = None
    remarks: Optional[str] = None
    attachment_url: Optional[str] = None
    status: Optional[str] = None


class MachineMaintenanceResponse(MachineMaintenanceBase):
    """Machine maintenance response schema."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductionLineBase(BaseModel):
    """Base production line schema."""

    name: str = Field(..., min_length=1, max_length=200)
    department_id: str
    supervisor_id: Optional[str] = None
    capacity: Optional[float] = None
    status: str = "Active"


class ProductionLineCreate(ProductionLineBase):
    """Create production line schema."""

    pass


class ProductionLineUpdate(BaseModel):
    """Update production line schema."""

    name: Optional[str] = None
    department_id: Optional[str] = None
    supervisor_id: Optional[str] = None
    capacity: Optional[float] = None
    status: Optional[str] = None


class ProductionLineResponse(ProductionLineBase):
    """Production line response schema."""

    id: str
    code: str
    machine_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OperationBase(BaseModel):
    """Base operation schema."""

    name: str = Field(..., min_length=1, max_length=200)
    department_id: str
    machine_category_id: Optional[str] = None
    estimated_time: Optional[float] = None
    sequence_order: Optional[int] = None
    standard_rate: Optional[float] = None
    description: Optional[str] = None
    status: str = "Active"


class OperationCreate(OperationBase):
    """Create operation schema."""

    pass


class OperationUpdate(BaseModel):
    """Update operation schema."""

    name: Optional[str] = None
    department_id: Optional[str] = None
    machine_category_id: Optional[str] = None
    estimated_time: Optional[float] = None
    sequence_order: Optional[int] = None
    standard_rate: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None


class OperationResponse(OperationBase):
    """Operation response schema."""

    id: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeMachineAssignmentBase(BaseModel):
    """Base employee machine assignment schema."""

    employee_id: str
    machine_id: str
    reason: Optional[str] = None
    status: str = "Active"


class EmployeeMachineAssignmentCreate(EmployeeMachineAssignmentBase):
    """Create employee machine assignment schema."""

    pass


class EmployeeMachineAssignmentUpdate(BaseModel):
    """Update employee machine assignment schema."""

    employee_id: Optional[str] = None
    machine_id: Optional[str] = None
    reason: Optional[str] = None
    status: Optional[str] = None


class EmployeeMachineAssignmentResponse(EmployeeMachineAssignmentBase):
    """Employee machine assignment response schema."""

    id: str
    assigned_date: datetime
    released_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeeOperationAssignmentBase(BaseModel):
    """Base employee operation assignment schema."""

    employee_id: str
    operation_id: str
    skill_level: Optional[str] = None
    efficiency: float = 100.0
    experience_years: float = 0
    certification: Optional[str] = None
    status: str = "Active"


class EmployeeOperationAssignmentCreate(EmployeeOperationAssignmentBase):
    """Create employee operation assignment schema."""

    pass


class EmployeeOperationAssignmentUpdate(BaseModel):
    """Update employee operation assignment schema."""

    employee_id: Optional[str] = None
    operation_id: Optional[str] = None
    skill_level: Optional[str] = None
    efficiency: Optional[float] = None
    experience_years: Optional[float] = None
    certification: Optional[str] = None
    status: Optional[str] = None


class EmployeeOperationAssignmentResponse(EmployeeOperationAssignmentBase):
    """Employee operation assignment response schema."""

    id: str
    assigned_date: datetime
    released_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    """Paginated response schema."""

    total: int
    page: int
    page_size: int
    total_pages: int
    items: List
