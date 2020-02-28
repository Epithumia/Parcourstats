from pyramid.view import view_config


@view_config(route_name='stats', renderer='parcourstats:templates/vue_template.jinja2', permission='auth')
def stats_js(request):
    session = request.session
    url = request.application_url
    if 'uuid' not in session:
        import uuid
        session['uuid'] = str(uuid.uuid4())
    short_title = "Statistiques"
    title = "Parcourstats - " + short_title
    return {'url': url, 'title': title, 'short_title': short_title}
