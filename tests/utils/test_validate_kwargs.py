"""Test validate_kwargs."""
import pytest

from phial.utils import validate_kwargs


def test_string_validation_succesful() -> None:
    """Test string validation is sucessful."""
    def test(name: str) -> None:
        pass
    kwargs = validate_kwargs(test, {"name": "string"})
    assert "name" in kwargs
    assert kwargs["name"] == "string"


def test_int_validation_succesful() -> None:
    """Test int validation is sucessful."""
    def test(age: int) -> None:
        pass
    kwargs = validate_kwargs(test, {"age": "1"})
    assert "age" in kwargs
    assert kwargs["age"] == 1


def test_args_validation_errors_correctly() -> None:
    """Test args validation errors correctly."""
    def test(name: str) -> None:
        pass
    with pytest.raises(Exception) as e:
        validate_kwargs(test, {"age": "string"})
    assert e is not None


def test_args_type_validation_errors_correctly() -> None:
    """Test args type validation errors correctly."""
    def test(age: int) -> None:
        pass
    with pytest.raises(Exception) as e:
        validate_kwargs(test, {"age": "string"})
    assert e is not None
