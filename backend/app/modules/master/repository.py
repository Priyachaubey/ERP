from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from app.modules.master.models import (
    Department,
    Designation,
    Shift,
    Machine,
    MachineCategory,
    MachineMaintenance,
    ProductionLine,
    Operation,
    EmployeeMachineAssignment,
    EmployeeOperationAssignment,
)


class DepartmentRepository:
    """Department repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Department:
        """Create department."""
        dept = Department(**data)
        db.add(dept)
        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def get_by_id(db: Session, dept_id: UUID) -> Optional[Department]:
        """Get department by ID."""
        return db.query(Department).filter(
            Department.id == dept_id,
            Department.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Department]:
        """Get department by code."""
        return db.query(Department).filter(
            Department.code == code,
            Department.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[List[Department], int]:
        """List departments."""
        query = db.query(Department).filter(Department.is_deleted == False)

        if status:
            query = query.filter(Department.status == status)

        if search:
            query = query.filter(
                or_(
                    Department.name.ilike(f"%{search}%"),
                    Department.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(Department.display_order, Department.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, dept_id: UUID, data: Dict[str, Any]) -> Optional[Department]:
        """Update department."""
        dept = DepartmentRepository.get_by_id(db, dept_id)
        if not dept:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(dept, key, value)
        db.commit()
        db.refresh(dept)
        return dept

    @staticmethod
    def delete(db: Session, dept_id: UUID) -> bool:
        """Soft delete department."""
        dept = DepartmentRepository.get_by_id(db, dept_id)
        if not dept:
            return False
        dept.is_deleted = True
        db.commit()
        return True

    @staticmethod
    def restore(db: Session, dept_id: UUID) -> Optional[Department]:
        """Restore department."""
        dept = db.query(Department).filter(
            Department.id == dept_id,
            Department.is_deleted == True
        ).first()
        if not dept:
            return None
        dept.is_deleted = False
        db.commit()
        db.refresh(dept)
        return dept


class DesignationRepository:
    """Designation repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Designation:
        """Create designation."""
        desig = Designation(**data)
        db.add(desig)
        db.commit()
        db.refresh(desig)
        return desig

    @staticmethod
    def get_by_id(db: Session, desig_id: UUID) -> Optional[Designation]:
        """Get designation by ID."""
        return db.query(Designation).filter(
            Designation.id == desig_id,
            Designation.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Designation]:
        """Get designation by code."""
        return db.query(Designation).filter(
            Designation.code == code,
            Designation.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        department_id: Optional[UUID] = None,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[List[Designation], int]:
        """List designations."""
        query = db.query(Designation).filter(Designation.is_deleted == False)

        if department_id:
            query = query.filter(Designation.department_id == department_id)

        if status:
            query = query.filter(Designation.status == status)

        if search:
            query = query.filter(
                or_(
                    Designation.name.ilike(f"%{search}%"),
                    Designation.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(Designation.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, desig_id: UUID, data: Dict[str, Any]) -> Optional[Designation]:
        """Update designation."""
        desig = DesignationRepository.get_by_id(db, desig_id)
        if not desig:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(desig, key, value)
        db.commit()
        db.refresh(desig)
        return desig

    @staticmethod
    def delete(db: Session, desig_id: UUID) -> bool:
        """Soft delete designation."""
        desig = DesignationRepository.get_by_id(db, desig_id)
        if not desig:
            return False
        desig.is_deleted = True
        db.commit()
        return True


class ShiftRepository:
    """Shift repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Shift:
        """Create shift."""
        shift = Shift(**data)
        db.add(shift)
        db.commit()
        db.refresh(shift)
        return shift

    @staticmethod
    def get_by_id(db: Session, shift_id: UUID) -> Optional[Shift]:
        """Get shift by ID."""
        return db.query(Shift).filter(
            Shift.id == shift_id,
            Shift.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Shift]:
        """Get shift by code."""
        return db.query(Shift).filter(
            Shift.code == code,
            Shift.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[List[Shift], int]:
        """List shifts."""
        query = db.query(Shift).filter(Shift.is_deleted == False)

        if status:
            query = query.filter(Shift.status == status)

        if search:
            query = query.filter(
                or_(
                    Shift.name.ilike(f"%{search}%"),
                    Shift.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(Shift.start_time).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, shift_id: UUID, data: Dict[str, Any]) -> Optional[Shift]:
        """Update shift."""
        shift = ShiftRepository.get_by_id(db, shift_id)
        if not shift:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(shift, key, value)
        db.commit()
        db.refresh(shift)
        return shift

    @staticmethod
    def delete(db: Session, shift_id: UUID) -> bool:
        """Soft delete shift."""
        shift = ShiftRepository.get_by_id(db, shift_id)
        if not shift:
            return False
        shift.is_deleted = True
        db.commit()
        return True


class MachineCategoryRepository:
    """Machine category repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> MachineCategory:
        """Create machine category."""
        category = MachineCategory(**data)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_by_id(db: Session, cat_id: UUID) -> Optional[MachineCategory]:
        """Get machine category by ID."""
        return db.query(MachineCategory).filter(
            MachineCategory.id == cat_id,
            MachineCategory.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[MachineCategory]:
        """Get machine category by code."""
        return db.query(MachineCategory).filter(
            MachineCategory.code == code,
            MachineCategory.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[List[MachineCategory], int]:
        """List machine categories."""
        query = db.query(MachineCategory).filter(MachineCategory.is_deleted == False)

        if status:
            query = query.filter(MachineCategory.status == status)

        if search:
            query = query.filter(
                or_(
                    MachineCategory.name.ilike(f"%{search}%"),
                    MachineCategory.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(MachineCategory.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, cat_id: UUID, data: Dict[str, Any]) -> Optional[MachineCategory]:
        """Update machine category."""
        category = MachineCategoryRepository.get_by_id(db, cat_id)
        if not category:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete(db: Session, cat_id: UUID) -> bool:
        """Soft delete machine category."""
        category = MachineCategoryRepository.get_by_id(db, cat_id)
        if not category:
            return False
        category.is_deleted = True
        db.commit()
        return True


class MachineRepository:
    """Machine repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Machine:
        """Create machine."""
        machine = Machine(**data)
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine

    @staticmethod
    def get_by_id(db: Session, machine_id: UUID) -> Optional[Machine]:
        """Get machine by ID."""
        return db.query(Machine).filter(
            Machine.id == machine_id,
            Machine.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Machine]:
        """Get machine by code."""
        return db.query(Machine).filter(
            Machine.code == code,
            Machine.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        department_id: Optional[UUID] = None,
        line_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Machine], int]:
        """List machines."""
        query = db.query(Machine).filter(Machine.is_deleted == False)

        if department_id:
            query = query.filter(Machine.department_id == department_id)

        if line_id:
            query = query.filter(Machine.production_line_id == line_id)

        if status:
            query = query.filter(Machine.status == status)

        if search:
            query = query.filter(
                or_(
                    Machine.name.ilike(f"%{search}%"),
                    Machine.code.ilike(f"%{search}%"),
                    Machine.serial_number.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(Machine.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, machine_id: UUID, data: Dict[str, Any]) -> Optional[Machine]:
        """Update machine."""
        machine = MachineRepository.get_by_id(db, machine_id)
        if not machine:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(machine, key, value)
        db.commit()
        db.refresh(machine)
        return machine

    @staticmethod
    def delete(db: Session, machine_id: UUID) -> bool:
        """Soft delete machine."""
        machine = MachineRepository.get_by_id(db, machine_id)
        if not machine:
            return False
        machine.is_deleted = True
        db.commit()
        return True


class MachineMaintenanceRepository:
    """Machine maintenance repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> MachineMaintenance:
        """Create machine maintenance."""
        maintenance = MachineMaintenance(**data)
        db.add(maintenance)
        db.commit()
        db.refresh(maintenance)
        return maintenance

    @staticmethod
    def get_by_id(db: Session, maint_id: UUID) -> Optional[MachineMaintenance]:
        """Get machine maintenance by ID."""
        return db.query(MachineMaintenance).filter(
            MachineMaintenance.id == maint_id,
            MachineMaintenance.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        machine_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[List[MachineMaintenance], int]:
        """List machine maintenance records."""
        query = db.query(MachineMaintenance).filter(MachineMaintenance.is_deleted == False)

        if machine_id:
            query = query.filter(MachineMaintenance.machine_id == machine_id)

        if status:
            query = query.filter(MachineMaintenance.status == status)

        total = query.count()
        items = query.order_by(MachineMaintenance.scheduled_date.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, maint_id: UUID, data: Dict[str, Any]) -> Optional[MachineMaintenance]:
        """Update machine maintenance."""
        maintenance = MachineMaintenanceRepository.get_by_id(db, maint_id)
        if not maintenance:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(maintenance, key, value)
        db.commit()
        db.refresh(maintenance)
        return maintenance


class ProductionLineRepository:
    """Production line repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> ProductionLine:
        """Create production line."""
        line = ProductionLine(**data)
        db.add(line)
        db.commit()
        db.refresh(line)
        return line

    @staticmethod
    def get_by_id(db: Session, line_id: UUID) -> Optional[ProductionLine]:
        """Get production line by ID."""
        return db.query(ProductionLine).filter(
            ProductionLine.id == line_id,
            ProductionLine.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[ProductionLine]:
        """Get production line by code."""
        return db.query(ProductionLine).filter(
            ProductionLine.code == code,
            ProductionLine.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        department_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[ProductionLine], int]:
        """List production lines."""
        query = db.query(ProductionLine).filter(ProductionLine.is_deleted == False)

        if department_id:
            query = query.filter(ProductionLine.department_id == department_id)

        if status:
            query = query.filter(ProductionLine.status == status)

        if search:
            query = query.filter(
                or_(
                    ProductionLine.name.ilike(f"%{search}%"),
                    ProductionLine.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(ProductionLine.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, line_id: UUID, data: Dict[str, Any]) -> Optional[ProductionLine]:
        """Update production line."""
        line = ProductionLineRepository.get_by_id(db, line_id)
        if not line:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(line, key, value)
        db.commit()
        db.refresh(line)
        return line

    @staticmethod
    def delete(db: Session, line_id: UUID) -> bool:
        """Soft delete production line."""
        line = ProductionLineRepository.get_by_id(db, line_id)
        if not line:
            return False
        line.is_deleted = True
        db.commit()
        return True


class OperationRepository:
    """Operation repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> Operation:
        """Create operation."""
        operation = Operation(**data)
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return operation

    @staticmethod
    def get_by_id(db: Session, op_id: UUID) -> Optional[Operation]:
        """Get operation by ID."""
        return db.query(Operation).filter(
            Operation.id == op_id,
            Operation.is_deleted == False
        ).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Operation]:
        """Get operation by code."""
        return db.query(Operation).filter(
            Operation.code == code,
            Operation.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        department_id: Optional[UUID] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[List[Operation], int]:
        """List operations."""
        query = db.query(Operation).filter(Operation.is_deleted == False)

        if department_id:
            query = query.filter(Operation.department_id == department_id)

        if status:
            query = query.filter(Operation.status == status)

        if search:
            query = query.filter(
                or_(
                    Operation.name.ilike(f"%{search}%"),
                    Operation.code.ilike(f"%{search}%"),
                )
            )

        total = query.count()
        items = query.order_by(Operation.sequence_order, Operation.name).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, op_id: UUID, data: Dict[str, Any]) -> Optional[Operation]:
        """Update operation."""
        operation = OperationRepository.get_by_id(db, op_id)
        if not operation:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(operation, key, value)
        db.commit()
        db.refresh(operation)
        return operation

    @staticmethod
    def delete(db: Session, op_id: UUID) -> bool:
        """Soft delete operation."""
        operation = OperationRepository.get_by_id(db, op_id)
        if not operation:
            return False
        operation.is_deleted = True
        db.commit()
        return True


class EmployeeMachineAssignmentRepository:
    """Employee machine assignment repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> EmployeeMachineAssignment:
        """Create assignment."""
        assignment = EmployeeMachineAssignment(**data)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_by_id(db: Session, assign_id: UUID) -> Optional[EmployeeMachineAssignment]:
        """Get assignment by ID."""
        return db.query(EmployeeMachineAssignment).filter(
            EmployeeMachineAssignment.id == assign_id,
            EmployeeMachineAssignment.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        employee_id: Optional[UUID] = None,
        machine_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[List[EmployeeMachineAssignment], int]:
        """List assignments."""
        query = db.query(EmployeeMachineAssignment).filter(EmployeeMachineAssignment.is_deleted == False)

        if employee_id:
            query = query.filter(EmployeeMachineAssignment.employee_id == employee_id)

        if machine_id:
            query = query.filter(EmployeeMachineAssignment.machine_id == machine_id)

        if status:
            query = query.filter(EmployeeMachineAssignment.status == status)

        total = query.count()
        items = query.order_by(EmployeeMachineAssignment.assigned_date.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, assign_id: UUID, data: Dict[str, Any]) -> Optional[EmployeeMachineAssignment]:
        """Update assignment."""
        assignment = EmployeeMachineAssignmentRepository.get_by_id(db, assign_id)
        if not assignment:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(assignment, key, value)
        db.commit()
        db.refresh(assignment)
        return assignment


class EmployeeOperationAssignmentRepository:
    """Employee operation assignment repository."""

    @staticmethod
    def create(db: Session, data: Dict[str, Any]) -> EmployeeOperationAssignment:
        """Create assignment."""
        assignment = EmployeeOperationAssignment(**data)
        db.add(assignment)
        db.commit()
        db.refresh(assignment)
        return assignment

    @staticmethod
    def get_by_id(db: Session, assign_id: UUID) -> Optional[EmployeeOperationAssignment]:
        """Get assignment by ID."""
        return db.query(EmployeeOperationAssignment).filter(
            EmployeeOperationAssignment.id == assign_id,
            EmployeeOperationAssignment.is_deleted == False
        ).first()

    @staticmethod
    def list(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        employee_id: Optional[UUID] = None,
        operation_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> tuple[List[EmployeeOperationAssignment], int]:
        """List assignments."""
        query = db.query(EmployeeOperationAssignment).filter(EmployeeOperationAssignment.is_deleted == False)

        if employee_id:
            query = query.filter(EmployeeOperationAssignment.employee_id == employee_id)

        if operation_id:
            query = query.filter(EmployeeOperationAssignment.operation_id == operation_id)

        if status:
            query = query.filter(EmployeeOperationAssignment.status == status)

        total = query.count()
        items = query.order_by(EmployeeOperationAssignment.assigned_date.desc()).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update(db: Session, assign_id: UUID, data: Dict[str, Any]) -> Optional[EmployeeOperationAssignment]:
        """Update assignment."""
        assignment = EmployeeOperationAssignmentRepository.get_by_id(db, assign_id)
        if not assignment:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(assignment, key, value)
        db.commit()
        db.refresh(assignment)
        return assignment
