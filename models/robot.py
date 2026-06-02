from dataclasses import dataclass, field
from typing import Optional

from models.task import Position, Task


@dataclass
class Robot:
    robot_id: int
    current_position: Position
    target_position: Optional[Position] = None
    status: str = "idle"
    assigned_task: Optional[Task] = None
    route: list[Position] = field(default_factory=list)
    total_distance: int = 0
    active_time: int = 0
    waiting_time: int = 0
    blocked_count: int = 0

    def assign_task(self, task: Task, current_time: int) -> None:
        self.assigned_task = task
        self.target_position = task.pickup_location
        self.status = "to_pickup"
        self.route = []
        task.status = "assigned"
        task.assigned_robot_id = self.robot_id
        task.started_at = current_time

    def clear_task(self) -> None:
        self.assigned_task = None
        self.target_position = None
        self.status = "idle"
        self.route = []

    def restore_motion_status(self) -> None:
        if self.status != "waiting" or self.assigned_task is None:
            return
        if self.assigned_task.status == "assigned":
            self.status = "to_pickup"
        elif self.assigned_task.status == "picked_up":
            self.status = "to_delivery"

