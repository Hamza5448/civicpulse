import time
from threading import Lock


class Metrics:
    request_buckets = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)
    triage_buckets = (0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)

    def __init__(self) -> None:
        self._lock = Lock()
        self.request_count = 0
        self.request_latency_sum = 0.0
        self.request_bucket_counts = [0] * len(self.request_buckets)
        self.triage_count = 0
        self.triage_latency_sum = 0.0
        self.triage_bucket_counts = [0] * len(self.triage_buckets)
        self.triage_fallback_count = 0

    def observe_request(self, started: float) -> None:
        latency = time.perf_counter() - started
        with self._lock:
            self.request_count += 1
            self.request_latency_sum += latency
            self._observe_bucket(latency, self.request_buckets, self.request_bucket_counts)

    def observe_triage(self, latency_seconds: float, *, fallback: bool) -> None:
        with self._lock:
            self.triage_count += 1
            self.triage_latency_sum += latency_seconds
            self._observe_bucket(latency_seconds, self.triage_buckets, self.triage_bucket_counts)
            self.triage_fallback_count += int(fallback)

    @staticmethod
    def _observe_bucket(value: float, bounds: tuple[float, ...], counts: list[int]) -> None:
        for index, bound in enumerate(bounds):
            if value <= bound:
                counts[index] += 1

    def prometheus(self) -> str:
        with self._lock:
            request_count = self.request_count
            request_sum = self.request_latency_sum
            request_counts = self.request_bucket_counts.copy()
            triage_count = self.triage_count
            triage_sum = self.triage_latency_sum
            triage_counts = self.triage_bucket_counts.copy()
            fallback_count = self.triage_fallback_count
        lines = [
            "# TYPE civicpulse_requests_total counter",
            f"civicpulse_requests_total {request_count}",
        ]
        lines.extend(
            self._histogram_lines(
                "civicpulse_request_latency_seconds",
                self.request_buckets,
                request_counts,
                request_count,
                request_sum,
            )
        )
        lines.extend(
            self._histogram_lines(
                "civicpulse_triage_latency_seconds",
                self.triage_buckets,
                triage_counts,
                triage_count,
                triage_sum,
            )
        )
        lines.extend(
            [
                "# TYPE civicpulse_triage_fallbacks_total counter",
                f"civicpulse_triage_fallbacks_total {fallback_count}",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _histogram_lines(
        name: str,
        bounds: tuple[float, ...],
        counts: list[int],
        count: int,
        total: float,
    ) -> list[str]:
        lines = [f"# TYPE {name} histogram"]
        lines.extend(f'{name}_bucket{{le="{bound:g}"}} {value}' for bound, value in zip(bounds, counts))
        lines.extend(
            [
                f'{name}_bucket{{le="+Inf"}} {count}',
                f"{name}_count {count}",
                f"{name}_sum {total}",
            ]
        )
        return lines
