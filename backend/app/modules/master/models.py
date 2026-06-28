from datetime import datetime, time
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Time,
    Table,
    Index,
    CheckConstraint,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import uuid

# Association tables
machine_operation_association = Table(
    "machine_operation_association",
    BaseModel.metadata,
    Column("machine_id", UUID(as_uuid=True), ForeignKey("machine.id")),
    Column("operation_id", UUID(as_uuid=True), ForeignKey("operation.id")),
)

operation_sequence_association = Table(
    "operation_sequence_association",
    BaseModel.metadata,
    Column("product_id", UUID(as_uuid=True)),
    Column("operation_id", UUID(as_uuid=True), ForeignKey("operation.id")),
)


class Department(BaseModel):
    """Department Master model."""

    __tablename__ = "department"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    display_order = Column(Integer, default=0, nullable=False)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    designations = relationship("Designation", backref="department", lazy="select")
    machines = relationship("Machine", backref="department", lazy="select")
    lines = relationship("ProductionLine", backref="department", lazy="select")
    operations = relationship("Operation", backref="department", lazy="select")

    __table_args__ = (
        Index("idx_department_code", "code"),
        Index("idx_department_status", "status"),
        Index("idx_department_name", "name"),
    )


class Designation(BaseModel):
    """Designation Master model."""

    __tablename__ = "designation"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)
    hierarchy_level = Column(Integer, nullable=True)
    salary_grade = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_designation_code", "code"),
        Index("idx_designation_department_id", "department_id"),
        Index("idx_designation_status", "status"),
    )


class Shift(BaseModel):
    """Shift Master model."""

    __tablename__ = "shift"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    shift_type = Column(String(50), nullable=False)  # Morning, Evening, Night, General, Custom
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    break_start = Column(Time, nullable=True)
    break_end = Column(Time, nullable=True)
    grace_time = Column(Integer, default=0, nullable=False)  # in minutes
    working_hours = Column(Float, nullable=False)
    weekly_off = Column(String(20), nullable=True)  # Day of week
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_shift_code", "code"),
        Index("idx_shift_shift_type", "shift_type"),
        Index("idx_shift_status", "status"),
    )


class MachineCategory(BaseModel):
    """Machine Category model."""

    __tablename__ = "machine_category"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    machines = relationship("Machine", backref="category", lazy="select")

    __table_args__ = (
        Index("idx_machine_category_code", "code"),
        Index("idx_machine_category_status", "status"),
    )


class Machine(BaseModel):
    """Machine Master model."""

    __tablename__ = "machine"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("machine_category.id"), nullable=False)
    brand = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    serial_number = Column(String(100), unique=True, nullable=True, index=True)
    purchase_date = Column(DateTime, nullable=True)
    warranty_expiry = Column(DateTime, nullable=True)
    capacity = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)  # units per minute
    power_consumption = Column(Float, nullable=True)  # in KW
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)
    production_line_id = Column(UUID(as_uuid=True), ForeignKey("production_line.id"), nullable=True)
    current_operator_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    status = Column(String(20), default="Available", nullable=False, index=True)
    maintenance_status = Column(String(20), default="Good", nullable=False)
    barcode = Column(String(100), unique=True, nullable=True)
    qr_code = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    remarks = Column(Text, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    maintenance_records = relationship("MachineMaintenance", backref="machine", lazy="select")
    assignments = relationship("EmployeeMachineAssignment", backref="machine", lazy="select")
    operations = relationship(
        "Operation",
        secondary=machine_operation_association,
        backref="machines",
        lazy="select",
    )

    __table_args__ = (
        Index("idx_machine_code", "code"),
        Index("idx_machine_department_id", "department_id"),
        Index("idx_machine_status", "status"),
        Index("idx_machine_serial_number", "serial_number"),
    )


class MachineMaintenance(BaseModel):
    """Machine Maintenance model."""

    __tablename__ = "machine_maintenance"

    machine_id = Column(UUID(as_uuid=True), ForeignKey("machine.id"), nullable=False)
    maintenance_type = Column(String(50), nullable=False)  # Preventive, Corrective
    scheduled_date = Column(DateTime, nullable=False, index=True)
    completed_date = Column(DateTime, nullable=True)
    technician_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    cost = Column(Float, nullable=True)
    remarks = Column(Text, nullable=True)
    attachment_url = Column(String(500), nullable=True)
    status = Column(String(20), default="Scheduled", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_machine_maintenance_machine_id", "machine_id"),
        Index("idx_machine_maintenance_scheduled_date", "scheduled_date"),
        Index("idx_machine_maintenance_status", "status"),
    )


class ProductionLine(BaseModel):
    """Production Line Master model."""

    __tablename__ = "production_line"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)
    supervisor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    capacity = Column(Float, nullable=True)
    machine_count = Column(Integer, default=0, nullable=False)
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    machines = relationship("Machine", backref="line", lazy="select")

    __table_args__ = (
        Index("idx_production_line_code", "code"),
        Index("idx_production_line_department_id", "department_id"),
        Index("idx_production_line_status", "status"),
    )


class Operation(BaseModel):
    """Operation Master model."""

    __tablename__ = "operation"

    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("department.id"), nullable=False)
    machine_category_id = Column(UUID(as_uuid=True), ForeignKey("machine_category.id"), nullable=True)
    estimated_time = Column(Float, nullable=True)  # in minutes
    sequence_order = Column(Integer, nullable=True)
    standard_rate = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    assignments = relationship("EmployeeOperationAssignment", backref="operation", lazy="select")

    __table_args__ = (
        Index("idx_operation_code", "code"),
        Index("idx_operation_department_id", "department_id"),
        Index("idx_operation_sequence_order", "sequence_order"),
        Index("idx_operation_status", "status"),
    )


class EmployeeMachineAssignment(BaseModel):
    """Employee Machine Assignment model."""

    __tablename__ = "employee_machine_assignment"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    machine_id = Column(UUID(as_uuid=True), ForeignKey("machine.id"), nullable=False)
    assigned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    released_date = Column(DateTime, nullable=True)
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_employee_machine_assignment_employee_id", "employee_id"),
        Index("idx_employee_machine_assignment_machine_id", "machine_id"),
        Index("idx_employee_machine_assignment_status", "status"),
    )


class EmployeeOperationAssignment(BaseModel):
    """Employee Operation Assignment model."""

    __tablename__ = "employee_operation_assignment"

    employee_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    operation_id = Column(UUID(as_uuid=True), ForeignKey("operation.id"), nullable=False)
    skill_level = Column(String(50), nullable=True)  # Beginner, Intermediate, Expert
    efficiency = Column(Float, default=100.0, nullable=False)  # percentage
    experience_years = Column(Float, default=0, nullable=False)
    certification = Column(String(200), nullable=True)
    status = Column(String(20), default="Active", nullable=False, index=True)
    assigned_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    released_date = Column(DateTime, nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (
        Index("idx_employee_operation_assignment_employee_id", "employee_id"),
        Index("idx_employee_operation_assignment_operation_id", "operation_id"),
        Index("idx_employee_operation_assignment_status", "status"),
    )
