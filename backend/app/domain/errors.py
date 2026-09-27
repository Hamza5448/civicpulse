class ComplaintNotFoundError(Exception):
    pass


class InvalidStatusTransitionError(Exception):
    def __init__(self, current: str, attempted: str) -> None:
        self.current = current
        self.attempted = attempted
        super().__init__(f"Invalid status transition: {current} -> {attempted}")
