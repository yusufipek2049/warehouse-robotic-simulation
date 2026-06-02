from models.robot import Robot
from models.task import Position


def resolve_moves(
    robots: list[Robot],
    desired_moves: dict[int, Position | None],
) -> tuple[dict[int, Position], set[int]]:
    current_positions = {robot.current_position: robot.robot_id for robot in robots}
    target_requests: dict[Position, list[int]] = {}
    for robot_id, target in desired_moves.items():
        if target is not None:
            target_requests.setdefault(target, []).append(robot_id)

    winning_robot_by_target = {
        target: min(robot_ids)
        for target, robot_ids in target_requests.items()
    }

    allowed_moves: dict[int, Position] = {}
    blocked_robot_ids: set[int] = set()

    for robot in robots:
        target = desired_moves.get(robot.robot_id)
        if target is None:
            continue

        occupant_id = current_positions.get(target)
        occupant_target = desired_moves.get(occupant_id) if occupant_id is not None else None
        is_position_swap = (
            occupant_id is not None
            and occupant_id != robot.robot_id
            and occupant_target == robot.current_position
        )
        occupant_is_moving_to_empty_cell = (
            occupant_id is not None
            and occupant_id != robot.robot_id
            and occupant_target is not None
            and occupant_target not in current_positions
            and winning_robot_by_target.get(occupant_target) == occupant_id
        )
        target_is_occupied_by_other = (
            occupant_id is not None
            and occupant_id != robot.robot_id
            and not is_position_swap
            and not occupant_is_moving_to_empty_cell
        )
        target_won_by_other = winning_robot_by_target[target] != robot.robot_id

        if target_is_occupied_by_other or target_won_by_other:
            blocked_robot_ids.add(robot.robot_id)
        else:
            allowed_moves[robot.robot_id] = target

    return allowed_moves, blocked_robot_ids
