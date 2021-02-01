import json

from pandas import read_sql, merge, concat
from sqlalchemy import not_, func
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import literal_column

from parcourstats.models import SerieBac, TypeBac, StatDetail, StatGenerale, StatAdmission, Candidat, Voeu, Specialite


def get_data(code, dbsession):
    data_total = dbsession.query((SerieBac.nom + ' - ' + TypeBac.nom + ' - Total').label('Bac'),
                                 StatDetail.timestamp,
                                 StatDetail.total) \
        .join(StatDetail.seriebac).filter(StatDetail.id_serie == SerieBac.id) \
        .join(StatDetail.typebac).filter(StatDetail.id_typebac == TypeBac.id) \
        .filter(StatDetail.id_formation == code) \
        .order_by(StatDetail.timestamp, SerieBac.id, TypeBac.id)
    data_confirmes = dbsession.query((SerieBac.nom + ' - ' + TypeBac.nom + ' - Confirmés').label('Bac'),
                                     StatDetail.timestamp,
                                     StatDetail.confirmes) \
        .filter(StatDetail.id_formation == code) \
        .join(StatDetail.seriebac).filter(StatDetail.id_serie == SerieBac.id) \
        .join(StatDetail.typebac).filter(StatDetail.id_typebac == TypeBac.id) \
        .order_by(StatDetail.timestamp, SerieBac.id, TypeBac.id)
    stats_total = read_sql(data_total.statement, data_total.session.bind)
    stats_total = stats_total.pivot(index='timestamp', columns='Bac')
    stats_total.columns = stats_total.columns.droplevel(0)

    stats_confirmes = read_sql(data_confirmes.statement, data_confirmes.session.bind)
    stats_confirmes = stats_confirmes.pivot(index='timestamp', columns='Bac')
    stats_confirmes.columns = stats_confirmes.columns.droplevel(0)

    stats = json.loads(merge(stats_total, stats_confirmes, on='timestamp').to_json())

    series_db = dbsession.query(SerieBac.nom).all()
    types_db = dbsession.query(TypeBac.nom).all()

    series = [x[0] for x in series_db]
    types = [x[0] for x in types_db]

    stats_gen_q = dbsession.query(StatGenerale.timestamp,
                                  StatGenerale.nb_voeux_total.label('Voeux (total)'),
                                  StatGenerale.nb_voeux_confirmes.label('Voeux (confirmés)'),
                                  StatGenerale.nb_filles_total.label('Filles (total)'),
                                  StatGenerale.nb_filles_confirmes.label('Filles (confirmés)'),
                                  StatGenerale.nb_garcons_total.label('Garçons (total)'),
                                  StatGenerale.nb_garcons_confirmes.label('Garçons (confirmés)'),
                                  StatGenerale.nb_boursiers_total.label('Boursiers (total)'),
                                  StatGenerale.nb_boursiers_confirmes.label('Boursiers (confirmés)'),
                                  StatGenerale.nb_non_boursiers_total.label('Non boursiers (total)'),
                                  StatGenerale.nb_non_boursiers_confirmes.label('Non boursiers (confirmés)')
                                  ) \
        .order_by(StatGenerale.timestamp).filter(StatGenerale.id_formation == code)
    stats_gen = read_sql(stats_gen_q.statement, stats_gen_q.session.bind, index_col='timestamp')
    stats_gen = json.loads(stats_gen.to_json())

    return {'data': dict(sorted(stats.items())), 'series': series, 'types': types, 'general': stats_gen}


def get_admissions(code, dbsession):
    data_query = dbsession.query(StatAdmission).join(StatAdmission.candidat)
    if code != '*':
        data_query = data_query.filter(Candidat.id_groupe == code)
    data = read_sql(data_query.statement, data_query.session.bind)
    data.replace(to_replace='', value='-', inplace=True)
    data_decision = data.groupby(['decision', 'timestamp']).count().reset_index().pivot(index='timestamp',
                                                                                        columns='decision',
                                                                                        values='id_candidat')
    data_decision = json.loads(data_decision.to_json())
    data_etat = data.groupby(['etat', 'timestamp']).count().reset_index().pivot(index='timestamp', columns='etat',
                                                                                values='id_candidat')
    data_etat = json.loads(data_etat.to_json())
    return {'decisions': data_decision, 'etats': data_etat}


