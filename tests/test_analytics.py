from backend.services.analytics_service import (
    calculate_monitor_stats,
)


def test_monitor_stats_without_results():

    result = calculate_monitor_stats(999999)

    assert result["total_checks"] == 0

    assert result["successful_checks"] == 0

    assert result["failed_checks"] == 0

    assert result["uptime_percentage"] == 0

    assert result["average_response_time_ms"] == 0