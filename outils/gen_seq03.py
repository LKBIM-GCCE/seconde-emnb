"""Génère les séances SEQ03 (S1 à S4) à partir des données réelles des maquettes converties."""
import json, collections
from pathlib import Path

SITE = Path("/home/claude/site-2emnb")
M = SITE / "media" / "maquettes"
OUT = SITE / "data" / "activites"


def charge(n):
    return json.load(open(M / f"{n}.json"))


def g(e, *ks):
    for grp, k in ks:
        v = e["props"].get(grp, {}).get(k)
        if v is not None:
            return v[0] if isinstance(v, list) else v


def surf(e):
    return g(e, ("Cotes", "Surface"), ("BaseQuantities", "NetFloorArea"))


def nb(D, cls, niveau=None):
    return sum(1 for e in D["elements"] if e["cls"] == cls and (niveau is None or e["niveau"] == niveau))


def piece(D, nom):
    return next(e for e in D["elements"] if e["cls"] == "IfcSpace" and e["nom"] == nom)


def rd(x, n=2):
    return round(float(x), n)


SOURCES = ["La classe de l'objet", "L'arborescence (le niveau)", "Le nom du type", "Les propriétés (Pset / Matériaux)", "Les quantités (Qto / Cotes)", "Le plan PDF"]

# ------------------------------------------------------------------ projets des groupes
PROJETS = [
    {"id": "villa-sabonnere", "nom": "Groupe 1 — Villa Sabonnère", "desc": "Maison individuelle de plain-pied, 3 chambres."},
    {"id": "villa-goyrans", "nom": "Groupe 2 — Villa Goyrans", "desc": "Grande maison individuelle sur terrain en pente, avec sous-sol."},
    {"id": "maison-quartier", "nom": "Groupe 3 — Maison de quartier", "desc": "Équipement public : salles polyvalentes, cuisine, sanitaires."},
    {"id": "siege-social", "nom": "Groupe 4 — Siège social de l'entreprise", "desc": "Immeuble de bureaux neuf sur deux niveaux, 24 pièces."},
]
D = {p["id"]: charge(p["id"]) for p in PROJETS}
B = charge("agence-architecte")

# Données de référence par projet (lues dans les maquettes, puis choisies pour être fiables)
REF = {
    "villa-sabonnere": dict(usage="Maison individuelle (logement)", toiture="Toiture en pente, en tuiles", mur="Brique 20 cm + enduit",
                            dallage=0.12, porte="0,83 m × 2,04 m", piece="SEJOUR", piece_lib="le séjour", niveau_piece="RDC",
                            vigil="cloison"),
    "villa-goyrans": dict(usage="Maison individuelle (logement)", toiture="Toiture en pente, en tuiles", mur="Brique 20 cm + enduit",
                          dallage=0.20, porte="0,83 m × 2,04 m", piece=None, piece_lib="la pièce n° 10", niveau_piece="RDC",
                          vigil="sans-nom"),
    "maison-quartier": dict(usage="Équipement public (ERP)", toiture="Toiture terrasse (plancher béton + étanchéité)", mur="Mur Duomur (béton + isolant)",
                            dallage=0.20, porte="0,93 m × 2,04 m", piece="Salle polyvalente 2", piece_lib="la salle polyvalente 2", niveau_piece="RDC",
                            vigil="fenetres"),
    "siege-social": dict(usage="Bureaux (lieu de travail)", toiture="Toiture en pente, couverture non précisée (toit générique)", mur="Brique 20 cm + enduit",
                         dallage=0.20, porte="0,92 m × 2,13 m", piece="Accueil", piece_lib="l'accueil", niveau_piece="RDC",
                         piece_t3="Reprographie", piece_t3_lib="la reprographie", vigil="wc"),
}
for pid, r in REF.items():
    d = D[pid]
    r["nb_spaces"] = nb(d, "IfcSpace"); r["nb_portes"] = nb(d, "IfcDoor"); r["nb_fenetres"] = nb(d, "IfcWindow")
    if r["piece"]:
        r["surf_piece"] = rd(surf(piece(d, r["piece"])))
    else:
        e = next(e for e in d["elements"] if e["cls"] == "IfcSpace" and e.get("numero") == "10")
        r["surf_piece"] = rd(surf(e))
    dal = max((e for e in d["elements"] if e["cls"] == "IfcSlab" and e["niveau"] in ("RDC",)), key=lambda e: surf(e) or 0)
    r["surf_dalle"] = rd(surf(dal)); r["type_dalle"] = dal["type"]
    r["niv_pieces"] = len({e["niveau"] for e in d["elements"] if e["cls"] == "IfcSpace"})
    r["portes_rdc"] = nb(d, "IfcDoor", "RDC")

