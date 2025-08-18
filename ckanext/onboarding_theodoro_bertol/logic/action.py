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
