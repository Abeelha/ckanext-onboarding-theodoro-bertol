import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from ckanext.onboarding_theodoro_bertol.views.home import home
from ckanext.onboarding_theodoro_bertol.views.admin import admin
# from ckanext.onboarding_theodoro_bertol.views.user import user
from ckanext.onboarding_theodoro_bertol.lib.helpers import get_helpers
import ckanext.onboarding_theodoro_bertol.logic.action as actions
import ckanext.onboarding_theodoro_bertol.logic.auth as auth

log = logging.getLogger(__name__)

class OnboardingTheodoroBertolPlugin(
    plugins.SingletonPlugin, 
    toolkit.DefaultDatasetForm
):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IDatasetForm, inherit=False)
    
    # IConfigurer
    def update_config(self, config_):
        log.info("OnboardingTheodoroBertolPlugin: update_config called")
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "onboarding_theodoro_bertol")
        log.info("OnboardingTheodoroBertolPlugin: template and asset directories configured")
    
    # IBlueprint
    def get_blueprint(self):
        log.info("OnboardingTheodoroBertolPlugin: get_blueprint called")
        return [home, admin]
    
    # ITemplateHelpers
    def get_helpers(self):
        log.info("OnboardingTheodoroBertolPlugin: get_helpers called")
        return get_helpers()
    
    # IActions
    def get_actions(self):
        return {
            'user_reviewer_grant': actions.user_reviewer_grant,
            'user_reviewer_revoke': actions.user_reviewer_revoke,
            'package_create': actions.package_create,
            'package_update': actions.package_update,
            'dataset_review': actions.dataset_review,
        }
    
    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'user_reviewer_grant': auth.user_reviewer_grant,
            'user_reviewer_revoke': auth.user_reviewer_revoke,
            'dataset_review': auth.dataset_review,
        }
    
    # IDatasetForm
    def is_fallback(self):
        return True

    def package_types(self):
        return []

    def _modify_package_schema(self, schema):
        schema.update({
            'review_status': [
                toolkit.get_validator('ignore_missing'),
                toolkit.get_converter('convert_to_extras'),
            ]
        })
        return schema

    def create_package_schema(self):
        schema = super().create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super().update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super().show_package_schema()
        schema.update({
            'review_status': [toolkit.get_converter('convert_from_extras')]
        })
        return schema

    def setup_template_variables(self, context, data_dict):
        return super().setup_template_variables(context, data_dict)

    def new_template(self):
        return super().new_template()

    def read_template(self):
        return super().read_template()

    def edit_template(self):
        return super().edit_template()

    def search_template(self):
        return super().search_template()

    def history_template(self):
        return super().history_template()

    def package_form(self):
        return super().package_form()
