import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import logging
from ckanext.onboarding_theodoro_bertol.views.home import home

log = logging.getLogger(__name__)

class OnboardingTheodoroBertolPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    
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
        return [home]
