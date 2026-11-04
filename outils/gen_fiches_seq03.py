"""Fiches synthèse SEQ03 (S1 à S3) au format des fiches de Kevin.
Gabarit : une fiche SEQ02 (en-tête, logo, filigrane, pied de page).
Usage : python gen_fiches_seq03.py gabarit.docx image_entete.jpg dossier_sortie"""
import copy, re, sys, subprocess, zipfile, shutil, os
from pathlib import Path
from docx import Document
from docx.oxml.ns import qn

GABARIT, IMAGE, SORTIE = sys.argv[1], sys.argv[2], Path(sys.argv[3])
SEQUENCE = " 03-LA MAQUETTE NUMERIQUE IFC"


def segs(txt):
    """'**gras** normal' -> [(texte, gras)]"""
    out = []
    for i, part in enumerate(re.split(r"\*\*", txt)):
        if part:
            out.append((part, i % 2 == 1))
    return out


def remplir(p, txt, base_run=None, gras_force=None, prefixe=None):
    runs = p.findall(qn("w:r"))
    modele = copy.deepcopy(base_run if base_run is not None else (runs[-1] if runs else None))
    for r in runs:
        p.remove(r)
    morceaux = (prefixe or []) + segs(txt)
    for texte, gras in morceaux:
        r = copy.deepcopy(modele)
        for t in r.findall(qn("w:t")):
            r.remove(t)
        rpr = r.find(qn("w:rPr"))
        if rpr is None:
            rpr = r.makeelement(qn("w:rPr"), {})
            r.insert(0, rpr)
        for tag in ("w:b", "w:bCs"):
            e = rpr.find(qn(tag))
            if e is not None:
                rpr.remove(e)
        if gras if gras_force is None else gras_force:
            rpr.append(rpr.makeelement(qn("w:b"), {}))
        t = r.makeelement(qn("w:t"), {})
        t.text = texte
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        r.append(t)
        p.append(r)


def paras(cell):
    return cell.findall(qn("w:p"))


def cellules(tr):
    return tr.findall(qn("w:tc"))


class Fiche:
    def __init__(self, seance):
        self.doc = Document(GABARIT)
        body = self.doc.element.body
        self.b = [copy.deepcopy(e) for e in body]
        self.sect = body[-1]
        for e in list(body)[:-1]:
            body.remove(e)
        self.body = body
        self.ajout(self.b[0])  # FICHE SYNTHESE
        for hdr in (s.header for s in self.doc.sections):
            for t in hdr._element.iter(qn("w:t")):
                if "02-LA LECTURE" in (t.text or ""):
                    t.text = SEQUENCE
                elif (t.text or "").startswith("S02-"):
                    t.text = seance

    def ajout(self, el):
        el = copy.deepcopy(el)
        self.sect.addprevious(el)
        return el

    def blanc(self):
        self.ajout(self.b[4])

    def section(self, n, titre):
        t = self.ajout(self.b[1])
        c = t.findall(".//" + qn("w:tc"))
        remplir(paras(c[0])[0], str(n), gras_force=True)
        remplir(paras(c[1])[0], "  " + titre, gras_force=True)

    def texte(self, txt):
        p = self.ajout(self.b[2])
        runs = p.findall(qn("w:r"))
        remplir(p, txt, base_run=runs[0])

    def _puces(self, cell, titre, puces, proto_titre, proto_puce, sym="▸"):
        for p in paras(cell):
            cell.remove(p)
        p = copy.deepcopy(proto_titre)
        remplir(p, titre, gras_force=True)
        cell.append(p)
        for txt in puces:
            p = copy.deepcopy(proto_puce)
            runs = p.findall(qn("w:r"))
            base = runs[-1]
            remplir(p, txt, base_run=base, prefixe=[("  " + sym + "  ", True)])
            cell.append(p)

    def deux(self, gauche, droite):
        """gauche/droite = (titre, [puces])"""
        t = self.ajout(self.b[7])
        c = t.findall(".//" + qn("w:tc"))
        for cell, (titre, puces) in zip(c, (gauche, droite)):
            ps = paras(cell)
            self._puces(cell, titre, puces, ps[0], ps[1])

    def trois(self, titre, sous, desc, droite_titre, droite):
        t = self.ajout(self.b[3])
        c = t.findall(".//" + qn("w:tc"))
        ps = paras(c[0])
        remplir(ps[0], titre, gras_force=True)
        remplir(ps[1], sous, base_run=ps[1].findall(qn("w:r"))[-1])
        remplir(ps[2], desc, base_run=ps[2].findall(qn("w:r"))[0])
        ps2 = paras(c[2])
        self._puces(c[2], droite_titre, droite, ps2[0], ps2[1])

    def tableau(self, entetes, lignes):
        t = self.ajout(self.b[11])
        trs = t.findall(qn("w:tr"))
        modele = copy.deepcopy(trs[1])
        for tr in trs[1:]:
            t.remove(tr)
        for c, txt in zip(cellules(trs[0]), entetes):
            remplir(paras(c)[0], txt)
        for ligne in lignes:
            tr = copy.deepcopy(modele)
            for c, txt in zip(cellules(tr), ligne):
                p = paras(c)[0]
                remplir(p, txt)
            t.append(tr)

    def retiens(self, puces, titre="💡  CE QUE JE RETIENS"):
        t = self.ajout(self.b[13])
        cell = t.findall(".//" + qn("w:tc"))[0]
        ps = paras(cell)
        for p in ps:
            cell.remove(p)
        p = copy.deepcopy(ps[0]); remplir(p, titre, gras_force=True); cell.append(p)
        for txt in puces:
            p = copy.deepcopy(ps[1])
            base = p.findall(qn("w:r"))[-1]
            remplir(p, txt, base_run=base, prefixe=[("▸  ", True)])
            cell.append(p)

    def enregistrer(self, nom):
        SORTIE.mkdir(parents=True, exist_ok=True)
        docx = SORTIE / f"{nom}.docx"
        self.doc.save(docx)
        # image d'en-tête : la maquette au lieu de la maison SEQ02
        tmp = docx.with_suffix(".tmp")
        with zipfile.ZipFile(docx) as zi, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zo:
            for it in zi.infolist():
                data = open(IMAGE, "rb").read() if it.filename == "word/media/image2.jpg" else zi.read(it)
                zo.writestr(it, data)
        shutil.move(tmp, docx)
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(SORTIE), str(docx)],
                       check=True, capture_output=True)
        return SORTIE / f"{nom}.pdf"


