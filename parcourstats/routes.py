def includeme(config):
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('home', '/')  # Page d'accueil
    config.add_route('stats', '/stats')  # Statistiques
    config.add_route('admin', '/admin')
    config.add_static_view('static', 'static', cache_max_age=3600)
