"""
Tests for core security and dependency injection functions.
"""
import jwt
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.deps import (
    get_current_user,
    get_current_user_optional,
    require_admin,
    require_evaluator,
)
from app.core.config import get_settings
from app.models.user import CurrentUser, UserRole


@pytest.fixture
def valid_token():
    """Generate a valid JWT token for testing."""
    settings = get_settings()
    payload = {
        "sub": "test@epam.com",
        "role": UserRole.ADMIN.value,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


@pytest.fixture
def expired_token():
    """Generate an expired JWT token for testing."""
    settings = get_settings()
    payload = {
        "sub": "test@epam.com",
        "role": UserRole.ADMIN.value,
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def test_get_current_user_with_valid_token(valid_token):
    """Test get_current_user with valid JWT token."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
    user = get_current_user(credentials=credentials)
    
    assert user.email == "test@epam.com"
    assert user.role == UserRole.ADMIN


def test_get_current_user_with_no_credentials():
    """Test get_current_user with no credentials raises 401."""
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=None)
    
    assert exc_info.value.status_code == 401
    assert "Not authenticated" in str(exc_info.value.detail)


def test_get_current_user_with_expired_token(expired_token):
    """Test get_current_user with expired token raises 401."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials)
    
    assert exc_info.value.status_code == 401
    assert "expired" in str(exc_info.value.detail).lower()


def test_get_current_user_with_invalid_token():
    """Test get_current_user with invalid token raises 401."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid.token.here")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials)
    
    assert exc_info.value.status_code == 401


def test_get_current_user_with_empty_credentials():
    """Test get_current_user with empty credentials raises 401."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")
    
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(credentials=credentials)
    
    assert exc_info.value.status_code == 401


def test_get_current_user_optional_with_valid_token(valid_token):
    """Test get_current_user_optional with valid token returns user."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
    user = get_current_user_optional(credentials=credentials)
    
    assert user is not None
    assert user.email == "test@epam.com"
    assert user.role == UserRole.ADMIN


def test_get_current_user_optional_with_no_credentials():
    """Test get_current_user_optional with no credentials returns None."""
    user = get_current_user_optional(credentials=None)
    assert user is None


def test_get_current_user_optional_with_invalid_token():
    """Test get_current_user_optional with invalid token returns None."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid")
    user = get_current_user_optional(credentials=credentials)
    assert user is None


def test_require_admin_with_admin_role(valid_token):
    """Test require_admin allows admin users."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
    user = require_admin(current_user=get_current_user(credentials=credentials))
    
    assert user.role == UserRole.ADMIN


def test_require_admin_rejects_non_admin(valid_token):
    """Test require_admin rejects non-admin users."""
    settings = get_settings()
    payload = {
        "sub": "submitter@epam.com",
        "role": UserRole.SUBMITTER.value,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = get_current_user(credentials=credentials)
    
    with pytest.raises(HTTPException) as exc_info:
        require_admin(current_user=user)
    
    assert exc_info.value.status_code == 403


def test_require_evaluator_allows_evaluator_role(valid_token):
    """Test require_evaluator allows evaluator users."""
    settings = get_settings()
    payload = {
        "sub": "evaluator@epam.com",
        "role": UserRole.EVALUATOR.value,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = get_current_user(credentials=credentials)
    
    result_user = require_evaluator(current_user=user)
    assert result_user.role == UserRole.EVALUATOR


def test_require_evaluator_allows_admin_role(valid_token):
    """Test require_evaluator allows admin users too."""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=valid_token)
    user = get_current_user(credentials=credentials)
    
    result_user = require_evaluator(current_user=user)
    assert result_user.role == UserRole.ADMIN


def test_require_evaluator_rejects_submitter(valid_token):
    """Test require_evaluator rejects submitter users."""
    settings = get_settings()
    payload = {
        "sub": "submitter@epam.com",
        "role": UserRole.SUBMITTER.value,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    user = get_current_user(credentials=credentials)
    
    with pytest.raises(HTTPException) as exc_info:
        require_evaluator(current_user=user)
    
    assert exc_info.value.status_code == 403
