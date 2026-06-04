"""Tests for the Memory class."""

import pytest

from warpos import Memory


class TestMemoryInit:
    def test_default_init(self):
        memory = Memory()
        assert memory.get() == []

    def test_max_messages(self):
        memory = Memory(max_messages=5)
        assert memory.max_messages == 5


class TestMemoryOperations:
    def test_add_message(self):
        memory = Memory()
        memory.add("user", "Hello")
        messages = memory.get()
        assert len(messages) == 1
        assert messages[0] == {"role": "user", "content": "Hello"}

    def test_add_multiple_messages(self):
        memory = Memory()
        memory.add("user", "Hello")
        memory.add("assistant", "Hi there!")
        memory.add("user", "How are you?")
        assert len(memory.get()) == 3

    def test_clear(self):
        memory = Memory()
        memory.add("user", "Hello")
        memory.add("assistant", "Hi!")
        memory.clear()
        assert memory.get() == []

    def test_max_messages_enforced(self):
        memory = Memory(max_messages=3)
        memory.add("user", "msg1")
        memory.add("assistant", "msg2")
        memory.add("user", "msg3")
        memory.add("assistant", "msg4")
        messages = memory.get()
        assert len(messages) == 3
        # Oldest message should be dropped
        assert messages[0]["content"] == "msg2"

    def test_empty_memory(self):
        memory = Memory()
        assert memory.get() == []
        memory.clear()
        assert memory.get() == []
