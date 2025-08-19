"""Tests for dataset review actions"""
import pytest
from unittest.mock import Mock, patch
import ckan.tests.factories as factories
import ckan.tests.helpers as helpers
from ckan.common import config
import ckan.logic as logic


class TestDatasetReviewActions:
    """Test dataset review action functionality"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test fixtures"""
        helpers.reset_db()
        
    def test_dataset_create_sets_pending_status(self):
        """Test that new datasets are created with pending review status"""
        user = factories.User()
        
        # Create a dataset
        dataset = helpers.call_action(
            'package_create',
            context={'user': user['name'], 'ignore_auth': True},
            name='test-dataset',
            title='Test Dataset',
            private=True
        )
        
        # Check that review_status is set to pending
        assert dataset.get('review_status') == 'pending'
        assert dataset.get('private') is True
        
    def test_dataset_review_approve(self):
        """Test approving a dataset"""
        sysadmin = factories.Sysadmin()
        user = factories.User()
        
        # Create a dataset
        dataset = helpers.call_action(
            'package_create',
            context={'user': user['name'], 'ignore_auth': True},
            name='test-dataset-approve',
            title='Test Dataset for Approval',
            private=True
        )
        
        # Grant reviewer permission to sysadmin (though sysadmins already have it)
        helpers.call_action(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=sysadmin['id']
        )
        
        # Approve the dataset
        result = helpers.call_action(
            'dataset_review',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            id=dataset['id'],
            review_status='approved'
        )
        
        # Check the dataset is approved and public
        assert result.get('review_status') == 'approved'
        assert result.get('private') is False
        
    def test_dataset_review_reject(self):
        """Test rejecting a dataset"""
        sysadmin = factories.Sysadmin()
        user = factories.User()
        
        # Create a dataset
        dataset = helpers.call_action(
            'package_create',
            context={'user': user['name'], 'ignore_auth': True},
            name='test-dataset-reject',
            title='Test Dataset for Rejection',
            private=True
        )
        
        # Reject the dataset
        result = helpers.call_action(
            'dataset_review',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            id=dataset['id'],
            review_status='rejected'
        )
        
        # Check the dataset is rejected and still private
        assert result.get('review_status') == 'rejected'
        assert result.get('private') is True
        
    def test_non_reviewer_cannot_review(self):
        """Test that non-reviewers cannot review datasets"""
        user = factories.User()
        dataset_owner = factories.User()
        
        # Create a dataset
        dataset = helpers.call_action(
            'package_create',
            context={'user': dataset_owner['name'], 'ignore_auth': True},
            name='test-dataset-auth',
            title='Test Dataset Auth',
            private=True
        )
        
        # Try to review as non-reviewer user
        with pytest.raises(logic.NotAuthorized):
            helpers.call_action(
                'dataset_review',
                context={'user': user['name'], 'ignore_auth': False},
                id=dataset['id'],
                review_status='approved'
            )
            
    def test_reviewer_permissions_grant_revoke(self):
        """Test granting and revoking reviewer permissions"""
        sysadmin = factories.Sysadmin()
        user = factories.User()
        
        # Grant reviewer permission
        result = helpers.call_action(
            'user_reviewer_grant',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=user['id']
        )
        
        assert result.get('success') is True
        
        # Check user is now a reviewer
        from ckanext.onboarding_theodoro_bertol.lib.helpers import user_is_reviewer
        assert user_is_reviewer(user['id']) is True
        
        # Revoke reviewer permission
        result = helpers.call_action(
            'user_reviewer_revoke',
            context={'user': sysadmin['name'], 'ignore_auth': True},
            user_id=user['id']
        )
        
        assert result.get('success') is True
        
        # Check user is no longer a reviewer
        assert user_is_reviewer(user['id']) is False