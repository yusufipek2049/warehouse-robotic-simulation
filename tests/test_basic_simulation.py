import unittest

from main import create_robots, create_tasks
from models.warehouse import Warehouse
from pathfinding.bfs import bfs_path
from simulation.engine import SimulationEngine


class BasicSimulationTest(unittest.TestCase):
    def test_small_simulation_completes(self) -> None:
        warehouse = Warehouse.create_default()
        robots = create_robots(warehouse, 2)
        tasks = create_tasks(warehouse, 5, seed=7)

        engine = SimulationEngine(
            warehouse=warehouse,
            robots=robots,
            tasks=tasks,
            pathfinder=bfs_path,
            max_steps=1_000,
        )
        result = engine.run()

        self.assertGreater(result["total_time"], 0)
        self.assertTrue(all(task.status == "completed" for task in result["tasks"]))
        self.assertEqual(len(result["history"]), result["total_time"])


if __name__ == "__main__":
    unittest.main()

