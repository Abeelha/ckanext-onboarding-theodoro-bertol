import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from ckanext.onboarding_theodoro_bertol.views.home import home
from ckanext.onboarding_theodoro_bertol.views.admin import admin
from ckanext.onboarding_theodoro_bertol.lib.helpers import get_helpers

log = logging.getLogger(__name__)

class OnboardingTheodoroBertolPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    
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
