import random

import pandas as pd

from analysis.metrics import calculate_replication_summary, calculate_summary
from analysis.plots import (
    plot_replication_confidence_intervals,
    plot_summary_metrics,
    plot_waiting_tasks_over_time,
)
from config.settings import (
    MAX_STEPS,
    OUTPUT_FIGURES_DIR,
    OUTPUT_TABLES_DIR,
    RANDOM_SEED,
    REPLICATION_BASE_SEED,
    REPLICATION_COUNT,
    ROBOT_COUNTS,
    TASK_COUNT,
    WAREHOUSE_HEIGHT,
    WAREHOUSE_WIDTH,
)
from models.robot import Robot
from models.task import Task
from models.warehouse import Warehouse
from pathfinding.bfs import bfs_path
from simulation.engine import SimulationEngine


def create_tasks(warehouse: Warehouse, task_count: int, seed: int) -> list[Task]:
    if task_count <= 0:
        raise ValueError("task_count must be greater than zero.")
    if not warehouse.pickup_points or not warehouse.delivery_points:
        raise ValueError("Warehouse must include pickup and delivery points.")

    random_generator = random.Random(seed)
    tasks: list[Task] = []
    for task_id in range(1, task_count + 1):
        pickup = random_generator.choice(warehouse.pickup_points)
        delivery = random_generator.choice(warehouse.delivery_points)
        tasks.append(
            Task(
                task_id=task_id,
                pickup_location=pickup,
                delivery_location=delivery,
                created_at=0,
            )
        )
    return tasks


def create_robots(warehouse: Warehouse, robot_count: int) -> list[Robot]:
    if robot_count <= 0:
        raise ValueError("robot_count must be greater than zero.")
    if robot_count > len(warehouse.start_positions):
        raise ValueError(
            f"Warehouse has {len(warehouse.start_positions)} start positions, "
            f"but {robot_count} robots were requested."
        )
    return [
        Robot(robot_id=index + 1, current_position=warehouse.start_positions[index])
        for index in range(robot_count)
    ]


def run_scenario(robot_count: int, seed: int = RANDOM_SEED) -> tuple[dict[str, float | int], pd.DataFrame]:
    warehouse = Warehouse.create_default(width=WAREHOUSE_WIDTH, height=WAREHOUSE_HEIGHT)
    tasks = create_tasks(warehouse, TASK_COUNT, seed)
    robots = create_robots(warehouse, robot_count)

    engine = SimulationEngine(
        warehouse=warehouse,
        robots=robots,
        tasks=tasks,
        pathfinder=bfs_path,
        max_steps=MAX_STEPS,
    )
    result = engine.run()
    summary = calculate_summary(
        robot_count=robot_count,
        total_time=int(result["total_time"]),
        robots=result["robots"],
        tasks=result["tasks"],
    )
    history = pd.DataFrame(result["history"])
    return summary, history


def run_replications() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_rows: list[dict[str, float | int]] = []

    for robot_count in ROBOT_COUNTS:
        for replication in range(1, REPLICATION_COUNT + 1):
            seed = REPLICATION_BASE_SEED + replication - 1
            summary, _ = run_scenario(robot_count, seed=seed)
            summary["replication"] = replication
            summary["seed"] = seed
            raw_rows.append(summary)

    raw_results = pd.DataFrame(raw_rows)
    summary_results = pd.DataFrame(calculate_replication_summary(raw_rows))
    return raw_results, summary_results


def main() -> None:
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    summaries: list[dict[str, float | int]] = []
    histories: dict[int, pd.DataFrame] = {}

    for robot_count in ROBOT_COUNTS:
        summary, history = run_scenario(robot_count)
        summaries.append(summary)
        histories[robot_count] = history
        history.to_csv(OUTPUT_TABLES_DIR / f"time_series_robot_{robot_count}.csv", index=False)

    results = pd.DataFrame(summaries)
    results.to_csv(OUTPUT_TABLES_DIR / "results.csv", index=False)

    plot_summary_metrics(results, OUTPUT_FIGURES_DIR)
    plot_waiting_tasks_over_time(histories, OUTPUT_FIGURES_DIR)

    replication_results, replication_summary = run_replications()
    replication_results.to_csv(OUTPUT_TABLES_DIR / "replications_raw.csv", index=False)
    replication_summary.to_csv(OUTPUT_TABLES_DIR / "replication_summary.csv", index=False)
    plot_replication_confidence_intervals(replication_summary, OUTPUT_FIGURES_DIR)

    display_results = results.rename(
        columns={
            "robot_count": "Robot sayısı",
            "completed_tasks": "Tamamlanan görev",
            "total_completion_time": "Toplam süre",
            "average_task_completion_time": "Ortalama görev süresi",
            "throughput": "Throughput",
            "robot_utilization": "Robot kullanım oranı",
            "average_waiting_time": "Ortalama bekleme",
            "total_distance": "Toplam mesafe",
            "blocked_waiting_count": "Bekleme/bloklanma",
        }
    )

    print("\nWarehouse Robotics Simulation - Özet sonuçlar")
    print(display_results.to_string(index=False))
    print("\n100 replikasyon özeti")
    print(
        replication_summary[
            [
                "robot_count",
                "replications",
                "total_completion_time_mean",
                "total_completion_time_ci95",
                "throughput_mean",
                "throughput_ci95",
                "blocked_waiting_count_mean",
                "blocked_waiting_count_ci95",
            ]
        ].to_string(index=False)
    )
    print(f"\nSonuç tablosu kaydedildi: {OUTPUT_TABLES_DIR / 'results.csv'}")
    print(f"Replikasyon özeti kaydedildi: {OUTPUT_TABLES_DIR / 'replication_summary.csv'}")
    print(f"Grafikler bu klasöre kaydedildi: {OUTPUT_FIGURES_DIR}")


if __name__ == "__main__":
    main()
