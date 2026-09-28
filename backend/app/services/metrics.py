import time


class Metrics:
    def __init__(self) -> None:
        self.request_count = 0
        self.request_latency_seconds: list[float] = []

    def observe_request(self, started: float) -> None:
        self.request_count += 1
        self.request_latency_seconds.append(time.perf_counter() - started)

    def prometheus(self) -> str:
        count = len(self.request_latency_seconds)
        total = sum(self.request_latency_seconds)
        return "\n".join(
            [
                "# TYPE civicpulse_requests_total counter",
                f"civicpulse_requests_total {self.request_count}",
                "# TYPE civicpulse_request_latency_seconds summary",
                f"civicpulse_request_latency_seconds_count {count}",
                f"civicpulse_request_latency_seconds_sum {total}",
                "",
            ]
        )
