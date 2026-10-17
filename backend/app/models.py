
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Self
from pydantic import BaseModel, ConfigDict, ValidationError, computed_field, model_validator, Field, AwareDatetime

class MachineStatus(str, Enum):
    RUNNING = "running"
    DOWN = "down"
    MAINTENANCE = "maintenance"

class MaintenanceType(str, Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class WorkOrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    
MachineCode = Annotated[str, Field(pattern=r"^[A-Z]{3}-[0-9]{3}$")]

class Machine(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    code: MachineCode
    name: str = Field(max_length=100, min_length=1)
    machine_type: str = Field(max_length=50, min_length=1)
    line: str = Field(max_length=50, min_length=1)
    status: MachineStatus
    operating_hours: float = Field(ge=0)
    
class WorkOrder(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    machine_code: MachineCode
    title: str = Field(max_length=120, min_length=3)
    description: str = Field(max_length=255, min_length=1)
    maintenance_type: MaintenanceType
    priority: Priority
    status: WorkOrderStatus = Field(default=WorkOrderStatus.OPEN)
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: AwareDatetime | None = Field(default=None)
    
    @model_validator(mode="after")
    def validate_completed_at(self) -> Self:
        if self.status is WorkOrderStatus.DONE and self.completed_at is None:
            raise ValueError("completed_at wajib diisi untuk work order berstatus done")
        if self.status is not WorkOrderStatus.DONE and self.completed_at is not None:
            raise ValueError(f"completed_at harus kosong untuk work order berstatus {self.status.value}")
        if self.status is WorkOrderStatus.DONE and self.created_at>self.completed_at:
                raise ValueError(
    f"completed_at ({self.completed_at}) tidak boleh lebih awal dari created_at ({self.created_at})"
)
        return self
    
    @computed_field
    @property
    def duration_hours(self) -> float | None:
        if self.completed_at:
            duration = (self.completed_at - self.created_at).total_seconds() / 3600
            return round(duration, 2)
        return None
    

if __name__ == "__main__":
    jam_08 = datetime(2026, 10, 17, 8, 0, tzinfo=timezone.utc)
    jam_10 = datetime(2026, 10, 17, 10, 0, tzinfo=timezone.utc)
    
    def coba(label: str, fungsi) -> object:
        try:
            hasil = fungsi()
            print(f"✅ DITERIMA  | {label}")
            return hasil
        except ValidationError as e:
            pesan = e.errors()[0]["msg"]
            print(f"❌ DITOLAK   | {label} → {pesan}")