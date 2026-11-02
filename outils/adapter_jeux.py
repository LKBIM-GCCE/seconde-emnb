"""Adapte les jeux HTML de découverte (créés pour le TP TEBDP) pour la Seconde EMNB :
tutoiement, bandeau et pied de page Seconde, thème graphique du site, barre de navigation
(retour à la maison des jeux + étapes Découvrir / S'entraîner / Se défier).
Usage : python adapter_jeux.py dossier_source dossier_sortie(jeux/decouverte)"""
import re, sys, json
from pathlib import Path

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])

# dossier source -> (slug, nom affiché)
THEMES = {
    "LE GROS OEUVRE": ("gros-oeuvre", "Gros œuvre"),
    "LA COUVERTURE": ("couverture", "Couverture et étanchéité"),
    "LES MENUISERIES EXT": ("menuiseries", "Menuiseries extérieures"),
    "LA PLATRERIE": ("platrerie", "Plâtrerie et plafonds"),
    "L'ELECTRICITE": ("electricite", "Électricité"),
    "LA PLOMBERIE": ("plomberie", "Plomberie et sanitaire"),
    "LES REVETEMENTS DE SOLS": ("sols", "Revêtements de sol"),
    "LES REVETEMENTS MURAUX": ("peinture", "Peinture et revêtements muraux"),
    "LEXIQUE BATIMENT": ("lexique", "Lexique du bâtiment"),
    "REGLEMENTATION INCENDIE": ("incendie", "Sécurité incendie"),
    "REGLEMENTATION PMR": ("pmr", "Accessibilité PMR"),
}
ETAPES = [("_1_decouvrir", "decouvrir", "1 · Découvrir"), ("_2_sentrainer", "sentrainer", "2 · S'entraîner"), ("_3_sedefier", "sedefier", "3 · Se défier")]

# Tutoiement (Seconde) — ordre : expressions longues d'abord
TU = [
    ("Reconnaîtrez-vous", "Reconnaîtras-tu"), ("référez-vous", "réfère-toi"),
    ("Vous vérifiez", "Tu vérifies"), ("vous semblent", "te semblent"), ("pour vous tester", "pour te tester"),
    ("vous êtes prêt(e)", "tu es prêt(e)"), ("Vous avez", "Tu as"), ("vous avez", "tu as"),
    ("vous savez", "tu sais"), ("vous maîtrisez", "tu maîtrises"), ("vous connaissez", "tu connais"), ("vous parlez", "tu parles"),
    ("Relisez", "Relis"), ("rejouez", "rejoue"), ("Rejouez", "Rejoue"), ("Cliquez", "Clique"), ("cliquez", "clique"),
    ("retrouvez", "retrouve"), ("Retrouvez", "Retrouve"), ("retentez", "retente"), ("Revenez", "Reviens"), ("Prenez", "Prends"),
    ("choisissez", "choisis"), ("Choisissez", "Choisis"), ("Retenez", "Retiens"), ("vérifiez", "vérifie"),
    ("déterminez", "détermine"), ("dimensionnez", "dimensionne"), ("calculez", "calcule"), ("cherchez", "cherche"),
    ("Utilisez", "Utilise"), ("utilisez", "utilise"), ("Remettez", "Remets"), ("Corrigez", "Corrige"), ("refaites", "refais"),
    ("Observez", "Observe"), ("observez", "observe"), ("Lisez", "Lis"), ("lisez", "lis"), ("Placez", "Place"), ("placez", "place"),
    ("Glissez", "Glisse"), ("glissez", "glisse"), ("Essayez", "Essaie"), ("essayez", "essaie"), ("Comparez", "Compare"),
]

THEME_CSS = '<link rel="stylesheet" href="../../../assets/jeux-theme.css">'
POLICES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&display=swap">')


def tutoyer(t):
    for a, b in TU:
        t = re.sub(r"(?<![\wÀ-ÿ])" + re.escape(a) + r"(?![\wÀ-ÿ])", b, t)
    return t


