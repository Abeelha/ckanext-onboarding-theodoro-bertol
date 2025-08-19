"""Tests for authorization functions"""
import pytest
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
import ckan.logic as logic


class TestAuthFunctions:
    """Test authorization functions"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        helpers.reset_db()
        
    def test_only_sysadmin_can_grant_reviewer(self):
        """Test that only sysadmins can grant reviewer permissions"""
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()
        target_user = factories.User()
        
        # Sysadmin should be able to grant
        result = helpers.call_auth(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'model': None},
            user_id=target_user['id']
        )
        assert result['success'] is True
        
        # Regular user should not be able to grant
        result = helpers.call_auth(
            'user_reviewer_grant',
            context={'user': regular_user['name'], 'model': None},
            user_id=target_user['id']
        )
        assert result['success'] is False
        
    def test_only_sysadmin_can_revoke_reviewer(self):
        """Test that only sysadmins can revoke reviewer permissions"""
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()
        target_user = factories.User()
        
        # Sysadmin should be able to revoke
        result = helpers.call_auth(
            'user_reviewer_revoke',
            context={'user': sysadmin['name'], 'model': None},
            user_id=target_user['id']
        )
        assert result['success'] is True
        
        # Regular user should not be able to revoke
        result = helpers.call_auth(
            'user_reviewer_revoke',
            context={'user': regular_user['name'], 'model': None},
            user_id=target_user['id']
        )
        assert result['success'] is False
        
    def test_only_reviewer_can_review_dataset(self):
        """Test that only reviewers can review datasets"""
        sysadmin = factories.Sysadmin()
        regular_user = factories.User()
        reviewer_user = factories.User()
        dataset = factories.Dataset(private=True)
        
        # Grant reviewer permission to reviewer_user
        helpers.call_action(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=reviewer_user['id']
        )
        
        # Sysadmin should be able to review (sysadmins are always reviewers)
        result = helpers.call_auth(
            'dataset_review',
            context={'user': sysadmin['name'], 'model': None},
            id=dataset['id'],
            review_status='approved'
        )
        assert result['success'] is True
        
        # Reviewer should be able to review
        result = helpers.call_auth(
            'dataset_review',
            context={'user': reviewer_user['name'], 'model': None},
            id=dataset['id'],
            review_status='approved'
        )
        assert result['success'] is True
        
        # Regular user should not be able to review
        result = helpers.call_auth(
            'dataset_review',
            context={'user': regular_user['name'], 'model': None},
            id=dataset['id'],
            review_status='approved'
        )
        assert result['success'] is False
        
    def test_anonymous_cannot_review(self):
        """Test that anonymous users cannot review datasets"""
        dataset = factories.Dataset(private=True)
        
        # Anonymous user should not be able to review
        result = helpers.call_auth(
            'dataset_review',
            context={'user': None, 'model': None},
            id=dataset['id'],
            review_status='approved'
        )
        assert result['success'] is False