USAGES = ["Maison individuelle (logement)", "Équipement public (ERP)", "Bureaux (lieu de travail)", "Bâtiment industriel"]
TOITS = ["Toiture en pente, en tuiles", "Toiture en pente, couverture non précisée (toit générique)", "Toiture terrasse (plancher béton + étanchéité)", "Toiture en bac acier"]
MURS = ["Brique 20 cm + enduit", "Mur Duomur (béton + isolant)", "Maçonnerie existante de 33 cm", "Ossature bois + bardage", "Parpaing 20 cm sans isolant"]
PORTES = ["0,73 m × 2,04 m", "0,83 m × 2,04 m", "0,92 m × 2,13 m", "0,93 m × 2,04 m"]


def q(question, choix, bonne, expl=""):
    return {"q": question, "choix": choix, "r": choix.index(bonne), "explication": expl}


# ================================================================== S1
s1 = {"id": "seq03-s1", "sequence": "seq03", "seance": "s1", "titre": "Pourquoi l'IFC ? Jeu Mission IFC",
      "intro": "Bienvenue à la cellule BIM Desk de l'agence Atelier Équerre ! Un partenaire n'arrive pas à ouvrir notre fichier Revit… Découvre pourquoi on échange les maquettes en IFC, puis joue à Mission IFC.",
      "blocs": [
          {"id": "lancement", "type": "exercice", "titre": "Lancement — Le fichier illisible", "duree": "15 min",
           "consigne": "Le gérant de l'agence t'écrit : « Le bureau d'études n'arrive pas à ouvrir notre maquette .rvt, il n'a pas Revit. Comment lui envoyer le projet ? » Donne ton avis avant de lire le cours.",
           "parties": [{"type": "qcm", "questions": [
               q("Pourquoi le bureau d'études ne peut-il pas ouvrir le fichier .rvt ?", ["Le fichier est abîmé", "C'est le format natif de Revit : il faut Revit pour l'ouvrir", "Le fichier est trop gros", "La version du fichier ne correspond pas à ma version de Revit plus ancienne"], "C'est le format natif de Revit : il faut Revit pour l'ouvrir", "Un fichier natif ne s'ouvre qu'avec le logiciel qui l'a créé."),
               q("Quelle solution te paraît la meilleure ?", ["Imprimer tous les plans", "Lui acheter Revit", "Exporter la maquette dans un format ouvert, lisible par tous", "Lui envoyer des photos de l'écran"], "Exporter la maquette dans un format ouvert, lisible par tous", "C'est le rôle du format IFC.")]},
               {"type": "redaction", "titre": "Ton hypothèse", "question": "Avec tes mots : comment envoyer une maquette à quelqu'un qui n'a pas Revit ?", "min": 30}]},
          {"id": "cours", "type": "cours", "titre": "Cours — Le format IFC", "duree": "15 min", "fichier": "seq03-s1-cours.html"},
          {"id": "jeu", "type": "exercice", "titre": "Mission IFC — Le jeu", "duree": "65 min",
           "consigne": "Joue les 4 missions : Explorer, Chasse aux objets, Arborescence, Propriétés. À la fin du jeu, recopie ton score ci-dessous.",
           "parties": [{"type": "jeu", "src": "../jeux/mission-ifc.html", "titreJeu": "Mission IFC"},
                       {"type": "redaction", "titre": "Mon résultat", "question": "Recopie ton score final et ton titre (ex. : 260 pts — Modeleur junior IFC).", "min": 3}]},
          {"id": "bilan", "type": "exercice", "titre": "Mise en commun — Les 3 notions", "duree": "15 min",
           "consigne": "Vérifie que tu as compris les trois notions vues dans le jeu.",
           "parties": [
               {"type": "associer", "titre": "1. Quelle est la classe IFC de chaque objet ?", "choix": ["IfcWall", "IfcSlab", "IfcDoor", "IfcWindow", "IfcRoof", "IfcStair", "IfcSpace"], "melanger": False,
                "items": [{"texte": "Un mur de façade", "reponse": "IfcWall"}, {"texte": "Le plancher du rez-de-chaussée", "reponse": "IfcSlab"}, {"texte": "La porte d'entrée", "reponse": "IfcDoor"},
                          {"texte": "Une baie vitrée", "reponse": "IfcWindow"}, {"texte": "La toiture", "reponse": "IfcRoof"}, {"texte": "L'escalier", "reponse": "IfcStair"}, {"texte": "La cuisine (la pièce)", "reponse": "IfcSpace"}]},
               {"type": "ordre", "titre": "2. Remets l'arborescence IFC dans l'ordre", "titreFrise": "Du plus grand au plus petit",
                "cartes": [{"nom": "Projet"}, {"nom": "Site"}, {"nom": "Bâtiment"}, {"nom": "Niveau"}, {"nom": "Élément"}]},
               {"type": "qcm", "titre": "3. Les propriétés", "questions": [
                   q("Où lit-on si un mur est porteur ?", ["Dans son nom", "Dans le jeu de propriétés Pset_WallCommon (LoadBearing)", "Dans l'arborescence", "On ne peut pas le savoir"], "Dans le jeu de propriétés Pset_WallCommon (LoadBearing)"),
                   q("Où lit-on la surface d'une dalle ?", ["Dans les quantités (Qto / Cotes)", "Dans la classe", "Dans le nom du projet"], "Dans les quantités (Qto / Cotes)"),
                   q("Pourquoi l'agence transmet-elle un IFC plutôt qu'un fichier Revit ?", ["Parce que c'est plus joli", "Parce que l'IFC est un format ouvert que tous les partenaires peuvent lire", "Parce que l'IFC est plus léger que tout"], "Parce que l'IFC est un format ouvert que tous les partenaires peuvent lire")]}]}]}


