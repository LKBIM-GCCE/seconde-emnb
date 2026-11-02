/* Visionneuse IFC — Seconde EMNB
   Charge media/maquettes/<id>.glb (géométrie) + <id>.json (données IFC converties).
   Utilisation : <div class="visionneuse" data-maquettes="villa-sabonnere,villa-goyrans" data-base="../"></div> */
(function () {
  const CLS_FR = {
    IfcWall: "Mur", IfcSlab: "Dalle / plancher", IfcRoof: "Toiture", IfcDoor: "Porte", IfcWindow: "Fenêtre", IfcStair: "Escalier",
    IfcFooting: "Fondation", IfcColumn: "Poteau", IfcBeam: "Poutre", IfcMember: "Élément de charpente", IfcPlate: "Plaque / panneau",
    IfcCovering: "Revêtement", IfcCurtainWall: "Mur-rideau", IfcRailing: "Garde-corps", IfcFurnishingElement: "Mobilier",
    IfcFlowTerminal: "Équipement sanitaire", IfcSpace: "Pièce (espace)", IfcBuildingElementProxy: "Autre objet", IfcStairFlight: "Volée d'escalier"
  };
  const PROP_FR = {
    IsExternal: "Élément extérieur ?", LoadBearing: "Élément porteur ?", ThermalTransmittance: "Coefficient U", FireRating: "Résistance au feu",
    NominalHeight: "Hauteur", NominalLength: "Longueur", NominalWidth: "Épaisseur", Width: "Épaisseur", Length: "Longueur", Height: "Hauteur",
    GrossFloorArea: "Surface brute au sol", NetFloorArea: "Surface nette au sol", GrossPerimeter: "Périmètre", GrossArea: "Surface brute", NetArea: "Surface nette",
    GrossVolume: "Volume brut", NetVolume: "Volume net", NetSideArea: "Surface nette (face)", GrossSideArea: "Surface brute (face)", GrossFootprintArea: "Emprise au sol",
    Perimeter: "Périmètre", PitchAngle: "Pente", GrossCeilingArea: "Surface de plafond", "Matériau(x)": "Matériau(x)"
  };
  const GROUPE_FR = { BaseQuantities: "Quantités de base (Qto)", Cotes: "Cotes", Matériaux: "Matériaux", "Données d'identification": "Identification" };
  const COULEUR = { IfcWall: 0xe4ddcc, IfcSlab: 0xb8bec6, IfcRoof: 0xc0583a, IfcDoor: 0xa0724a, IfcWindow: 0x8cc8ec, IfcStair: 0xc8a066,
    IfcFooting: 0x8d8d8d, IfcColumn: 0x9ea3ab, IfcBeam: 0x9ea3ab, IfcMember: 0xcda877, IfcPlate: 0xbfbfb2, IfcCovering: 0xe9e3d3, IfcCurtainWall: 0x8cc8ec,
    IfcRailing: 0x666a70, IfcFurnishingElement: 0xd9cdb4, IfcFlowTerminal: 0xf3f3f3, IfcSpace: 0x3d7bf0, IfcBuildingElementProxy: 0xb3b3b3 };
  const nomCls = c => CLS_FR[c] || c.replace(/^Ifc/, "");
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const fmt = v => {
    if (v === true) return 'Oui <span class="v-mono">(TRUE)</span>';
    if (v === false) return 'Non <span class="v-mono">(FALSE)</span>';
    if (Array.isArray(v)) return `${String(v[0]).replace(".", ",")} ${v[1]}`;
    return esc(v);
  };

  function creer(root) {
    const ids = root.dataset.maquettes.split(",").map(s => s.trim());
    const base = root.dataset.base || "";
    root.innerHTML = `
<div class="v-barre">
  <label class="v-projet">Projet <select class="v-sel-projet">${ids.map(i => `<option value="${i}">${i}</option>`).join("")}</select></label>
  <label>Niveau <select class="v-sel-niveau"></select></label>
  <label class="v-coupe-lab">Coupe <input type="range" class="v-coupe" min="0" max="1000" value="1000" aria-label="Plan de coupe horizontal"></label>
  <button type="button" class="v-btn v-pieces" aria-pressed="false">Pièces</button>
  <button type="button" class="v-btn v-recentrer">Recentrer</button>
  <button type="button" class="v-btn v-capture">📷 Capture</button>
</div>
<div class="v-corps">
  <div class="v-vue"><canvas></canvas><div class="v-charge">Chargement de la maquette…</div><p class="v-aide">Glisser : tourner · Molette / pincer : zoomer · Clic droit : déplacer · Clic : sélectionner</p></div>
  <aside class="v-panneau">
    <div class="v-onglets" role="tablist"><button role="tab" class="on" data-o="insp">Inspecteur</button><button role="tab" data-o="arbo">Arborescence</button></div>
    <div class="v-insp"></div><div class="v-arbo" hidden></div>
  </aside>
</div>`;
    const $ = s => root.querySelector(s);
    if (ids.length === 1) $(".v-projet").hidden = true;
    const canvas = $("canvas"), vue = $(".v-vue");
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 2)); renderer.localClippingEnabled = true;
    const scene = new THREE.Scene(); scene.background = new THREE.Color(0xe9eef6);
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 2000);
    const controls = new THREE.OrbitControls(camera, canvas); controls.enableDamping = true;
    scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 0.85));
    const soleil = new THREE.DirectionalLight(0xffffff, 0.55); soleil.position.set(30, 60, 20); scene.add(soleil);
    const coupe = new THREE.Plane(new THREE.Vector3(0, -1, 0), 1e6);
    const grille = new THREE.GridHelper(200, 200, 0xc3cfe0, 0xd8e0ec); scene.add(grille);

    let D = null, modele = null, objets = [], parId = {}, sel = null, bornes = null, piecesOn = false, niveauOn = "";
    const surbrillance = new THREE.MeshLambertMaterial({ color: 0xf2600f, emissive: 0x7a2600, clippingPlanes: [coupe], side: THREE.DoubleSide });

    function taille() {
      const w = vue.clientWidth, h = vue.clientHeight;
      renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    }
    new ResizeObserver(taille).observe(vue);
    (function boucle() { controls.update(); renderer.render(scene, camera); requestAnimationFrame(boucle); })();

    function recentrer() {
      if (!bornes) return;
      const c = bornes.getCenter(new THREE.Vector3()), r = bornes.getSize(new THREE.Vector3()).length();
      controls.target.copy(c); camera.position.set(c.x + r * 0.6, c.y + r * 0.55, c.z + r * 0.75);
      camera.near = r / 200; camera.far = r * 20; camera.updateProjectionMatrix();
    }

    function charger(id) {
      $(".v-charge").hidden = false; $(".v-charge").textContent = "Chargement de la maquette…";
      if (modele) scene.remove(modele);
      sel = null; objets = []; parId = {};
      Promise.all([fetch(`${base}media/maquettes/${id}.json`).then(r => r.json()),
        new Promise((ok, ko) => new THREE.GLTFLoader().load(`${base}media/maquettes/${id}.glb`, ok, undefined, ko))])
        .then(([data, gltf]) => {
          D = data; D.parId = {}; D.elements.forEach(e => D.parId[e.id] = e);
          root.querySelector(".v-sel-projet").selectedOptions[0].textContent = D.projet;
          modele = gltf.scene; scene.add(modele);
          modele.traverse(o => {
            if (!o.isMesh) return;
            let n = o; while (n && !D.parId[n.name]) n = n.parent;
            if (!n) return;
            const e = D.parId[n.name];
            if (!o.geometry.attributes.normal) o.geometry.computeVertexNormals();
            o.geometry.deleteAttribute && o.geometry.deleteAttribute("color");
            const transp = { IfcSpace: 0.16, IfcWindow: 0.45, IfcCurtainWall: 0.45 }[e.cls];
            const mat = new THREE.MeshLambertMaterial({ color: COULEUR[e.cls] || 0xbfc5cc, clippingPlanes: [coupe], side: THREE.DoubleSide });
            if (transp) { mat.transparent = true; mat.opacity = transp; mat.depthWrite = false; }
            o.material = mat; o.userData = { el: e, mat };
            objets.push(o); (parId[e.id] = parId[e.id] || []).push(o);
          });
          bornes = new THREE.Box3();
          objets.forEach(o => { if (!["IfcSpace", "IfcBuildingElementProxy"].includes(o.userData.el.cls)) bornes.expandByObject(o); });
          grille.position.y = bornes.min.y - 0.01;
          $(".v-sel-niveau").innerHTML = `<option value="">Tous les niveaux</option>` + D.niveaux.map(n => `<option>${esc(n.nom)}</option>`).join("");
          niveauOn = ""; $(".v-coupe").value = 1000; majCoupe();
          visibilite(); recentrer(); inspecteur(); arbo();
          $(".v-charge").hidden = true;
          root.dispatchEvent(new CustomEvent("maquette-chargee", { detail: D }));
        })
        .catch(() => { $(".v-charge").textContent = "Impossible de charger la maquette. Vérifie ta connexion puis recharge la page."; });
    }

    function visibilite() {
      objets.forEach(o => {
        const e = o.userData.el;
        o.visible = (e.cls === "IfcSpace" ? piecesOn : true) && (!niveauOn || e.niveau === niveauOn);
      });
    }
    function majCoupe() {
      if (!bornes) return;
      const t = $(".v-coupe").value / 1000;
      coupe.constant = t >= 0.999 ? 1e6 : bornes.min.y + (bornes.max.y - bornes.min.y) * t;
    }
    function choisir(id) {
      if (sel) (parId[sel] || []).forEach(o => o.material = o.userData.mat);
      sel = id;
      if (sel) (parId[sel] || []).forEach(o => o.material = surbrillance);
      inspecteur();
      root.dispatchEvent(new CustomEvent("selection", { detail: sel ? D.parId[sel] : null }));
    }

    function inspecteur() {
      const z = $(".v-insp");
      if (!sel) { z.innerHTML = `<p class="v-vide">Clique sur un objet de la maquette pour lire ses informations IFC.</p>`; return; }
      const e = D.parId[sel];
      const chemin = [D.arbo.Projet, D.arbo.Site, D.arbo["Bâtiment"], e.niveau || "—", nomCls(e.cls)];
      let h = `<p class="v-classe"><b>${esc(e.ifc)}</b> ${esc(nomCls(e.ifc.replace("StandardCase", "")))}</p>${e.partie_de ? `<p class="v-partie">fait partie de <b>${esc(e.partie_de)}</b> (${esc(nomCls(e.partie_de))})</p>` : ""}
<p class="v-nom">${esc(e.nom || "(sans nom)")}</p>
<p class="v-chemin" title="Arborescence IFC">${chemin.map(esc).join(" › ")}</p>`;
      if (e.numero) h += `<dl class="v-dl"><dt>N° de pièce</dt><dd>${esc(e.numero)}</dd></dl>`;
      if (e.type) h += `<dl class="v-dl"><dt>Type</dt><dd>${esc(e.type)}</dd></dl>`;
      const ordre = Object.keys(e.props).sort((a, b) => (a.startsWith("Pset") ? 0 : 1) - (b.startsWith("Pset") ? 0 : 1));
      for (const g of ordre) {
        h += `<details class="v-pset" ${g.startsWith("Pset") || g === "Matériaux" || g === "Cotes" ? "open" : ""}><summary>${esc(GROUPE_FR[g] || g)} <span class="v-mono">${esc(g)}</span></summary><dl class="v-dl">`;
        for (const [k, v] of Object.entries(e.props[g])) h += `<dt title="${esc(k)}">${esc(PROP_FR[k] || k)}</dt><dd>${fmt(v)}</dd>`;
        h += `</dl></details>`;
      }
      z.innerHTML = h;
    }

    function arbo() {
      const z = $(".v-arbo");
      let h = `<p class="v-racine">${esc(D.arbo.Projet)} › ${esc(D.arbo.Site)} › ${esc(D.arbo["Bâtiment"])}</p>`;
      for (const n of D.niveaux) {
        const els = D.elements.filter(e => e.niveau === n.nom);
        if (!els.length) continue;
        const parCls = {};
        els.forEach(e => (parCls[e.cls] = parCls[e.cls] || []).push(e));
        h += `<details class="v-niv"><summary>${esc(n.nom)} <small>(${String(n.altitude).replace(".", ",")} m)</small></summary>`;
        for (const [c, l] of Object.entries(parCls).sort()) {
          h += `<details class="v-cls"><summary><b>${esc(nomCls(c))}</b> <span class="v-mono">${c}</span> <span class="v-nb">${l.length}</span></summary><ul>` +
            l.map(e => `<li><button type="button" data-id="${e.id}">${esc(e.nom || e.id)}</button></li>`).join("") + `</ul></details>`;
        }
        h += `</details>`;
      }
      z.innerHTML = h;
      z.querySelectorAll("button[data-id]").forEach(b => b.onclick = () => { choisir(b.dataset.id); onglet("insp"); });
    }
    function onglet(o) {
      root.querySelectorAll(".v-onglets button").forEach(b => b.classList.toggle("on", b.dataset.o === o));
      $(".v-insp").hidden = o !== "insp"; $(".v-arbo").hidden = o !== "arbo";
    }

    // interactions
    const ray = new THREE.Raycaster(); let down = null;
    canvas.addEventListener("pointerdown", e => down = [e.clientX, e.clientY]);
    canvas.addEventListener("pointerup", e => {
      if (!down || Math.hypot(e.clientX - down[0], e.clientY - down[1]) > 5) return;
      const r = canvas.getBoundingClientRect();
      ray.setFromCamera({ x: (e.clientX - r.left) / r.width * 2 - 1, y: -(e.clientY - r.top) / r.height * 2 + 1 }, camera);
      const hits = ray.intersectObjects(objets.filter(o => o.visible), false)
        .filter(hit => coupe.distanceToPoint(hit.point) >= -1e-3 && (piecesOn || hit.object.userData.el.cls !== "IfcSpace"));
      choisir(hits.length ? hits[0].object.userData.el.id : null);
    });
    $(".v-sel-projet").onchange = e => charger(e.target.value);
    $(".v-sel-niveau").onchange = e => { niveauOn = e.target.value; visibilite(); };
    $(".v-coupe").oninput = majCoupe;
    $(".v-pieces").onclick = e => { piecesOn = !piecesOn; e.target.setAttribute("aria-pressed", piecesOn); visibilite(); };
    $(".v-recentrer").onclick = recentrer;
    $(".v-capture").onclick = () => {
      renderer.render(scene, camera);
      const a = document.createElement("a"); a.download = `capture-${D ? D.fichier.replace(/\.ifc$/i, "") : "maquette"}.png`;
      a.href = canvas.toDataURL("image/png"); a.click();
    };
    root.querySelectorAll(".v-onglets button").forEach(b => b.onclick = () => onglet(b.dataset.o));
    charger(ids[0]);
    root.api = { charger, choisir, donnees: () => D };
  }

  window.EMNB_visionneuse = creer;
  document.querySelectorAll(".visionneuse[data-maquettes]").forEach(creer);
})();