# ─────────────────────────── S1 ───────────────────────────
f = Fiche("S01-POURQUOI L'IFC ?")
f.section(1, "NATIF OU IFC — À QUOI ÇA SERT ?")
f.texte("L'agence conçoit ses projets sous **Revit** (fichier **natif** .rvt). Ses partenaires (économiste, bureau d'études, entreprise, client) n'ont pas tous ce logiciel : pour partager la maquette, on l'**exporte en IFC**.")
f.trois("🔒  NATIF = CONCEVOIR", ".rvt · lisible par Revit seulement", "Le fichier de travail de l'agence : on y modifie le projet.",
        "🌐 IFC = ÉCHANGER :",
        ["**Format ouvert** et normalisé (Industry Foundation Classes)",
         "Lisible avec une **visionneuse gratuite**, comme celle du site",
         "Partagé avec l'économiste, le BET, l'entreprise, le client",
         "On **consulte** l'IFC, on ne modifie pas le projet dedans"])
f.blanc()
f.section(2, "LES 3 NOTIONS D'UNE MAQUETTE IFC")
f.blanc()
f.tableau(["NOTION", "OÙ JE LA LIS", "CE QU'ELLE M'APPREND"], [
    ["1. La classe", "Inspecteur : IfcWall, IfcDoor, IfcSpace…", "Ce qu'est l'objet (un mur, une porte, une pièce…)"],
    ["2. L'arborescence", "Projet › Site › Bâtiment › Niveau › Élément", "Où se trouve l'objet (à quel niveau)"],
    ["3. Les propriétés", "Pset_… et quantités Qto / Cotes", "Ce qu'il contient : extérieur ? porteur ? longueur, surface, volume"],
])
f.blanc()
f.section(3, "LES CLASSES IFC À CONNAÎTRE")
f.blanc()
f.tableau(["CLASSE IFC", "OBJET", "REMARQUE"], [
    ["IfcWall", "Mur / cloison", "Porteur ou non : voir le Pset_WallCommon"],
    ["IfcSlab", "Dalle, plancher", "Épaisseur et surface dans les quantités"],
    ["IfcRoof", "Toiture", "Regroupe les pans de toit"],
    ["IfcDoor / IfcWindow", "Porte / fenêtre", "Se comptent dans l'arborescence"],
    ["IfcStair", "Escalier", "Relie deux niveaux"],
    ["IfcSpace", "Pièce (local)", "Porte le nom et la surface de la pièce"],
    ["IfcFooting", "Fondation (semelle)", "Niveau « Fondation », sous le RDC"],
    ["IfcFurnishingElement", "Mobilier", "N'est pas un ouvrage du bâtiment"],
])
f.blanc()
f.deux(("🖥  DANS LA VISIONNEUSE", ["**Clic** sur un objet → inspecteur (classe, chemin, propriétés)",
                                  "**Niveaux** : n'afficher que le RDC ou le R+1",
                                  "**Coupe** horizontale pour voir à l'intérieur",
                                  "**Pièces** : afficher / masquer les IfcSpace",
                                  "**📷 Capture** : image PNG de la vue"]),
       ("⚠  ATTENTION", ["L'IFC est une **copie** du projet à un instant donné",
                         "Une modification se fait dans le **natif**, puis on réexporte",
                         "La qualité de l'IFC dépend des **réglages d'export**",
                         "Une donnée bizarre ? On **vérifie** et on **signale**"]))
