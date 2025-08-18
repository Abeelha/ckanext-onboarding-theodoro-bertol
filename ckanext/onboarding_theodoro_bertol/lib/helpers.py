import ckan.model as model
from sqlalchemy import Boolean, or_

def get_current_user_info():
    """Helper function to get current user information"""
    return {
        'message': 'This comes from a helper function!',
        'timestamp': 'Generated at page load'
    }

def user_is_reviewer(user_id):
    """Check if a user has reviewer permissions"""
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
    
    result = q.first()
    return result is not None

def get_helpers():
    return {
        'get_current_user_info': get_current_user_info,
        'user_is_reviewer': user_is_reviewer
    }
