"""Passe les textes du site du tutoiement au vouvoiement, et met les titres d'exercices à l'infinitif.
convertir(texte, titre=False) : vouvoiement ; si titre=True, le verbe d'action en tête de titre passe à l'infinitif.
Usage : python vouvoyer.py fichier... (JSON, HTML, JS, PY : seuls les textes sont modifiés)."""
import json, re, sys
from pathlib import Path

W = r"A-Za-zÀ-ÖØ-öø-ÿŒœ"
# impératif 2e sing. -> (impératif 2e plur., infinitif)
IMP = {
 "Analyse": ("Analysez", "Analyser"), "Annote": ("Annotez", "Annoter"), "Arrondis": ("Arrondissez", "Arrondir"),
 "Associe": ("Associez", "Associer"), "Calcule": ("Calculez", "Calculer"), "Cherche": ("Cherchez", "Chercher"),
 "Choisis": ("Choisissez", "Choisir"), "Cite": ("Citez", "Citer"), "Clique": ("Cliquez", "Cliquer"), "Coche": ("Cochez", "Cocher"),
 "Compare": ("Comparez", "Comparer"), "Complète": ("Complétez", "Compléter"), "Consulte": ("Consultez", "Consulter"),
 "Construis": ("Construisez", "Construire"), "Convertis": ("Convertissez", "Convertir"), "Découvre": ("Découvrez", "Découvrir"),
 "Déplace": ("Déplacez", "Déplacer"), "Descends": ("Descendez", "Descendre"), "Développe": ("Développez", "Développer"),
 "Distingue": ("Distinguez", "Distinguer"), "Définis": ("Définissez", "Définir"), "Envoie": ("Envoyez", "Envoyer"),
 "Essaie": ("Essayez", "Essayer"), "Examine": ("Examinez", "Examiner"), "Explique": ("Expliquez", "Expliquer"),
 "Explore": ("Explorez", "Explorer"), "Fais": ("Faites", "Faire"), "Identifie": ("Identifiez", "Identifier"),
 "Indique": ("Indiquez", "Indiquer"), "Joue": ("Jouez", "Jouer"), "Justifie": ("Justifiez", "Justifier"), "Lis": ("Lisez", "Lire"),
 "Localise": ("Localisez", "Localiser"), "Mets": ("Mettez", "Mettre"), "Nomme": ("Nommez", "Nommer"), "Observe": ("Observez", "Observer"),
 "Ordonne": ("Ordonnez", "Ordonner"), "Ouvre": ("Ouvrez", "Ouvrir"), "Prépare": ("Préparez", "Préparer"), "Présente": ("Présentez", "Présenter"),
 "Propose": ("Proposez", "Proposer"), "Recopie": ("Recopiez", "Recopier"), "Regarde": ("Regardez", "Regarder"), "Relis": ("Relisez", "Relire"),
 "Relève": ("Relevez", "Relever"), "Remets": ("Remettez", "Remettre"), "Repère": ("Repérez", "Repérer"), "Retrouve": ("Retrouvez", "Retrouver"),
 "Rédige": ("Rédigez", "Rédiger"), "Réponds": ("Répondez", "Répondre"), "Saisis": ("Saisissez", "Saisir"), "Signale": ("Signalez", "Signaler"),
 "Sélectionne": ("Sélectionnez", "Sélectionner"), "Télécharge": ("Téléchargez", "Télécharger"), "Traduis": ("Traduisez", "Traduire"),
 "Transmets": ("Transmettez", "Transmettre"), "Travaille": ("Travaillez", "Travailler"), "Trie": ("Triez", "Trier"), "Trouve": ("Trouvez", "Trouver"),
 "Utilise": ("Utilisez", "Utiliser"), "Valide": ("Validez", "Valider"), "Vérifie": ("Vérifiez", "Vérifier"), "Écoute": ("Écoutez", "Écouter"),
 "Écris": ("Écrivez", "Écrire"), "Rouvre": ("Rouvrez", "Rouvrir"), "Recharge": ("Rechargez", "Recharger"), "Tourne": ("Tournez", "Tourner"),
 "Prends": ("Prenez", "Prendre"), "Va": ("Allez", "Aller"), "Reviens": ("Revenez", "Revenir"), "Commence": ("Commencez", "Commencer"),
 "Imagine": ("Imaginez", "Imaginer"), "Remplis": ("Remplissez", "Remplir"), "Relie": ("Reliez", "Relier"), "Corrige": ("Corrigez", "Corriger"),
 "Termine": ("Terminez", "Terminer"), "Continue": ("Continuez", "Continuer"), "Montre": ("Montrez", "Montrer"), "Garde": ("Gardez", "Garder"),
 "Note": ("Notez", "Noter"), "Place": ("Placez", "Placer"), "Classe": ("Classez", "Classer"), "Compte": ("Comptez", "Compter"),
 "Range": ("Rangez", "Ranger"), "Active": ("Activez", "Activer"), "Affiche": ("Affichez", "Afficher"), "Masque": ("Masquez", "Masquer"),
 "Pose": ("Posez", "Poser"), "Projette": ("Projetez", "Projeter"), "Glisse": ("Glissez", "Glisser"), "Survole": ("Survolez", "Survoler"),
 "Efface": ("Effacez", "Effacer"), "Recommence": ("Recommencez", "Recommencer"), "Ajoute": ("Ajoutez", "Ajouter"), "Change": ("Changez", "Changer"),
 "Décris": ("Décrivez", "Décrire"), "Résume": ("Résumez", "Résumer"), "Réfléchis": ("Réfléchissez", "Réfléchir"), "Pense": ("Pensez", "Penser"),
 "Retiens": ("Retenez", "Retenir"), "Demande": ("Demandez", "Demander"), "Imprime": ("Imprimez", "Imprimer"), "Zoome": ("Zoomez", "Zoomer"),
 "Agrandis": ("Agrandissez", "Agrandir"), "Tape": ("Tapez", "Taper"), "Entoure": ("Entourez", "Entourer"), "Souligne": ("Soulignez", "Souligner"),
 "Rejoue": ("Rejouez", "Rejouer"), "Passe": ("Passez", "Passer"), "Lance": ("Lancez", "Lancer"), "Accède": ("Accédez", "Accéder"),
 "Enregistre": ("Enregistrez", "Enregistrer"), "Sois": ("Soyez", "Être"), "Aide": ("Aidez", "Aider"), "Écoute-la": ("Écoutez-la", "L'écouter"),
}
# mots ambigus (noms communs) : impératif seulement s'ils sont suivis d'un complément typique
AMBIGUS = {"Note", "Place", "Classe", "Compte", "Range", "Active", "Affiche", "Masque", "Pose", "Montre", "Garde", "Passe", "Change",
           "Lance", "Aide", "Va", "Tape", "Trie", "Termine", "Demande", "Continue", "Cite", "Coche", "Commence", "Explore", "Propose"}
