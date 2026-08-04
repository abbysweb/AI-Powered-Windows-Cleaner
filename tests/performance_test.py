import os
import time

import psutil

from ai_health_copilot.core.cleaner.windows_temp import WindowsTempCleaner


def test_performance_memory_and_speed():
    # Setup
    process = psutil.Process(os.getpid())
    start_memory = process.memory_info().rss
    start_time = time.time()

    # Run scan
    cleaner = WindowsTempCleaner()
    cleaner.scan()

    end_time = time.time()
    end_memory = process.memory_info().rss

    scan_time_ms = (end_time - start_time) * 1000
    memory_diff_kb = (end_memory - start_memory) / 1024

    print("\\nPerformance Metrics:")
    print(f"Scan Time: {scan_time_ms:.2f} ms")
    print(f"Memory Diff: {memory_diff_kb:.2f} KB")

    # Hard thresholds for performance validation
    assert scan_time_ms < 5000, f"Scan time too slow: {scan_time_ms:.2f} ms"
    assert memory_diff_kb < 50000, f"Memory leak detected: {memory_diff_kb:.2f} KB"