def prise_en_main(pid):
    """Vrai / faux propres à chaque maquette : on ne peut répondre qu'en explorant SON projet."""
    d = D[pid]
    niv = [n["nom"] for n in d["niveaux"]]
    a = lambda c: nb(d, c)
    F = {
        "villa-sabonnere": [
            ("La maquette a un niveau « R+1 » (un étage).", "R+1" in niv, f"Niveaux : {', '.join(niv)}. La maison est de plain-pied."),
            ("La maquette contient des meubles (IfcFurnishingElement).", a("IfcFurnishingElement") > 0, f"{a('IfcFurnishingElement')} meubles : regarde l'onglet Arborescence."),
            ("Les fondations sont rangées sur un niveau à part, sous le RDC.", "FONDATION" in niv, "Le niveau FONDATION contient les semelles (IfcFooting).")],
        "villa-goyrans": [
            ("La maquette a un niveau « SOU SOL » sous le RDC.", "SOU SOL" in niv, "Choisis le niveau SOU SOL dans le menu Niveau."),
            ("Il n'y a aucun poteau (IfcColumn) dans la maquette.", a("IfcColumn") == 0, f"Il y a {a('IfcColumn')} poteaux (IfcColumn)."),
            ("La toiture est faite de plusieurs objets IfcRoof.", a("IfcRoof") > 1, f"{a('IfcRoof')} objets IfcRoof : la maison a plusieurs pans et volumes de toiture.")],
        "maison-quartier": [
            ("La maquette contient des poteaux (IfcColumn).", a("IfcColumn") > 0, f"{a('IfcColumn')} poteaux : regarde l'onglet Arborescence."),
            ("La maquette contient des meubles (IfcFurnishingElement).", a("IfcFurnishingElement") > 0, "Aucun meuble n'a été exporté dans cette maquette."),
            ("Le bâtiment a un étage « R+1 ».", "R+1" in niv, f"Niveaux : {', '.join(niv)}. Toutes les pièces sont au RDC.")],
        "siege-social": [
            ("La maquette a un niveau « R+1 » avec des pièces.", any(e["cls"] == "IfcSpace" and e["niveau"] == "R+1" for e in d["elements"]), "Choisis R+1 dans le menu Niveau et active « Pièces »."),
            ("La maquette contient des meubles (IfcFurnishingElement).", a("IfcFurnishingElement") > 0, "Aucun meuble n'a été exporté : les bureaux sont vides."),
            ("Les fondations sont rangées sur un niveau à part, sous le RDC.", "Fondation" in niv, "Le niveau Fondation contient les semelles (IfcFooting).")],
    }[pid]
    return {"type": "vraifaux", "pour": [pid], "titre": "Ta maquette : vrai ou faux ?",
            "items": [{"texte": tx, "reponse": bool(rep), "explication": ex} for tx, rep, ex in F]}

# ================================================================== S2
def fiche_identite(pid):
    r = REF[pid]
    return [
        {"type": "qcm", "pour": [pid], "titre": "1. Le projet", "questions": [
            q("Quel est l'usage du bâtiment ?", USAGES, r["usage"]),
            q("Quel type de toiture a ce bâtiment ?", TOITS, r["toiture"], "Regarde la toiture en 3D, puis clique dessus : son type et son matériau sont dans l'inspecteur."),
            q("Le bâtiment a-t-il un escalier ?", ["Oui : au moins un escalier (IfcStair) relie deux niveaux", "Non : il n'y a pas d'escalier dans la maquette"],
              "Oui : au moins un escalier (IfcStair) relie deux niveaux" if nb(D[pid], "IfcStair") else "Non : il n'y a pas d'escalier dans la maquette",
              "Regarde la classe IfcStair dans l'onglet Arborescence.")]},
        {"type": "nombre", "pour": [pid], "titre": "2. Les chiffres clés (onglet Arborescence)", "items": [
            {"texte": "Nombre d'objets IfcSpace (pièces)", "valeur": r["nb_spaces"], "tolerance": 0, "unite": "u"},
            {"texte": "Nombre de portes (IfcDoor)", "valeur": r["nb_portes"], "tolerance": 0, "unite": "u"},
            {"texte": "Nombre de niveaux qui contiennent des pièces", "valeur": r["niv_pieces"], "tolerance": 0, "unite": "u"}]}]


