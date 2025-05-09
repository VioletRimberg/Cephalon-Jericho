from src.message_provider import MessageProvider, MessageEntry
import random


def test_is_constructable():
    provider = MessageProvider()
    assert provider is not None
    assert len(provider.entries) == 0


def test_can_add():
    provider = MessageProvider()
    provider.add("TEST", MessageEntry("FOOBAR", 1))
    assert len(provider.entries) == 1


def test_can_add_twice():
    provider = MessageProvider()
    provider.add("TEST", MessageEntry("FOOBAR", 1))
    provider.add("TEST", MessageEntry("FOOBAR2", 1))
    assert len(provider.entries) == 1


def test_reports_missing_key():
    provider = MessageProvider()
    message = provider(key="test")
    assert message is not None
    assert message == "Message-Key `test` is not defined!"


def test_renders_entry():
    provider = MessageProvider()
    provider.add("TEST", MessageEntry("Hello {{ user }}", 1))
    message = provider(key="TEST", user="Rynn")
    assert message == "Hello Rynn"


def test_samples_entries():
    provider = MessageProvider()
    provider.add("TEST", MessageEntry("1", 1))
    provider.add("TEST", MessageEntry("2", 1))
    random.seed(42)
    messages = [provider("TEST") for i in range(4)]
    assert messages == ["2", "1", "1", "1"]


def test_samples_weighted_entries():
    provider = MessageProvider()
    provider.add("TEST", MessageEntry("1", 1))
    provider.add("TEST", MessageEntry("2", 100_000))
    random.seed(42)
    messages = [provider("TEST") for i in range(4)]
    assert messages == ["2", "2", "2", "2"]


def test_is_constructable_from_csv():
    provider = MessageProvider.from_csv("messages.csv")
    assert provider is not None
    assert len(provider.entries) == 2
    message = provider(key="TEST", user="Rynn")
    assert message == "Hello Opperator Rynn"


def test_is_constructable_from_gsheet():
    provider = MessageProvider.from_gsheets(
        "1-UUJIz0-0A0OCO4ShtYi5iYPkTVWypbZzlpAfWCz60o"
    )
    # assert provider is not None
    assert provider is not None, (
        "Provider could not be constructed from the given sheet."
    )
    assert provider.entries, "No entries were loaded from the sheet."


# assert len(provider.entries) >= 2
# message = provider(key = "TEST", user = "Rynn")
# assert message == "This is a test message for Rynn."
