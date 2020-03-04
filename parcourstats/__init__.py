from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator

from .models.acl import groupfinder, RootFactory


# noinspection PyUnusedLocal
def main(global_config, **settings):
    """
    Application principale

    :return: Une application WSG
    """
    config = Configurator(settings=settings, root_factory=RootFactory)
    config.include('pyramid_jinja2')
    config.add_jinja2_extension('jinja2.ext.do')
    config.include('pyramid_redis_sessions')
    config.include('pyramid_dogpile_cache2')
    config.include('pyramid_tm')
    config.include('cornice')

    config.set_authentication_policy(
        AuthTktAuthenticationPolicy('seekr1t', callback=groupfinder)
    )

    config.set_authorization_policy(
        ACLAuthorizationPolicy()
    )

    config.include('.models')
    config.include('.routes')
    config.scan(ignore='.tests')
    return config.make_wsgi_app()