f.blanc()
f.retiens(["**IFC** → format **ouvert** pour **échanger** la maquette ; le natif (.rvt) sert à **concevoir**.",
           "**Classe** → ce qu'est l'objet (IfcWall = mur, IfcSpace = pièce…).",
           "**Arborescence** → où il est : Projet › Site › Bâtiment › Niveau › Élément.",
           "**Propriétés** → ce qu'il contient : Pset (extérieur, porteur) et quantités (m, m², m³).",
           "Une maquette IFC est une **base de données** : on l'interroge, on ne la redessine pas."])
p1 = f.enregistrer("seq03-s1")

# ─────────────────────────── S2 ───────────────────────────
f = Fiche("S02-LIRE LA MAQUETTE")
f.section(1, "LA MÉTHODE DU TICKET")
f.texte("À la cellule **BIM Desk**, chaque demande d'un partenaire arrive sous forme de **ticket**. Pour y répondre, on suit toujours la même méthode : **demande → donnée → recherche → source**.")
f.trois("🎫  UN TICKET", "= une question d'un partenaire", "Économiste, bureau d'études, conducteur de travaux, client…",
        "Je réponds toujours en 4 étapes :",
        ["**1. Demande** : je reformule ce qu'on me demande",
         "**2. Donnée** : quelle information précise me faut-il ?",
         "**3. Recherche** : où la trouver dans la maquette ?",
         "**4. Source** : je note où je l'ai trouvée"])
f.blanc()
f.section(2, "OÙ TROUVER UNE INFORMATION ?")
f.blanc()
f.tableau(["JE CHERCHE…", "JE REGARDE…", "EXEMPLE"], [
    ["Ce qu'est un objet", "Sa classe", "IfcDoor = une porte"],
    ["Où il se trouve", "L'arborescence (niveau)", "Projet › … › RDC › Porte"],
    ["Ses dimensions types", "Le nom du type", "PP (0.83m x 2.04m) = porte de 0,83 × 2,04 m"],
    ["De quoi il est fait", "Ses matériaux (une propriété)", "Enduit monocouche + Brique"],
    ["S'il est extérieur ou porteur", "Le Pset (Pset_WallCommon…)", "IsExternal = Oui"],
    ["Une longueur, une surface, un volume", "Les quantités (Qto / Cotes)", "Surface = 40,27 m²"],
    ["Une info absente de la maquette", "Les plans PDF", "Une cote, une note, le cartouche"],
])
f.blanc()
f.section(3, "EXEMPLE DE TICKET TRAITÉ")
f.blanc()
f.tableau(["ÉTAPE", "QUESTION À SE POSER", "EXEMPLE — VILLA SABONNÈRE"], [
    ["1. Demande", "Qu'est-ce qu'on me demande ?", "« Quelle est la surface du séjour ? »"],
    ["2. Donnée", "Quel objet, quelle propriété ?", "La surface d'une pièce (IfcSpace)"],
    ["3. Recherche", "Où cliquer dans la maquette ?", "RDC › IfcSpace « SEJOUR » › Cotes › Surface"],
    ["4. Source", "D'où vient ma réponse ?", "40,27 m² — maquette IFC (Cotes)"],
])
f.blanc()
f.deux(("⚠  TICKET VIGILANCE", ["Pièce **sans nom** (toutes appelées « Surface »)",
                              "**IsExternal = Oui** sur une cloison intérieure",
                              "**WC de 15 m²**, autant qu'un bureau",
                              "**Aucune fenêtre** (façade en mur-rideau)"]),
       ("✅  JE RÉAGIS", ["Je ne recopie pas **sans réfléchir**",
                         "Je **compare** avec le plan PDF",
                         "Je **signale** l'anomalie au chef de projet",
                         "Je note toujours ma **source**"]))
