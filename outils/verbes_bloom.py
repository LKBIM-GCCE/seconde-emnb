"""[Appliqué le 25/11/2026 — ne plus relancer : les textes ont depuis été passés au vouvoiement (vouvoyer.py).]
Reformule les consignes des activités en ligne avec des verbes d'action (taxonomie de Bloom,
niveaux 1 à 3 adaptés à la Seconde) et ajoute un badge « verbe » à chaque mission.
Script idempotent : relançable sans effet si déjà appliqué. La SEQ03 S4 a déjà ses verbes (gen_seq03.py)."""
import json
from pathlib import Path

RAC = Path(__file__).resolve().parent.parent / "data" / "activites"

# id activité -> id bloc -> {verbe, consigne (texte complet), t: {ancien titre: nouveau}, q: {ancienne question: nouvelle}}
M = {
 "seq01-s1": {
  "td01": {"verbe": "Identifier", "consigne": "Identifie l'acteur qui parle, à partir des indices de chaque carte (et d'internet si besoin). Le secteur du bâtiment fait intervenir de nombreux acteurs aux rôles bien distincts."},
  "td02": {"verbe": "Associer", "t": {"Exercice 1 — Relie chaque métier à sa tâche principale": "Exercice 1 — Associe chaque métier à sa tâche principale",
                                      "Exercice 2 — Écris chaque sigle en toutes lettres": "Exercice 2 — Traduis chaque sigle en toutes lettres",
                                      "Exercice 3 — Et toi ?": "Exercice 3 — Explique ton choix de métier"},
           "q": {"« Parmi ces métiers, lequel t'attire le plus ? Pourquoi ? » Réponds en 2 à 3 phrases.": "Cite le métier qui t'attire le plus parmi ceux-ci, puis explique pourquoi en 2 à 3 phrases."}},
  "td03": {"verbe": "Compléter", "t": {"Exercice 1 — Place chaque acteur dans la bonne case": "Exercice 1 — Complète le schéma : place chaque acteur dans la bonne case",
                                       "Exercice 2 — Contractuel ou fonctionnel ?": "Exercice 2 — Classe chaque lien : contractuel ou fonctionnel ?",
                                       "Exercice 3 — Question de réflexion": "Exercice 3 — Explique ton choix"},
           "q": {"« Parmi toutes ces relations, laquelle te semble la plus importante pour la réussite d'un projet ? Justifie ta réponse. »": "Indique la relation qui te semble la plus importante pour la réussite d'un projet, puis explique pourquoi."}},
 },
 "seq01-s2": {
  "td04": {"verbe": "Ordonner"},
  "td05": {"verbe": "Identifier", "t": {"Exercice 1 — Les 8 dossiers": "Exercice 1 — Identifie la phase de chacun des 8 dossiers"}},
  "td06": {"verbe": "Compléter", "t": {"Partie 1 — Coche chaque case où l'acteur intervient": "Partie 1 — Complète le tableau : coche chaque case où l'acteur intervient",
                                       "Partie 2 — Qui est-ce ?": "Partie 2 — Identifie l'acteur décrit",
                                       "Partie 3 — Vrai ou faux ?": "Partie 3 — Distingue le vrai du faux"}},
  "quiz": {"verbe": "Répondre"},
 },
 "seq01-s3": {
  "bugs": {"verbe": "Identifier", "t": {"1. Quel acteur est en cause ?": "1. Identifie l'acteur en cause",
                                        "2. Quelle phase n'a pas été respectée ?": "2. Indique la phase qui n'a pas été respectée",
                                        "3. Quelle solution concrète ?": "3. Sélectionne la solution concrète"}},
  "dossier": {"verbe": "Ordonner", "t": {"1. Remets les documents dans l'ordre chronologique": "1. Ordonne les documents dans l'ordre chronologique",
                                         "2. À quelle phase appartient chaque document ?": "2. Associe chaque document à sa phase",
                                         "3. Qui produit ce document ?": "3. Identifie qui produit chaque document",
                                         "4. Qui le reçoit et l'utilise ?": "4. Identifie qui reçoit et utilise chaque document"}},
  "tableau": {"verbe": "Compléter", "t": {"1. Qui intervient à chaque grande étape ?": "1. Complète le tableau : qui intervient à chaque grande étape ?",
                                          "2. Qui fait quoi ?": "2. Associe chaque tâche à son acteur"}},
 },
 "seq01-s4": {
  "role": {"verbe": "Préparer", "t": {"1. Quelles sont les conséquences de la terrasse ajoutée ?": "1. Identifie les conséquences de la terrasse ajoutée",
                                      "2. Ma réaction (modèle du tour de table)": "2. Prépare ta réaction (modèle du tour de table)"}},
  "bim": {"verbe": "Comparer", "t": {"1. Vrai ou faux ?": "1. Distingue le vrai du faux", "2. À quoi sert le BIM ?": "2. Définis le BIM avec tes mots"},
          "q": {"Selon toi, à quoi sert le BIM dans un projet de construction ? Formule une définition avec tes mots.": "Définis avec tes mots à quoi sert le BIM dans un projet de construction."}},
  "qcm": {"verbe": "Répondre"},
  "bilan": {"verbe": "Expliquer", "q": {"Sur ton futur métier : dans quel acteur de la construction te reconnais-tu le plus ? Pourquoi ?": "Indique l'acteur de la construction dans lequel tu te reconnais le plus, puis explique pourquoi."}},
 },
 "seq02-s1": {
  "classer": {"verbe": "Classer", "t": {"À quoi sert chaque type de plan ?": "Associe chaque type de plan à son usage"}},
  "situation": {"verbe": "Localiser", "t": {"1. Lis les informations du plan": "1. Relève les informations du plan", "3. Synthèse": "3. Explique le rôle du plan"}},
  "masse": {"verbe": "Identifier", "t": {"1. Informations sur la parcelle": "1. Relève les informations sur la parcelle",
                                         "2. Les réseaux représentés": "2. Identifie les réseaux représentés", "3. Synthèse": "3. Distingue les deux plans"}},
 },
 "seq02-s2": {
  "defi": {"verbe": "Localiser", "consigne": "Tu viens d'emménager dans la Villa Camacho. Pour chaque situation, localise la pièce du rez-de-chaussée où tu te trouves."},
  "niveaux": {"verbe": "Identifier", "t": {"1. Rez-de-chaussée : nomme les pièces": "1. Rez-de-chaussée : identifie et nomme les pièces",
                                           "2. Étage : nomme les pièces": "2. Étage : identifie et nomme les pièces",
                                           "3. Lis les informations du plan RDC": "3. Relève les informations du plan RDC"}},
  "facades": {"verbe": "Relier", "t": {"Synthèse": "Explique la différence entre plan et façade"}},
 },
 "seq02-s3": {
  "traits": {"verbe": "Localiser", "consigne": "Localise sur les plans les traits de coupe A-A et B-B.",
             "q": {"À quoi servent les traits de coupe sur un plan ? Réponds en une phrase.": "Explique en une phrase à quoi servent les traits de coupe sur un plan."}},
  "coupeA": {"verbe": "Identifier"},
  "hauteurs": {"verbe": "Relever", "consigne": "Relève les cotes de hauteur sur la coupe A-A. Les cotes sont en centimètres : convertis les valeurs en mètres."},
  "echelles": {"verbe": "Calculer", "t": {"1. Quelle échelle pour quel plan ?": "1. Associe chaque plan à son échelle",
                                          "2. Du réel vers le plan": "2. Calcule : du réel vers le plan", "3. Du plan vers le réel": "3. Calcule : du plan vers le réel"}},
 },
 "seq02-s4": {
  "phase": {"verbe": "Identifier", "consigne": "Identifie la phase de chaque plan décrit, à partir de son niveau de détail."},
  "etude": {"verbe": "Comparer", "t": {"1. Ces évolutions ont-elles eu lieu entre l'APS et l'APD ?": "1. Compare l'APS et l'APD : ces évolutions ont-elles eu lieu ?",
                                       "2. Pourquoi ces évolutions ?": "2. Explique ces évolutions"}},
  "quiz": {"verbe": "Répondre"},
  "bilan": {"verbe": "Expliquer", "q": {"Quelle est, pour toi, la chose la plus importante apprise dans cette séquence sur la lecture de plans ? Pourquoi ?": "Cite la chose la plus importante que tu as apprise dans cette séquence sur la lecture de plans, puis explique pourquoi."}},
 },
 "seq03-s1": {
  "lancement": {"verbe": "Expliquer", "t": {"Ton hypothèse": "Explique ton hypothèse"},
                "q": {"Avec tes mots : comment envoyer une maquette à quelqu'un qui n'a pas Revit ?": "Explique avec tes mots comment envoyer une maquette à quelqu'un qui n'a pas Revit."}},
  "jeu": {"verbe": "Explorer", "t": {"Mon résultat": "Indique ton résultat"},
          "q": {"Recopie ton score final et ton titre (ex. : 260 pts — Modeleur junior IFC).": "Indique ton score final et ton titre (ex. : 260 pts — Modeleur junior IFC)."}},
  "plan": {"verbe": "Identifier", "t": {"1. Rez-de-chaussée : quelle est la classe IFC de chaque repère ?": "1. Rez-de-chaussée : identifie la classe IFC de chaque repère",
                                        "2. Étage : quelle est la classe IFC de chaque repère ?": "2. Étage : identifie la classe IFC de chaque repère",
                                        "3. Dans quel niveau la maquette range-t-elle ces objets ?": "3. Indique le niveau où la maquette range ces objets",
                                        "4. Le plan et la maquette se complètent": "4. Compare le plan et la maquette"}},
  "bilan": {"verbe": "Classer", "t": {"1. Classe, niveau ou propriété ? Range chaque information": "1. Classe chaque information : classe, niveau ou propriété ?",
                                      "2. Remets l'arborescence IFC dans l'ordre": "2. Ordonne l'arborescence IFC",
                                      "3. Les propriétés": "3. Localise les propriétés"}},
 },
 "seq03-s2": {
  "flash": {"verbe": "Répondre"},
  "prise": {"verbe": "Manipuler", "t": {"Les gestes de base": "Identifie les gestes de base", "Ta maquette : vrai ou faux ?": "Examine ta maquette : vrai ou faux ?"}},
  "identite": {"verbe": "Compléter", "t": {"1. Le projet": "1. Identifie le projet", "2. Les chiffres clés (onglet Arborescence)": "2. Relève les chiffres clés (onglet Arborescence)",
                                           "3. Le dossier de plans : ouvre le PDF du projet": "3. Relève les informations du plan PDF (ouvre le PDF du projet)"}},
  "tickets": {"verbe": "Identifier", "t": {"Tes sources": "Indique tes sources", "Ticket 5 — Vigilance": "Ticket 5 — Repère la donnée fausse (vigilance)"}},
 },
 "seq03-s3": {
  "defi": {"verbe": "Distinguer"},
  "quanti": {"verbe": "Relever", "t": {"1. Compter (Arborescence › Par type d'objet)": "1. Compte les objets (Arborescence › Par type d'objet)",
                                       "2. Relever des quantités": "2. Relève les quantités"}},
  "ecarts": {"verbe": "Comparer"},
  "capture": {"verbe": "Produire", "t": {"Justifie ton choix": "Explique ton choix"},
              "q": {"En une ou deux phrases : pourquoi une capture annotée est-elle la bonne forme de réponse pour ce ticket ?": "Explique en une ou deux phrases pourquoi une capture annotée est la bonne forme de réponse pour ce ticket."}},
 },
}

for aid, blocs in M.items():
    f = RAC / f"{aid}.json"
    a = json.loads(f.read_text(encoding="utf-8"))
    ids = {b["id"]: b for b in a["blocs"]}
    for bid, r in blocs.items():
        b = ids[bid]  # KeyError si un bloc a été renommé : on le saura
        b["verbe"] = r["verbe"]
        if "consigne" in r: b["consigne"] = r["consigne"]
        for p in b.get("parties", []):
            for old, new in r.get("t", {}).items():
                if p.get("titre") == old: p["titre"] = new
            for old, new in r.get("q", {}).items():
                if p.get("question") == old: p["question"] = new
        reste = [o for o in r.get("t", {}) if any(p.get("titre") == o for p in b.get("parties", []))]
        assert not reste, (aid, bid, reste)
    f.write_text(json.dumps(a, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("✔", aid)
