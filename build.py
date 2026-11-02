#!/usr/bin/env python3
"""
Générateur du site Seconde EMNB.
Lit data/progression.json (séquences), data/activites/*.json (séances en ligne)
et fabrique toutes les pages dans docs/ (publié par GitHub Pages). Usage : python build.py
"""
import json, shutil
from html import escape as e
from pathlib import Path

RACINE = Path(__file__).parent
DATA = json.loads((RACINE / "data" / "progression.json").read_text(encoding="utf-8"))
SITE, COMP = DATA["site"], DATA["competences"]
SORTIE = RACINE / "docs"
ILLUS = {f.stem: f.read_text(encoding="utf-8") for f in (RACINE / "assets" / "illus").glob("*.svg")}

ACTS = {}  # séances en ligne : (séquence, séance) -> définition
for f in sorted((RACINE / "data" / "activites").glob("*.json")):
    a = json.loads(f.read_text(encoding="utf-8"))
    a["_cours"] = {b["id"]: (f.parent / b["fichier"]).read_text(encoding="utf-8") for b in a["blocs"] if b["type"] == "cours"}
    ACTS[(a["sequence"], a["seance"])] = a

# fiches synthèse (PDF dans fiches/) : par séance, et une fiche A3 par séquence
FICHES = {(f.stem.split("-")[0], f.stem.split("-")[1]): f.name for f in (RACINE / "fiches").glob("seq0?-s?.pdf")}
FICHES_SEQ = {f.stem.split("-")[0]: f.name for f in (RACINE / "fiches").glob("seq0?-synthese-*.pdf")}

POLICES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&display=swap" rel="stylesheet">')


def comp_pills(codes):
    return "".join(f'<span class="comp" title="{e(COMP.get(c, ""))}">{e(c)}</span>' for c in codes)


def cote(texte, cls=""):
    """Ligne de cote façon plan d'architecte : ├──── texte ────┤"""
    return f'<span class="cote {cls}" aria-hidden="true"><span>{e(texte)}</span></span>'


def bouton_fiche(seq_id, seance_id, base):
    f = FICHES.get((seq_id, seance_id))
    if not f:
        return ""
    return f'<a class="btn-fiche" href="{base}fiches/{f}" download><span class="ico-fiche" aria-hidden="true">📌</span><span><b>Ma fiche synthèse</b><small>PDF à télécharger ou imprimer</small></span></a>'


# ---------- gabarit ----------
def page(titre, contenu, prof=0, fil=None, extra_tete="", extra_pied="", classe=""):
    base = "../" * prof
    nav_seq = "".join(f'<a href="{base}{s["id"]}/index.html">{e(s["numero"])}</a>' for s in DATA["sequences"] if s["statut"] == "en_ligne")
    fil_html = ""
    if fil:
        fil_html = '<nav class="fil" aria-label="Fil d\'Ariane">' + " / ".join(
            f'<a href="{base}{u}">{e(t)}</a>' if u else f'<span aria-current="page">{e(t)}</span>' for t, u in fil) + "</nav>"
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)} · {e(SITE["titre"])}</title>
{POLICES}
<link rel="stylesheet" href="{base}assets/style.css">{extra_tete}
</head><body class="{classe}">
<header class="entete">
  <a class="marque" href="{base}index.html"><span class="logo" aria-hidden="true">2<small>de</small></span>
    <span><strong>{e(SITE["titre"])}</strong><em>{e(SITE["sous_titre"])}</em></span></a>
  <nav class="menu" aria-label="Séquences">{nav_seq}<a href="{base}competences.html">Compétences</a></nav>
  <img class="logo-lycee" src="{base}assets/logo-lycee.jpg" alt="Lycée Urbain Vitry" width="72" height="36">
