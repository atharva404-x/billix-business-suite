
import time
from typing import Any, Dict, List

class MetricsCollector:
    """
    Application metrics collector tracking request volumes, latency distributions,
    HTTP status codes, and service uptime.
    """

    def __init__(self):
        self.start_time: float = time.time()
        self.total_requests: int = 0
        self.status_codes: Dict[str, int] = {}
        self.error_count: int = 0
        self.latencies: List[float] = []
        self._max_latency_history: int = 1000

    def record_request(self, status_code: int, duration_ms: float) -> None:
        """Record an incoming request completion with its status code and latency."""
        self.total_requests += 1

        code_str = str(status_code)
        self.status_codes[code_str] = self.status_codes.get(code_str, 0) + 1

        if status_code >= 500:
            self.error_count += 1

        # Keep a rolling buffer of recent latencies
        self.latencies.append(round(duration_ms, 2))
        if len(self.latencies) > self._max_latency_history:
            self.latencies.pop(0)

    def get_summary(self) -> Dict[str, Any]:
        """Generate a summary of application metrics."""
        uptime = round(time.time() - self.start_time, 2)
        avg_latency = round(sum(self.latencies) / len(self.latencies), 2) if self.latencies else 0.0
        p95_latency = round(sorted(self.latencies)[int(len(self.latencies) * 0.95)], 2) if self.latencies else 0.0

        return {
            "uptime_seconds": uptime,
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "status_codes": self.status_codes,
            "latency_ms": {
                "avg": avg_latency,
                "p95": p95_latency,
                "recent_sample_count": len(self.latencies),
            },
        }

# Global metrics singleton
metrics_collector = MetricsCollector()