def tickets_info(pid):
    r = REF[pid]
    t = [{"type": "qcm", "pour": [pid], "titre": "Tickets du maître d'ouvrage et du conducteur de travaux", "questions": [
        q("Ticket 1 — MOA : « De quoi seront faits les murs de façade ? » Réponse :", MURS, r["mur"]),
        q("Ticket 1 — Où as-tu trouvé cette information ?", SOURCES, "Les propriétés (Pset / Matériaux)", "Les matériaux d'un objet sont rangés dans ses propriétés (bloc Matériaux de l'inspecteur)."),
        q("Ticket 2 — Conducteur de travaux : « Quelles sont les dimensions des portes intérieures les plus courantes ? »", PORTES, r["porte"], "Le nom du type de porte contient ses dimensions (largeur × hauteur)."),
        q("Ticket 2 — Où as-tu trouvé cette information ?", SOURCES, "Le nom du type", "Le nom du type de porte contient ses dimensions (largeur × hauteur)."),
        q(f"Ticket 3 — MOA : « À quel niveau se trouve {r.get('piece_t3_lib', r['piece_lib'])} ? »", [n["nom"] for n in D[pid]["niveaux"]],
          piece(D[pid], r["piece_t3"])["niveau"] if r.get("piece_t3") else r["niveau_piece"], "Le chemin de l'inspecteur indique le niveau."),
        q("Ticket 3 — Où as-tu trouvé cette information ?", SOURCES, "L'arborescence (le niveau)")]},
        {"type": "nombre", "pour": [pid], "titre": "Ticket 4 — Conducteur de travaux : « Quelle est l'épaisseur du dallage du RDC ? »", "items": [
            {"texte": "Épaisseur du dallage du RDC", "valeur": r["dallage"], "tolerance": 0.005, "unite": "m", "explication": f"Type : {r['type_dalle']} — lu dans les Cotes (Épaisseur)."}]}]
    v = r["vigil"]
    if v == "cloison":
        t.append({"type": "qcm", "pour": [pid], "titre": "Ticket 5 — Vigilance", "questions": [
            q("Clique sur une cloison intérieure (plaque de plâtre). Sa propriété IsExternal (élément extérieur ?) vaut Oui. Que fais-tu ?",
              ["Je réponds au client que c'est un mur de façade", "La donnée est fausse (mauvais réglage à l'export) : je vérifie sur le plan et je le signale", "Je supprime la cloison"],
              "La donnée est fausse (mauvais réglage à l'export) : je vérifie sur le plan et je le signale",
              "Une maquette peut contenir des erreurs : ici toutes les parois ont été exportées comme « extérieures ».")]})
    elif v == "sans-nom":
        t.append({"type": "qcm", "pour": [pid], "titre": "Ticket 5 — Vigilance", "questions": [
            q("Active « Pièces » et clique sur une pièce : elles s'appellent toutes « Surface ». Le client te demande la surface de la cuisine. Que fais-tu ?",
              ["Je donne une surface au hasard", "Je repère la cuisine sur le plan PDF, je retrouve son numéro dans la maquette, puis je signale que les pièces ne sont pas nommées", "Je réponds que la maison n'a pas de cuisine"],
              "Je repère la cuisine sur le plan PDF, je retrouve son numéro dans la maquette, puis je signale que les pièces ne sont pas nommées",
              "Les pièces n'ont pas été nommées dans Revit : la maquette seule ne suffit pas.")]})
    elif v == "wc":
        t.append({"type": "qcm", "pour": [pid], "titre": "Ticket 5 — Vigilance", "questions": [
            q("Au R+1, les WC homme et femme font chacun 15,03 m², autant qu'un bureau. Le client te demande la surface des sanitaires. Que fais-tu ?",
              ["Je donne 30,06 m² sans rien dire", "C'est suspect : je compare avec le plan PDF et je signale la donnée au chef de projet", "Je réponds qu'il n'y a pas de WC"],
              "C'est suspect : je compare avec le plan PDF et je signale la donnée au chef de projet",
              "Les pièces ont sans doute été mal découpées dans Revit : il faut lire la donnée, pas seulement la recopier.")]})
    else:
        t.append({"type": "qcm", "pour": [pid], "titre": "Ticket 5 — Vigilance", "questions": [
            q("Le MOA demande combien de fenêtres compte le bâtiment. L'arborescence n'affiche aucun IfcWindow. Pourquoi ?",
              ["Le bâtiment n'a aucune ouverture", "Les vitrages ont été modélisés autrement (murs-rideaux : montants IfcMember + panneaux IfcPlate) : je vérifie sur le plan et je le signale", "La maquette est vide"],
              "Les vitrages ont été modélisés autrement (murs-rideaux : montants IfcMember + panneaux IfcPlate) : je vérifie sur le plan et je le signale",
              "Une même chose peut être modélisée de plusieurs façons : il faut toujours regarder la maquette avant de compter.")]})
    return t


