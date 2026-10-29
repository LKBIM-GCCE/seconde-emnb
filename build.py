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
</header>
<main>{fil_html}{contenu}</main>
<footer class="pied"><span>{e(SITE["etablissement"])}</span><span>{e(SITE["enseignant"])}</span><span>{e(SITE["annee"])}</span></footer>
<script src="{base}assets/progression.js"></script>{extra_pied}
</body></html>"""


# ---------- pages ----------
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
<section class="projet-fil">
  <h2 class="titre-section">Du plan à la maison {cote("un projet réel")}</h2>
  <div class="trois-temps">
    <figure><img src="media/projet/villa-maquette.jpg" alt="Maquette 3D de la Villa Camacho" loading="lazy"><figcaption><b>1. La maquette</b> Le projet est dessiné et modélisé au bureau d'études.</figcaption></figure>
    <figure><img src="media/projet/villa-chantier.jpg" alt="Chantier de la Villa Camacho : murs en briques montés" loading="lazy"><figcaption><b>2. Le chantier</b> Les entreprises construisent à partir des plans.</figcaption></figure>
    <figure><img src="media/projet/villa-livree.jpg" alt="Villa Camacho livrée" loading="lazy"><figcaption><b>3. La livraison</b> Le client prend possession de sa maison.</figcaption></figure>
  </div>
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
    lignes = ""
    for code, lib in COMP.items():
        cases = ""
        for s in seqs:
            liens = [f'<a href="{s["id"]}/{x["id"]}.html">S{k}</a>' for k, x in enumerate(s["seances"], 1) if code in x["competences"]]
            cases += f'<td>{" ".join(liens)}</td>'
        lignes += f"<tr><th scope='row'><b>{e(code)}</b><small>{e(lib)}</small></th>{cases}</tr>"
    return page("Compétences", f'''
<section class="titre-seance"><h1>Les compétences de l'année</h1><p class="chapo">Chaque case renvoie à la séance où la compétence est travaillée.</p></section>
<section class="bloc tableau"><table><thead><tr><th>Compétence</th>{tete}</tr></thead><tbody>{lignes}</tbody></table></section>''',
        fil=[("Accueil", "index.html"), ("Compétences", None)])


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
        extra_tete='<link rel="stylesheet" href="../assets/activites.css">', extra_pied='<script src="../assets/activites.js"></script>')


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
    ids = {a["id"]: [b["id"] for b in a["blocs"] if b["type"] != "cours" and any(x["type"] not in ("image", "texte", "redaction") for x in b["parties"])] for a in ACTS.values()}
    contenu = contenu.replace("ACTS_OPTIONS", opts).replace("ACTS_IDS", json.dumps(ids))
    return page("Vérifier un certificat", contenu, extra_tete='<link rel="stylesheet" href="assets/activites.css"><meta name="robots" content="noindex">')


# ---------- construction ----------
def main():
    if SORTIE.exists():
        shutil.rmtree(SORTIE)
    SORTIE.mkdir()
    for d in ("assets", "media", "fiches"):
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
    for chemin, html in pages.items():
        (SORTIE / chemin).parent.mkdir(parents=True, exist_ok=True)
        (SORTIE / chemin).write_text(html, encoding="utf-8")
    print(f"✔ {len(pages)} pages · {len(ACTS)} séances en ligne · {len(FICHES)} fiches synthèse")


if __name__ == "__main__":
    main()