</header>
<main>{fil_html}{contenu}</main>
<footer class="pied"><img class="pied-logo" src="{base}assets/logo-lycee.jpg" alt="Lycée Urbain Vitry" width="96" height="48"><span>{e(SITE["etablissement"])}</span><span>{e(SITE["enseignant"])}</span><span>{e(SITE["annee"])}</span></footer>
<script src="{base}assets/progression.js"></script>{extra_pied}
</body></html>"""


# ---------- pages ----------

# Familles de compétences (vademecum 2de EMNB) et explications « en clair » pour les élèves
FAMILLES = {
    "C1": ("S'informer, communiquer", "fam1", "Chercher l'information, savoir qui fait quoi, transmettre au bon interlocuteur."),
    "C2": ("Analyser", "fam2", "Comprendre un dossier ou une maquette, repérer les données utiles, faire des choix."),
    "C3": ("Produire", "fam3", "Mesurer, dessiner, modéliser, calculer : fabriquer un document du métier."),
    "C4": ("Contrôler", "fam4", "Classer, vérifier, s'assurer que le dossier est juste et à jour."),
}
EN_CLAIR = {
    "C1.1.1": ("Je sais dire quel est mon rôle dans l'équipe et à qui je rends compte.", "SEQ01 : situer l'assistant d'études parmi les acteurs du projet."),
    "C1.1.3": ("Je sais qui fait quoi sur un projet : maître d'ouvrage, architecte, économiste, bureau d'études, entreprises.", "SEQ01 : relier chaque acteur à sa mission et à sa phase."),
    "C1.2.1": ("Je sais trouver une information, dire d'où elle vient et si elle est fiable.", "SEQ03 : noter la source de chaque réponse (maquette ou plan)."),
    "C1.3.2": ("Je sais choisir le bon moyen pour transmettre une information.", "SEQ03 : envoyer un fichier IFC plutôt qu'un fichier Revit."),
    "C2.1.1": ("Je sais m'y retrouver dans un dossier de plans ou dans une maquette.", "SEQ02 : identifier les pièces du dossier de la Villa Camacho."),
    "C2.1.2": ("Je sais repérer les ouvrages et les travaux concernés par une demande.", "SEQ02 : repérer murs, cloisons, ouvertures sur les plans de niveaux."),
    "C2.2.1": ("Je sais de quelles données j'ai besoin pour répondre à une demande.", "SEQ03 : la méthode du ticket (demande → donnée → recherche → source)."),
    "C2.2.2": ("Je sais classer des critères pour faire un choix, du plus important au moins important.", "SEQ03 : précision, rapidité, lisibilité pour choisir la forme de réponse."),
    "C2.2.3": ("Je sais choisir entre une réponse en chiffres (tableau) et une réponse en image (capture, plan).", "SEQ03 : tableau pour l'économiste, capture annotée pour le conducteur de travaux."),
    "C3.2.1": ("Je sais mesurer, utiliser une échelle et vérifier mes mesures.", "SEQ02 : lire une cote et retrouver une dimension réelle avec l'échelle."),
    "C4.1.1": ("Je sais classer et nommer les documents d'un dossier.", "SEQ02 : ranger les plans du dossier dans le bon ordre."),
}
NIVEAUX = [("NA", "Non acquis", "Je n'y arrive pas encore : on reprend ensemble.", "na"),
           ("ECA", "En cours d'acquisition", "J'y arrive avec de l'aide ou je fais encore des erreurs.", "eca"),
           ("A", "Acquis", "Je le fais seul(e), de façon juste et fiable.", "a")]


def puce_fam(code):
    nom, cls, _ = FAMILLES[code[:2]]
    return f'<span class="fam {cls}">{e(code[:2])} · {e(nom)}</span>'


def accueil():
    etapes = ""
    for k, s in enumerate(DATA["sequences"], 1):
        illu = ILLUS.get(s["id"], "")
        cartouche = f'<table class="cartouche"><tr><td>Séquence</td><td>{e(s["numero"])}</td></tr><tr><td>Période</td><td>{e(s["periode"])}</td></tr>' + \
                    (f'<tr><td>Durée</td><td>{e(s["duree"])}</td></tr>' if s["duree"] else "") + "</table>"
        if s["statut"] == "en_ligne":
            etapes += f'''<li class="etape-seq"><a class="feuille" href="{s["id"]}/index.html">
<div class="illu">{illu}</div><h2>{e(s["titre"])}</h2><p>{e(s["problematique"])}</p>{cartouche}
<span class="avance" data-acts="{" ".join(ACTS[(s["id"], x["id"])]["id"] + ":" + str(sum(1 for b in ACTS[(s["id"], x["id"])]["blocs"] if b["type"] != "cours")) for x in s["seances"] if (s["id"], x["id"]) in ACTS)}"></span></a></li>'''
        else:
            etapes += f'''<li class="etape-seq bientot"><div class="feuille"><div class="illu">{illu}</div><h2>{e(s["titre"])}</h2>
<p>Cette séquence arrive plus tard dans l'année.</p>{cartouche}</div></li>'''
    fam_html = "".join(f'<li class="{c}"><b>{k}</b><span>{e(n)}</span><small>{e(d)}</small></li>' for k, (n, c, d) in FAMILLES.items())
    return page("Accueil", f'''
<section class="hero">
  <div class="hero-texte">
    <h1>Lire un plan, modéliser un bâtiment, le chiffrer.</h1>
    <p>Bienvenue en Seconde EMNB. Ici tu retrouves toutes les séances de l'année : tu peux les faire en ligne, vérifier tes réponses et télécharger ta fiche synthèse.</p>
    <a class="btn-grand" href="seq01/index.html">Commencer par la séquence 1</a>
  </div>
  <figure class="hero-photo">
    <img src="media/projet/villa-livree.jpg" alt="La Villa Camacho terminée : maison à étage avec bardage bois et toiture en tuiles">
    <svg class="hero-cotes" viewBox="0 0 100 66" preserveAspectRatio="none" aria-hidden="true">
      <path d="M6 61 H94 M6 58 V64 M94 58 V64" /><path d="M97 8 V56 M94 8 H100 M94 56 H100" />
    </svg>
    <span class="hero-cote-h">18,10 m</span><span class="hero-cote-v">+6,30</span>
    <figcaption>La Villa Camacho, maison réelle étudiée en séquence 2.</figcaption>
  </figure>
</section>
<section class="parcours">
  <h2 class="titre-section">Ton parcours de l'année {cote("5 séquences")}</h2>
  <ol class="route">{etapes}</ol>
</section>
<section class="projets-annee">
  <h2 class="titre-section">Les projets que tu vas étudier {cote("des bâtiments réels")}</h2>
  <p class="chapo">Toute l'année, tu travailles sur de vrais projets, comme dans un bureau d'études.</p>
  <article class="projet-carte">
    <header><span class="projet-seq">SEQ02 · La lecture de plans</span><h3>La Villa Camacho</h3>
      <p>Une maison individuelle réelle, suivie de la maquette à la livraison.</p></header>
    <div class="trois-temps">
      <figure><img src="media/projet/villa-maquette.jpg" alt="Maquette 3D de la Villa Camacho" loading="lazy"><figcaption><b>1. La maquette</b> Le projet est dessiné et modélisé au bureau d'études.</figcaption></figure>
      <figure><img src="media/projet/villa-chantier.jpg" alt="Chantier de la Villa Camacho : murs en briques montés" loading="lazy"><figcaption><b>2. Le chantier</b> Les entreprises construisent à partir des plans.</figcaption></figure>
      <figure><img src="media/projet/villa-livree.jpg" alt="Villa Camacho livrée" loading="lazy"><figcaption><b>3. La livraison</b> Le client prend possession de sa maison.</figcaption></figure>
    </div>
  </article>
  <article class="projet-carte">
    <header><span class="projet-seq">SEQ03 · La maquette numérique IFC</span><h3>Les projets de l'agence Atelier Équerre</h3>
      <p>Chaque groupe explore une maquette IFC dans la visionneuse du site. L'évaluation porte sur les futurs bureaux de l'agence.</p></header>
    <div class="cinq-maquettes">
      <figure><img src="media/projet/maquette-villa-sabonnere.jpg" alt="Maquette de la villa Sabonnère" loading="lazy"><figcaption><b>Groupe 1</b> Villa Sabonnère</figcaption></figure>
      <figure><img src="media/projet/maquette-villa-goyrans.jpg" alt="Maquette de la villa Goyrans" loading="lazy"><figcaption><b>Groupe 2</b> Villa Goyrans</figcaption></figure>
      <figure><img src="media/projet/maquette-maison-quartier.jpg" alt="Maquette de la maison de quartier" loading="lazy"><figcaption><b>Groupe 3</b> Maison de quartier</figcaption></figure>
      <figure><img src="media/projet/maquette-siege-social.jpg" alt="Maquette du siège social de l'entreprise" loading="lazy"><figcaption><b>Groupe 4</b> Siège social</figcaption></figure>
      <figure class="eval"><img src="media/projet/maquette-agence-architecte.jpg" alt="Maquette des futurs bureaux de l'agence" loading="lazy"><figcaption><b>Évaluation</b> Futurs bureaux de l'agence</figcaption></figure>
    </div>
  </article>
</section>
<section class="comp-minute">
  <h2 class="titre-section">Les compétences en 1 minute {cote("ce qu'on évalue")}</h2>
  <p class="chapo">Une compétence, c'est un savoir-faire du métier que tu montres en situation. Elles sont rangées en 4 familles :</p>
  <ul class="familles">{fam_html}</ul>
  <a class="btn-lien" href="competences.html">Comprendre les compétences →</a>
</section>''', classe="p-accueil")


def page_sequence(s):
    lignes = ""
    for i, x in enumerate(s["seances"], 1):
        act = ACTS.get((s["id"], x["id"]))
        lignes += f'''<li class="pas"><a href="{x["id"]}.html"><span class="borne">S{i}</span>
<span class="pas-txt"><b>{e(x["titre"])}</b><small>{e(x["duree"])} — {e(x["evaluation"])}</small></span>
<span class="pas-etat" {f'data-act="{act["id"]}" data-nb="{sum(1 for b in act["blocs"] if b["type"] != "cours")}"' if act else ""}></span></a></li>'''
    fiche_seq = ""
    if s["id"] in FICHES_SEQ:
        fiche_seq = f'<a class="btn-fiche large" href="../fiches/{FICHES_SEQ[s["id"]]}" download><span class="ico-fiche" aria-hidden="true">🗂️</span><span><b>Fiche synthèse A3 de la séquence</b><small>Tout ce qu\'il faut retenir sur une seule page</small></span></a>'
    return page(s["numero"], f'''
<section class="bandeau-seq">
  <div><p class="numero-seq">{e(s["numero"])}</p><h1>{e(s["titre"])}</h1>{cote(f'{s["periode"]} — {s["duree"]}')}</div>
  <div class="illu grande">{ILLUS.get(s["id"], "")}</div>
</section>
<section class="bulle"><h2>La question de la séquence</h2><p>{e(s["problematique"])}</p></section>
<section class="mission"><h2>Ta mission</h2><p>{e(s["contexte"])}</p></section>
<section><h2 class="titre-section">Les séances {cote(f'{len(s["seances"])} × 2 h')}</h2><ol class="chemin">{lignes}</ol></section>
{fiche_seq}''', prof=1, fil=[("Accueil", "index.html"), (s["numero"], None)])


def page_seance(s, i):
    x = s["seances"][i]
    act = ACTS.get((s["id"], x["id"]))
    objectifs = "".join(f"<li>{e(o)}</li>" for o in x["objectifs"])
    comps = "".join(f"<li><b>{e(c)}</b> {e(COMP.get(c, ''))}</li>" for c in x["competences"])
    deroule = "".join(f'''<li><span class="temps">{e(d["temps"])}</span><div><h3>{e(d["etape"])}</h3>
<ul>{"".join(f"<li>{e(a)}</li>" for a in d["eleves"])}</ul></div></li>''' for d in x["deroule"])
    cta = ""
    if act:
        nb = sum(1 for b in act["blocs"] if b["type"] != "cours")
        cta = f'''<a class="cta-seance" href="{x["id"]}-en-ligne.html"><span class="cta-play" aria-hidden="true">▶</span>
<span><b>Faire la séance en ligne</b><small>{nb} activités corrigées tout de suite, puis ton certificat à déposer sur l'ENT</small></span>
<span class="pas-etat" data-act="{act["id"]}" data-nb="{nb}"></span></a>'''
    prec = s["seances"][i - 1] if i > 0 else None
    suiv = s["seances"][i + 1] if i + 1 < len(s["seances"]) else None
    nav = '<nav class="pagination">' + (f'<a href="{prec["id"]}.html">S{i} · {e(prec["titre"])}</a>' if prec else "<span></span>") \
        + (f'<a class="suiv" href="{suiv["id"]}.html">S{i+2} · {e(suiv["titre"])}</a>' if suiv else "<span></span>") + "</nav>"
    return page(f'{s["numero"]} S{i+1}', f'''
<section class="titre-seance"><p class="numero-seq">{e(s["numero"])} · séance {i+1}</p><h1>{e(x["titre"])}</h1>{cote(x["duree"])}</section>
<div class="actions">{cta}{bouton_fiche(s["id"], x["id"], "../")}</div>
<div class="deux-col">
<section class="bloc"><h2>À la fin de la séance, je sais…</h2><ul class="coche">{objectifs}</ul></section>
<section class="bloc"><h2>Compétences travaillées</h2><ul class="liste-comp">{comps}</ul><p class="eval">Évaluation : {e(x["evaluation"])}</p></section>
</div>
<details class="bloc deroule"><summary>Voir le déroulé de la séance</summary><ol class="frise">{deroule}</ol></details>
{nav}''', prof=1, fil=[("Accueil", "index.html"), (s["numero"], f'{s["id"]}/index.html'), (f"Séance {i+1}", None)])


def page_competences():
    seqs = [s for s in DATA["sequences"] if s["statut"] == "en_ligne"]
    tete = "".join(f"<th>{e(s['numero'])}</th>" for s in seqs)
    lignes, fam_prec = "", None
    for code, lib in COMP.items():
        if code[:2] != fam_prec:
            fam_prec = code[:2]
            nom, cls, _ = FAMILLES[fam_prec]
            lignes += f'<tr class="ligne-fam {cls}"><th colspan="{len(seqs) + 1}" scope="rowgroup">{e(fam_prec)} · {e(nom)}</th></tr>'
        cases = ""
        for s in seqs:
            liens = [f'<a href="{s["id"]}/{x["id"]}.html">S{k}</a>' for k, x in enumerate(s["seances"], 1) if code in x["competences"]]
            cases += f'<td>{" ".join(liens)}</td>'
        clair, ex = EN_CLAIR.get(code, ("", ""))
        lignes += (f"<tr><th scope='row'><b>{e(code)}</b><small>{e(lib)}</small>"
                   + (f"<span class='clair'>{e(clair)}</span><span class='exemple'>Exemple — {e(ex)}</span>" if clair else "")
                   + f"</th>{cases}</tr>")
    familles = "".join(f'<li class="{c}"><b>{k}</b><span>{e(n)}</span><small>{e(d)}</small></li>' for k, (n, c, d) in FAMILLES.items())
    niveaux = "".join(f'<li class="niv-{c}"><b>{e(a)}</b><span>{e(n)}</span><small>{e(d)}</small></li>' for a, n, d, c in NIVEAUX)
    return page("Compétences", f"""
