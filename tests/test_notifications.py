from med_tracker.notifications import notify_low_stock
from tests.fakes import MockNotificationChannel


def test_notify_records_call() -> None:
    mock = MockNotificationChannel()
    notify_low_stock("Paracetamol", 5, channels=[mock])
    assert mock.sent == [("Paracetamol", 5)]


def test_notify_hits_every_channel() -> None:
    a, b = MockNotificationChannel(), MockNotificationChannel()
    notify_low_stock("Paracetamol", 5, channels=[a, b])
    assert a.sent == [("Paracetamol", 5)]
    assert b.sent == [("Paracetamol", 5)]


def test_notify_empty_channels_no_error() -> None:
    notify_low_stock("Med", 3, channels=[])  # This case is for when nothing is sent