s2_parties_id = [{"type": "projet", "choix": PROJETS}, {"type": "visionneuse"}]
for p in PROJETS: s2_parties_id += fiche_identite(p["id"])
s2_parties_tk = [{"type": "projet", "choix": PROJETS}, {"type": "visionneuse"}]
for p in PROJETS: s2_parties_tk += tickets_info(p["id"])

s2 = {"id": "seq03-s2", "sequence": "seq03", "seance": "s2", "titre": "Lire la maquette du projet",
      "intro": "L'agence confie un vrai projet à ton groupe. Tu vas prendre en main la maquette dans la visionneuse, remplir la fiche d'identité du projet, puis traiter les tickets du maître d'ouvrage et du conducteur de travaux.",
      "blocs": [
          {"id": "flash", "type": "exercice", "titre": "Rappel — 3 questions flash", "duree": "10 min",
           "parties": [{"type": "qcm", "questions": [
               q("Quelle est la classe IFC d'une porte ?", ["IfcWall", "IfcDoor", "IfcOpening", "IfcGate"], "IfcDoor"),
               q("Où voit-on le niveau d'un objet ?", ["Dans l'arborescence (le chemin de l'inspecteur)", "Dans sa couleur", "Dans le nom du fichier"], "Dans l'arborescence (le chemin de l'inspecteur)"),
               q("Où lit-on l'épaisseur d'un mur ?", ["Dans ses propriétés / quantités", "Dans la classe", "Ce n'est jamais indiqué"], "Dans ses propriétés / quantités")]}]},
          {"id": "prise", "type": "exercice", "titre": "Prise en main de la visionneuse", "duree": "20 min",
           "consigne": "Choisis le projet de ton groupe. Fais tourner la maquette, choisis un niveau, déplace le curseur « Coupe » pour voir à l'intérieur, active « Pièces », clique sur des objets. Ouvre l'onglet Arborescence.",
           "parties": [{"type": "projet", "choix": PROJETS}, {"type": "visionneuse"},
                       {"type": "vraifaux", "titre": "Les gestes de base", "items": [
                           {"texte": "Le curseur « Coupe » permet de voir l'intérieur du bâtiment, comme un plan de niveau.", "reponse": True, "explication": "C'est une coupe horizontale."},
                           {"texte": "Le bouton « Pièces » ajoute des meubles dans la maquette.", "reponse": False, "explication": "Il affiche les pièces (IfcSpace), en bleu transparent."}]}]
                      + [prise_en_main(p["id"]) for p in PROJETS]},
          {"id": "identite", "type": "exercice", "titre": "Mission — La fiche d'identité du projet", "duree": "20 min",
           "consigne": "Complète la fiche d'identité de ton projet en cherchant dans la maquette.", "parties": s2_parties_id},
          {"id": "cours", "type": "cours", "titre": "Cours — La méthode du ticket", "duree": "10 min", "fichier": "seq03-s2-cours.html"},
          {"id": "tickets", "type": "exercice", "titre": "Mission — Les tickets « information »", "duree": "40 min",
           "consigne": "Pour chaque ticket : identifie la donnée nécessaire, trouve la réponse dans la maquette, puis indique ta source.", "parties": s2_parties_tk}]}

# ================================================================== S3
def tickets_quanti(pid):
    r = REF[pid]
    return [{"type": "nombre", "pour": [pid], "titre": "1. Compter (Arborescence › Par type d'objet)", "items": [
        ({"texte": "Nombre de fenêtres (IfcWindow)", "valeur": r["nb_fenetres"], "tolerance": 0, "unite": "u"} if r["nb_fenetres"]
         else {"texte": "Nombre de poteaux (IfcColumn)", "valeur": nb(D[pid], "IfcColumn"), "tolerance": 0, "unite": "u"}),
        {"texte": "Nombre de portes (IfcDoor) au RDC", "valeur": r["portes_rdc"], "tolerance": 0, "unite": "u"}]},
        {"type": "nombre", "pour": [pid], "titre": "2. Relever des quantités", "items": [
            {"texte": f"Surface de {r['piece_lib']} (active « Pièces » et clique dessus)", "valeur": r["surf_piece"], "tolerance": 0.06, "unite": "m²"},
            {"texte": "Surface du dallage du RDC (la plus grande dalle du RDC)", "valeur": r["surf_dalle"], "tolerance": 0.6, "unite": "m²", "explication": f"Type : {r['type_dalle']}."}]}]


