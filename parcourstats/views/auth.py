from parcourstats.models.acl import RESTFactory
from pyramid.authentication import extract_http_basic_credentials
from pyramid.httpexceptions import HTTPFound, HTTPUnauthorized
from pyramid.security import (
    remember,
    forget,
)
from pyramid.view import forbidden_view_config, view_config

from parcourstats.models import User


def resource_factory_predicate(factory):
    """
    Méthode nécessaire pour gérer différents traitements pour les requêtes de type API/REST et les
    vues de page "normales"

    :param factory: ACL
    :return: vrai si l'ACL effectif est celui passé en paramètre.
    """

    # noinspection PyUnusedLocal
    def check_factory(context, request):
        return isinstance(request.context, factory)

    return check_factory


@forbidden_view_config(custom_predicates=(resource_factory_predicate(RESTFactory),))
def require_login(request):
    """
    Traitement de la connexion pour ce qui est API/REST. Déclenche un challenge BasicAuth en cas de non
    login ou erreur.

    Les deux formats prenom.nom et prenom.nom@u-psud.fr sont acceptés

    :param request: La requête
    :return: Une redirection vers la ressource demandée.
    """
    c = extract_http_basic_credentials(request)
    if c is None:
        response = HTTPUnauthorized()
        session = request.session
        session.pop('role', None)
        response.headers.extend(forget(request))
        return response
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:  # pragma: no cover
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    form_login = c.username.split("@u-psud.fr")[0]
    form_password = c.password
    user = request.dbsession.query(User).filter(User.id == form_login).first()
    if user and user.verify_password(form_password):
        headers = remember(request, form_login)
        return HTTPFound(location=came_from, headers=headers)
    else:  # pragma: no cover
        response = HTTPUnauthorized()
        session = request.session
        session.pop('role', None)
        response.headers.extend(forget(request))
        return response


@view_config(route_name='login', renderer='templates/login.jinja2')
@forbidden_view_config(renderer='templates/login.jinja2')
def login(request):
    """
    Traitement de la connexion. Si celle-ci est échouée, on renvoie à la page d'accueil,
    sinon la vue demandée est traitée.

    Les deux formats prenom.nom et prenom.nom@u-psud.fr sont acceptés

    :param request: La requête
    :return: Le dictionnaire des paramètres pour générer la vue.
    """
    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/'  # never use the login form itself as came_from
    came_from = request.params.get('came_from', referrer)
    message = ''
    form_login = ''
    form_password = ''

    if 'form.submitted' in request.POST:
        form_login = request.POST['login']
        form_password = request.POST['password']
        user = request.dbsession.query(User).filter(User.name == form_login).first()
        if user and user.verify_password(form_password):
            headers = remember(request, form_login)
            return HTTPFound(location=came_from, headers=headers)
        else:
            message = 'Invalid credentials'

    return dict(
        message=message,
        url=request.application_url,
        came_from=came_from,
        login=form_login,
        password=form_password
    )


@view_config(route_name='logout', renderer='templates/logout.jinja2')
def logout(request):
    """
    Déconnecte l'utilisateur.
    """
    session = request.session
    session.pop('role', None)
    headers = forget(request)
    request.response.headerlist.extend(headers)
    return {'url': request.application_url}  # On se déconnecte
