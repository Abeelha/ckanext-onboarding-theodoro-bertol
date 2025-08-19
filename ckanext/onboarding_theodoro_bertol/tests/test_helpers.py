"""Tests for helper functions"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
from ckanext.onboarding_theodoro_bertol.lib.helpers import user_is_reviewer, get_current_user_info


class TestHelpers:
    """Test helper functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        helpers.reset_db()
        
    def test_user_is_reviewer_with_sysadmin(self):
        """Test that sysadmins are considered reviewers"""
        sysadmin = factories.Sysadmin()
        
        # Sysadmins should always be reviewers
        assert user_is_reviewer(sysadmin['id']) is True
        assert user_is_reviewer(sysadmin['name']) is True
        
    def test_user_is_reviewer_with_reviewer_permission(self):
        """Test user_is_reviewer with explicit reviewer permission"""
        sysadmin = factories.Sysadmin()
        user = factories.User()
        
        # Initially user should not be a reviewer
        assert user_is_reviewer(user['id']) is False
        
        # Grant reviewer permission
        helpers.call_action(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=user['id']
        )
        
        # Now user should be a reviewer
        assert user_is_reviewer(user['id']) is True
        assert user_is_reviewer(user['name']) is True
        
    def test_user_is_reviewer_with_regular_user(self):
        """Test that regular users are not reviewers"""
        user = factories.User()
        
        # Regular users should not be reviewers
        assert user_is_reviewer(user['id']) is False
        assert user_is_reviewer(user['name']) is False
        
    def test_user_is_reviewer_with_none(self):
        """Test user_is_reviewer with None user_id"""
        assert user_is_reviewer(None) is False
        
    def test_user_is_reviewer_with_invalid_user(self):
        """Test user_is_reviewer with invalid user_id"""
        assert user_is_reviewer('invalid-user-id') is False
        
    def test_user_is_reviewer_after_revoke(self):
        """Test user_is_reviewer after revoking permission"""
        sysadmin = factories.Sysadmin()
        user = factories.User()
        
        # Grant reviewer permission
        helpers.call_action(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=user['id']
        )
        
        # User should be a reviewer
        assert user_is_reviewer(user['id']) is True
        
        # Revoke reviewer permission
        helpers.call_action(
            'user_reviewer_revoke',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=user['id']
        )
        
        # User should no longer be a reviewer
        assert user_is_reviewer(user['id']) is False
        
    def test_get_current_user_info(self):
        """Test get_current_user_info helper"""
        info = get_current_user_info()
        
        assert 'message' in info
        assert info['message'] == 'This comes from a helper function!'
        assert 'timestamp' in info
        assert info['timestamp'] == 'Generated at page load'