s3_parties = [{"type": "projet", "choix": PROJETS}, {"type": "visionneuse"}]
for p in PROJETS: s3_parties += tickets_quanti(p["id"])
s3 = {"id": "seq03-s3", "sequence": "seq03", "seance": "s3", "titre": "Répondre à l'économiste : tickets quantitatifs",
      "intro": "L'économiste de l'agence a besoin de quantités sur ton projet. Tu vas compter, relever des surfaces avec leur unité, et choisir la bonne forme de réponse : un tableau de valeurs ou une capture annotée.",
      "blocs": [
          {"id": "defi", "type": "exercice", "titre": "Défi — Numérique ou graphique ?", "duree": "10 min",
           "parties": [{"type": "qcm", "questions": [
               q("L'économiste veut connaître le nombre de fenêtres et leur surface. Quelle réponse lui est la plus utile ?", ["Un tableau de valeurs", "Une capture de la façade"], "Un tableau de valeurs", "Il va calculer un prix : il lui faut des nombres."),
               q("Le conducteur de travaux veut savoir où passe un mur porteur. Quelle réponse lui est la plus utile ?", ["Un tableau de valeurs", "Une capture annotée de la maquette"], "Une capture annotée de la maquette", "Il doit voir et localiser.")]}]},
          {"id": "cours", "type": "cours", "titre": "Cours — Graphique ou numérique ?", "duree": "10 min", "fichier": "seq03-s3-cours.html"},
          {"id": "quanti", "type": "exercice", "titre": "Mission — Les tickets quantitatifs", "duree": "45 min",
           "consigne": "Choisis ton projet, puis relève les valeurs demandées avec leur unité.", "parties": s3_parties},
          {"id": "ecarts", "type": "exercice", "titre": "Mission — Plan ou maquette ?", "duree": "15 min",
           "consigne": "Compare une surface lue sur le plan PDF avec la même surface dans la maquette.",
           "parties": [{"type": "qcm", "questions": [
               q("Le plan indique 40,30 m² et la maquette 40,27 m² pour la même pièce. Pourquoi ?", ["La maquette est fausse", "Une différence d'arrondi ou de méthode de calcul", "Ce n'est pas la même pièce"], "Une différence d'arrondi ou de méthode de calcul"),
               q("Une surface « brute » de dalle est plus grande que la surface « nette » des pièces. Pourquoi ?", ["La surface brute compte aussi l'emprise des murs", "C'est une erreur", "La surface nette compte les meubles"], "La surface brute compte aussi l'emprise des murs"),
               q("Le plan et la maquette donnent deux valeurs très différentes. Que fais-tu ?", ["Je choisis au hasard", "Je note les deux valeurs, leur source, et je signale l'écart", "Je prends toujours la plus grande"], "Je note les deux valeurs, leur source, et je signale l'écart")]}]},
          {"id": "capture", "type": "exercice", "titre": "Mission — La capture annotée", "duree": "15 min",
           "consigne": "Ticket du conducteur de travaux : « Montre-moi où se trouvent les portes du RDC. » Dans la visionneuse : choisis le niveau RDC, descends la coupe, clique sur une porte, puis clique sur « 📷 Capture ». Annote l'image (Paint, ou l'outil Capture de Windows) et transmets-la à ton professeur.",
           "parties": [{"type": "projet", "choix": PROJETS}, {"type": "visionneuse"},
                       {"type": "redaction", "titre": "Justifie ton choix", "question": "En une ou deux phrases : pourquoi une capture annotée est-elle la bonne forme de réponse pour ce ticket ?", "min": 40,
                        "exemple": "Le conducteur de travaux doit voir où sont les portes : une image annotée se comprend sans moi, plus vite qu'une liste."}]}]}

