class RateLimitExceededError(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__("Complaint submission rate limit exceeded")
