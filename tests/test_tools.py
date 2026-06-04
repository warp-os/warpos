"""Tests for the @tool decorator."""

import pytest

from warpos import tool


class TestToolDecorator:
    def test_basic_tool(self):
        @tool
        def my_func(x: int) -> int:
            """Double a number."""
            return x * 2

        assert hasattr(my_func, "__tool__")
        assert my_func.__tool_name__ == "my_func"
        assert my_func.__tool_description__ == "Double a number."

    def test_tool_preserves_function(self):
        @tool
        def add(a: int, b: int) -> int:
            """Add two numbers."""
            return a + b

        assert add(2, 3) == 5

    def test_tool_with_no_args(self):
        @tool
        def get_time() -> str:
            """Get current time."""
            return "2024-01-01T00:00:00"

        result = get_time()
        assert result == "2024-01-01T00:00:00"

    def test_tool_requires_docstring(self):
        with pytest.raises(ValueError):

            @tool
            def no_doc(x: int) -> int:
                return x

    def test_tool_requires_type_hints(self):
        with pytest.raises(ValueError):

            @tool
            def no_hints(x) -> int:
                """Has docstring but no type hints."""
                return x

    def test_tool_schema(self):
        @tool
        def greet(name: str, greeting: str = "Hello") -> str:
            """Greet someone."""
            return f"{greeting}, {name}!"

        schema = greet.__tool_schema__
        assert schema["name"] == "greet"
        assert "name" in schema["parameters"]["properties"]
        assert "greeting" in schema["parameters"]["properties"]

    def test_tool_error_handling(self):
        @tool
        def failing(x: int) -> int:
            """A tool that fails."""
            raise ValueError("boom")

        # Tool should not raise — errors are caught at the agent level
        # The tool itself can still raise; the agent handles it
        with pytest.raises(ValueError):
            failing(1)
