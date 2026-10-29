# Site Seconde EMNB

Site statique de la classe de Seconde EMNB, publié avec GitHub Pages.

## Organisation

```
site-2emnb/
├── data/progression.json   ← LE SEUL FICHIER À MODIFIER pour le contenu
├── assets/style.css        ← l'apparence du site
├── build.py                ← le générateur (ne pas toucher)
└── docs/                   ← le site généré, publié par GitHub Pages
    └── ressources/         ← déposer ici les PDF, IFC, fiches (non effacé par build.py)
```

## Ajouter ou modifier du contenu

1. Ouvrir `data/progression.json`.
2. Compléter une activité : `seances` (titre, durée, contenu) et `ressources`
   (`fichier` pour un document déposé dans `docs/ressources/`, `lien` pour un site externe).
3. Lancer `python build.py` → toutes les pages sont régénérées.
4. Vérifier en ouvrant `docs/index.html` dans le navigateur.
5. Envoyer sur GitHub (commit + push).

## Publier sur GitHub Pages (une seule fois)

1. Créer un dépôt public sur github.com (ex. `seconde-emnb`).
2. Y déposer le contenu de ce dossier.
3. Dépôt → **Settings → Pages** → Source : *Deploy from a branch* → branche `main`, dossier `/docs`.
4. Le site est en ligne à l'adresse `https://<identifiant>.github.io/seconde-emnb/`.

## Point de vigilance

Le dépôt est **public** : ne jamais y mettre de noms d'élèves, de notes ou de documents
sous droits (DCE réels d'entreprises, plans clients) sans autorisation.