COMPL = r"(?:le|la|les|l['’]|un|une|des|du|chaque|ton|ta|tes|ce|cet|cette|ces|sur|ici|dans|tous|toutes|tout|bien|d['’]abord|à|au|aux|en|y|-la|-le|-les|-moi|-toi|ensemble|deux|trois|quatre|cinq|ses|son|sa)\b"
DEBUT = r"(?:(?<=^)|(?<=[.!?:;«\"(—–·>\n]\s)|(?<=[.!?:;«\"(—–·>\n])|(?<=\bpuis\s)|(?<=,\s)|(?<=\bet\s)|(?<=\bou\s)|(?<=\bensuite\s)|(?<=\balors\s)|(?<=\bsinon\s)|(?<=\bpuis,\s))"

# « tu + verbe » et inversions
TU_V = {"as": "avez", "es": "êtes", "vas": "allez", "peux": "pouvez", "dois": "devez", "veux": "voulez", "sais": "savez", "fais": "faites",
        "dis": "dites", "lis": "lisez", "réponds": "répondez", "viens": "venez", "rejoins": "rejoignez", "construis": "construisez",
        "connais": "connaissez", "reçois": "recevez", "obtiens": "obtenez", "prends": "prenez", "mets": "mettez", "vois": "voyez", "crois": "croyez",
        "choisis": "choisissez", "finis": "finissez", "reconnais": "reconnaissez", "apprends": "apprenez", "intègres": "intégrez", "avais": "aviez",
        "étais": "étiez", "pourras": "pourrez", "auras": "aurez", "seras": "serez", "iras": "irez", "sauras": "saurez", "devras": "devrez",
        "relèves": "relevez", "complètes": "complétez", "repères": "repérez", "maîtrises": "maîtrisez", "découvres": "découvrez", "ouvres": "ouvrez",
        "transmets": "transmettez", "remets": "remettez", "écris": "écrivez", "décris": "décrivez", "pars": "partez", "sors": "sortez",
        "pourrais": "pourriez", "aimerais": "aimeriez", "voudrais": "voudriez", "serais": "seriez", "aurais": "auriez", "ferais": "feriez",
        "vérifies": "vérifiez", "envoies": "envoyez", "paies": "payez", "essaies": "essayez", "te": "vous"}


