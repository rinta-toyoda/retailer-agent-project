"""Simple passing tests to verify test infrastructure works."""
import pytest


class TestSimple:
    """Basic tests to verify pytest is working."""

    def test_basic_assertion(self):
        """Test that basic assertions work."""
        assert 1 + 1 == 2

    def test_string_operations(self):
        """Test string operations."""
        text = "hello"
        assert text.upper() == "HELLO"
        assert len(text) == 5

    def test_list_operations(self):
        """Test list operations."""
        items = [1, 2, 3]
        assert len(items) == 3
        assert 2 in items

    def test_dict_operations(self):
        """Test dictionary operations."""
        data = {"name": "Test", "value": 123}
        assert data["name"] == "Test"
        assert data.get("value") == 123

    def test_with_parametrize(self):
        """Test parametrized test."""
        values = [1, 2, 3, 4, 5]
        for val in values:
            assert val > 0
