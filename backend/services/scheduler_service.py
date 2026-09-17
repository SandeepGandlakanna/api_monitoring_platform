import time
from datetime import datetime
from sqlmodel import Session, select
from backend.database import engine
from backend.models import Monitor
from backend.services.monitor_service import check_monitor


def run_monitoring_loop():
    print("Monitoring scheduler started...")
    while True:
        with Session(engine) as session:
            monitors = session.exec(
                select(Monitor).where(
                    Monitor.is_active == True
                )
            ).all()

            current_time = datetime.utcnow()

            for monitor in monitors:

                if monitor.last_checked_at is not None:

                    elapsed_seconds = (
                        current_time
                        - monitor.last_checked_at
                    ).total_seconds()

                    if (
                        elapsed_seconds
                        < monitor.check_interval_seconds
                    ):
                        continue

                try:

                    print(
                        f"Checking monitor: "
                        f"{monitor.name}"
                    )

                    check_monitor(monitor)

                    print(
                        f"Check completed: "
                        f"{monitor.name}"
                    )

                except Exception as error:

                    print(
                        f"Monitoring error for "
                        f"{monitor.name}: {error}"
                    )

        time.sleep(5)


def start_scheduler():

    import threading

    scheduler_thread = threading.Thread(
        target=run_monitoring_loop,
        daemon=True,
    )

    scheduler_thread.start()

    print(
        "Background monitoring scheduler started!"
    )