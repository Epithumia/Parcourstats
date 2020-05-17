from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey)
from sqlalchemy.orm import (
    relationship,
    backref)

from .meta import Base


class Formation(Base):
    """
    Formation

    Sert à identifier une formation
    """
    __tablename__ = 'formation'
    code = Column(Integer, primary_key=True, autoincrement=True, doc="Identifiant interne de la série")
    etablissement = Column(String, nullable=False, doc="Nom de l'établissement, *obligatoire*.")
    type_formation = Column(String, nullable=False, doc="Type de formation, *obligatoire*.")
    domaine = Column(String, nullable=False, doc="Domaine de la formation, *obligatoire*.")
    mention = Column(String, nullable=False, doc="Mention de la formation', *obligatoire*.")


class SerieBac(Base):
    """
    Filière

    Sert à identifier les différentes séries du bac
    """
    __tablename__ = 'seriebac'
    id = Column(Integer, primary_key=True, autoincrement=True, doc="Identifiant interne de la série")
    nom = Column(String, nullable=False, doc="Nom de la série, *obligatoire*.")


def nom_dossier_par_defaut(context):
    return context.get_current_parameters()['nom']


# noinspection PyIncorrectDocstring,PyUnresolvedReferences
class TypeBac(Base):
    """
    TypeBac

    Sert à enregistrer les informations sur un type de bac
    """
    __tablename__ = 'typebac'
    id = Column(Integer, primary_key=True, autoincrement=True, doc="Identifiant interne du TypeBac.")
    nom = Column(String, nullable=False, doc="Nom du semestre, *obligatoire*.")


class StatDetail(Base):
    """
    StatDetail

    Représente les données détaillées par série/type
    """
    __tablename__ = 'statdetail'
    id_formation = Column(Integer, ForeignKey('formation.code'), primary_key=True,
                          doc="Identifiant de la formation. Fait partie de la clef primaire.")
    id_serie = Column(Integer, ForeignKey('seriebac.id'), primary_key=True,
                      doc="Identifiant de la série de bac. Fait partie de la clef primaire.")
    id_typebac = Column(Integer, ForeignKey('typebac.id'), primary_key=True,
                        doc="Identifiant du code de bac. Fait partie de la clef primaire.")
    timestamp = Column(DateTime, primary_key=True,
                       doc="Date et heure de récupération. Fait partie de la clef primaire.")

    total = Column(Integer, doc="Nombre de voeux.")
    confirmes = Column(Integer, doc="Nombre de voeux confirmés.")

    seriebac = relationship("SerieBac", backref=backref("stats", cascade='all'), foreign_keys=[id_serie],
                            doc="Relation vers :class:`.SerieBac`")
    typebac = relationship("TypeBac", backref=backref("stats", cascade='all'), foreign_keys=[id_typebac],
                           doc="Relation vers :class:`.TypeBac`")


class StatGenerale(Base):
    """
    StatDetail

    Représente les données globales
    """
    __tablename__ = 'statgenerale'
    id_formation = Column(Integer, ForeignKey('formation.code'), primary_key=True,
                          doc="Identifiant de la formation. Fait partie de la clef primaire.")
    timestamp = Column(DateTime, primary_key=True,
                       doc="Date et heure de récupération. Fait partie de la clef primaire.")

    nb_voeux_total = Column(Integer, default=0, doc="Nombre de voeux total.")
    nb_filles_total = Column(Integer, default=0, doc="Nombre de voeux (filles) total.")
    nb_garcons_total = Column(Integer, default=0, doc="Nombre de voeux (garçons) total.")
    nb_boursiers_total = Column(Integer, default=0, doc="Nombre de voeux (boursiers) total.")
    nb_non_boursiers_total = Column(Integer, default=0, doc="Nombre de voeux (non boursiers) total.")

    nb_voeux_confirmes = Column(Integer, default=0, doc="Nombre de voeux confirmés.")
    nb_filles_confirmes = Column(Integer, default=0, doc="Nombre de voeux (filles) confirmés.")
    nb_garcons_confirmes = Column(Integer, default=0, doc="Nombre de voeux (garçons) confirmés.")
    nb_boursiers_confirmes = Column(Integer, default=0, doc="Nombre de voeux (boursiers) confirmés.")
    nb_non_boursiers_confirmes = Column(Integer, default=0, doc="Nombre de voeux (non boursiers) confirmés.")


class Groupe(Base):
    """
    Groupe

    Groupe Parcoursup
    """
    __tablename__ = 'groupe'

    code = Column(Integer, primary_key=True, doc="Identifiant du groupe")
    libelle = Column(String, doc="Libellé du groupe")
    places = Column(Integer, doc="Nombre de places")
    nbAppel = Column(Integer, doc="Nombre de candidats à appeler")

    id_formation = Column(Integer, ForeignKey('formation.code'),
                          doc="Identifiant de la formation. Fait partie de la clef primaire.")
    formation = relationship("Formation", backref=backref("groupes", cascade='all'), foreign_keys=[id_formation],
                             doc="Relation vers :class:`.Formation`")


class Candidat(Base):
    """
    Canddiat

    Données de base sur chaque candidat
    """
    __tablename__ = 'candidat'

    id = Column(Integer, primary_key=True, doc="Identifiant (numéro de dossier) du candidat")
    nom = Column(String, doc="Nom du candidat")
    prenom = Column(String, doc="Prénom du candidat")
    profil = Column(String, doc="Profil parcoursup du candidat")
    etablissement = Column(String, doc="Etablissement d'origine du candidat")
    ordreAppel = Column(Integer, doc="Ordre d'appel Parcoursup")
    classement = Column(Integer, doc="Classement")

    id_groupe = Column(Integer, ForeignKey('groupe.code'),
                       doc="Identifiant de la formation. Fait partie de la clef primaire.")
    groupe = relationship("Groupe", backref=backref("candidats", cascade='all'), foreign_keys=[id_groupe],
                          doc="Relation vers :class:`.Groupe`")


class StatAdmission(Base):
    """
    StatAdmission

    Suivi des admissions
    """
    __tablename__ = 'statadmission'

    id_candidat = Column(Integer, ForeignKey('candidat.id'), primary_key=True,
                         doc="Identifiant du candidat. Fait partie de la clef primaire.")
    timestamp = Column(DateTime, primary_key=True,
                       doc="Date et heure de récupération. Fait partie de la clef primaire.")
    etat = Column(String, doc="Etatde la proposition Parcoursup")
    decision = Column(String, doc="Décision du candidat")

    candidat = relationship("Candidat", backref=backref("statsadmissions", cascade='all'), foreign_keys=[id_candidat],
                          doc="Relation vers :class:`.Candidat`")
