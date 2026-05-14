"""
Tests for configuration module.
"""
import pytest
from app.core.config import get_settings, Settings


def test_get_settings_returns_settings_instance():
    """Test that get_settings returns a Settings instance."""
    settings = get_settings()
    assert isinstance(settings, Settings)


def test_get_settings_has_required_fields():
    """Test that settings has all required fields."""
    settings = get_settings()
    
    assert hasattr(settings, "app_name")
    assert hasattr(settings, "environment")
    assert hasattr(settings, "mongo_uri")
    assert hasattr(settings, "mongo_db_name")
    assert hasattr(settings, "secret_key")
    assert hasattr(settings, "algorithm")
    assert hasattr(settings, "access_token_expire_minutes")


def test_get_settings_app_name():
    """Test app name is set."""
    settings = get_settings()
    assert settings.app_name == "InnovatEPAM Portal"


def test_get_settings_has_mongo_config():
    """Test MongoDB configuration is available."""
    settings = get_settings()
    assert settings.mongo_uri is not None
    assert settings.mongo_db_name is not None


def test_get_settings_has_jwt_config():
    """Test JWT configuration is available."""
    settings = get_settings()
    assert settings.secret_key is not None
    assert settings.algorithm == "HS256"
    assert settings.access_token_expire_minutes >= 1


def test_get_settings_cached():
    """Test that get_settings returns same instance (cached)."""
    settings1 = get_settings()
    settings2 = get_settings()
    assert settings1 is settings2


def test_settings_bcrypt_schemes():
    """Test bcrypt schemes are configured."""
    settings = get_settings()
    assert "bcrypt" in settings.bcrypt_schemes
