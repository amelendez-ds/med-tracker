class MockNotificationChannel:
    """Test double: records what would have been sent instead of sending it"""

    def __init__(self) -> None:
        self.sent: list[tuple[str, int]] = []

    def send(self, med_name: str, days_left: int) -> None:
        self.sent.append((med_name, days_left))
