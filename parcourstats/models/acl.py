# -*- coding: utf-8 -*-
from sqlalchemy.orm.exc import NoResultFound

__author__ = 'Rafaël Lopez'

from pyramid.security import Allow, Authenticated
from sqlalchemy import (
    Column,
    String,
    Integer,
    Unicode,
    DateTime
)
from passlib.apps import custom_app_context as pstats_pwd_context

from .meta import Base

import datetime


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True, nullable=False)
    password = Column(Unicode(255), nullable=False)
    last_logged = Column(DateTime, default=datetime.datetime.utcnow)

    def verify_password(self, password):
        # is it cleartext?
        if password == self.password:
            self.set_password(password)

        return pstats_pwd_context.verify(password, self.password)

    def set_password(self, password):
        password_hash = pstats_pwd_context.encrypt(password)
        self.password = password_hash


class Special(Base):
    """
    Special

    Sert à définir/identifier les droits d'utilisateurs spéciaux
    """
    __tablename__ = 'special'
    id = Column(String, primary_key=True, doc="Identifiant de l'utilisateur")
    role = Column(String, nullable=False, doc="Rôle de l'utilisateur")


class RootFactory(object):
    """
    Liste des permissions pour chacun des groupes utilisateurs.
    """
    __acl__ = [(Allow, 'Admin', 'admin'),
               (Allow, 'Admin', 'auth'),
               (Allow, Authenticated, 'auth')
               ]

    def __init__(self, request):
        self.request = request


# noinspection PyMissingConstructor
class RESTFactory(RootFactory):

    def __init__(self, request):
        self.request = request


def groupfinder(username, request):
    """
    Permet de récupérer le groupe de l'utilisateur pour une requête donnée

    :param username: Le nom unique (distinguished name) de l'utilisateur
    :param request: La requête web
    :return: le ou les groupes d'appartenance de l'utilisateur
    """
    session = request.session
    if 'role' in session:
        return session['role']
    try:
        spe = request.dbsession.query(Special).filter(Special.id == username).one()
        session['role'] = [spe.role]
        return [spe.role]
    except NoResultFound:
        pass
    return Authenticated
