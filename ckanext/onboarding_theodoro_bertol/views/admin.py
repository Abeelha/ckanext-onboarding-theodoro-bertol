from flask import Blueprint
import ckan.lib.base as base
import ckan.model as model
import logging

log = logging.getLogger(__name__)

admin = Blueprint('onboarding_admin', __name__, url_prefix='/ckan-admin')

def _get_reviewers():
    # For now, we'll just return sysadmins as placeholder
    # We'll improve this later to use actual reviewer permissions
    q = model.Session.query(model.User).filter(
        model.User.sysadmin.is_(True),
        model.User.state == 'active')
    return q

def reviewers():
    log.info("Admin reviewers page accessed")
    data = dict(reviewers=[u.name for u in _get_reviewers()])
    return base.render('admin/reviewers.html', extra_vars=data)

admin.add_url_rule(
    '/reviewers', view_func=reviewers, methods=['GET'], strict_slashes=False
)
