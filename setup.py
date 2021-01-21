from setuptools import setup, find_packages

requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'pyramid-redis-sessions',
    'pyramid_bootstrap',
    'pyramid_dogpile_cache2',
    'SQLAlchemy>=1.2.3',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'pandas',
    'iso8601',
    'cornice',
    'dictalchemy',
    'colanderalchemy',
    'simplejson',
    'alembic',
    'selenium',
    'passlib',
    'gunicorn'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest<5',  # includes virtualenv
    'pytest-cov',
    'python-ldap-test',
    'pytest-localserver',
    'flaky'
]

docs_require = [
    'sphinx',
    'sphinx-autobuild',
]

setup(name='parcourstats',
      version='2.0.0',
      description='parcourstats',
      long_description='Utilistaire pour récupérer et afficher les statistiques Parcoursup',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Rafaël Lopez',
      author_email='rafael.lopez@u-psud.fr',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
          'docs': docs_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = parcourstats:main
      [console_scripts]
      initialisation_parcourstats_db = parcourstats.scripts.initializedb:main
      fetch_parcourstats_db = parcourstats.scripts.fetch_stats:main
      """,
      )
