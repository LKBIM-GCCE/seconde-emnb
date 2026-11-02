# Site Seconde EMNB

Site de la classe de Seconde EMNB (Lycée des métiers Urbain Vitry), publié avec GitHub Pages depuis le dossier `docs/`.

## Organisation

| Dossier / fichier | Rôle |
|---|---|
| `data/progression.json` | Séquences et séances (titres, objectifs, compétences, déroulé) |
| `data/activites/*.json` | Séances faisables en ligne (cours + activités corrigées) |
| `data/activites/*-cours*.html` | Contenu des cours (avec schémas) |
| `media/maquettes/*.glb / *.json` | Maquettes IFC converties pour la visionneuse 3D |
| `jeux/mission-ifc.html` | Jeu Mission IFC (SEQ03 S1) |
| `fiches/` | Fiches synthèse PDF |
| `plans/` | Plans PDF des projets publiés |
| `assets/` | Style, moteur d'activités, visionneuse IFC, three.js |
| `build.py` | Génère toutes les pages dans `docs/` |

## Mettre à jour

`python build.py` régénère tout le site dans `docs/`.

Les maquettes IFC sont converties avec `outils/ifc2web.py` (ifcopenshell) :
une géométrie `.glb` + un fichier `.json` (classes, niveaux, propriétés, quantités en m / m² / m³).

## Vérifier un certificat

Page `verifier.html` (absente des menus).
