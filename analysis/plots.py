from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def plot_summary_metrics(results: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _line_plot(
        results,
        "robot_count",
        "total_completion_time",
        "Robot Sayısına Göre Toplam Tamamlanma Süresi",
        "Robot sayısı",
        "Zaman adımı",
        output_dir / "total_completion_time_by_robot_count.png",
    )
    _line_plot(
        results,
        "robot_count",
        "throughput",
        "Robot Sayısına Göre Throughput",
        "Robot sayısı",
        "Tamamlanan görev / zaman",
        output_dir / "throughput_by_robot_count.png",
    )
    _line_plot(
        results,
        "robot_count",
        "average_waiting_time",
        "Robot Sayısına Göre Ortalama Bekleme Süresi",
        "Robot sayısı",
        "Zaman adımı",
        output_dir / "average_waiting_time_by_robot_count.png",
    )


def plot_waiting_tasks_over_time(histories: dict[int, pd.DataFrame], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))
    for robot_count, history in histories.items():
        plt.plot(history["time"], history["waiting_tasks"], label=f"{robot_count} robot")
    plt.title("Zaman İçinde Bekleyen Görev Sayısı")
    plt.xlabel("Zaman adımı")
    plt.ylabel("Bekleyen görev sayısı")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_dir / "waiting_tasks_over_time.png", dpi=150)
    plt.close()


def plot_replication_confidence_intervals(replication_summary: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    _errorbar_plot(
        replication_summary,
        "robot_count",
        "total_completion_time_mean",
        "total_completion_time_ci95",
        "100 Replikasyon: Ortalama Toplam Tamamlanma Süresi",
        "Robot sayısı",
        "Ortalama zaman adımı",
        output_dir / "replication_total_completion_time_ci.png",
    )
    _errorbar_plot(
        replication_summary,
        "robot_count",
        "throughput_mean",
        "throughput_ci95",
        "100 Replikasyon: Ortalama Throughput",
        "Robot sayısı",
        "Tamamlanan görev / zaman",
        output_dir / "replication_throughput_ci.png",
    )


def _line_plot(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: Path,
) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(data[x_column], data[y_column], marker="o")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _errorbar_plot(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    error_column: str,
    title: str,
    xlabel: str,
    ylabel: str,
    output_path: Path,
) -> None:
    plt.figure(figsize=(8, 5))
    plt.errorbar(
        data[x_column],
        data[y_column],
        yerr=data[error_column],
        marker="o",
        capsize=5,
    )
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
