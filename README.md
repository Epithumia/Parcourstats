# Parcourstats

Logiciel de récupération et d'affichage des statistiques Parcoursup pour une ou plusieurs formations.

## Démarrage

Les instructions suivantes devraient vous aider à installer et utiliser cet outil.

### Pré-requis

Il faut :
- Python >=3.6
- Npm >=10
- Redis
- Chrome
Sous Debian/Ubuntu par exemple :
```
sudo sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list'
sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sudo apt-get update
sudo apt-get install -qq bsdtar google-chrome-stable
```
- Le ChromeDriver approprié (ou FirefoxDriver)
```
PLATFORM=linux64
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
sudo curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip | sudo bsdtar -xvf - -C ./bin/
```

### Installation

Il faut (idéalement) créer un environnement virtuel (via `virtualenv`) ou a minima créer un dossier
qui sera ensuite réservé avec la bonne distribution python dedans (avec `pyenv` par exemple).
Une fois dans le dossier :

```
git clone https://github.com/Epithumia/Parcourstats
cd Parcourstats
pip install -e . 
alembic upgrade head
npm install
npm run build
```

## Utilisation

### Récupérer des données de Parcoursup

Un exemple de fichier de configuration est donné par [parcoursup_dut_info.sample.ini](). Il faut compléter
les différents champs. Il faut a minima login et mot de passe et le *code* de la formation à récupérer. A défaut de code,
on peut donner les quatre champs *etbt* (Etablissement), *type_formation*, *domaine* et *mention*.

L'URL pour SQLAlchemy ne devrait pas être modifiée. Si c'est le cas, il faut la modifier aussi dans [migration.ini](),
renommer le fichier créé à l'étape précédente, et modifier l'url dans les fichiers de configuration pour l'affichage
(cf. section suivante).

```
fetch_parcoursup_db <fichier.ini>
``` 

Le programme limite volontairement la fréquence des données à 4/jour (minuit, 6h, midi, 18h).

### Afficher les données

Un exemple de fichier de configuration est donné par [development.sample.ini]() pour le développement, 
et par [production.sample.ini]() pour le mise en production.

Pour récupérer plusieurs formations, il faut plusieurs fichiers de configuration. A utiliser à vos risques et périls,
je n'ai accès qu'à une et je ne peux pas tester que cela récupère bien les détails des différentes formations.

```
pserve development.ini
```
Puis ouvrir http://0.0.0.0:6543 dans son navigateur. L'installation créé un utilisateur *test* ayant pour
mot de passe *test*.

Pour le moment, la gestion des utilisateurs est très sommaire, les modifications sont à faire directement
dans la base sqlite (avec `sqlite3` par exemple).

Pour la mise en production :
```
gunicorn --timeout 180 --workers 4 --paster production.ini
```
Tout cela peut tourner derrière un serveur Nginx.

## Démo

[https://pstatsdemo.grendel.fr](https://pstatsdemo.grendel.fr/stats)

## Frameworks

* [Pyramid](https://trypyramid.com/) - Framework Web Python (backend, API)
* [Vue.js](https://vuejs.org/) - Framework Web JS (frontend)
* [Apexcharts.js](https://apexcharts.com/) - Visualisation

## Contribuer

Toutes les contributions/améliorations sont les bienvenues.

## Auteur

* **Rafaël Lopez** - *Création* - [Epithumia](https://github.com/Epithumia)

## Licence

GPLv3 (voir [LICENSE.md](LICENSE.md))