<section class="titre-seance"><h1>Les compétences de l'année</h1>
<p class="chapo">Ce que tu apprends à faire en Seconde EMNB, comme un professionnel des études du bâtiment.</p></section>

<section class="bloc comp-intro">
  <h2>C'est quoi une compétence ?</h2>
  <div class="trois-cartes">
    <div><b>🛠 Un savoir-faire du métier</b><p>Pas seulement « savoir », mais <b>savoir faire</b> : lire un plan, trouver une donnée dans une maquette, choisir comment répondre.</p></div>
    <div><b>🎯 Montrée en situation</b><p>Tu la montres pendant une mission : un ticket à traiter, un dossier à analyser, une présentation au client.</p></div>
    <div><b>📈 Elle progresse</b><p>La même compétence revient dans plusieurs séquences : à chaque fois, tu vas un peu plus loin.</p></div>
  </div>
</section>

<section class="bloc">
  <h2>Comment lire un code de compétence ?</h2>
  <div class="decode">
    <span class="d-code"><i class="d1">C2</i><i class="d2">.2</i><i class="d3">.3</i></span>
    <ul>
      <li><i class="d1">C2</i> la famille : <b>Analyser</b></li>
      <li><i class="d2">.2</i> le groupe : <b>Proposer des choix techniques, numériques et graphiques</b></li>
      <li><i class="d3">.3</i> la compétence : <b>Choisir les données numériques ou graphiques</b></li>
    </ul>
  </div>