catalogue = []
for dossier, (slug, nom) in THEMES.items():
    d = SRC / dossier
    if not d.exists():
        print("absent :", dossier); continue
    fichiers = {}
    for suf, cle, lib in ETAPES:
        f = next(iter(d.glob(f"*{suf}.html")), None)
        if f: fichiers[cle] = (f, lib)
    (OUT / slug).mkdir(parents=True, exist_ok=True)
    etapes_nav = [(cle, lib, f"{cle}.html") for cle, (f, lib) in fichiers.items()]
    for cle, (f, lib) in fichiers.items():
        t = f.read_text(encoding="utf-8")
        titre = re.search(r"<title>(.*?)</title>", t).group(1)
        # bandeau
        t = t.replace('<span class="badge">Entraînement · Découverte</span>', '<span class="badge">Découverte libre</span>')
        t = t.replace('<span class="badge">TP TEBDP</span>', '<span class="badge">2de EMNB</span>')
        # pied de page
        def pied(m):
            txt = m.group(1)
            savoirs = re.search(r"Connaissances mobilisées : (.*?)(?: \((?:CP\d+(?: · CP\d+)*)\))?\.(.*)$", txt)
            if savoirs:
                txt = f"Seconde EMNB · Découverte libre, pour le plaisir d'apprendre · Tu découvres : {savoirs.group(1)}.{savoirs.group(2)}"
            return f"<footer>{txt}</footer>"
        t = re.sub(r"<footer>(.*?)</footer>", pied, t, flags=re.S)
        t = tutoyer(t)
        # thème + polices
        t = t.replace("</head>", POLICES + THEME_CSS + "</head>", 1)
        # barre de navigation
        liens = "".join(f'<a href="{href}"{" aria-current=\"page\"" if c == cle else ""}>{l}</a>' for c, l, href in etapes_nav)
        barre = (f'<nav class="jeux-barre" aria-label="Navigation des jeux"><a class="jeux-retour" href="../../../jeux.html">🏠 La maison des jeux</a>'
                 f'<span class="jeux-theme">{nom}</span><span class="jeux-etapes">{liens}</span></nav>')
        vu = (f'<script>(function(){{try{{var k="emnb-jeux-vus",v=JSON.parse(localStorage.getItem(k)||"[]");'
              f'if(v.indexOf("{slug}/{cle}")<0){{v.push("{slug}/{cle}");localStorage.setItem(k,JSON.stringify(v))}}}}catch(e){{}}}})()</script>')
        t = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + barre + vu, t, count=1)
        # afficher la première planche dès l'ouverture (sinon la zone de jeu reste vide)
        t = t.replace("</body>", '<script>window.addEventListener("load",function(){var p=document.querySelectorAll("svg.planche");'
                      'if(p.length&&!Array.prototype.some.call(p,function(s){return getComputedStyle(s).display!=="none"})){'
                      'var b=document.querySelector(".planches button");if(b)b.click()}});</script></body>', 1)
        (OUT / slug / f"{cle}.html").write_text(t, encoding="utf-8")
    catalogue.append({"slug": slug, "nom": nom, "etapes": [{"cle": c, "lib": l, "href": f"jeux/decouverte/{slug}/{h}"} for c, l, h in etapes_nav]})

(OUT / "catalogue.json").write_text(json.dumps(catalogue, ensure_ascii=False, indent=1), encoding="utf-8")
restes = set()
for f in OUT.rglob("*.html"):
    restes |= set(re.findall(r"[^\s>\"']*\b(?:vous|Vous|[a-zà-ÿ]+ez)\b[^\s<\"']*", f.read_text(encoding="utf-8")))
print(len(catalogue), "thèmes ·", sum(len(c["etapes"]) for c in catalogue), "jeux")
print("à vérifier :", sorted(restes)[:60])
