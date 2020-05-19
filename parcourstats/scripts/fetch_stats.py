# -*- coding: utf-8 -*-
import datetime
import optparse

import transaction
from pandas import read_html
from pyramid.paster import bootstrap, setup_logging, get_appsettings
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from sqlalchemy import engine_from_config

from parcourstats.models import get_session_factory, get_tm_session, StatGenerale, SerieBac, TypeBac, StatDetail, \
    Formation, Groupe, Candidat, StatAdmission


def run(args):
    config_uri = args[0]
    with bootstrap(config_uri):
        setup_logging(config_uri)
        settings = get_appsettings(config_uri)
        engine = engine_from_config(settings, 'sqlalchemy.')
        login = settings['parcoursup.login']
        mdp = settings['parcoursup.mdp']
        etbt = settings.get('parcoursup.etbt', None)
        type_formation = settings.get('parcoursup.type_formation', None)
        domaine = settings.get('parcoursup.domaine', None)
        mention = settings.get('parcoursup.mention', None)
        code = settings.get('parcoursup.code_formation', None)
        sf = get_session_factory(engine)
        dbsession = get_tm_session(sf, transaction.manager)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        browser = webdriver.Chrome(chrome_options=chrome_options)
        browser.get('https://gestion.parcoursup.fr/Gestion')
        element = WebDriverWait(browser, 90).until(lambda x: x.find_element_by_name('g_ea_cod'))
        element.send_keys(login)
        element = browser.find_element_by_name('g_ea_mot_pas')
        element.send_keys(mdp)
        element = browser.find_element_by_class_name('bouton')
        element.click()
        element = WebDriverWait(browser, 90).until(lambda x: x.find_element_by_link_text('Candidatures'))
        element.click()
        element = WebDriverWait(browser, 90).until(lambda x: x.find_element_by_link_text('Statistiques'))
        element.click()
        ligne = 0
        fpath = '/html/body/div[2]/div[4]/div[2]/div[3]/div/table/tbody/tr['
        try:
            for n in range(1, 50):
                element1 = browser.find_element_by_xpath(fpath + str(n) + ']/td[1]')
                element2 = browser.find_element_by_xpath(fpath + str(n) + ']/td[2]')
                element3 = browser.find_element_by_xpath(fpath + str(n) + ']/td[3]')
                element4 = browser.find_element_by_xpath(fpath + str(n) + ']/td[4]')
                element5 = browser.find_element_by_xpath(fpath + str(n) + ']/td[5]')
                if (code and element5.text == code) or (
                        element1.text == etbt and
                        element2.text == type_formation and
                        element3.text == domaine and
                        element4.text == mention):
                    ligne = n
                    code = element5.text
                    etbt = element1.text
                    type_formation = element2.text
                    domaine = element3.text
                    mention = element4.text
        except NoSuchElementException:
            pass
        if ligne == 0:
            print('Formation inconnue')
            browser.close()
            exit(1)
        fo = dbsession.query(Formation).filter(Formation.code == code).first()
        if fo is None:
            fo = Formation(code=code)
        fo.type_formation = type_formation
        fo.etablissement = etbt
        fo.domaine = domaine
        fo.mention = mention
        dbsession.add(fo)
        transaction.manager.commit()
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[7]')
        nb_voeux_total = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[9]')
        nb_filles_total = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[10]')
        nb_garcons_total = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[11]')
        nb_boursiers_total = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[12]')
        nb_non_boursiers_total = element.text

        element = browser.find_element_by_id('choix_stats')
        sel = Select(element)
        sel.select_by_visible_text('Total des voeux confirmés')

        element = WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_xpath(fpath + str(ligne) + ']/td[7]'))
        nb_voeux_confirmes = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[9]')
        nb_filles_confirmes = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[10]')
        nb_garcons_confirmes = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[11]')
        nb_boursiers_confirmes = element.text
        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[12]')
        nb_non_boursiers_confirmes = element.text

        now = datetime.datetime.now()
        if now.time().hour < 6:
            prev = datetime.datetime(now.year, now.month, now.day)
        elif now.time().hour < 12:
            prev = datetime.datetime(now.year, now.month, now.day, 6, 0, 0)
        elif now.time().hour < 18:
            prev = datetime.datetime(now.year, now.month, now.day, 12, 0, 0)
        else:
            prev = datetime.datetime(now.year, now.month, now.day, 18, 0, 0)

        stat_gen_q = dbsession.query(StatGenerale).filter(StatGenerale.id_formation == code,
                                                          StatGenerale.timestamp.between(prev, now)).first()
        if stat_gen_q is None:
            stat_gen_q = StatGenerale(id_formation=code)

        stat_gen_q.nb_voeux_total = nb_voeux_total
        stat_gen_q.nb_voeux_confirmes = nb_voeux_confirmes
        stat_gen_q.nb_boursiers_confirmes = nb_boursiers_confirmes
        stat_gen_q.nb_boursiers_total = nb_boursiers_total
        stat_gen_q.nb_filles_confirmes = nb_filles_confirmes
        stat_gen_q.nb_filles_total = nb_filles_total
        stat_gen_q.nb_garcons_confirmes = nb_garcons_confirmes
        stat_gen_q.nb_garcons_total = nb_garcons_total
        stat_gen_q.nb_non_boursiers_confirmes = nb_non_boursiers_confirmes
        stat_gen_q.nb_non_boursiers_total = nb_non_boursiers_total
        stat_gen_q.timestamp = prev

        dbsession.add(stat_gen_q)
        transaction.manager.commit()

        element = browser.find_element_by_xpath(fpath + str(ligne) + ']/td[13]/a')
        element.click()

        element = WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_id('choix_details_stats'))
        sel = Select(element)
        sel.select_by_visible_text('Total des voeux')
        element = WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_id('choix_details_stats'))
        sel = Select(element)

        path = '/html/body/div[2]/div[4]/div/div[2]/div[3]/div/table/tbody/tr['
        try:
            details_total = {}
            for i in range(1, 30):
                j = 1
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                serie_bac = cell.text
                if serie_bac not in details_total.keys():
                    details_total[serie_bac] = {}
                seriebac_q = dbsession.query(SerieBac).filter(SerieBac.nom == serie_bac).first()

                if seriebac_q is None:
                    seriebac_q = SerieBac()
                    seriebac_q.nom = serie_bac
                    dbsession.add(seriebac_q)
                    transaction.manager.commit()

                j = 2
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                type_bac = cell.text
                typebac_q = dbsession.query(TypeBac).filter(TypeBac.nom == type_bac).first()

                if typebac_q is None:
                    typebac_q = TypeBac()
                    typebac_q.nom = type_bac
                    dbsession.add(typebac_q)
                    transaction.manager.commit()
                j = 3
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                nb_voeux_serie_type = cell.text
                details_total[serie_bac][type_bac] = nb_voeux_serie_type
                typebac_q = dbsession.query(TypeBac).filter(TypeBac.nom == type_bac).first()
                seriebac_q = dbsession.query(SerieBac).filter(SerieBac.nom == serie_bac).first()
                stat = dbsession.query(StatDetail).filter(StatDetail.id_typebac == typebac_q.id,
                                                          StatDetail.id_serie == seriebac_q.id,
                                                          StatDetail.timestamp == prev,
                                                          StatDetail.id_formation == code).first()
                if stat is None:
                    stat = StatDetail(id_typebac=typebac_q.id, id_serie=seriebac_q.id, timestamp=prev, total=0,
                                      confirmes=0, id_formation=code)
                stat.total = nb_voeux_serie_type
                dbsession.add(stat)
                transaction.manager.commit()

        except NoSuchElementException:
            pass
        transaction.manager.commit()
        sel.select_by_visible_text('Total des voeux confirmés')
        WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_id('choix_details_stats'))
        try:
            details_confirmes = {}
            for i in range(1, 30):
                j = 1
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                serie_bac = cell.text
                if serie_bac not in details_confirmes.keys():
                    details_confirmes[serie_bac] = {}
                seriebac_q = dbsession.query(SerieBac).filter(SerieBac.nom == serie_bac).first()

                if seriebac_q is None:
                    seriebac_q = SerieBac()
                    seriebac_q.nom = serie_bac
                    dbsession.add(seriebac_q)
                    transaction.manager.commit()
                j = 2
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                type_bac = cell.text
                typebac_q = dbsession.query(TypeBac).filter(TypeBac.nom == type_bac).first()

                if typebac_q is None:
                    typebac_q = SerieBac()
                    typebac_q.nom = type_bac
                    dbsession.add(typebac_q)
                    transaction.manager.commit()
                j = 3
                xpath = path + str(i) + ']/td[' + str(j) + ']'
                cell = browser.find_element_by_xpath(xpath)
                nb_voeux_serie_type = cell.text
                details_confirmes[serie_bac][type_bac] = nb_voeux_serie_type
                typebac_q = dbsession.query(TypeBac).filter(TypeBac.nom == type_bac).first()
                seriebac_q = dbsession.query(SerieBac).filter(SerieBac.nom == serie_bac).first()
                stat = dbsession.query(StatDetail).filter(StatDetail.id_typebac == typebac_q.id,
                                                          StatDetail.id_serie == seriebac_q.id,
                                                          StatDetail.timestamp == prev,
                                                          StatGenerale.id_formation == code).first()
                if stat is None:
                    stat = StatDetail(id_typebac=typebac_q.id, id_serie=seriebac_q.id, timestamp=prev, total=0,
                                      confirmes=0, id_formation=code)
                stat.confirmes = nb_voeux_serie_type
                dbsession.add(stat)
                transaction.manager.commit()
        except NoSuchElementException:
            pass

        element = WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_link_text('Admissions'))
        element.click()
        element = WebDriverWait(browser, 90).until(
            lambda x: x.find_element_by_link_text('Suivi des admissions'))
        element.click()
        fpath = '/html/body/div[2]/div[4]/div/div/div[3]/div/table/tbody/tr['
        try:
            for n in range(1, 50):
                element2 = browser.find_element_by_xpath(fpath + str(n) + ']/td[2]')
                if (code and element2.text == code):
                    ligne = n
        except NoSuchElementException:
            pass
        if ligne == 0:
            print('Formation inconnue')
            browser.close()
            exit(1)

        try:
            for n in range(ligne, 50):
                fpath = '/html/body/div[2]/div[4]/div/div/div[3]/div/table/tbody/tr['
                code_groupe = browser.find_element_by_xpath(fpath + str(n) + ']/td[4]').text
                libelle = browser.find_element_by_xpath(fpath + str(n) + ']/td[5]').text
                places = browser.find_element_by_xpath(fpath + str(n) + ']/td[6]').text
                nb_cand = browser.find_element_by_xpath(fpath + str(n) + ']/td[7]').text
                groupe = dbsession.query(Groupe).filter(Groupe.code == code_groupe)
                if groupe.count() == 0 and libelle != 'Total':
                    groupe = Groupe(code=code_groupe, libelle=libelle, places=places, nbAppel=nb_cand,
                                    id_formation=code)
                    dbsession.add(groupe)
                    transaction.manager.commit()
                # /html/body/div[2]/div[4]/div/div/div[3]/div/table/tbody/tr[1]/td[12]
                if libelle != 'Total':
                    details = browser.find_element_by_xpath(fpath + str(n) + ']/td[18]')
                    details.click()

                    # /html/body/div[2]/div[5]/div/div[2]/div[1]/div[2]/div/label/select/
                    element = WebDriverWait(browser, 90).until(
                        lambda x: x.find_element_by_xpath(
                            '/html/body/div[2]/div[5]/div/div[2]/div[1]/div[2]/div/label/select'))
                    sel = Select(element)
                    sel.select_by_visible_text('Tout')
                    # Get tous les candidats du groupe
                    tpath = '/html/body/div[2]/div[5]/div/div[2]/div[3]/div/table'
                    table = browser.find_element_by_xpath(tpath)
                    df = read_html(table.get_attribute('outerHTML'))
                    d = df[0000]
                    d.columns = ['ordre', 'classement', 'date', 'id_candidat', 'nom', 'profil', 'etabl', 'etat',
                                 'decision', 'dossier']
                    list_cand = dbsession.query(Candidat.id).filter(Candidat.id_groupe == code_groupe).all()
                    list_cand = [x[0] for x in list_cand]
                    for row in d[
                        ['ordre', 'classement', 'id_candidat', 'nom', 'profil', 'etabl', 'etat', 'decision']].values:
                        try:
                            if int(row[2]) not in list_cand:
                                candidat = Candidat(id=int(row[2]), nom=row[3], profil=row[4], etablissement=row[5],
                                                    ordreAppel=int(row[0]), classement=int(row[1]), id_groupe=code_groupe)
                                dbsession.add(candidat)
                                transaction.manager.commit()
                            stat_adm = dbsession.query(StatAdmission).filter(StatAdmission.id_candidat == int(row[2]),
                                                                             StatAdmission.timestamp == prev).first()
                            if stat_adm is None:
                                stat_adm = StatAdmission(id_candidat=int(row[2]), timestamp=prev, etat=row[6],
                                                         decision=row[7])
                            else:
                                stat_adm.etat = row[6]
                                stat_adm.decision = row[7]
                            dbsession.add(stat_adm)
                            transaction.manager.commit()
                        except ValueError:
                            pass
                    element = WebDriverWait(browser, 90).until(
                        lambda x: x.find_element_by_link_text('Admissions'))
                    element.click()
                    # TODO : lien ci-dessous
                    element = WebDriverWait(browser, 90).until(
                        lambda x: x.find_element_by_link_text('Suivi des admissions'))
                    element.click()

        except NoSuchElementException:
            pass
        browser.close()


def main():
    usage = 'usage: %prog [options] fichier'
    parser = optparse.OptionParser(usage=usage, add_help_option=False)
    parser.add_option('-h', '--help', action='help',
                      help="Affiche ce message d'aide et termine.")
    (opt, args) = parser.parse_args()
    if len(args) != 1:
        parser.error("Mauvais nombre de paramètres")
    run(args)


if __name__ == '__main__':
    main()