f.blanc()
f.retiens(["**Ticket** → une demande d'un partenaire, traitée avec la même méthode à chaque fois.",
           "**Méthode** → demande → donnée nécessaire → recherche → source.",
           "**Classe** = quoi · **arborescence** = où · **type** = dimensions · **Pset / matériaux** = caractéristiques · **quantités** = combien.",
           "**Plans PDF** → pour ce que la maquette ne dit pas (cotes, notes, cartouche).",
           "**Vigilance** → une maquette peut contenir des erreurs : je vérifie et je signale."])
p2 = f.enregistrer("seq03-s2")

# ─────────────────────────── S3 ───────────────────────────
f = Fiche("S03-REPONDRE A L'ECONOMISTE")
f.section(1, "RÉPONSE NUMÉRIQUE OU GRAPHIQUE ?")
f.texte("L'**économiste** a besoin de **quantités**. Le **conducteur de travaux** a besoin de **voir** où se trouvent les choses. Une même maquette, **deux façons de répondre**.")
f.deux(("🔢  RÉPONSE NUMÉRIQUE", ["Un **nombre** ou un **tableau** + l'**unité**",
                               "Pour **compter, mesurer, comparer**",
                               "Ex. : 11 fenêtres · séjour 40,27 m²",
                               "Ex. : épaisseur du dallage 0,12 m",
                               "Demandeur type : l'**économiste**"]),
       ("📷  RÉPONSE GRAPHIQUE", ["Une **capture annotée** de la maquette",
                                "Vue 3D, coupe, objet sélectionné, repères",
                                "Pour **voir, localiser, comprendre**",
                                "Ex. : où est l'escalier ? le mur porteur ?",
                                "Demandeur type : le **conducteur de travaux**"]))
f.blanc()
f.section(2, "LES UNITÉS")
f.blanc()
f.tableau(["GRANDEUR", "UNITÉ", "DANS LA MAQUETTE"], [
    ["Longueur, épaisseur, hauteur", "m", "Longueur, Épaisseur, Hauteur"],
    ["Surface", "m²", "Surface, NetFloorArea"],
    ["Volume", "m³", "Volume, NetVolume"],
    ["Nombre d'objets", "u (unités)", "Comptage dans l'arborescence"],
])
f.texte("📌 Sur les plans, les cotes sont souvent en **cm** ou en **mm** : 3 500 mm = 350 cm = **3,50 m**. Je convertis toujours avant de comparer.")
f.blanc()
f.section(3, "TRAITER UN TICKET QUANTITATIF")
f.trois("🧮  ADDITIONNER", "ex. : surface des pièces du RDC", "Somme des IfcSpace du niveau, au centième près.",
        "Avant de répondre, je vérifie :",
        ["Le **bon niveau** (RDC ou R+1)",
         "Le **bon objet** (la pièce IfcSpace, pas la dalle)",
         "L'**unité** et l'**arrondi** (2 chiffres après la virgule)",
         "La **cohérence** : un WC n'a pas la surface d'un bureau"])
f.blanc()
f.section(4, "PLAN OU MAQUETTE : POURQUOI DES ÉCARTS ?")
f.blanc()
f.tableau(["CAUSE", "EXPLICATION", "CE QUE JE FAIS"], [
    ["Brut ou net", "Dalle = sous les murs ; pièce = entre les murs", "Je précise de quelle surface je parle"],
    ["Arrondis", "40,27 m² dans la maquette, 40,3 m² sur un tableau", "J'indique la précision utilisée"],
    ["Plan pas à jour", "Maquette modifiée après l'édition du plan", "Je compare les dates, je signale"],
    ["Erreur d'export", "Propriété mal renseignée dans l'IFC", "Je vérifie sur le plan, je signale"],
])
f.blanc()
f.retiens(["**Voir, localiser, comprendre** → réponse **graphique** (capture annotée).",
           "**Compter, mesurer, comparer** → réponse **numérique** (valeur + unité).",
           "**Unités** de la maquette : m, m², m³ et u. Je convertis les cotes des plans.",
           "**Écart** plan / maquette → brut ou net, arrondi, plan pas à jour, erreur d'export.",
           "Je note toujours la **valeur ET sa source**. La bonne forme dépend du **demandeur**."])
p3 = f.enregistrer("seq03-s3")
print(p1, p2, p3)
