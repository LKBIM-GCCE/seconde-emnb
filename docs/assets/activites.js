/* Moteur d'activités interactives — Seconde EMNB
   Types de blocs : cours, ordre, indices, td06, qcm.
   Les résultats sont gardés dans le navigateur (localStorage) et résumés dans un certificat. */
(function () {
  const A = JSON.parse(document.getElementById("activite-data").textContent);
  const COURS = document.getElementById("cours-html").innerHTML;
  const CLE = "emnb-" + A.id;
  const $ = (s, el = document) => el.querySelector(s);
  const h = (tag, attrs = {}, ...kids) => {
    const el = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (v == null || v === false) continue;
      if (k === "class") el.className = v;
      else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
      else if (k === "html") el.innerHTML = v;
      else el.setAttribute(k, v);
    }
    for (const k of kids.flat()) if (k != null) el.append(k.nodeType ? k : document.createTextNode(k));
    return el;
  };

  // ---------- état (navigateur) ----------
  let etat = { nom: "", res: {}, essais: {} };
  try { etat = Object.assign(etat, JSON.parse(localStorage.getItem(CLE)) || {}); } catch (e) {}
  const sauver = () => { try { localStorage.setItem(CLE, JSON.stringify(etat)); } catch (e) {} };

  // mélange stable (même ordre pour tous les élèves d'un même essai)
  function melange(arr, graine) {
    const a = arr.slice(); let s = graine;
    for (let i = a.length - 1; i > 0; i--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor(s / 233280 * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  const selectPhase = (valeur = "") => h("select", { class: "sel" },
    h("option", { value: "" }, "— choisir —"), ...A.phases.map(p => { const o = h("option", { value: p }, p); if (p === valeur) o.selected = true; return o; }));

  // ---------- navigation ----------
  const nav = $("#etapes"), zone = $("#zone");
  const blocs = A.blocs.concat([{ id: "certificat", type: "certificat", titre: "Mon certificat" }]);
  let courant = 0;

  function majNav() {
    nav.innerHTML = "";
    blocs.forEach((b, i) => {
      const r = etat.res[b.id];
      const badge = b.type === "cours" ? (etat.res.cours ? "✓" : "") : r ? `${r.pts}/${r.max}` : "";
      nav.append(h("button", { class: "etape" + (i === courant ? " actif" : "") + (r ? " fait" : ""), onclick: () => ouvrir(i) },
        h("span", { class: "n" }, b.type === "certificat" ? "★" : String(i)), h("span", { class: "t" }, b.titre.split(" — ")[0]),
        badge ? h("span", { class: "b" }, badge) : null));
    });
  }

  function ouvrir(i) {
    courant = i; majNav();
    const b = blocs[i];
    zone.innerHTML = "";
    const tete = h("header", { class: "bloc-tete" }, h("h2", {}, b.titre), b.duree ? h("span", { class: "duree" }, "⏱ " + b.duree) : null);
    zone.append(tete);
    if (b.consigne) zone.append(h("p", { class: "consigne" }, b.consigne));
    ({ cours, ordre, indices, td06, qcm, certificat })[b.type](b);
    window.scrollTo({ top: $("#activite").offsetTop - 70, behavior: "smooth" });
  }

  function piedValider(b, valider, corrige) {
    const pied = h("div", { class: "pied-bloc" });
    const res = etat.res[b.id];
    if (corrige && res) {
      pied.append(h("p", { class: "score " + (res.pts / res.max >= .7 ? "ok" : "ko") }, `Résultat : ${res.pts} / ${res.max}`),
        h("button", { class: "btn sec", onclick: () => { delete etat.res[b.id]; sauver(); ouvrir(courant); } }, "↺ Recommencer"),
        courant < blocs.length - 1 ? h("button", { class: "btn", onclick: () => ouvrir(courant + 1) }, "Activité suivante →") : null);
    } else {
      pied.append(h("button", { class: "btn", onclick: valider }, "Valider mes réponses"));
    }
    zone.append(pied);
  }
  function enregistrer(b, pts, max, detail) {
    etat.essais[b.id] = (etat.essais[b.id] || 0) + 1;
    etat.res[b.id] = { pts, max, detail }; sauver(); ouvrir(courant);
  }

  // ---------- COURS ----------
  function cours(b) {
    zone.append(h("div", { class: "cours", html: COURS }));
    const p = h("div", { class: "pied-bloc" });
    p.append(h("button", { class: "btn", onclick: () => { etat.res.cours = { lu: true }; sauver(); ouvrir(courant + 1); } }, "J'ai lu le cours → TD 04"));
    zone.append(p);
  }

  // ---------- ORDRE (frise) ----------
  function ordre(b) {
    const res = etat.res[b.id];
    const n = b.cartes.length;
    let place = res ? res.detail : Array(n).fill(null);   // index de carte par case
    const ordreCartes = melange(b.cartes.map((_, i) => i), 7 + (etat.essais[b.id] || 0));
    const frise = h("ol", { class: "frise-cases" }), pioche = h("div", { class: "pioche" });
    function dessiner() {
      frise.innerHTML = ""; pioche.innerHTML = "";
      place.forEach((ci, k) => {
        const c = ci == null ? null : b.cartes[ci];
        const cls = "case" + (c ? " pleine" : "") + (res ? (ci === k ? " juste" : " faux") : "");
        frise.append(h("li", { class: cls, onclick: () => { if (!res && c) { place[k] = null; dessiner(); } } },
          h("span", { class: "num" }, String(k + 1)), h("b", {}, c ? c.nom : "…"),
          res && ci !== k ? h("small", {}, "Réponse : " + b.cartes[k].nom) : null));
      });
      if (!res) ordreCartes.filter(ci => !place.includes(ci)).forEach(ci => {
        const c = b.cartes[ci];
        pioche.append(h("button", { class: "carte-phase", onclick: () => { const k = place.indexOf(null); if (k >= 0) { place[k] = ci; dessiner(); } } },
          h("b", {}, c.nom), h("span", {}, c.texte), h("small", {}, "Acteur : " + c.acteur)));
      });
    }
    dessiner();
    zone.append(h("h3", { class: "sous" }, "Ma frise"), frise);
    if (!res) zone.append(h("h3", { class: "sous" }, "Les cartes à placer"), pioche);
    piedValider(b, () => {
      if (place.includes(null)) return alerte("Place toutes les cartes sur la frise avant de valider.");
      enregistrer(b, place.filter((ci, k) => ci === k).length, n, place);
    }, true);
  }

  // ---------- INDICES (dossiers + documents) ----------
  function indices(b) {
    const res = etat.res[b.id], d = res ? res.detail : { phases: [], indices: [], docs: [] };
    const grille = h("div", { class: "dossiers" });
    b.dossiers.forEach((dos, i) => {
      const sel = selectPhase(d.phases[i]);
      const carte = h("div", { class: "dossier" + (res ? (d.phases[i] === dos.reponse ? " juste" : " faux") : "") },
        h("h4", {}, "Dossier n° " + (i + 1)));
      const ul = h("ul", { class: "indices" });
      dos.indices.forEach((t, k) => ul.append(h("li", {
        class: d.indices[i] === k ? "choisi" : "",
        onclick: () => { if (res) return; d.indices[i] = k; [...ul.children].forEach((li, j) => li.classList.toggle("choisi", j === k)); }
      }, t)));
      sel.disabled = !!res; sel.onchange = () => d.phases[i] = sel.value;
      carte.append(ul, h("label", { class: "lab" }, "Phase : ", sel));
      if (res && d.phases[i] !== dos.reponse) carte.append(h("p", { class: "corr" }, "Réponse : " + dos.reponse));
      grille.append(carte);
    });
    zone.append(h("p", { class: "aide" }, "Astuce : clique sur un indice pour le surligner comme « indice déterminant »."), grille);

    const tab = h("table", { class: "assoc" });
    b.documents.items.forEach((it, i) => {
      const sel = selectPhase(d.docs[i]); sel.disabled = !!res; sel.onchange = () => d.docs[i] = sel.value;
      const ok = res && d.docs[i] === it.reponse;
      tab.append(h("tr", { class: res ? (ok ? "juste" : "faux") : "" }, h("td", {}, String.fromCharCode(65 + i) + ". " + it.texte),
        h("td", {}, sel, res && !ok ? h("small", { class: "corr" }, " → " + it.reponse) : null)));
    });
    zone.append(h("h3", { class: "sous" }, b.documents.titre), tab);
    piedValider(b, () => {
      const nbD = b.dossiers.length, nbDoc = b.documents.items.length;
      for (let i = 0; i < nbD; i++) if (!d.phases[i] || d.indices[i] == null) return alerte(`Dossier n° ${i + 1} : choisis la phase et clique sur ton indice déterminant.`);
      for (let i = 0; i < nbDoc; i++) if (!d.docs[i]) return alerte("Associe tous les documents à une phase.");
      const pts = b.dossiers.filter((x, i) => d.phases[i] === x.reponse).length + b.documents.items.filter((x, i) => d.docs[i] === x.reponse).length;
      enregistrer(b, pts, nbD + nbDoc, d);
    }, true);
  }

  // ---------- TD06 (grille + phrases + vrai/faux) ----------
  function td06(b) {
    const res = etat.res[b.id], d = res ? res.detail : { grille: b.grille.lignes.map(() => Array(8).fill(false)), phrases: [], vf: [] };
    // partie 1
    const t = h("table", { class: "grille-ap" });
    t.append(h("thead", {}, h("tr", {}, h("th", {}, "Acteur"), ...b.grille.colonnes.map(c => h("th", {}, c)))));
    const tb = h("tbody");
    b.grille.lignes.forEach((l, i) => {
      const tr = h("tr", {}, h("th", {}, l.acteur));
      [...l.cases].forEach((attendu, k) => {
        const cb = h("input", { type: "checkbox", "aria-label": `${l.acteur} — ${b.grille.colonnes[k]}` });
        cb.checked = d.grille[i][k]; cb.disabled = !!res; cb.onchange = () => d.grille[i][k] = cb.checked;
        let cls = "";
        if (res) cls = attendu === "○" ? "souple" : ((attendu === "●") === d.grille[i][k] ? "juste" : "faux");
        tr.append(h("td", { class: cls, title: res ? ({ "●": "intervient", "○": "ponctuellement", "-": "n'intervient pas" })[attendu] : "" }, cb));
      });
      tb.append(tr);
    });
    t.append(tb);
    zone.append(h("h3", { class: "sous" }, b.grille.titre), h("p", { class: "aide" }, b.grille.aide), h("div", { class: "table-scroll" }, t));
    if (res) zone.append(h("p", { class: "aide" }, "Vert = juste · Rouge = à revoir · Gris = intervention ponctuelle (acceptée)."));
    // partie 2
    const ph = h("ol", { class: "phrases" });
    b.phrases.items.forEach((it, i) => {
      const sel = h("select", { class: "sel" }, h("option", { value: "" }, "— qui ? —"), ...b.phrases.choix.map(c => { const o = h("option", { value: c }, c); if (d.phrases[i] === c) o.selected = true; return o; }));
      sel.disabled = !!res; sel.onchange = () => d.phrases[i] = sel.value;
      const ok = res && d.phrases[i] === it.reponse;
      ph.append(h("li", { class: res ? (ok ? "juste" : "faux") : "" }, sel, " ", it.texte, res && !ok ? h("small", { class: "corr" }, " → " + it.reponse) : null));
    });
    zone.append(h("h3", { class: "sous" }, b.phrases.titre), ph);
    // partie 3
    const vf = h("ol", { class: "vf" });
    b.vraifaux.items.forEach((it, i) => {
      const li = h("li", { class: res ? (d.vf[i] === it.reponse ? "juste" : "faux") : "" }, h("span", {}, it.texte));
      const g = h("span", { class: "vf-btn" });
      [[true, "Vrai"], [false, "Faux"]].forEach(([v, lib]) => g.append(h("button", {
        class: "pill" + (d.vf[i] === v ? " on" : ""), disabled: res ? "" : null,
        onclick: () => { d.vf[i] = v; [...g.children].forEach(x => x.classList.toggle("on", x.textContent === lib)); }
      }, lib)));
      if (res) [...g.querySelectorAll("button")].forEach(x => x.disabled = true);
      li.append(g);
      if (res) li.append(h("small", { class: "expl" }, (it.reponse ? "Vrai. " : "Faux. ") + it.explication));
      vf.append(li);
    });
    zone.append(h("h3", { class: "sous" }, b.vraifaux.titre), vf);
    if (res) zone.append(h("p", { class: "detail-score" }, `Partie 1 : ${d.parts[0]}/${b.grille.lignes.length} acteurs bien placés · Partie 2 : ${d.parts[1]}/${b.phrases.items.length} · Partie 3 : ${d.parts[2]}/${b.vraifaux.items.length}`));
    piedValider(b, () => {
      for (let i = 0; i < b.phrases.items.length; i++) if (!d.phrases[i]) return alerte("Partie 2 : complète toutes les phrases.");
      for (let i = 0; i < b.vraifaux.items.length; i++) if (d.vf[i] == null) return alerte("Partie 3 : réponds Vrai ou Faux à chaque affirmation.");
      const p1 = b.grille.lignes.filter((l, i) => [...l.cases].every((a, k) => a === "○" || (a === "●") === d.grille[i][k])).length;
      const p2 = b.phrases.items.filter((x, i) => d.phrases[i] === x.reponse).length;
      const p3 = b.vraifaux.items.filter((x, i) => d.vf[i] === x.reponse).length;
      d.parts = [p1, p2, p3];
      enregistrer(b, p1 + p2 + p3, b.grille.lignes.length + b.phrases.items.length + b.vraifaux.items.length, d);
    }, true);
  }

  // ---------- QCM ----------
  function qcm(b) {
    const res = etat.res[b.id], d = res ? res.detail : [];
    const ol = h("ol", { class: "qcm" });
    b.questions.forEach((q, i) => {
      const li = h("li", { class: res ? (d[i] === q.r ? "juste" : "faux") : "" }, h("p", { class: "q" }, q.q));
      const opts = h("div", { class: "opts" });
      q.choix.forEach((c, k) => {
        const cls = "opt" + (d[i] === k ? " on" : "") + (res && k === q.r ? " bonne" : "");
        opts.append(h("button", { class: cls, onclick: () => { if (res) return; d[i] = k; [...opts.children].forEach((x, j) => x.classList.toggle("on", j === k)); } }, c));
      });
      li.append(opts);
      if (res) li.append(h("small", { class: "expl" }, q.explication));
      ol.append(li);
    });
    zone.append(ol);
    piedValider(b, () => {
      const manque = b.questions.findIndex((_, i) => d[i] == null);
      if (manque >= 0) return alerte(`Réponds à la question ${manque + 1} avant de valider.`);
      enregistrer(b, b.questions.filter((q, i) => d[i] === q.r).length, b.questions.length, d);
    }, true);
  }

  // ---------- CERTIFICAT ----------
  function code(texte) { // empreinte courte (FNV-1a) — sert à repérer un certificat modifié
    let x = 2166136261;
    for (const ch of texte + "|emnb-urbain-vitry") { x ^= ch.charCodeAt(0); x = Math.imul(x, 16777619) >>> 0; }
    const s = x.toString(36).toUpperCase().padStart(7, "0");
    return s.slice(0, 2) + "-" + s.slice(2, 6);
  }
  function certificat() {
    const notes = A.blocs.filter(b => b.type !== "cours");
    const faits = notes.filter(b => etat.res[b.id]);
    const champ = h("input", { type: "text", class: "nom", placeholder: "Prénom + initiale du nom (ex : Léa M.)", value: etat.nom, maxlength: "40" });
    champ.oninput = () => { etat.nom = champ.value.trim(); sauver(); };
    zone.append(h("label", { class: "lab-nom" }, "Ton prénom et l'initiale de ton nom : ", champ));
    const btn = h("button", { class: "btn" }, "Afficher mon certificat");
    zone.append(h("div", { class: "pied-bloc" }, btn));
    const cible = h("div");
    zone.append(cible);
    btn.onclick = () => {
      if (!etat.nom || etat.nom.length < 2) return alerte("Écris ton prénom et l'initiale de ton nom.");
      if (faits.length < notes.length) return alerte(`Il te reste ${notes.length - faits.length} activité(s) à valider avant d'obtenir ton certificat.`);
      const maint = new Date(), date = maint.toLocaleDateString("fr-FR"), heure = maint.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
      const tot = faits.reduce((s, b) => s + etat.res[b.id].pts, 0), max = faits.reduce((s, b) => s + etat.res[b.id].max, 0);
      const ligne = faits.map(b => `${b.id}:${etat.res[b.id].pts}/${etat.res[b.id].max}`).join(";");
      const c = code(`${A.id}|${etat.nom}|${ligne}|${date}`);
      cible.innerHTML = "";
      cible.append(h("div", { class: "certif" },
        h("p", { class: "certif-sur" }, "Seconde EMNB · Lycée des métiers Urbain Vitry"),
        h("h3", {}, "Certificat de séance"),
        h("p", { class: "certif-seance" }, A.titre),
        h("p", { class: "certif-nom" }, etat.nom),
        h("table", {}, ...faits.map(b => h("tr", {}, h("td", {}, b.titre.split(" — ")[0] + " — " + (b.titre.split(" — ")[1] || "")),
          h("td", {}, `${etat.res[b.id].pts} / ${etat.res[b.id].max}`), h("td", { class: "ess" }, `${etat.essais[b.id] || 1} essai(s)`)))),
        h("p", { class: "certif-total" }, `Total : ${tot} / ${max}  (${Math.round(tot / max * 100)} %)`),
        h("p", { class: "certif-pied" }, `${date} à ${heure} · Code de contrôle : `, h("b", {}, c))));
      const lignes = faits.map(b => [b.titre, `${etat.res[b.id].pts} / ${etat.res[b.id].max}`, `${etat.essais[b.id] || 1} essai(s)`]);
      const telecharger = () => imageCertificat({ nom: etat.nom, lignes, total: `Total : ${tot} / ${max}  (${Math.round(tot / max * 100)} %)`, pied: `${date} à ${heure}`, code: c });
      cible.append(h("div", { class: "pied-bloc" },
        h("button", { class: "btn", onclick: telecharger }, "⬇ Télécharger mon certificat (image)"),
        h("span", { class: "aide" }, "Puis dépose le fichier sur l'ENT.")));
    };
  }

  // dessine le certificat dans une image PNG et la télécharge
  function imageCertificat(d) {
    const W = 1200, H = 720 + d.lignes.length * 56, cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    const x = cv.getContext("2d"), F = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
    const txt = (t, px, y, opt = {}) => { x.font = `${opt.poids || 400} ${px}px ${F}`; x.fillStyle = opt.c || "#1c2228"; x.textAlign = opt.a || "center"; x.fillText(t, opt.x ?? W / 2, y); };
    x.fillStyle = "#f4f2ec"; x.fillRect(0, 0, W, H);
    x.strokeStyle = "#c4521f"; x.lineWidth = 6; x.strokeRect(30, 30, W - 60, H - 60); x.lineWidth = 2; x.strokeRect(44, 44, W - 88, H - 88);
    x.fillStyle = "#c4521f"; x.beginPath(); x.roundRect(W / 2 - 34, 78, 68, 68, 12); x.fill();
    txt("2de", 30, 124, { poids: 800, c: "#fff" });
    txt("SECONDE EMNB · LYCÉE DES MÉTIERS URBAIN VITRY", 20, 186, { poids: 600, c: "#5d6670" });
    txt("Certificat de séance", 52, 252, { poids: 800, c: "#c4521f" });
    txt(A.titre, 28, 298, { poids: 600 });
    txt(d.nom, 60, 388, { poids: 800 });
    let y = 460;
    x.strokeStyle = "#dedad0"; x.lineWidth = 1.5;
    d.lignes.forEach(([t, s, e]) => {
      txt(t, 24, y, { a: "left", x: 140 }); txt(s, 26, y, { a: "right", x: 900, poids: 700 }); txt(e, 18, y, { a: "right", x: W - 140, c: "#5d6670" });
      x.beginPath(); x.moveTo(140, y + 20); x.lineTo(W - 140, y + 20); x.stroke(); y += 56;
    });
    txt(d.total, 34, y + 46, { poids: 800 });
    txt(`${d.pied}  ·  Code de contrôle : ${d.code}`, 22, y + 100, { c: "#5d6670" });
    const fichier = `certificat_${A.id}_${d.nom.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^A-Za-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`;
    cv.toBlob(blob => {
      const a = h("a", { href: URL.createObjectURL(blob), download: fichier });
      document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
    }, "image/png");
  }

  function alerte(msg) {
    let a = $("#alerte"); if (!a) { a = h("div", { id: "alerte", role: "status" }); document.body.append(a); }
    a.textContent = msg; a.classList.add("vu"); clearTimeout(a._t); a._t = setTimeout(() => a.classList.remove("vu"), 3500);
  }

  $("#raz").onclick = () => { if (confirm("Effacer toutes tes réponses de cette séance ?")) { etat = { nom: "", res: {}, essais: {} }; sauver(); ouvrir(0); } };
  window.EMNB_code = code;
  ouvrir(0);
})();