</section>

<section class="bloc">
  <h2>Les 4 familles</h2>
  <ul class="familles">{familles}</ul>
</section>

<section class="bloc">
  <h2>Comment je suis évalué(e) ?</h2>
  <p>Pour chaque compétence, ton professeur note ton niveau sur une grille de suivi :</p>
  <ul class="niveaux">{niveaux}</ul>
  <p class="aide">Les certificats des séances en ligne montrent ton travail ; la note vient de la grille, du travail rendu et de l'oral.</p>
</section>

<section class="bloc tableau">
  <h2>Où chaque compétence est travaillée</h2>
  <p class="aide">Chaque case renvoie à la séance où la compétence est travaillée.</p>
  <table class="table-comp"><thead><tr><th>Compétence</th>{tete}</tr></thead><tbody>{lignes}</tbody></table>
</section>""", fil=[("Accueil", "index.html"), ("Compétences", None)])


def VIS(a):
    return any(p["type"] == "visionneuse" for bl in a["blocs"] if bl["type"] != "cours" for p in bl["parties"])


def page_en_ligne(s, i, a):
    x = s["seances"][i]
    donnees = json.dumps({k: v for k, v in a.items() if k != "_cours"}, ensure_ascii=False).replace("</", "<\\/")
    contenu = f'''
<section class="titre-seance en-ligne"><p class="numero-seq">{e(s["numero"])} · séance {i+1} en ligne</p><h1>{e(x["titre"])}</h1>
<p class="chapo">{e(a["intro"])}</p></section>
<div id="activite"><nav id="etapes" aria-label="Étapes de la séance"></nav><section id="zone" aria-live="polite"></section></div>
<div class="bas-seance">{bouton_fiche(s["id"], x["id"], "../")}<button class="lien-raz" id="raz">Effacer mes réponses et tout recommencer</button></div>
<script type="application/json" id="activite-data">{donnees}</script>
{"".join(f'<template id="cours-{k}">{v}</template>' for k, v in a["_cours"].items())}'''
    return page(f'{s["numero"]} S{i+1} en ligne', contenu, prof=1,
        fil=[("Accueil", "index.html"), (s["numero"], f'{s["id"]}/index.html'), (f"Séance {i+1}", f'{s["id"]}/{x["id"]}.html'), ("En ligne", None)],
        extra_tete='<link rel="stylesheet" href="../assets/activites.css">' + ('<link rel="stylesheet" href="../assets/visionneuse.css">' if VIS(a) else ""), classe="large" if VIS(a) else "",
        extra_pied=('<script src="../assets/vendor/three.min.js"></script><script src="../assets/vendor/OrbitControls.js"></script><script src="../assets/vendor/GLTFLoader.js"></script><script src="../assets/visionneuse.js"></script>' if VIS(a) else "") + '<script src="../assets/activites.js"></script>')


def page_verifier():
    contenu = '''
<section class="titre-seance"><h1>Vérifier un certificat</h1><p class="chapo">Page réservée à l'enseignant : recopie les informations lues sur le certificat.</p></section>
<section class="bloc"><form id="v" class="verif">
<label>Séance <select name="act">ACTS_OPTIONS</select></label>
<label>Nom tel qu'écrit <input name="nom" required></label>
<label>Date (jj/mm/aaaa) <input name="date" required placeholder="29/10/2026"></label>
<label>Scores dans l'ordre, séparés par des espaces <input name="sc" required placeholder="7/8 15/16 20/22 11/12"></label>
<label>Code lu sur le certificat <input name="code" required placeholder="AB-12CD"></label>
<button class="btn">Vérifier</button></form><p id="vr" class="score"></p></section>
<script>
const IDS = ACTS_IDS;
function code(t){let x=2166136261;for(const ch of t+"|emnb-urbain-vitry"){x^=ch.charCodeAt(0);x=Math.imul(x,16777619)>>>0;}const s=x.toString(36).toUpperCase().padStart(7,"0");return s.slice(0,2)+"-"+s.slice(2,6);}
document.getElementById("v").onsubmit=ev=>{ev.preventDefault();const f=new FormData(ev.target);const act=f.get("act");
const sc=f.get("sc").trim().split(/\\s+/);const ligne=IDS[act].map((id,k)=>id+":"+(sc[k]||"")).join(";");
const ok=code(act+"|"+f.get("nom").trim()+"|"+ligne+"|"+f.get("date").trim())===f.get("code").trim().toUpperCase();
const r=document.getElementById("vr");r.textContent=ok?"✔ Certificat authentique":"✘ Le code ne correspond pas : certificat modifié ou mal recopié";r.className="score "+(ok?"ok":"ko");};
</script>'''
    opts = "".join(f'<option value="{e(a["id"])}">{e(a["id"])} — {e(a["titre"])}</option>' for a in ACTS.values())
    ids = {a["id"]: [b["id"] for b in a["blocs"] if b["type"] != "cours" and any(x["type"] in ("ordre", "indices", "associer", "grille", "vraifaux", "qcm", "saisie", "nombre", "schema") for x in b["parties"])] for a in ACTS.values()}
    contenu = contenu.replace("ACTS_OPTIONS", opts).replace("ACTS_IDS", json.dumps(ids))
    return page("Vérifier un certificat", contenu, extra_tete='<link rel="stylesheet" href="assets/activites.css"><meta name="robots" content="noindex">')


# ---------- construction ----------
def main():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    for d in ("assets", "media", "fiches", "jeux", "plans"):
        if (RACINE / d).exists():
            shutil.copytree(RACINE / d, SORTIE / d, dirs_exist_ok=True)
    (SORTIE / ".nojekyll").touch()
    pages = {"index.html": accueil(), "competences.html": page_competences(), "verifier.html": page_verifier()}
    for s in DATA["sequences"]:
        if s["statut"] != "en_ligne": continue
        pages[f'{s["id"]}/index.html'] = page_sequence(s)
        for i, x in enumerate(s["seances"]):
            pages[f'{s["id"]}/{x["id"]}.html'] = page_seance(s, i)
            if (s["id"], x["id"]) in ACTS:
                pages[f'{s["id"]}/{x["id"]}-en-ligne.html'] = page_en_ligne(s, i, ACTS[(s["id"], x["id"])])
    # Anti-cache : chaque CSS / JS du site reçoit ?v=<empreinte>, le navigateur recharge dès qu'il change
    import hashlib, re as _re
    def version(m):
        fichier = RACINE / "assets" / m.group(2)
        v = hashlib.md5(fichier.read_bytes()).hexdigest()[:8] if fichier.exists() else ""
        return m.group(1) + m.group(2) + (f"?v={v}" if v else "") + m.group(3)
    pages = {c: _re.sub(r'(assets/)([\w./-]+\.(?:css|js))(")', version, h) for c, h in pages.items()}
    for chemin, html in pages.items():
        (SORTIE / chemin).parent.mkdir(parents=True, exist_ok=True)
        (SORTIE / chemin).write_text(html, encoding="utf-8")
    print(f"✔ {len(pages)} pages · {len(ACTS)} séances en ligne · {len(FICHES)} fiches synthèse")


if __name__ == "__main__":
    main()
