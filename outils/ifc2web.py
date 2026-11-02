"""Convertit une maquette IFC en deux fichiers légers pour la visionneuse du site :
  <nom>.glb  : géométrie, un nœud par élément (nommé par son GlobalId)
  <nom>.json : arborescence, classes, niveaux, propriétés et quantités (en m, m², m³)
Usage : python ifc2web.py fichier.ifc dossier_sortie nom_court "Titre du projet"
"""
import sys, json, math, collections
import numpy as np, trimesh
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.element as UE, ifcopenshell.util.unit as UU

src, out, nom, titre = sys.argv[1:5]
m = ifcopenshell.open(src)
LS = UU.calculate_unit_scale(m)          # facteur vers le mètre
SCALE = {"IfcLengthMeasure": LS, "IfcPositiveLengthMeasure": LS, "IfcAreaMeasure": LS ** 2, "IfcVolumeMeasure": LS ** 3}
UNITE = {"IfcLengthMeasure": "m", "IfcPositiveLengthMeasure": "m", "IfcAreaMeasure": "m²", "IfcVolumeMeasure": "m³",
         "IfcThermalTransmittanceMeasure": "W/m².K", "IfcPlaneAngleMeasure": "°", "IfcCountMeasure": ""}
GARDER = ("Pset_", "BaseQuantities", "Cotes", "Matériaux et finitions", "Données d'identification", "Construction", "Dimensions", "Texte", "Identity Data", "Qto_")
IGNORER_PROP = {"id", "Reference", "IfcGUID", "Type IfcGUID", "ExtendToStructure"}
IGNORER_CLS = {"IfcOpeningElement", "IfcAnnotation", "IfcGrid", "IfcSite"}

COULEURS = {"IfcWall": (0.86, 0.84, 0.78, 1), "IfcSlab": (0.70, 0.72, 0.74, 1), "IfcRoof": (0.75, 0.33, 0.20, 1), "IfcDoor": (0.62, 0.45, 0.28, 1),
            "IfcWindow": (0.55, 0.78, 0.92, 0.55), "IfcStair": (0.78, 0.63, 0.40, 1), "IfcFooting": (0.55, 0.55, 0.55, 1), "IfcColumn": (0.60, 0.62, 0.66, 1),
            "IfcBeam": (0.60, 0.62, 0.66, 1), "IfcMember": (0.80, 0.66, 0.45, 1), "IfcPlate": (0.75, 0.75, 0.70, 1), "IfcCovering": (0.90, 0.88, 0.82, 1),
            "IfcCurtainWall": (0.55, 0.78, 0.92, 0.5), "IfcRailing": (0.4, 0.4, 0.42, 1), "IfcFurnishingElement": (0.85, 0.80, 0.70, 1),
            "IfcFlowTerminal": (0.95, 0.95, 0.95, 1), "IfcSpace": (0.30, 0.55, 0.95, 0.18), "IfcBuildingElementProxy": (0.7, 0.7, 0.7, 1)}
FAMILLE = {"IfcWallStandardCase": "IfcWall", "IfcSlabStandardCase": "IfcSlab", "IfcDoorStandardCase": "IfcDoor", "IfcWindowStandardCase": "IfcWindow",
           "IfcBeamStandardCase": "IfcBeam", "IfcColumnStandardCase": "IfcColumn", "IfcStairFlight": "IfcStair"}


def val(nv):
    if nv is None: return None
    t = nv.is_a(); v = nv.wrappedValue
    if isinstance(v, bool) or t == "IfcBoolean": return bool(v)
    if t == "IfcLogical": return {True: True, False: False}.get(v, None)
    if isinstance(v, (int, float)):
        v = v * SCALE.get(t, 1)
        v = round(v, 3) if abs(v) < 1000 else round(v, 1)
        u = UNITE.get(t)
        return [v, u] if u else v
    s = str(v).strip()
    return s or None


