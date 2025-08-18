import ckan.authz as authz
from ckan.common import _

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
