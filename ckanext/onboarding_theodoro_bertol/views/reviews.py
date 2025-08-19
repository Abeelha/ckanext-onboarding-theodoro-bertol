from flask import Blueprint
from ckan.common import g, _, request
import ckan.logic as logic
import ckan.lib.helpers as h
import ckan.model as model
from ckan.lib.base import render
import logging

log = logging.getLogger(__name__)

reviews = Blueprint("onboarding_reviews", __name__, url_prefix="/dataset-reviews")

def dataset_reviews_list():
    """List all datasets pending review or recently reviewed"""
    context = {
        'user': g.user,
        'auth_user_obj': g.userobj,
        'for_view': True
    }
    
    # Check if user is a reviewer
    from ckanext.onboarding_theodoro_bertol.lib.helpers import user_is_reviewer
    is_reviewer = user_is_reviewer(g.userobj.id if g.userobj else None)
    
    if not is_reviewer:
        h.flash_error(_('You must be a reviewer to access this page'))
        return h.redirect_to('home.index')
    
    try:
        # Get filter parameters
        review_status = request.args.get('review_status', '')
        
        # Build search query
        search_params = {
            'q': '*:*',
            'rows': 100,
            'sort': 'metadata_modified desc',
            'facet.field': ['review_status']
        }
        
        # Add review status filter if specified
        if review_status:
            search_params['fq'] = f'review_status:{review_status}'
        
        # Search for datasets
        package_search = logic.get_action('package_search')
        search_results = package_search(context, search_params)
        
        # Filter datasets based on user access
        filtered_datasets = []
        for dataset in search_results.get('results', []):
            # Check if user has access to this dataset
            try:
                logic.check_access('package_show', context, {'id': dataset['id']})
                # Add reviewer info if available
                if dataset.get('reviewer_id'):
                    try:
                        user_show = logic.get_action('user_show')
                        reviewer = user_show(context, {'id': dataset['reviewer_id']})
                        dataset['reviewer_name'] = reviewer.get('display_name', reviewer.get('name'))
                    except:
                        dataset['reviewer_name'] = 'Unknown'
                filtered_datasets.append(dataset)
            except logic.NotAuthorized:
                continue
        
        # Get review status facets
        facets = search_results.get('facets', {}).get('review_status', {})
        
        extra_vars = {
            'datasets': filtered_datasets,
            'total_count': len(filtered_datasets),
            'facets': facets,
            'current_filter': review_status,
            'is_reviewer': is_reviewer
        }
        
        return render('reviews/list.html', extra_vars)
        
    except Exception as e:
        log.error(f"Error loading dataset reviews: {e}")
        h.flash_error(_('Error loading dataset reviews'))
        return h.redirect_to('home.index')

# Register routes
reviews.add_url_rule('/', view_func=dataset_reviews_list, methods=['GET'])