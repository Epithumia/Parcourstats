import json

from pandas import read_sql, merge

from parcourstats.models import SerieBac, TypeBac, StatDetail, StatGenerale, StatAdmission, Candidat


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
    data_accept = data_etat.filter(regex="Formation acceptée \(.*")
    data_refus = data_etat.filter(regex = 'Proposition refusée.*')
    data_renonce = data_etat.filter(regex = 'Renonce.*')
    data_etat['Formation acceptée (total)'] = data_accept.sum(axis=1)
    data_etat['Refus (total)'] = data_refus.sum(axis=1)
    data_etat['Renonce (total)'] = data_renonce.sum(axis=1)

    data_etat = json.loads(data_etat.to_json())
    return {'decisions': data_decision, 'etats': data_etat}
