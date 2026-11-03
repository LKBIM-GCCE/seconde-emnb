"""Maison des jeux — version BTS MEC, en UN SEUL fichier HTML autonome (pour Google Sites).
Les 26 jeux sont embarqués dans la page et s'ouvrent dans une fenêtre par-dessus la maison.
Usage : python maison_bts.py dossier_jeux_source fichier_sortie.html [url_base_jeux dossier_jeux_sortie]
Avec url_base_jeux : les jeux sont écrits à part (dossier_jeux_sortie) et chargés depuis cette adresse
(page légère, adaptée au « code intégré » de Google Sites)."""
import re, sys, json
from html import escape as e
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from maison_jeux import ZONES, DECOR

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
BASE = sys.argv[3] if len(sys.argv) > 3 else ""
DOSSIER_JEUX = Path(sys.argv[4]) if len(sys.argv) > 4 else None
THEMES = {
    "LE GROS OEUVRE": ("gros-oeuvre", "Gros œuvre"), "LA COUVERTURE": ("couverture", "Couverture et étanchéité"),
    "LES MENUISERIES EXT": ("menuiseries", "Menuiseries extérieures"), "LA PLATRERIE": ("platrerie", "Plâtrerie et plafonds"),
    "L'ELECTRICITE": ("electricite", "Électricité"), "LA PLOMBERIE": ("plomberie", "Plomberie et sanitaire"),
    "LES REVETEMENTS DE SOLS": ("sols", "Revêtements de sol"), "LES REVETEMENTS MURAUX": ("peinture", "Peinture et revêtements muraux"),
    "LEXIQUE BATIMENT": ("lexique", "Lexique du bâtiment"), "REGLEMENTATION INCENDIE": ("incendie", "Sécurité incendie"),
    "REGLEMENTATION PMR": ("pmr", "Accessibilité PMR"),
}
ETAPES = [("_1_decouvrir", "decouvrir", "1 · Découvrir"), ("_2_sentrainer", "sentrainer", "2 · S'entraîner"), ("_3_sedefier", "sedefier", "3 · Se défier")]
# Regard « économiste » : pourquoi ce lot compte pour le métré et le chiffrage
ECO = {
    "gros-oeuvre": "Le lot le plus lourd du budget : fondations, murs, planchers se métrent au m³, m² et kg d'acier.",
    "couverture": "Surfaces de toiture en rampant, linéaires de rives, faîtages et gouttières : un métré à part entière.",
    "menuiseries": "Chiffrées à l'unité selon dimensions, matériau, vitrage et performance thermique.",
    "platrerie": "Cloisons et doublages au m², ossatures et bandes : un lot de métré très répétitif.",
    "electricite": "Points lumineux, prises, circuits : un lot technique chiffré à l'unité et au forfait.",
    "plomberie": "Appareils sanitaires à l'unité, réseaux au mètre linéaire : alimentation et évacuation.",
    "sols": "Surfaces nettes par local, plinthes au mètre linéaire, chutes à prévoir selon la pose.",
    "peinture": "Surfaces de murs et plafonds déduction faite des baies, préparation des supports comprise.",
    "lexique": "Le vocabulaire commun pour lire un CCTP, un DPGF et dialoguer avec la maîtrise d'œuvre.",
    "incendie": "Les exigences de sécurité pèsent sur le coût : dégagements, désenfumage, équipements.",
    "pmr": "L'accessibilité impose des dimensions et des équipements qu'il faut savoir chiffrer.",
}
DESC = {
    "sols": "Carrelage, parquet, sol souple : complexes, supports et types de pose.",
    "lexique": "Le vocabulaire du dessinateur et du projeteur.",
    "electricite": "Prises, tableau électrique, volumes de salle de bains.",
}
THEME_CSS = """:root{--jaune:#ffc52e;--jaune-clair:#fff4d1;--encre:#13223f;--gris:#55637e;--vert:#1f8a5b;--vert-clair:#ddf3e8;--rouge:#c62828;--rouge-clair:#fdecea;--bleu:#1f55d6;--ligne:#cfd9e8}
body{font-family:"Atkinson Hyperlegible",system-ui,sans-serif;font-size:16.5px;background:#eef3f9}
h1,h2,.question,.resultat .note{font-family:"Bricolage Grotesque","Trebuchet MS",sans-serif}
.cadre{border:1.5px solid var(--bleu);border-radius:10px;box-shadow:0 5px 0 var(--jaune)}
header{background:#0f2c6e;color:#fff}.badge{background:var(--jaune);color:var(--encre)}
.consigne{background:var(--jaune-clair);border-left-color:#f2600f}
.btn,.onglets button.actif{background:var(--bleu);border-color:var(--bleu)}
button:hover:not(:disabled){border-color:#f2600f}
.barre{height:10px;border-radius:5px}.barre div{background:linear-gradient(90deg,var(--jaune),#f2600f)}
.resultat .note{color:#f2600f}.fiche{border-left-color:#f2600f}.fiche h2{color:#0f2c6e}footer{background:#f6f9fd}"""
POLICES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&display=swap">')
PLANCHE = ('<script>window.addEventListener("load",function(){var p=document.querySelectorAll("svg.planche");'
           'if(p.length&&!Array.prototype.some.call(p,function(s){return getComputedStyle(s).display!=="none"})){'
           'var b=document.querySelector(".planches button");if(b)b.click()}});</script>')

