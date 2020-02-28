from cornice import Service

perms = Service(name='checkperm', path='/api/checkperm', description="Vérifie une permission")


@perms.post()
def get_info(request):
    """
    Vérifie si l'utilisateur a une permission donnée

    :param request: la requête envoyée contenant la permission
    :return: Vrai si l'utilisateur a cette permission, Faux sinon
    """
    p = request.json
    if 'permission' in p:
        perm = p['permission']
        if request.has_permission(perm):
            return {'permission': True}
    return {'permission': False}