def get_repartition(code, dbsession):
    Specialite2 = aliased(Specialite)

    deux_spe_subq = dbsession.query(Voeu.id) \
        .join(Voeu.specialites) \
        .filter(Specialite.nom.like('%(T)%')) \
        .group_by(Voeu.id) \
        .having(func.count() >= 2) \
        .subquery()
    une_spe_subq = dbsession.query(Voeu.id) \
        .join(Voeu.specialites) \
        .filter(Specialite.nom.like('%(T)%')) \
        .group_by(Voeu.id) \
        .having(func.count() == 1) \
        .subquery()
    zero_spe_subq = dbsession.query(Voeu.id) \
        .filter(not_(Voeu.id.in_(deux_spe_subq))) \
        .filter(not_(Voeu.id.in_(une_spe_subq))) \
        .subquery()

    data_query_zero = dbsession.query(Voeu, literal_column("'NA'").label('nom_spe'),
                                      literal_column("'NA'").label('nom_spe2'),
                                      SerieBac.nom.label('serie_bac')) \
        .join(Voeu.seriebac) \
        .filter(Voeu.actif == 1) \
        .filter(Voeu.id.in_(zero_spe_subq))

    data_query_un = dbsession.query(Voeu, Specialite.nom.label('nom_spe'),
                                    literal_column("'NA'").label('nom_spe2'),
                                    SerieBac.nom.label('serie_bac')) \
        .join(Specialite, Voeu.specialites) \
        .join(Voeu.seriebac) \
        .filter(Voeu.actif == 1) \
        .filter(Specialite.nom.like('%(T)%')) \
        .filter(Voeu.id.in_(une_spe_subq))

    data_query_deux = dbsession.query(Voeu, Specialite.nom.label('nom_spe'),
                                      Specialite2.nom.label('nom_spe2'),
                                      SerieBac.nom.label('serie_bac')) \
        .join(Specialite, Voeu.specialites) \
        .join(Specialite2, Voeu.specialites) \
        .join(Voeu.seriebac) \
        .filter(Voeu.actif == 1) \
        .filter(Specialite.nom.like('%(T)%')) \
        .filter(Specialite2.nom.like('%(T)%')) \
        .filter(Specialite.nom < Specialite2.nom) \
        .filter(Voeu.id.in_(deux_spe_subq))

    data_query = data_query_deux.union(data_query_zero, data_query_un) \
        .order_by(Specialite.nom, Voeu.id)
    if code != '*':
        data_query = data_query.filter(Voeu.id_groupe == code)

    data = read_sql(data_query.statement, data_query.session.bind)

    data_ant_neo = data[['voeu_statut', 'voeu_id']].drop_duplicates().groupby(
        ['voeu_statut']).count().reset_index().set_index('voeu_statut').rename(
        columns={'voeu_id': 'Répartition Néo/Anté'})
    data_filiere = data[['serie_bac', 'voeu_id']].drop_duplicates().groupby(
        ['serie_bac']).count().reset_index().set_index('serie_bac').rename(columns={'voeu_id': 'Série du bac'})
    data_spes = data[['nom_spe', 'nom_spe2', 'voeu_id']].drop_duplicates().groupby(['nom_spe', 'nom_spe2']).count().reset_index()
    data_spes['noms_spes'] = data_spes['nom_spe'] + ' & ' + data_spes['nom_spe2']
    data_spes = data_spes[['noms_spes', 'voeu_id']].set_index('noms_spes').rename(columns={'voeu_id': 'Spécialités'})

    stats_repartition = concat([data_ant_neo, data_filiere, data_spes]).fillna(0).transpose()
    labels = stats_repartition.columns.tolist()
    stats_repartition = json.loads(stats_repartition.to_json(force_ascii=False))

    return {'stats': stats_repartition, 'labels': labels}