jeux, catalogue = {}, []
for dossier, (slug, nom) in THEMES.items():
    d = SRC / dossier
    etapes = []
    for suf, cle, lib in ETAPES:
        f = next(iter(d.glob(f"*{suf}.html")), None)
        if not f: continue
        t = f.read_text(encoding="utf-8")
        t = t.replace('<span class="badge">Entraînement · Découverte</span>', '<span class="badge">Autoformation</span>')
        t = t.replace('<span class="badge">TP TEBDP</span>', '<span class="badge">BTS MEC</span>')
        def pied(m):
            s = re.search(r"Connaissances mobilisées : (.*?)(?: \((?:CP\d+(?: · CP\d+)*)\))?\.(.*)$", m.group(1))
            return f"<footer>BTS MEC · Autoformation · Connaissances mobilisées : {s.group(1)}.{s.group(2)}</footer>" if s else m.group(0)
        t = re.sub(r"<footer>(.*?)</footer>", pied, t, flags=re.S)
        t = t.replace("</head>", POLICES + f"<style>{THEME_CSS}</style></head>", 1)
        t = t.replace("</body>", PLANCHE + "</body>", 1)
        jeux[f"{slug}/{cle}"] = t
        etapes.append({"cle": cle, "lib": lib})
    catalogue.append((slug, nom, etapes))

