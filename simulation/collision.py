from models.robot import Robot
from models.task import Position


def resolve_moves(
    robots: list[Robot],
    desired_moves: dict[int, Position | None],
) -> tuple[dict[int, Position], set[int]]:
    current_positions = {robot.current_position: robot.robot_id for robot in robots}
    robot_positions = {robot.robot_id: robot.current_position for robot in robots}
    target_requests: dict[Position, list[int]] = {}
    for robot_id, target in desired_moves.items():
        if target is not None:
            target_requests.setdefault(target, []).append(robot_id)

    winning_robot_by_target = _choose_target_winners(
        current_positions,
        robot_positions,
        desired_moves,
        target_requests,
    )

    candidate_ids = {
        robot_id
        for robot_id, target in desired_moves.items()
        if target is not None and winning_robot_by_target[target] == robot_id
    }
    allowed_robot_ids = set(candidate_ids)

    changed = True
    while changed:
        changed = False
        for robot_id in list(allowed_robot_ids):
            target = desired_moves[robot_id]
            if target is None:
                allowed_robot_ids.remove(robot_id)
                changed = True
                continue

            occupant_id = current_positions.get(target)
            if (
                occupant_id is not None
                and occupant_id != robot_id
                and occupant_id not in allowed_robot_ids
            ):
                allowed_robot_ids.remove(robot_id)
                changed = True

    allowed_moves = {
        robot_id: desired_moves[robot_id]
        for robot_id in allowed_robot_ids
        if desired_moves[robot_id] is not None
    }
    blocked_robot_ids = candidate_ids - allowed_robot_ids
    blocked_robot_ids.update(
        robot_id
        for robot_id, target in desired_moves.items()
        if target is not None and robot_id not in candidate_ids
    )

    return allowed_moves, blocked_robot_ids


def _choose_target_winners(
    current_positions: dict[Position, int],
    robot_positions: dict[int, Position],
    desired_moves: dict[int, Position | None],
    target_requests: dict[Position, list[int]],
) -> dict[Position, int]:
    winners: dict[Position, int] = {}
    for target, robot_ids in target_requests.items():
        occupant_id = current_positions.get(target)
        swap_robot_ids = [
            robot_id
            for robot_id in robot_ids
            if (
                occupant_id is not None
                and occupant_id != robot_id
                and desired_moves.get(occupant_id) == robot_positions[robot_id]
            )
        ]

        if swap_robot_ids:
            winners[target] = min(swap_robot_ids)
        else:
            winners[target] = min(robot_ids)
    return winners
