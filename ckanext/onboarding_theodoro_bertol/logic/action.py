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


@tk.chained_action
def package_create(up_func, context, data_dict):
    """Override package_create to set default review status"""
    # Set default review status to pending for new datasets
    if 'review_status' not in data_dict:
        data_dict['review_status'] = 'pending'
        data_dict['private'] = True  # Make pending datasets private by default
    
    result = up_func(context, data_dict)
    log.info(f"Created dataset {result['id']} with review status: {data_dict.get('review_status', 'pending')}")
    return result

@tk.chained_action
def package_update(up_func, context, data_dict):
    """Override package_update to maintain review status logic"""
    # Don't change review_status unless explicitly set
    result = up_func(context, data_dict)
    log.info(f"Updated dataset {result['id']}")
    return result

def dataset_review(context, data_dict):
    """Review a dataset - approve or reject"""
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
    
    # Update review status
    update_data = {
        'id': dataset_id,
        'review_status': review_status
    }
    
    # If approved, make the dataset public
    if review_status == 'approved':
        update_data['private'] = False
    
    # Update the dataset
    package_patch = tk.get_action('package_patch')
    result = package_patch(context, update_data)
    
    log.info(f"Dataset {dataset_id} review status changed to: {review_status}")
    return result
