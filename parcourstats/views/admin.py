from pyramid.view import view_config


@view_config(route_name='admin', renderer='parcourstats:templates/vue_template.jinja2', permission='admin')
def admin(request):
    short_title = "Menu Administrateur"
    title = "Parcourstats - " + short_title
    return {'url': request.application_url, 'title': title, 'short_title': short_title}