def proprietes(el):
    res = {}
    for rel in getattr(el, "IsDefinedBy", []) or []:
        if not rel.is_a("IfcRelDefinesByProperties"): continue
        d = rel.RelatingPropertyDefinition
        if not d.Name or not d.Name.startswith(GARDER): continue
        bloc = {}
        if d.is_a("IfcPropertySet"):
            for p in d.HasProperties:
                if p.is_a("IfcPropertySingleValue") and p.Name not in IGNORER_PROP:
                    v = val(p.NominalValue)
                    if v is not None: bloc[p.Name] = v
        elif d.is_a("IfcElementQuantity"):
            for q in d.Quantities:
                for attr, t in (("LengthValue", "IfcLengthMeasure"), ("AreaValue", "IfcAreaMeasure"), ("VolumeValue", "IfcVolumeMeasure"), ("CountValue", "IfcCountMeasure")):
                    if hasattr(q, attr) and getattr(q, attr) is not None:
                        x = getattr(q, attr) * SCALE.get(t, 1)
                        bloc[q.Name] = [round(x, 3), UNITE[t]] if UNITE[t] else round(x, 3)
        if bloc: res.setdefault(d.Name, {}).update(bloc)
    # matériau
    mats = []
    for r in getattr(el, "HasAssociations", []) or []:
        if r.is_a("IfcRelAssociatesMaterial"):
            mm = r.RelatingMaterial
            if mm.is_a("IfcMaterial"): mats.append(mm.Name)
            elif mm.is_a("IfcMaterialLayerSetUsage"): mats += [l.Material.Name for l in mm.ForLayerSet.MaterialLayers if l.Material]
            elif mm.is_a("IfcMaterialLayerSet"): mats += [l.Material.Name for l in mm.MaterialLayers if l.Material]
            elif mm.is_a("IfcMaterialList"): mats += [x.Name for x in mm.Materials]
    if mats: res["Matériaux"] = {"Matériau(x)": " + ".join(dict.fromkeys(mats))}
    return res


def niveau(el):
    c = UE.get_container(el)
    if c is None and el.is_a("IfcSpace"):
        for r in el.Decomposes or []: c = r.RelatingObject
    while c is not None and not c.is_a("IfcBuildingStorey"):
        p = UE.get_aggregate(c) or UE.get_container(c); c = p
    return c


# ---- géométrie
st = ifcopenshell.geom.settings(); st.set(st.USE_WORLD_COORDS, True)
scene = trimesh.Scene(); elements = []; vus = set()
it = ifcopenshell.geom.iterator(st, m, include=[e for e in m.by_type("IfcProduct") if e.is_a() not in IGNORER_CLS and (e.is_a("IfcElement") or e.is_a("IfcSpace"))])
if it.initialize():
    while True:
        sh = it.get(); el = m.by_guid(sh.guid)
        v = np.array(sh.geometry.verts).reshape(-1, 3); f = np.array(sh.geometry.faces).reshape(-1, 3)
        if len(f):
            v = v[:, [0, 2, 1]] * np.array([1, 1, -1])   # IFC (Z haut) -> glTF (Y haut)
            cls = FAMILLE.get(el.is_a(), el.is_a()); fam = cls if cls in COULEURS else next((k for k in COULEURS if el.is_a(k)), "IfcBuildingElementProxy")
            col = (np.array(COULEURS.get(fam)) * 255).astype(np.uint8)
            mesh = trimesh.Trimesh(vertices=v, faces=f, process=False)
            mesh.visual = trimesh.visual.ColorVisuals(mesh, face_colors=np.tile(col, (len(f), 1)))
            scene.add_geometry(mesh, node_name=sh.guid, geom_name=sh.guid)
            vus.add(sh.guid)
        if not it.next(): break

# ---- données
projet = m.by_type("IfcProject")[0]
niveaux = sorted(m.by_type("IfcBuildingStorey"), key=lambda s: float(s.Elevation or 0))
for el in m.by_type("IfcProduct"):
    if el.GlobalId not in vus: continue
    cls = FAMILLE.get(el.is_a(), el.is_a())
    s = niveau(el)
    typ = UE.get_type(el)
    parent = UE.get_aggregate(el)
    if parent is not None and parent.is_a() in ("IfcRoof", "IfcStair"):
        cls = parent.is_a()
    e = {"id": el.GlobalId, "cls": cls, "ifc": el.is_a(), "nom": (el.LongName if el.is_a("IfcSpace") and el.LongName else el.Name) or "",
         "type": typ.Name if typ else "", "niveau": s.Name if s else "", "props": proprietes(el)}
    if el.is_a("IfcSpace"): e["numero"] = el.Name or ""
    if parent is not None and parent.is_a() in ("IfcRoof", "IfcStair", "IfcCurtainWall"): e["partie_de"] = parent.is_a()
    elements.append(e)

data = {"projet": titre, "fichier": src.split("/")[-1], "schema": m.schema,
        "arbo": {"Projet": projet.Name or titre, "Site": (m.by_type("IfcSite")[0].Name if m.by_type("IfcSite") else "") or "Site",
                 "Bâtiment": (m.by_type("IfcBuilding")[0].Name if m.by_type("IfcBuilding") else "") or "Bâtiment"},
        "niveaux": [{"nom": s.Name, "altitude": round(float(s.Elevation or 0) * LS, 2)} for s in niveaux],
        "elements": elements}
scene.export(f"{out}/{nom}.glb")
json.dump(data, open(f"{out}/{nom}.json", "w"), ensure_ascii=False, separators=(",", ":"))
c = collections.Counter(e["cls"] for e in elements)
print(nom, len(elements), "éléments", dict(c.most_common(8)))
