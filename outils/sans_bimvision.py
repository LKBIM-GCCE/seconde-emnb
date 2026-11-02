"""Remplace les mentions BIMvision (et le tableur / dossier réseau) par la visionneuse du site,
paragraphe par paragraphe, dans des .docx / .pptx / .xlsx (sans toucher à la mise en forme).
Usage : python sans_bimvision.py entree sortie"""
import re, sys, zipfile

R = [
    ("Lisible avec une visionneuse gratuite : BIMvision", "Lisible avec une visionneuse gratuite : la visionneuse 3D du site"),
    ("BIMVISION : LES GESTES DE BASE", "VISIONNEUSE : LES GESTES DE BASE"),
    ("Arborescence → isoler un niveau ou une classe", "Niveaux → n'afficher qu'un niveau (RDC, R+1…)"),
    ("Masquer / afficher → voir à l'intérieur", "Pièces → afficher / masquer les IfcSpace"),
    ("Plan de coupe → couper le bâtiment", "Coupe → couper le bâtiment à l'horizontale"),
    ("Visionneuse gratuite → BIMvision", "Visionneuse gratuite → celle du site"),
    ("BIMVISION – REPÈRES", "VISIONNEUSE – REPÈRES"),
    ("Plan de coupe → voir l'intérieur", "Coupe → voir l'intérieur"),
    ("Capture → outil de capture d'écran", "📷 Capture → image PNG de la vue"),
    ("villas Sabonnères", "villas Sabonnère"), ("villa Sabonnères", "villa Sabonnère"),
    ("Prise en main de BIMvision", "Prise en main de la visionneuse du site"),
    ("BIMvision + tableur + plans PDF", "Visionneuse du site + plans PDF"),
    ("BIMvision + 1 projet", "Visionneuse du site + 1 projet"),
    ("Lire la maquette du projet (BIMvision)", "Lire la maquette du projet (visionneuse du site)"),
    ("4 projets de l'agence (BIMvision)", "4 projets de l'agence (visionneuse du site)"),
    ("Poste prof : maquette .rvt + export .ifc + BIMvision", "Poste prof : maquette .rvt + export .ifc + visionneuse du site"),
    ("Ouvrir le dossier réseau du groupe : IFC + plans PDF", "Choisir le projet du groupe sur le site : maquette IFC + plans PDF"),
    ("Dossiers réseau EMNB_S03_G1 à G4 (IFC + PDF)", "Site de la classe : maquettes IFC + plans PDF des 4 projets"),
    ("Prise en main BIMvision", "Prise en main de la visionneuse"),
    ("Ouvrir l'IFC du projet dans BIMvision", "Ouvrir la maquette du projet dans la visionneuse du site"),
    ("BIMvision installé sur chaque poste", "Accès au site de la classe sur chaque poste"),
    ("Fiche méthode - LKBIM-SEQ03-FICHE_METHODE_BIMVISION.pdf", "Séance en ligne SEQ03 S2 - prise en main de la visionneuse"),
    ("Réaliser la capture dans BIMvision et l'annoter", "Réaliser la capture (bouton 📷 de la visionneuse) et l'annoter"),
    ("Montrer le regroupement des objets par classe dans BIMvision", "Montrer le regroupement des objets par classe (onglet Arborescence de la visionneuse)"),
    ("Reporter les résultats dans le tableur", "Saisir les résultats dans l'activité en ligne"),
    ("Reporter les valeurs avec leur unité dans le tableur", "Saisir les valeurs avec leur unité dans l'activité en ligne"),
    ("Aider les groupes à structurer le tableur", "Aider les groupes à structurer leurs relevés"),
    ("Tableur - LKBIM-SEQ03-S3-RELEVE_QUANTITES.xlsx", "Séance en ligne SEQ03 S3 - relevé des quantités"),
    ("Tableur de relevé", "Séance en ligne SEQ03 S3"),
    ("Outil de capture + annotation", "Bouton 📷 Capture de la visionneuse + annotation"),
    ("EMNB_S03_S4_Agence.ifc + plans PDF", "Maquette IFC de l'agence (site) + plans PDF"),
    ("dans BIMvision", "dans la visionneuse du site"),
    ("BIMvision", "la visionneuse du site"),
]

PARA = re.compile(r"(<(w:p|a:p|si)\b[^>]*>)(.*?)(</\2>)", re.S)
TXT = re.compile(r"(<(w:t|a:t|t)\b[^>]*>)(.*?)(</\2>)", re.S)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def unesc(s):
    return s.replace("&lt;", "<").replace("&gt;", ">").replace("&apos;", "'").replace("&quot;", '"').replace("&amp;", "&")


def traiter(xml, compteur):
    def para(m):
        corps = m.group(3)
        ts = list(TXT.finditer(corps))
        if not ts:
            return m.group(0)
        texte = "".join(unesc(t.group(3)) for t in ts)
        neuf = texte
        for a, b in R:
            neuf = neuf.replace(a, b)
        if neuf == texte:
            return m.group(0)
        compteur.append((texte[:70], neuf[:70]))
        cible = max(range(len(ts)), key=lambda i: len(ts[i].group(3).strip(" ▸✔→")))
        out, pos = [], 0
        for i, t in enumerate(ts):
            out.append(corps[pos:t.start()])
            ouvre = t.group(1)
            if i == cible and "xml:space" not in ouvre:
                ouvre = ouvre[:-1] + ' xml:space="preserve">'
            out.append(ouvre + (esc(neuf) if i == cible else "") + t.group(4))
            pos = t.end()
        out.append(corps[pos:])
        return m.group(1) + "".join(out) + m.group(4)
    return PARA.sub(para, xml)


src, dst = sys.argv[1], sys.argv[2]
n = []
with zipfile.ZipFile(src) as zi, zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zo:
    for it in zi.infolist():
        data = zi.read(it)
        if it.filename.endswith(".xml") and ("word/" in it.filename or "ppt/slides/" in it.filename or it.filename == "xl/sharedStrings.xml"):
            data = traiter(data.decode("utf-8"), n).encode("utf-8")
        zo.writestr(it, data)
for a, b in n:
    print(f"  {a!r} -> {b!r}")
print(f"{len(n)} paragraphes modifiés")
