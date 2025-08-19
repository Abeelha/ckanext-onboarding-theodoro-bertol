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
    # New datasets start as private without review status
    # Review is only needed when changing from private to public
    if 'private' not in data_dict:
        data_dict['private'] = True  # Default to private

    # Only set review status if creating as public
    if not data_dict.get('private', True):
        data_dict['review_status'] = 'pending'
        data_dict['private'] = True  # Force private until approved
        log.info(f"Dataset creation attempted as public - setting to pending review")

    result = up_func(context, data_dict)
    log.info(f"Created dataset {result['id']} - private: {result.get('private')}, review_status: {result.get('review_status', 'none')}")
    return result

@tk.chained_action
def package_update(up_func, context, data_dict):
    """Override package_update to handle private->public transitions"""
    dataset_id = data_dict.get('id')

    # Get current dataset state
    if dataset_id:
        try:
            package_show = tk.get_action('package_show')
            current_dataset = package_show(context, {'id': dataset_id})

            # Check if user is trying to change from private to public
            current_private = current_dataset.get('private', True)
            new_private = data_dict.get('private')
            current_review_status = current_dataset.get('review_status', '')

            # If changing from private to public and not already approved
            if current_private and new_private is False and current_review_status != 'approved':
                # Set to pending review and keep private
                data_dict['review_status'] = 'pending'
                data_dict['private'] = True
                log.info(f"Dataset {dataset_id} attempted to go public - setting to pending review")

                # Store that user tried to make it public (for later notification)
                if 'reviewer_id' in current_dataset:
                    data_dict['last_reviewer_id'] = current_dataset.get('reviewer_id')

            # If dataset was rejected and is being edited, set back to pending
            elif current_review_status == 'rejected' and 'title' in data_dict:
                data_dict['review_status'] = 'pending'
                log.info(f"Rejected dataset {dataset_id} modified - setting back to pending review")

                # Store last reviewer for notification
                if 'reviewer_id' in current_dataset:
                    data_dict['last_reviewer_id'] = current_dataset.get('reviewer_id')
                    data_dict['resubmitted_after_rejection'] = True

        except Exception as e:
            log.warning(f"Could not check current dataset state: {e}")

    result = up_func(context, data_dict)
    log.info(f"Updated dataset {result['id']} - private: {result.get('private')}, review_status: {result.get('review_status', 'none')}")
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

    # Get reviewer user
    user = context.get('auth_user_obj') or context.get('user_obj')
    reviewer_id = user.id if user else context.get('user')

    # Check if this was resubmitted after rejection and send notification
    if dataset.get('resubmitted_after_rejection') and dataset.get('last_reviewer_id'):
        try:
            # Send email notification to last reviewer
            _send_resubmission_notification(dataset.get('last_reviewer_id'), dataset)
        except Exception as e:
            log.warning(f"Could not send email notification: {e}")

    # Update review status
    update_data = {
        'id': dataset_id,
        'review_status': review_status,
        'reviewer_id': reviewer_id,
        'review_date': tk.h.render_datetime(tk.h.date_str_to_datetime(''), with_hours=True),
        'resubmitted_after_rejection': False
    }

    # If approved, make the dataset public
    if review_status == 'approved':
        update_data['private'] = False

    # Update the dataset
    package_patch = tk.get_action('package_patch')
    result = package_patch(context, update_data)

    log.info(f"Dataset {dataset_id} review status changed to: {review_status} by reviewer: {reviewer_id}")
    return result

def _send_resubmission_notification(reviewer_id, dataset):
    """Send email notification to reviewer when dataset is resubmitted"""
    try:
        # Get reviewer user
        user_show = tk.get_action('user_show')
        reviewer = user_show({'ignore_auth': True}, {'id': reviewer_id})

        if reviewer.get('email'):
            # Prepare email
            subject = f"Dataset Resubmitted for Review: {dataset.get('title', 'Untitled')}"
            body = f"""
            Hello {reviewer.get('display_name', 'Reviewer')},

            A dataset you previously reviewed has been modified and resubmitted for review.

            Dataset: {dataset.get('title', 'Untitled')}
            URL: {tk.url_for('dataset.read', id=dataset['id'], _external=True)}

            The dataset is now pending your review.

            Best regards,
            CKAN System
            """

            # Send email using CKAN's mailer
            from ckan.lib.mailer import send_mail
            send_mail(reviewer['email'], subject, body)
            log.info(f"Sent resubmission notification to {reviewer['email']} for dataset {dataset['id']}")
    except Exception as e:
        log.error(f"Failed to send email notification: {e}")