# ---------------- la maison
zones, cartes = "", ""
for slug, nom, etapes in catalogue:
    emo, desc, x, y, forme = ZONES[slug]
    desc = DESC.get(slug, desc)
    larg = int(len(nom) * 8.2 + 26); ex = max(10, min(990 - larg, x - larg // 2)); ey = y + 28 if y < 560 else y - 64
    zones += (f'<a class="mj-zone" href="#{slug}/decouvrir" data-jeu="{slug}/decouvrir" data-slug="{slug}" aria-label="{e(nom)}">'
              f'<g class="mj-surv">{forme}</g><g class="mj-pin" transform="translate({x} {y})"><circle r="21"/><text y="8" text-anchor="middle">{emo}</text>'
              f'<g class="mj-ok"><circle cx="17" cy="-17" r="9"/><path d="M12.5 -17l3 3 6-6"/></g></g>'
              f'<g class="mj-etiq"><rect x="{ex}" y="{ey}" width="{larg}" height="30" rx="15"/><text x="{ex + larg / 2}" y="{ey + 20}" text-anchor="middle">{e(nom)}</text></g></a>')
    boutons = "".join(f'<a class="mj-etape" href="#{slug}/{s["cle"]}" data-jeu="{slug}/{s["cle"]}">{e(s["lib"])}</a>' for s in etapes)
    cartes += (f'<li class="mj-carte" data-slug="{slug}"><span class="mj-emo" aria-hidden="true">{emo}</span><h3>{e(nom)}</h3>'
               f'<p>{e(desc)}</p><p class="mj-eco"><b>Œil de l\'économiste</b> {e(ECO[slug])}</p><div class="mj-etapes">{boutons}</div></li>')

CAT = {slug: {"nom": nom, "etapes": etapes} for slug, nom, etapes in catalogue}
if BASE:
    for k, v in jeux.items():
        (DOSSIER_JEUX / k).parent.mkdir(parents=True, exist_ok=True)
        (DOSSIER_JEUX / f"{k}.html").write_text(v, encoding="utf-8")
    data = json.dumps({"base": BASE, "jeux": {k: 1 for k in jeux}, "cat": CAT}, ensure_ascii=False)
else:
    data = json.dumps({"jeux": jeux, "cat": CAT}, ensure_ascii=False).replace("</", "<\\/")

page = f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Maison des jeux · BTS MEC</title>{POLICES}
<style>
:root{{--calque:#eef3f9;--carte:#fff;--encre:#13223f;--doux:#55637e;--plan:#1f55d6;--plan-fonce:#0f2c6e;--plan-pale:#dfe8fb;--chantier:#f2600f;--signal:#ffc52e;--trait:#cfd9e8;
--titre:"Bricolage Grotesque","Trebuchet MS",sans-serif;--texte:"Atkinson Hyperlegible",system-ui,sans-serif}}
*{{box-sizing:border-box}}html,body{{margin:0}}
body{{background:var(--calque);color:var(--encre);font:16.5px/1.55 var(--texte);
background-image:linear-gradient(rgba(31,85,214,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(31,85,214,.07) 1px,transparent 1px);background-size:24px 24px}}
.page{{max-width:1080px;margin:0 auto;padding:18px 14px 40px}}
.tete{{display:flex;align-items:center;gap:14px;flex-wrap:wrap;background:var(--plan-fonce);color:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 5px 0 var(--signal)}}
.tete .logo{{flex:none;background:var(--signal);color:var(--encre);border-radius:8px;padding:6px 10px;font:800 16px/1 var(--titre)}}
.tete h1{{margin:0;font:800 clamp(22px,3.4vw,30px)/1.15 var(--titre)}}.tete p{{margin:2px 0 0;opacity:.85;font-size:15px}}
.intro{{display:flex;justify-content:space-between;align-items:center;gap:12px 24px;flex-wrap:wrap;margin:18px 2px 0}}
.intro p{{margin:0;max-width:44em;color:var(--doux)}}
.mj-compteur{{display:flex;align-items:center;gap:10px;font-weight:700}}
.mj-jauge{{width:200px;height:14px;border-radius:7px;background:var(--plan-pale);overflow:hidden}}
.mj-jauge i{{display:block;height:100%;width:0;background:linear-gradient(90deg,var(--signal),var(--chantier));transition:width .6s}}
.mj-maison{{margin:14px 0 0;background:var(--carte);border:1.5px solid var(--plan);border-radius:12px;padding:8px;box-shadow:0 6px 0 var(--signal)}}
.mj-maison svg{{display:block;width:100%;height:auto;border-radius:8px}}
.mj-zone{{cursor:pointer;outline:none}}.mj-surv>*{{fill:rgba(255,197,46,0);transition:fill .2s}}
.mj-zone:hover .mj-surv>*,.mj-zone:focus-visible .mj-surv>*{{fill:rgba(255,197,46,.45);stroke:#f2600f;stroke-width:3}}
.mj-pin circle{{fill:#ffc52e;stroke:#13223f;stroke-width:2.5}}.mj-pin text{{font-size:22px}}
@media (prefers-reduced-motion:no-preference){{.mj-pin>circle{{animation:pouls 2.4s ease-in-out infinite}}}}
@keyframes pouls{{0%,100%{{stroke-width:2.5}}50%{{stroke-width:6;stroke:#f2600f}}}}
.mj-zone:hover .mj-pin>circle,.mj-zone:focus-visible .mj-pin>circle{{fill:#f2600f}}
.mj-ok{{display:none}}.mj-ok circle{{fill:#1f8a5b;stroke:#fff;stroke-width:2}}.mj-ok path{{fill:none;stroke:#fff;stroke-width:2.4;stroke-linecap:round}}
.mj-zone.vu .mj-ok{{display:inline}}
.mj-etiq{{opacity:0;transition:opacity .15s;pointer-events:none}}.mj-etiq rect{{fill:#0f2c6e}}.mj-etiq text{{fill:#fff;font:700 15px var(--texte)}}
.mj-zone:hover .mj-etiq,.mj-zone:focus-visible .mj-etiq{{opacity:1}}
.legende{{font-size:14.5px;color:var(--doux);padding:8px 8px 2px;margin:0}}
h2{{font:800 24px/1.2 var(--titre);margin:34px 2px 14px}}
.mj-cartes{{list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}}
.mj-carte{{position:relative;background:var(--carte);border:1px solid var(--trait);border-radius:10px;padding:16px;display:flex;flex-direction:column}}
.mj-carte.vu{{border-color:#1f8a5b}}.mj-carte.vu::after{{content:"✓ exploré";position:absolute;top:12px;right:12px;font-size:12px;font-weight:700;color:#fff;background:#1f8a5b;padding:2px 8px;border-radius:10px}}
.mj-emo{{font-size:32px;line-height:1}}.mj-carte h3{{margin:8px 0 4px;font:800 19px/1.2 var(--titre)}}
.mj-carte p{{margin:0 0 8px;color:var(--doux);font-size:14.5px}}
.mj-eco{{background:#fff4d1;border-left:3px solid var(--chantier);padding:6px 9px;border-radius:4px;flex:1}}.mj-eco b{{display:block;color:var(--encre);font-size:13px}}
.mj-etapes{{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}}
.mj-etape{{text-decoration:none;font-weight:700;font-size:14px;color:var(--plan);border:1.5px solid var(--plan);border-radius:20px;padding:4px 10px}}
.mj-etape:hover{{background:var(--plan);color:#fff}}.mj-etape.vu{{background:var(--plan-pale)}}.mj-etape.vu::before{{content:"✓ ";color:#1f8a5b}}
.pied{{text-align:center;color:var(--doux);font-size:13px;margin-top:30px}}
/* fenêtre de jeu */
#fenetre{{position:fixed;inset:0;z-index:10;display:none;flex-direction:column;background:var(--calque)}}
#fenetre.ouvert{{display:flex}}
.f-barre{{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;padding:10px 14px;background:#fff;border-bottom:1.5px solid var(--plan)}}
.f-barre button{{font:700 15px var(--texte);cursor:pointer;border-radius:8px;padding:7px 12px;border:0}}
#f-retour{{background:var(--plan-fonce);color:#fff}}#f-retour:hover{{background:var(--chantier)}}
#f-titre{{font:800 17px var(--titre);color:var(--plan-fonce)}}
#f-etapes{{display:flex;flex-wrap:wrap;gap:6px;margin-left:auto}}
#f-etapes button{{background:#fff;color:var(--plan);border:1.5px solid var(--plan);border-radius:20px;padding:5px 11px;font-size:14px}}
#f-etapes button[aria-current="true"]{{background:var(--signal);border-color:var(--signal);color:var(--encre)}}
#f-cadre{{flex:1;border:0;width:100%;background:var(--calque)}}
</style></head><body>
<div class="page">
<header class="tete"><span class="logo">BTS MEC</span><div><h1>La maison des jeux</h1><p>Management économique de la construction · découvrir les ouvrages avant de les métrer et de les chiffrer</p></div></header>
<div class="intro"><p>Cliquez sur une partie de la maison pour ouvrir le jeu du lot correspondant. Chaque thème propose jusqu'à 3 étapes : <b>Découvrir</b>, <b>S'entraîner</b>, <b>Se défier</b>.</p>
<div class="mj-compteur" aria-live="polite"><span>Lots explorés : <b>0 / {len(catalogue)}</b></span><span class="mj-jauge"><i></i></span></div></div>
<figure class="mj-maison"><svg viewBox="0 0 1000 640" role="img" aria-label="Coupe d'une maison : chaque partie ouvre un jeu">{DECOR}{zones}</svg>
<p class="legende">Astuce : sur téléphone, utilisez plutôt la liste des lots ci-dessous.</p></figure>
<h2>Tous les lots</h2><ul class="mj-cartes">{cartes}</ul>
<p class="pied">BTS MEC · Autoformation · Les jeux s'ouvrent dans cette page, aucune installation nécessaire.</p>
</div>
<div id="fenetre" role="dialog" aria-modal="true" aria-labelledby="f-titre">
<div class="f-barre"><button id="f-retour" type="button">🏠 Retour à la maison</button><span id="f-titre"></span><span id="f-etapes"></span></div>
<iframe id="f-cadre" title="Jeu"></iframe></div>
<script id="donnees" type="application/json">{data}</script>
<script>
(function(){{
var D=JSON.parse(document.getElementById('donnees').textContent),K='bts-mec-jeux-vus',vus=[];
try{{vus=JSON.parse(localStorage.getItem(K)||'[]')}}catch(e){{}}
function sauver(){{try{{localStorage.setItem(K,JSON.stringify(vus))}}catch(e){{}}}}
function maj(){{var faits=new Set(vus.map(function(x){{return x.split('/')[0]}}));
document.querySelectorAll('[data-slug]').forEach(function(el){{el.classList.toggle('vu',faits.has(el.dataset.slug))}});
document.querySelectorAll('.mj-etape').forEach(function(a){{a.classList.toggle('vu',vus.indexOf(a.dataset.jeu)>=0)}});
var n=Object.keys(D.cat).length;var c=document.querySelector('.mj-compteur');c.querySelector('b').textContent=faits.size+' / '+n;c.querySelector('i').style.width=(100*faits.size/n)+'%'}}
var fen=document.getElementById('fenetre'),cadre=document.getElementById('f-cadre');
function ouvrir(id){{if(!D.jeux[id])return;var slug=id.split('/')[0],cle=id.split('/')[1],t=D.cat[slug];
document.getElementById('f-titre').textContent=t.nom;
var et=document.getElementById('f-etapes');et.innerHTML='';
t.etapes.forEach(function(s){{var b=document.createElement('button');b.type='button';b.textContent=s.lib;if(s.cle===cle)b.setAttribute('aria-current','true');
b.onclick=function(){{ouvrir(slug+'/'+s.cle)}};et.appendChild(b)}});
if(D.base){{cadre.removeAttribute('srcdoc');cadre.src=D.base+id+'.html'}}else{{cadre.srcdoc=D.jeux[id]}}fen.classList.add('ouvert');document.body.style.overflow='hidden';
if(vus.indexOf(id)<0){{vus.push(id);sauver()}}maj();document.getElementById('f-retour').focus()}}
function fermer(){{fen.classList.remove('ouvert');if(D.base){{cadre.src='about:blank'}}else{{cadre.srcdoc=''}}document.body.style.overflow=''}}
document.addEventListener('click',function(ev){{var a=ev.target.closest('[data-jeu]');if(a){{ev.preventDefault();ouvrir(a.dataset.jeu)}}}});
document.getElementById('f-retour').onclick=fermer;
document.addEventListener('keydown',function(ev){{if(ev.key==='Escape'&&fen.classList.contains('ouvert'))fermer()}});
maj();}})();
</script></body></html>"""
OUT.write_text(page, encoding="utf-8")
print(OUT, round(OUT.stat().st_size / 1024), "Ko ·", len(jeux), "jeux")
