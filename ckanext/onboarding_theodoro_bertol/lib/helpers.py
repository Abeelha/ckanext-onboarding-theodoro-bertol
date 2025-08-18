def get_current_user_info():
    """Helper function to get current user information"""
    return {
        'message': 'This comes from a helper function!',
        'timestamp': 'Generated at page load'
    }

def get_helpers():
    return {
        'get_current_user_info': get_current_user_info
    }
