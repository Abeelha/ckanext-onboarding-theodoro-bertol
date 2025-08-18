import ckan.authz as authz
import ckan.model as model
from sqlalchemy import Boolean, or_
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


def _user_has_review_permission(user_id):
    """Helper to check if user has review permissions"""
    if not user_id:
        return False
        
    q = model.Session.query(model.User).filter(
        or_(model.User.id == user_id, model.User.name == user_id),
        or_(
            model.User.plugin_extras.op("->>")("review_permission").cast(Boolean) == True,
            model.User.sysadmin == True  # Sysadmins are also reviewers
        ),
        model.User.state == 'active'
    )
    
    return q.first() is not None

def dataset_approve(context, data_dict):
    """Only reviewers can approve datasets"""
    user = context['user']
    user_id = authz.get_user_id_for_username(user, allow_none=True)
    
    if user and _user_has_review_permission(user_id):
        return {'success': True}
    return {'success': False, 'msg': _('Only reviewers can approve datasets')}

def dataset_reject(context, data_dict):
    """Only reviewers can reject datasets"""
    user = context['user']
    user_id = authz.get_user_id_for_username(user, allow_none=True)
    
    if user and _user_has_review_permission(user_id):
        return {'success': True}
    return {'success': False, 'msg': _('Only reviewers can reject datasets')}
