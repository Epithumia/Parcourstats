from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config, notfound_view_config


@view_config(route_name='home', renderer='parcourstats:templates/home.jinja2')
def home(request):
    """
    Vue par défaut, page d'accueil d'parcourstats.
    """
    return {'project': 'parcourstats', 'menu_url': request.route_url('stats'), 'url': request.application_url}


@view_config(context=Exception, require_csrf=False)
def internal_server_error(exc, request):
    """
    Génère une vue par défaut quand une vue lève une Exception. La vue est marquée comme exemptée de CSRF pour éviter
    des problèmes d'exceptions en POST. Voir aussi https://github.com/Pylons/pyramid_tm/issues/40

    L'exception capturée est envoyée à Sentry si celui-ci est configuré.
    """
    msg = exc.args[0] if exc.args else ""
    url = request.application_url

    # Dire au client Sentry de capturer l'erreur et l'envoyer.
    request.raven.captureException()

    html = render('parcourstats:templates/500.jinja2', {'url': url, 'msg': msg}, request=request)
    resp = Response(html)
    resp.status_code = 500

    # Dire à Redis de ne pas générer de cookie pour cette session
    resp.cache_control.public = True

    return resp


@notfound_view_config(renderer='parcourstats:templates/404.jinja2')
def notfound_view(request):
    """
    Vue pour les chemins inexistants.

    :param request: La requête.
    :return: void. La page 404 est instanciée et affichée au visiteur.
    """
    request.response.status = 404
    return {'url': request.application_url}



