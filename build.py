#!/usr/bin/env python3
"""
Générateur du site Seconde EMNB.
Lit data/progression.json et fabrique toutes les pages dans docs/
(dossier publié par GitHub Pages). Usage : python build.py
"""
import json, re, shutil
from html import escape as e
from pathlib import Path

RACINE = Path(__file__).parent
DATA = json.loads((RACINE / "data" / "progression.json").read_text(encoding="utf-8"))
SITE, COMP = DATA["site"], DATA["competences"]
SORTIE = RACINE / "docs"

TYPES = {  # type de ressource -> (icône, libellé)
    "cours": ("📘", "Cours"), "td": ("✏️", "TD / TP"), "synthese": ("📌", "Fiche synthèse"),
    "presentation": ("🖥️", "Présentation"), "plan": ("📐", "Plan"), "maquette": ("🧊", "Maquette"),
    "video": ("🎬", "Vidéo"), "qcm": ("✅", "QCM"), "lien": ("🔗", "Lien"),
}


# ---------- outils ----------
def lien_integrable(url):
    """Transforme un lien Google Drive / Docs / Slides / YouTube en lien d'aperçu intégrable."""
    m = re.search(r"drive\.google\.com/file/d/([^/]+)", url)
    if m: return f"https://drive.google.com/file/d/{m[1]}/preview"
    m = re.search(r"docs\.google\.com/(document|presentation|spreadsheets|forms)/d/([^/]+)", url)
    if m:
        kind, id_ = m[1], m[2]
        return f"https://docs.google.com/forms/d/{id_}/viewform?embedded=true" if kind == "forms" \
            else f"https://docs.google.com/{kind}/d/{id_}/preview"
    m = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)", url)
    if m: return f"https://www.youtube-nocookie.com/embed/{m[1]}"
    return url


def comp_pills(codes):
    return "".join(f'<span class="comp" title="{e(COMP.get(c, ""))}">{e(c)}</span>' for c in codes)


def ressource_html(r, base):
    icone, libelle = TYPES.get(r["type"], ("📄", "Document"))
    if not r["lien"]:
        return f'''<li class="res off"><span class="ico">{icone}</span><span class="txt"><b>{e(r["nom"])}</b><small>{libelle} · bientôt disponible</small></span></li>'''
    url = r["lien"] if r["lien"].startswith("http") else base + r["lien"]
    bloc = f'''<li class="res"><a href="{e(url)}" target="_blank" rel="noopener"><span class="ico">{icone}</span><span class="txt"><b>{e(r["nom"])}</b><small>{libelle} · ouvrir ↗</small></span></a>'''
    if r.get("integrer"):
        bloc += f'<div class="embed"><iframe src="{e(lien_integrable(url))}" loading="lazy" allowfullscreen></iframe></div>'
    return bloc + "</li>"


def liste_ressources(rs, base):
    if not rs:
        return '<p class="vide">Les documents de cette séance seront ajoutés prochainement.</p>'
    return '<ul class="ressources">' + "".join(ressource_html(r, base) for r in rs) + "</ul>"


# ---------- gabarit ----------
def page(titre, contenu, prof=0, fil=None):
    base = "../" * prof
    nav_seq = "".join(
        f'<a href="{base}{s["id"]}/index.html">{e(s["numero"])}</a>' for s in DATA["sequences"] if s["statut"] == "en_ligne")
    fil_html = ""
    if fil:
        fil_html = '<nav class="fil">' + " › ".join(
            f'<a href="{base}{u}">{e(t)}</a>' if u else f"<span>{e(t)}</span>" for t, u in fil) + "</nav>"
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titre)} · {e(SITE["titre"])}</title>
<link rel="stylesheet" href="{base}assets/style.css">
</head><body>
<header class="entete">
  <a class="marque" href="{base}index.html"><span class="logo">2<small>de</small></span>
    <span><strong>{e(SITE["titre"])}</strong><em>{e(SITE["sous_titre"])}</em></span></a>
  <nav class="menu">{nav_seq}<a href="{base}competences.html">Compétences</a></nav>
