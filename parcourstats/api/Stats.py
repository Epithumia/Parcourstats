from cornice.resource import resource, view

from parcourstats.models import Formation, Groupe
from parcourstats.models import acl
from parcourstats.utils import get_data, get_admissions


@resource(collection_path='/api/stats', path='/api/stats/{serie}/{type}', factory=acl.RESTFactory)
class ApiStats(object):
    def __init__(self, request, context=None):
        self.request = request

    @view(renderer='json', permission='auth')
    def collection_get(self):
        dbsession = self.request.dbsession
        formations = dbsession.query(Formation.code.label('Code'),
                                     (Formation.etablissement + ' - ' +
                                      Formation.type_formation + ' - ' +
                                      Formation.domaine + ' - ' +
                                      Formation.mention).label('Nom')).all()
        liste_f = []
        liste_stats = {}
        for f in formations:
            liste_f.append((f.Code, f.Nom))
            liste_stats[f.Code] = get_data(f.Code, dbsession)

        return {'liste_f': liste_f, 'liste_stats': liste_stats}


@resource(collection_path='/api/admissions', path='/api/admissions/{groupe}', factory=acl.RESTFactory)
class ApiAdmissions(object):
    def __init__(self, request, context=None):
        self.request = request

    @view(renderer='json', permission='auth')
    def collection_get(self):
        dbsession = self.request.dbsession
        formations = dbsession.query(Formation.code.label('Code'),
                                     (Formation.etablissement + ' - ' +
                                      Formation.type_formation + ' - ' +
                                      Formation.domaine + ' - ' +
                                      Formation.mention).label('Nom')).all()
        liste_f = []
        liste_stats = {}
        for f in formations:
            groupes = dbsession.query(Groupe).filter(Groupe.id_formation == f.Code).all()
            liste_groupes = [(x.code, x.libelle, x.places, x.nbAppel) for x in groupes]
            liste_f.append((f.Code, f.Nom, liste_groupes))
            for g in groupes:
                liste_stats[g.code] = get_admissions(g.code, dbsession)

        return {'liste_f': liste_f, 'liste_stats': liste_stats}
