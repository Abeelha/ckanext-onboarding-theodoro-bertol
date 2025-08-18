from ckan.plugins import toolkit as tk
from ckan.common import _
import ckan.logic as logic
import ckan.model as model
import logging

log = logging.getLogger(__name__)

def user_reviewer_grant(context, data_dict):
    """Grant reviewer permission to a user"""
    tk.check_access('user_reviewer_grant', context, data_dict)
    
    username = data_dict.get('username')
    if not username:
        raise logic.ValidationError({'username': [_('Username is required')]})
    
    user = model.User.get(username)
    if not user:
        raise logic.NotFound(_('User not found'))
    
    # Store reviewer permission in plugin_extras
    if not user.plugin_extras:
        user.plugin_extras = {}
    
    user.plugin_extras['review_permission'] = True
    user.save()
    model.repo.commit()
    
    log.info(f"Granted reviewer permission to user: {username}")
    return {'success': True, 'user': user.name}

def user_reviewer_revoke(context, data_dict):
    """Revoke reviewer permission from a user"""
    tk.check_access('user_reviewer_revoke', context, data_dict)
    
    username = data_dict.get('username')
    if not username:
        raise logic.ValidationError({'username': [_('Username is required')]})
    
    user = model.User.get(username)
    if not user:
        raise logic.NotFound(_('User not found'))
    
    # Remove reviewer permission from plugin_extras
    if user.plugin_extras and 'review_permission' in user.plugin_extras:
        user.plugin_extras['review_permission'] = False
        user.save()
        model.repo.commit()
    
    log.info(f"Revoked reviewer permission from user: {username}")
    return {'success': True, 'user': user.name}

def dataset_review(context, data_dict):
    """Approve or reject a dataset"""
    tk.check_access('dataset_review', context, data_dict)
    
    dataset_id = data_dict.get('id')
    review_status = data_dict.get('review_status')
    
    if not dataset_id:
        raise logic.ValidationError({'id': [_('Dataset ID is required')]})
    
    if review_status not in ['approved', 'rejected']:
        raise logic.ValidationError({'review_status': [_('Review status must be approved or rejected')]})
    
    # Get the dataset
    package_show = tk.get_action('package_show')
    dataset = package_show(context, {'id': dataset_id})
    
    # Update the dataset
    package_patch = tk.get_action('package_patch')
    updated_data = {
        'id': dataset_id,
        'review_status': review_status
    }
    
    # If approved, make it public
    if review_status == 'approved':
        updated_data['private'] = False
    
    result = package_patch(context, updated_data)
    
    log.info(f"Dataset {dataset_id} review status changed to: {review_status}")
    return result