def conj(v):
    """2e pers. sing. -> 2e pers. plur. (présent, imparfait, futur, conditionnel)."""
    if v in TU_V: return TU_V[v]
    if v.endswith("ras"): return v[:-1] + "ez"
    if v.endswith("rais"): return v[:-4] + "riez"
    if v.endswith("ais") and len(v) > 4: return v[:-3] + "iez"
    if v.endswith("es"): return v[:-2] + "ez"
    if v.endswith("is"): return v[:-1] + "ssez"
    return v


def _imp(m, titre):
    w, suite = m.group(1), m.group(2) or ""
    base = w[0].upper() + w[1:]
    if base not in IMP: return m.group(0)
    pl, inf = IMP[base]
    if titre:
        r = inf
        suite = {"-la": "", "-le": "", "-les": "", "-toi": ""}.get(suite, suite)
    else:
        r = pl
    if w[0].islower(): r = r[0].lower() + r[1:]
    return r + suite


def convertir(t, titre=False):
    if not isinstance(t, str) or not re.search(r"\b(?:[Tt]u|[Tt]e|[Tt]oi|[Tt]on|[Tt]a|[Tt]es|t['’])\b|[" + W + r"]", t):
        return t
    # impératifs (en début de phrase / après « puis », « , », « et »…)
    noms = "|".join(sorted((re.escape(k) for k in IMP), key=len, reverse=True))
    noms_min = "|".join(sorted((re.escape(k[0].lower() + k[1:]) for k in IMP), key=len, reverse=True))
    pat = re.compile(DEBUT + r"(" + noms + "|" + noms_min + r")(-la|-le|-les|-moi|-toi|-y|-en|-lui)?(?![" + W + r"-])")

    def rep(m):
        w = m.group(1); base = w[0].upper() + w[1:]
        if base in AMBIGUS and not m.group(2):
            after = t[m.end():]
            if not re.match(r"\s+" + COMPL, after): return m.group(0)
        return _imp(m, titre)
    t = pat.sub(rep, t)
    # infinitif : supprimer les possessifs « ton/ta/tes » après un verbe à l'infinitif en titre -> votre/vos (fait plus bas)
    # pronoms réfléchis à l'impératif
    t = re.sub(r"-toi\b", "-vous", t)
    # inversions : as-tu, fais-tu, présentes-tu…
    t = re.sub(r"\b([" + W + r"]+)-t-il\b", r"\1-t-il", t)
    t = re.sub(r"\b([" + W + r"]+)-tu\b", lambda m: conj(m.group(1)) + "-vous", t)
    # ne te / te / t'
    t = re.sub(r"\b([Nn]e) te (\w+) pas\b", lambda m: f"{m.group(1)} vous {conj(m.group(2)) if m.group(2) != 'trompe' else 'trompez'} pas", t)
    t = re.sub(r"\btu te ([" + W + r"]+)", lambda m: "vous vous " + conj(m.group(1)), t)
    t = re.sub(r"\bTu te ([" + W + r"]+)", lambda m: "Vous vous " + conj(m.group(1)), t)
    # tu + (ne/n') + (pronoms) + verbe
    def tu_verbe(m):
        su, neg, pro, v = m.group(1), m.group(2) or "", m.group(3) or "", m.group(4)
        return ("Vous" if su == "Tu" else "vous") + " " + neg + pro + conj(v)
    t = re.sub(r"\b(Tu|tu) (ne |n['’])?((?:l['’]|le |la |les |en |y |lui |leur )*)([" + W + r"]+)", tu_verbe, t)
    t = re.sub(r"\b([Tt])['’](?=[aeiouyéèêàâhAEIOUÉ])", lambda m: "Vous " if m.group(1) == "T" else "vous ", t)
    t = re.sub(r"\b[Tt]e(?= (?:[" + W + r"]))", lambda m: "Vous" if m.group(0) == "Te" else "vous", t)
    t = re.sub(r"\btoi\b", "vous", t); t = re.sub(r"\bToi\b", "Vous", t)
    t = re.sub(r"\btoi-même\b", "vous-même", t)
    # possessifs
    t = re.sub(r"\bton\b", "votre", t); t = re.sub(r"\bTon\b", "Votre", t)
    t = re.sub(r"\bta\b", "votre", t); t = re.sub(r"\bTa\b", "Votre", t)
    t = re.sub(r"\btes\b", "vos", t); t = re.sub(r"\bTes\b", "Vos", t)
    t = re.sub(r"\btien(ne)?s?\b", "vôtre", t)
    return t


