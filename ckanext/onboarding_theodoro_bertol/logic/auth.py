import ckan.authz as authz
from ckan.common import _
from ckanext.onboarding_theodoro_bertol.lib.helpers import user_is_reviewer

def user_reviewer_grant(context, data_dict):
    """Only sysadmins can grant reviewer permissions"""
    user = context['user']
    if authz.is_sysadmin(user):
        return {'success': True}
    return {'success': False, 'msg': _('Only sysadmins can grant reviewer permissions')}

def user_reviewer_revoke(context, data_dict):
    """Only sysadmins can revoke reviewer permissions"""
    user = context['user']
    if authz.is_sysadmin(user):
        return {'success': True}
    return {'success': False, 'msg': _('Only sysadmins can revoke reviewer permissions')}


def dataset_review(context, data_dict):
    """Only users with reviewer permissions can review datasets"""
    user = context['user']
    user_id = authz.get_user_id_for_username(user, allow_none=True)
    
    if user and user_is_reviewer(user_id):
        return {'success': True}
    
    return {
        'success': False,
        'msg': _('User {} not authorized to review datasets').format(user)
    }
