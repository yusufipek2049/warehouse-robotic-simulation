from models.robot import Robot
from models.task import Task


def calculate_summary(robot_count: int, total_time: int, robots: list[Robot], tasks: list[Task]) -> dict[str, float | int]:
    completed_tasks = [task for task in tasks if task.status == "completed" and task.completed_at is not None]
    if not completed_tasks:
        raise ValueError("Metrics require at least one completed task.")

    completion_times = [task.completed_at - task.created_at for task in completed_tasks]
    total_active_time = sum(robot.active_time for robot in robots)
    total_waiting_time = sum(robot.waiting_time for robot in robots)
    total_distance = sum(robot.total_distance for robot in robots)
    blocked_count = sum(robot.blocked_count for robot in robots)

    denominator = max(total_time, 1)
    return {
        "robot_count": robot_count,
        "completed_tasks": len(completed_tasks),
        "total_completion_time": total_time,
        "average_task_completion_time": sum(completion_times) / len(completion_times),
        "throughput": len(completed_tasks) / denominator,
        "robot_utilization": total_active_time / (len(robots) * denominator),
        "average_waiting_time": total_waiting_time / len(robots),
        "total_distance": total_distance,
        "blocked_waiting_count": blocked_count,
    }

