from flask import Blueprint
from ckan.common import request, current_user, g, _
import ckan.logic as logic
from ckan.lib.helpers import url_for, flash_success, flash_error, redirect_to
import logging

log = logging.getLogger(__name__)

dataset = Blueprint("onboarding_dataset", __name__, url_prefix="/dataset")

def review():
    """Handle dataset review form submissions"""
    dataset_id = request.form.get("id")
    review_status = request.form.get("review_status")
    
    log.info(f"Review action called - dataset_id: {dataset_id}, review_status: {review_status}")
    
    if not dataset_id or not review_status:
        flash_error(_("Missing required parameters"))
        return redirect_to("dataset.read", id=dataset_id or "")
    
    try:
        context = {
            "user": g.user,
            "auth_user_obj": g.userobj,
            "ignore_auth": False
        }
        
        # Call the dataset_review action
        result = logic.get_action("dataset_review")(context, {
            "id": dataset_id,
            "review_status": review_status
        })
        
        if review_status == "approved":
            flash_success(_("Dataset has been approved successfully"))
        elif review_status == "rejected":
            flash_success(_("Dataset has been rejected"))
        else:
            flash_success(_("Dataset review status updated"))
            
        log.info(f"Dataset review successful - dataset_id: {dataset_id}, new status: {review_status}")
        
    except logic.NotAuthorized as e:
        log.warning(f"Not authorized to review dataset - user: {g.user}, dataset_id: {dataset_id}")
        flash_error(_("You are not authorized to review datasets"))
    except logic.NotFound as e:
        log.error(f"Dataset not found - dataset_id: {dataset_id}")
        flash_error(_("Dataset not found"))
    except Exception as e:
        log.error(f"Error reviewing dataset: {str(e)}")
        flash_error(_("An error occurred while reviewing the dataset: %s") % str(e))
    
    return redirect_to("dataset.read", id=dataset_id)

# Register the route
dataset.add_url_rule("/review", view_func=review, methods=["POST"])