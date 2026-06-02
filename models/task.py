from dataclasses import dataclass
from typing import Optional


Position = tuple[int, int]


@dataclass
class Task:
    task_id: int
    pickup_location: Position
    delivery_location: Position
    created_at: int = 0
    assigned_robot_id: Optional[int] = None
    started_at: Optional[int] = None
    completed_at: Optional[int] = None
    status: str = "waiting"