# ---------- application aux fichiers ----------
NE_PAS = {"id", "type", "src", "fichier", "pour", "critere", "reponse", "accepte", "valeur", "unite", "r", "projet", "ifc", "glb", "verbe",
          "cle", "href", "slug", "icone", "image", "plan", "code"}


def walk(o, cle=None):
    if isinstance(o, dict):
        return {k: (v if k in NE_PAS else walk(v, k)) for k, v in o.items()}
    if isinstance(o, list):
        return [walk(v, cle) for v in o]
    if isinstance(o, str):
        if cle in ("html",) or "<" in o:
            return html(o)
        return convertir(o, titre=(cle == "titre"))
    return o


def html(s):
    # textes hors balises + attributs placeholder/title/aria-label/alt
    s = re.sub(r'((?:placeholder|title|aria-label|alt)=")([^"]*)(")', lambda m: m.group(1) + convertir(m.group(2)) + m.group(3), s)
    parts = re.split(r"(<script[\s\S]*?</script>|<style[\s\S]*?</style>|<[^>]+>)", s)
    out = []
    for p in parts:
        if p.startswith("<script"): out.append(litteraux(p))
        elif p.startswith("<"): out.append(p)
        else: out.append(convertir(p))
    return "".join(out)


def litteraux(code, py=False):
    """Convertit uniquement le contenu des chaînes "…", '…' et `…` (code JS/Python). Les commentaires sont laissés tels quels."""
    pat = (r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|#[^\n]*|' if py else r'//[^\n]*|/\*[\s\S]*?\*/|') + \
          r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'|`(?:\\.|[^`\\])*`'

    def f(m):
        s = m.group(0)
        if s.startswith(("//", "/*", "#")): return s
        q = 3 if s[:3] in ('"""', "\'\'\'") else 1
        c = s[q:-q]
        if not re.search(r"[A-Za-zÀ-ÿ]{2,} [A-Za-zÀ-ÿ]", c): return s  # identifiants, clés, classes CSS : ignorés
        c = html(c) if ("<" in c and ">" in c) else convertir(c)
        return s[:q] + c + s[-q:]
    return re.sub(pat, f, code)


if __name__ == "__main__":
    for nom in sys.argv[1:]:
        p = Path(nom); s = p.read_text(encoding="utf-8")
        if p.suffix == ".json":
            n = json.dumps(walk(json.loads(s)), ensure_ascii=False, indent=1) + "\n"
        elif p.suffix == ".html":
            n = html(s)
        else:
            n = litteraux(s, py=p.suffix == ".py")
        if n != s:
            p.write_text(n, encoding="utf-8"); print("✔", nom)


# ---------- titres : verbe d'action à l'infinitif ----------
PL_INF = {v[0]: v[1] for v in IMP.values()}
SG_INF = {k: v[1] for k, v in IMP.items()}


def titre_infinitif(t):
    """« Exercice 1 — Associez chaque… » / « 3. Relève… » -> « … Associer chaque… ». Possessifs : votre/vos conservés."""
    def r(m):
        w, suite = m.group(2), m.group(3) or ""
        base = w[0].upper() + w[1:]
        inf = PL_INF.get(base)
        if not inf: return m.group(0)
        if w[0].islower(): inf = inf[0].lower() + inf[1:]
        if suite in ("-la", "-le", "-les"): inf = {"-la": "la ", "-le": "le ", "-les": "les "}[suite] + inf; suite = ""
        if suite in ("-vous", "-toi"): inf = "vous " + inf; suite = ""
        return m.group(1) + inf + suite
    return re.sub(r"(^|— |– |· |\d+\. |: |\| )([" + W + r"]+)(-la|-le|-les|-vous|-toi)?(?![" + W + r"-])", r, t)