</header>
<main>{fil_html}{contenu}</main>
<footer class="pied">{e(SITE["etablissement"])} · {e(SITE["enseignant"])} · {e(SITE["annee"])}</footer>
</body></html>"""


# ---------- pages ----------
def accueil():
    cartes = ""
    for s in DATA["sequences"]:
        if s["statut"] == "en_ligne":
            cartes += f'''<a class="carte" href="{s["id"]}/index.html">
  <div class="carte-haut"><span class="num">{e(s["numero"])}</span><span class="periode">{e(s["periode"])}</span></div>
  <h2>{e(s["titre"])}</h2><p>{e(s["problematique"])}</p>
  <span class="meta">{len(s["seances"])} séances · {e(s["duree"])}</span></a>'''
        else:
            cartes += f'''<div class="carte off"><div class="carte-haut"><span class="num">{e(s["numero"])}</span><span class="periode">À venir</span></div>
  <h2>{e(s["titre"])}</h2><p>Cette séquence sera publiée dans l'année.</p></div>'''
    return page("Accueil", f'''
<section class="hero"><p class="sur">{e(SITE["annee"])}</p><h1>Bienvenue en Seconde EMNB</h1>
<p>Retrouve ici chaque séquence de l'année : ce que tu vas apprendre, le déroulé des séances et tous les documents (cours, TD, plans, fiches synthèse).</p></section>
<section class="grille">{cartes}</section>''')


def page_sequence(s):
    lignes = "".join(f'''<a class="seance-ligne" href="{x["id"]}.html"><span class="num-s">S{i}</span>
  <div><h3>{e(x["titre"])}</h3><p>{e(x["duree"])} · {e(x["evaluation"])}</p></div><div class="comps">{comp_pills(x["competences"])}</div></a>'''
        for i, x in enumerate(s["seances"], 1))
    res_seq = ""
    if s.get("ressources_sequence"):
        res_seq = f'<section class="bloc"><h2>Documents de la séquence</h2>{liste_ressources(s["ressources_sequence"], "../")}</section>'
    return page(s["numero"], f'''
<section class="titre"><span class="num">{e(s["numero"])}</span><h1>{e(s["titre"])}</h1>
<p class="periode">{e(s["periode"])} · {e(s["duree"])}</p></section>
<section class="bloc probl"><h2>Problématique</h2><p>{e(s["problematique"])}</p></section>
<section class="bloc"><h2>Ta mission</h2><p>{e(s["contexte"])}</p></section>
<section class="bloc"><h2>Les séances</h2><div class="liste">{lignes}</div></section>{res_seq}''',
        prof=1, fil=[("Accueil", "index.html"), (s["numero"], None)])


def page_seance(s, i):
    x = s["seances"][i]
    objectifs = "".join(f"<li>{e(o)}</li>" for o in x["objectifs"])
    comps = "".join(f"<li><b>{e(c)}</b> {e(COMP.get(c, ''))}</li>" for c in x["competences"])
    deroule = "".join(f'''<li><span class="temps">{e(d["temps"])}</span><div><h3>{e(d["etape"])}</h3>
<ul>{"".join(f"<li>{e(a)}</li>" for a in d["eleves"])}</ul></div></li>''' for d in x["deroule"])
    prec = s["seances"][i - 1] if i > 0 else None
    suiv = s["seances"][i + 1] if i + 1 < len(s["seances"]) else None
    nav = '<nav class="pagination">' + (f'<a href="{prec["id"]}.html">← S{i} · {e(prec["titre"])}</a>' if prec else "<span></span>") \
        + (f'<a href="{suiv["id"]}.html">S{i+2} · {e(suiv["titre"])} →</a>' if suiv else "<span></span>") + "</nav>"
    return page(f'{s["numero"]} S{i+1}', f'''
<section class="titre"><span class="num">{e(s["numero"])} · S{i+1}</span><h1>{e(x["titre"])}</h1>
<p class="periode">{e(x["duree"])} · Évaluation : {e(x["evaluation"])}</p></section>
<div class="deux-col">
<section class="bloc"><h2>À la fin de la séance, je sais…</h2><ul class="coche">{objectifs}</ul></section>
<section class="bloc"><h2>Compétences travaillées</h2><ul class="liste-comp">{comps}</ul></section>
</div>
<section class="bloc"><h2>Documents</h2>{liste_ressources(x["ressources"], "../")}</section>
<section class="bloc"><h2>Déroulé de la séance</h2><ol class="frise">{deroule}</ol></section>
{nav}''', prof=1, fil=[("Accueil", "index.html"), (s["numero"], f'{s["id"]}/index.html'), (f"S{i+1}", None)])


def page_competences():
    seqs = [s for s in DATA["sequences"] if s["statut"] == "en_ligne"]
    tete = "".join(f"<th>{e(s['numero'])}</th>" for s in seqs)
    lignes = ""
    for code, lib in COMP.items():
        cases = ""
        for s in seqs:
            liens = [f'<a href="{s["id"]}/{x["id"]}.html">S{k}</a>' for k, x in enumerate(s["seances"], 1) if code in x["competences"]]
            cases += f'<td>{" ".join(liens) if liens else ""}</td>'
        lignes += f"<tr><th scope='row'><b>{e(code)}</b><small>{e(lib)}</small></th>{cases}</tr>"
    return page("Compétences", f'''
<section class="titre"><h1>Les compétences de l'année</h1><p class="periode">Clique sur une séance pour y aller.</p></section>
<section class="bloc tableau"><table><thead><tr><th>Compétence</th>{tete}</tr></thead><tbody>{lignes}</tbody></table></section>''',
        fil=[("Accueil", "index.html"), ("Compétences", None)])


# ---------- construction ----------
def main():
    if SORTIE.exists():
        for f in SORTIE.iterdir():
            if f.name != "ressources":  # les documents déposés ne sont jamais effacés
                shutil.rmtree(f) if f.is_dir() else f.unlink()
    SORTIE.mkdir(exist_ok=True)
    shutil.copytree(RACINE / "assets", SORTIE / "assets", dirs_exist_ok=True)
    (SORTIE / ".nojekyll").touch()
    pages = {"index.html": accueil(), "competences.html": page_competences()}
    for s in DATA["sequences"]:
        if s["statut"] != "en_ligne": continue
        pages[f'{s["id"]}/index.html'] = page_sequence(s)
        for i, x in enumerate(s["seances"]):
            pages[f'{s["id"]}/{x["id"]}.html'] = page_seance(s, i)
    for chemin, html in pages.items():
        (SORTIE / chemin).parent.mkdir(parents=True, exist_ok=True)
        (SORTIE / chemin).write_text(html, encoding="utf-8")
    nb_res = sum(len(x["ressources"]) for s in DATA["sequences"] for x in s["seances"])
    nb_ok = sum(1 for s in DATA["sequences"] for x in s["seances"] for r in x["ressources"] if r["lien"])
    print(f"✔ {len(pages)} pages générées · documents en ligne : {nb_ok}/{nb_res}")


if __name__ == "__main__":
    main()
