"""
Tests for security utility functions.
"""
import pytest
from app.core.security import hash_password, verify_password


def test_hash_password_creates_hash():
    """Test that hash_password creates a non-empty hash."""
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed is not None
    assert len(hashed) > 0
    assert hashed != password


def test_hash_password_different_each_call():
    """Test that hashing same password produces different hashes."""
    password = "same_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2


def test_verify_password_correct_password():
    """Test that verify_password returns True for correct password."""
    password = "correct_password"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_wrong_password():
    """Test that verify_password returns False for wrong password."""
    password = "correct_password"
    wrong_password = "wrong_password"
    hashed = hash_password(password)
    
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty_password():
    """Test verify_password with empty password."""
    password = ""
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    assert verify_password("nonempty", hashed) is False


def test_verify_password_long_password():
    """Test verify_password with very long password."""
    password = "x" * 1000
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_special_characters():
    """Test verify_password with special characters."""
    password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_unicode():
    """Test verify_password with unicode characters."""
    password = "café_café_café_ñ_ñ_ñ"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_invalid_hash_format():
    """Test verify_password with invalid hash format."""
    invalid_hash = "not_a_valid_hash"
    
    result = verify_password("password", invalid_hash)
    assert result is False


def test_verify_password_empty_hash():
    """Test verify_password with empty hash."""
    result = verify_password("password", "")
    assert result is False