# ================================================================== S4 (évaluation : futurs bureaux de l'agence = agence-architecte)
esp_b = [e for e in B["elements"] if e["cls"] == "IfcSpace"]
surf_locaux = rd(sum(surf(e) for e in esp_b))
niv_pieces_b = len({e["niveau"] for e in esp_b})
terrasse = next(e for e in B["elements"] if e["cls"] == "IfcSlab" and e["type"].endswith("00- Terrasse"))
p43 = next(e for e in esp_b if e.get("numero") == "43")
EVAL = ["agence-architecte"]
GRILLE_S4 = json.load(open(SITE / "data" / "grilles" / "seq03-s4.json"))
V = lambda verbe, qui: {"verbe": verbe, "demandeur": qui}
s4 = {"id": "seq03-s4", "sequence": "seq03", "seance": "s4", "titre": "Évaluation : les futurs bureaux de l'agence",
      "intro": "Tu es assistant(e) à la cellule BIM Desk de l'agence Atelier Équerre. Le client, l'économiste et le conducteur de travaux t'envoient des questions (tickets) sur le projet des futurs bureaux. Tu dois y répondre seul(e), à partir de la maquette numérique IFC et des plans PDF.",
      "grille": [{"code": g["code"], "nom": g["nom"], "criteres": [{"id": c[3], "nom": c[0], "prof": c[4]} for c in g["criteres"]]} for g in GRILLE_S4["groupes"]],
      "blocs": [
          {"id": "mission", "type": "cours", "titre": "Ta mission et ce qu'on attend de toi", "duree": "5 min", "fichier": "seq03-s4-cours.html"},
          {"id": "decouverte", "type": "exercice", "titre": "Découverte du projet (non noté)", "duree": "15 min", **V("Explorer", "Toi"),
           "consigne": "Avant de traiter les tickets, explore la maquette des futurs bureaux : niveaux, pièces, terrasses. Ouvre aussi les plans PDF. Cette partie n'est pas notée.",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "nombre", "items": [
                           {"texte": "Nombre de niveaux qui contiennent des pièces (IfcSpace)", "valeur": niv_pieces_b, "tolerance": 0, "unite": "u"},
                           {"texte": "Nombre de locaux (IfcSpace) dans tout le bâtiment", "valeur": len(esp_b), "tolerance": 0, "unite": "u"}]}]},
          {"id": "t1", "type": "exercice", "titre": "Ticket 1 — Les façades", "duree": "8 min", **V("Identifier", "Client"),
           "consigne": "Le client te demande d'IDENTIFIER les matériaux des murs de façade et leur finition, en précisant où tu as trouvé chaque information.",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "qcm", "critere": "t1", "questions": [
                           q("Composition des murs de façade", ["Brique 20 cm + enduit", "Maçonnerie existante de 33 cm", "Mur Duomur (béton + isolant)", "Ossature bois + bardage"], "Maçonnerie existante de 33 cm",
                             "Type « 00- Ext Mur existant 33cm » : on garde les murs du bâtiment existant."),
                           q("Source de la composition", SOURCES, "Le nom du type", "Le type « 00- Ext Mur existant 33cm » donne la nature et l'épaisseur du mur."),
                           q("Finition des façades dans le projet", ["Briquette en terre cuite apparente", "Enduit gratté fin, teinte beige (RAL 1014)", "Bardage bois", "Peinture blanche"], "Enduit gratté fin, teinte beige (RAL 1014)",
                             "Indiqué sur les façades « état projeté » et dans la notice du permis de construire."),
                           q("Source de la finition", SOURCES, "Le plan PDF", "La maquette ne contient pas la teinte de l'enduit : il faut le plan.")]}]},
          {"id": "t2", "type": "exercice", "titre": "Ticket 2 — L'acrotère", "duree": "8 min", **V("Relever", "Conducteur de travaux"),
           "consigne": "Le conducteur de travaux te demande de RELEVER la hauteur de l'acrotère le plus haut, par rapport au terrain naturel (TN).",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "qcm", "critere": "t2-source", "questions": [
                           q("Où trouves-tu cette hauteur le plus directement ?", SOURCES, "Le plan PDF", "La cote altimétrique « Acrotère … m/TN » est écrite sur les façades.")]},
                       {"type": "nombre", "critere": "t2-valeur", "items": [
                           {"texte": "Hauteur de l'acrotère le plus haut (par rapport au TN)", "valeur": 5.82, "tolerance": 0.01, "unite": "m",
                            "explication": "Cote « Acrotère 5,82 m/TN » sur les façades du permis de construire (dans la maquette : haut des murs « Acrotère 20 » du niveau Toiture terrasse)."}]}]},
          {"id": "t3", "type": "exercice", "titre": "Ticket 3 — La pièce n° 43", "duree": "6 min", **V("Localiser", "Client"),
           "consigne": "Le client te demande de LOCALISER la pièce n° 43 et d'IDENTIFIER son usage.",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "qcm", "critere": "t3", "questions": [
                           q("Usage et niveau de la pièce n° 43", ["Bureau direction, au R+1", f"{p43['nom']}, au {p43['niveau']}", "Salle de réunion, au RDC", "Archives, au RDC"], f"{p43['nom']}, au {p43['niveau']}",
                             "Active « Pièces », clique sur la pièce : son numéro et son nom sont dans l'inspecteur, son niveau dans le chemin."),
                           q("Quelle forme de réponse est la plus adaptée pour le client ?", ["Un tableau de valeurs", "Une phrase courte (nom + niveau)", "Une capture annotée"], "Une phrase courte (nom + niveau)")]}]},
          {"id": "t4", "type": "exercice", "titre": "Ticket 4 — La surface des locaux", "duree": "12 min", **V("Calculer", "Économiste"),
           "consigne": "L'économiste te demande de CALCULER la surface totale des locaux clos et couverts, et de lui SIGNALER ce que tu n'as pas compté.",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "qcm", "critere": "t4-objets", "questions": [
                           q("Quels objets additionnes-tu ?", ["Les dalles (IfcSlab) du RDC et du R+1", "Les pièces (IfcSpace) du RDC et du R+1", "Les pièces (IfcSpace) du RDC seulement", "Les toitures (IfcRoof)"], "Les pièces (IfcSpace) du RDC et du R+1",
                             "Un local clos et couvert = une pièce (IfcSpace). Une dalle compte aussi l'emprise des murs.")]},
                       {"type": "nombre", "critere": "t4-total", "items": [{"texte": "Surface totale des locaux clos et couverts", "valeur": surf_locaux, "tolerance": 0.6, "unite": "m²",
                                                                          "explication": f"{len(esp_b)} locaux : RDC + R+1. Les terrasses ne sont pas des locaux."}]},
                       {"type": "qcm", "critere": "vigilance", "questions": [
                           q(f"Au R+1, une terrasse accessible de {str(rd(surf(terrasse))).replace('.', ',')} m² (dalle « Terrasse ») donne sur les bureaux. L'ajoutes-tu au total ?",
                             ["Oui, c'est une surface du bâtiment", "Non : une terrasse n'est ni close ni couverte, je l'exclus et je le précise dans ma réponse", "Oui, mais seulement la moitié"],
                             "Non : une terrasse n'est ni close ni couverte, je l'exclus et je le précise dans ma réponse", "Lire ce que l'on additionne, pas seulement le total.")]},
                       {"type": "redaction", "titre": "Ta réponse à l'économiste", "question": "Rédige ta réponse comme un message : la surface avec son unité, sa source, et ce que tu as exclu.", "min": 40,
                        "exemple": "Surface des locaux clos et couverts : … m² (somme des IfcSpace du RDC et du R+1). Je n'ai pas compté …"}]},
          {"id": "t5", "type": "exercice", "titre": "Ticket 5 — La capture annotée", "duree": "12 min", **V("Produire", "Conducteur de travaux"),
           "consigne": "Le conducteur de travaux te demande de PRODUIRE une capture annotée qui localise la terrasse accessible et les toitures terrasses.",
           "parties": [{"type": "visionneuse", "maquettes": EVAL},
                       {"type": "texte", "html": "<ol><li>Choisis une vue où l'on voit bien la terrasse et les toitures terrasses (tourne, utilise la coupe ou le filtre Niveau).</li><li>Clique sur <b>📷 Capture</b> : l'image est téléchargée.</li><li>Annote-la (Paint ou l'outil Capture de Windows) : flèches, noms des éléments, légende.</li><li>Transmets-la à ton professeur avec ton certificat.</li></ol>"},
                       {"type": "redaction", "critere": "t5", "titre": "Justifie ton choix", "question": "En une ou deux phrases : pourquoi as-tu choisi cette vue, et pourquoi une capture est-elle la bonne forme de réponse pour ce ticket ?", "min": 30}]},
          {"id": "oral", "type": "exercice", "titre": "Préparer l'oral au client", "duree": "5 min", **V("Justifier", "Client"),
           "consigne": "En classe, tu présenteras en 2 minutes UN ticket au client (ton professeur). Tu devras JUSTIFIER ta source et ta forme de réponse.",
           "parties": [{"type": "redaction", "critere": "oral", "titre": "Mon plan d'oral", "question": "Quel ticket vas-tu présenter ? Note en 2 ou 3 phrases : la demande, ta réponse, ta source et pourquoi tu as choisi cette forme de réponse.", "min": 40}]}]}

for s in (s1, s2, s3, s4):
    if s["id"] in ("seq03-s2", "seq03-s3", "seq03-s4"):
        s["plans"] = {k: f"plans/{k}.pdf" for k in ("villa-sabonnere", "villa-goyrans", "maison-quartier", "siege-social", "agence-architecte")}
    json.dump(s, open(OUT / f"{s['id']}.json", "w"), ensure_ascii=False, indent=1)
print({k: {x: v[x] for x in ("nb_spaces", "nb_portes", "nb_fenetres", "surf_piece", "surf_dalle", "portes_rdc", "niv_pieces", "dallage")} for k, v in REF.items()})
print("agence (S4):", niv_pieces_b, len(esp_b), surf_locaux, rd(surf(terrasse)), p43["nom"], p43["niveau"])
