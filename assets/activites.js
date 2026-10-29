/* Moteur d'activités interactives — Seconde EMNB
   Une séance = des blocs (cours ou exercice). Un exercice = des parties réutilisables :
   ordre · indices · associer · grille · vraifaux · qcm · saisie · nombre · redaction · schema · image · texte
   Les réponses restent dans le navigateur (localStorage) ; la fin de séance produit un certificat PNG. */
(function () {
  const A = JSON.parse(document.getElementById("activite-data").textContent);
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
    for (const k of kids.flat()) if (k != null && k !== false) el.append(k.nodeType ? k : document.createTextNode(k));
    return el;
  };
  const norm = s => String(s || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[’'`\-–—.,;:!?()«»"]/g, " ").replace(/\s+/g, " ").trim();
  const accepte = (rep, v) => Array.isArray(rep) ? rep.includes(v) : rep === v;
  const affiche = rep => Array.isArray(rep) ? rep.join(" ou ") : rep;

  // ---------- état ----------
  let etat = { nom: "", res: {}, essais: {} };
  try { etat = Object.assign(etat, JSON.parse(localStorage.getItem(CLE)) || {}); } catch (e) {}
  const sauver = () => { try { localStorage.setItem(CLE, JSON.stringify(etat)); } catch (e) {} };
  function melange(arr, graine) {
    const a = arr.slice(); let s = graine * 7919 + 13;
    for (let i = a.length - 1; i > 0; i--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor(s / 233280 * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; }
    return a;
  }
  const selectListe = (choix, valeur, vide = "— choisir —") => h("select", { class: "sel" },
    h("option", { value: "" }, vide), ...choix.map(p => { const o = h("option", { value: p }, p); if (p === valeur) o.selected = true; return o; }));
  const cls = (fini, ok) => fini ? (ok ? "juste" : "faux") : "";

  // ======================================================================
  // PARTIES : chacune reçoit (définition, d = réponses mutables, fini, graine)
  // et renvoie { el, manque() -> message|null, score() -> [pts, max] }
  // ======================================================================
  const P = {};

  P.image = (p) => ({
    el: h("figure", { class: "figure" }, h("img", { src: p.src, alt: p.alt || "", loading: "lazy" }), p.legende ? h("figcaption", {}, p.legende) : null,
      h("a", { class: "zoom", href: p.src, target: "_blank", rel: "noopener" }, "🔍 Agrandir")),
    manque: () => null, score: () => [0, 0]
  });

  P.texte = (p) => ({ el: h("div", { class: "texte-partie", html: p.html }), manque: () => null, score: () => [0, 0] });

  P.ordre = (p, d, fini, g) => {
    const n = p.cartes.length;
    d.place = d.place || Array(n).fill(null);
    const pioche = melange(p.cartes.map((_, i) => i), g);
    const frise = h("ol", { class: "frise-cases" }), zone = h("div", { class: "pioche" }), el = h("div", {}, h("h4", { class: "mini" }, p.titreFrise || "Ma frise"), frise);
    if (!fini) el.append(h("h4", { class: "mini" }, "Les cartes à placer"), zone);
    function dessiner() {
      frise.innerHTML = ""; zone.innerHTML = "";
      d.place.forEach((ci, k) => {
        const c = ci == null ? null : p.cartes[ci];
        frise.append(h("li", { class: "case" + (c ? " pleine " : " ") + cls(fini, ci === k), onclick: () => { if (!fini && c) { d.place[k] = null; dessiner(); } } },
          h("span", { class: "num" }, String(k + 1)), h("b", {}, c ? c.nom : "…"), fini && ci !== k ? h("small", {}, "Réponse : " + p.cartes[k].nom) : null));
      });
      if (!fini) pioche.filter(ci => !d.place.includes(ci)).forEach(ci => {
        const c = p.cartes[ci];
        zone.append(h("button", { class: "carte-phase", onclick: () => { const k = d.place.indexOf(null); if (k >= 0) { d.place[k] = ci; dessiner(); } } },
          h("b", {}, c.nom), c.texte ? h("span", {}, c.texte) : null, c.acteur ? h("small", {}, "Acteur : " + c.acteur) : null));
      });
    }
    dessiner();
    return { el, manque: () => d.place.includes(null) ? "Place toutes les cartes." : null, score: () => [d.place.filter((ci, k) => ci === k).length, n] };
  };

  P.indices = (p, d, fini) => {
    d.ph = d.ph || []; d.ind = d.ind || [];
    const el = h("div", { class: "dossiers" });
    p.dossiers.forEach((dos, i) => {
      const sel = selectListe(p.choix, d.ph[i]); sel.disabled = fini; sel.onchange = () => d.ph[i] = sel.value;
      const ul = h("ul", { class: "indices" });
      dos.indices.forEach((t, k) => ul.append(h("li", { class: d.ind[i] === k ? "choisi" : "", onclick: () => { if (fini) return; d.ind[i] = k; [...ul.children].forEach((li, j) => li.classList.toggle("choisi", j === k)); } }, t)));
      el.append(h("div", { class: "dossier " + cls(fini, accepte(dos.reponse, d.ph[i])) }, h("h4", {}, (dos.titre || (p.titreDossier || "Dossier n° ") + (i + 1))), ul,
        h("label", { class: "lab" }, (p.libelle || "Phase") + " : ", sel), fini && !accepte(dos.reponse, d.ph[i]) ? h("p", { class: "corr" }, "Réponse : " + affiche(dos.reponse)) : null,
        fini && dos.explication ? h("small", { class: "expl" }, dos.explication) : null));
    });
    return {
      el: h("div", {}, p.surligner === false ? null : h("p", { class: "aide" }, "Clique sur l'indice qui te permet d'être sûr : il sera surligné."), el),
      manque: () => { for (let i = 0; i < p.dossiers.length; i++) if (!d.ph[i] || (p.surligner !== false && d.ind[i] == null)) return `${p.titreDossier || "Dossier n° "}${i + 1} : choisis la réponse${p.surligner === false ? "" : " et clique sur ton indice déterminant"}.`; return null; },
      score: () => [p.dossiers.filter((x, i) => accepte(x.reponse, d.ph[i])).length, p.dossiers.length]
    };
  };

  // associer : liste déroulante (ou boutons si ≤ 3 choix) par élément ; option image + repères numérotés (x, y en %)
  P.associer = (p, d, fini, g) => {
    d.v = d.v || [];
    const choix = p.melanger === false ? p.choix : melange(p.choix, g + 3);
    const pills = p.style === "boutons" || p.choix.length <= 3;
    const ol = h("ol", { class: "assoc-liste" + (pills ? " pills" : "") });
    p.items.forEach((it, i) => {
      const ok = accepte(it.reponse, d.v[i]);
      let ctrl;
      if (pills) {
        ctrl = h("span", { class: "vf-btn" });
        p.choix.forEach(c => ctrl.append(h("button", { class: "pill" + (d.v[i] === c ? " on" : ""), disabled: fini, onclick: () => { d.v[i] = c; [...ctrl.children].forEach(x => x.classList.toggle("on", x.textContent === c)); } }, c)));
      } else {
        ctrl = selectListe(choix, d.v[i], p.vide || "— choisir —"); ctrl.disabled = fini; ctrl.onchange = () => d.v[i] = ctrl.value;
      }
      ol.append(h("li", { class: cls(fini, ok) }, h("span", { class: "it" }, it.texte), ctrl,
        fini && !ok ? h("small", { class: "corr" }, "→ " + affiche(it.reponse)) : null,
        fini && it.explication ? h("small", { class: "expl" }, it.explication) : null));
    });
    const el = h("div", {});
    if (p.image) {
      const fig = h("div", { class: "plan-reperes" }, h("img", { src: p.image, alt: p.alt || "" }));
      p.items.forEach((it, i) => it.x != null && fig.append(h("span", { class: "repere " + cls(fini, accepte(it.reponse, d.v[i])), style: `left:${it.x}%;top:${it.y}%` }, String(i + 1))));
      el.append(h("div", { class: "fig-wrap" }, fig, h("a", { class: "zoom", href: p.image, target: "_blank", rel: "noopener" }, "🔍 Agrandir l'image")));
    }
    el.append(ol);
    return {
      el, manque: () => p.items.some((_, i) => !d.v[i]) ? "Réponds à chaque ligne." : null,
      score: () => [p.items.filter((it, i) => accepte(it.reponse, d.v[i])).length, p.items.length]
    };
  };

  P.grille = (p, d, fini) => {
    d.g = d.g || p.lignes.map(l => Array(l.cases.length).fill(false));
    const t = h("table", { class: "grille-ap" });
    t.append(h("thead", {}, h("tr", {}, h("th", {}, p.entete || "Acteur"), ...p.colonnes.map(c => h("th", {}, c)))));
    const tb = h("tbody");
    p.lignes.forEach((l, i) => {
      const tr = h("tr", {}, h("th", {}, l.acteur));
      [...l.cases].forEach((att, k) => {
        const cb = h("input", { type: "checkbox", "aria-label": `${l.acteur} — ${p.colonnes[k]}` });
        cb.checked = d.g[i][k]; cb.disabled = fini; cb.onchange = () => d.g[i][k] = cb.checked;
        tr.append(h("td", { class: fini ? (att === "○" ? "souple" : cls(true, (att === "●") === d.g[i][k])) : "" }, cb));
      });
      tb.append(tr);
    });
    t.append(tb);
    const ligneOk = (l, i) => [...l.cases].every((a, k) => a === "○" || (a === "●") === d.g[i][k]);
    return {
      el: h("div", {}, p.aide ? h("p", { class: "aide" }, p.aide) : null, h("div", { class: "table-scroll" }, t),
        fini ? h("p", { class: "aide" }, "Vert = juste · Rouge = à revoir · Gris = intervention ponctuelle (acceptée).") : null),
      manque: () => null, score: () => [p.lignes.filter(ligneOk).length, p.lignes.length]
    };
  };

  P.vraifaux = (p, d, fini) => {
    d.v = d.v || [];
    const ol = h("ol", { class: "vf" });
    p.items.forEach((it, i) => {
      const g = h("span", { class: "vf-btn" });
      [[true, "Vrai"], [false, "Faux"]].forEach(([v, lib]) => g.append(h("button", { class: "pill" + (d.v[i] === v ? " on" : ""), disabled: fini,
        onclick: () => { d.v[i] = v; [...g.children].forEach(x => x.classList.toggle("on", x.textContent === lib)); } }, lib)));
      ol.append(h("li", { class: cls(fini, d.v[i] === it.reponse) }, h("span", {}, it.texte), g,
        fini ? h("small", { class: "expl" }, (it.reponse ? "Vrai. " : "Faux. ") + (it.explication || "")) : null));
    });
    return { el: ol, manque: () => p.items.some((_, i) => d.v[i] == null) ? "Réponds Vrai ou Faux à chaque affirmation." : null, score: () => [p.items.filter((x, i) => d.v[i] === x.reponse).length, p.items.length] };
  };

  P.qcm = (p, d, fini) => {
    d.v = d.v || [];
    const ol = h("ol", { class: "qcm" });
    p.questions.forEach((q, i) => {
      const opts = h("div", { class: "opts" });
      q.choix.forEach((c, k) => opts.append(h("button", { class: "opt" + (d.v[i] === k ? " on" : "") + (fini && k === q.r ? " bonne" : ""), disabled: fini,
        onclick: () => { d.v[i] = k; [...opts.children].forEach((x, j) => x.classList.toggle("on", j === k)); } }, c)));
      ol.append(h("li", { class: cls(fini, d.v[i] === q.r) }, q.image ? h("img", { class: "q-img", src: q.image, alt: "" }) : null, h("p", { class: "q" }, q.q), opts,
        fini && q.explication ? h("small", { class: "expl" }, q.explication) : null));
    });
    return { el: ol, manque: () => { const m = p.questions.findIndex((_, i) => d.v[i] == null); return m >= 0 ? `Réponds à la question ${m + 1}.` : null; }, score: () => [p.questions.filter((q, i) => d.v[i] === q.r).length, p.questions.length] };
  };

  // saisie : texte libre corrigé par mots-clés — motscles = [["maitre"], ["ouvrage"]] : chaque groupe doit être présent
  P.saisie = (p, d, fini) => {
    d.v = d.v || [];
    const ok = i => { const v = " " + norm(d.v[i]) + " "; return p.items[i].motscles.every(gr => gr.some(m => v.includes(norm(m)))); };
    const ol = h("ol", { class: "saisies" });
    p.items.forEach((it, i) => {
      const inp = h("input", { type: "text", class: "champ", value: d.v[i] || "", placeholder: it.aide || "", disabled: fini, autocomplete: "off" });
      inp.oninput = () => d.v[i] = inp.value;
      ol.append(h("li", { class: cls(fini, ok(i)) }, h("label", {}, h("b", {}, it.texte), inp), fini && !ok(i) ? h("small", { class: "corr" }, "→ " + it.reponse) : null));
    });
    return { el: ol, manque: () => p.items.some((_, i) => !String(d.v[i] || "").trim()) ? "Complète chaque champ." : null, score: () => [p.items.filter((_, i) => ok(i)).length, p.items.length] };
  };

  // nombre : valeur numérique avec tolérance
  P.nombre = (p, d, fini) => {
    d.v = d.v || [];
    const val = i => parseFloat(String(d.v[i] || "").replace(",", ".").replace(/[\s+]/g, ""));
    const ok = i => Math.abs(val(i) - p.items[i].valeur) <= (p.items[i].tolerance ?? 0.005);
    const ol = h("ol", { class: "saisies" });
    p.items.forEach((it, i) => {
      const inp = h("input", { type: "text", inputmode: "decimal", class: "champ court", value: d.v[i] || "", disabled: fini, autocomplete: "off" });
      inp.oninput = () => d.v[i] = inp.value;
      ol.append(h("li", { class: cls(fini, ok(i)) }, h("label", {}, h("b", {}, it.texte), h("span", { class: "nb" }, inp, it.unite ? h("span", { class: "unite" }, it.unite) : null)),
        fini && !ok(i) ? h("small", { class: "corr" }, `→ ${String(it.valeur).replace(".", ",")} ${it.unite || ""}`) : null,
        fini && it.explication ? h("small", { class: "expl" }, it.explication) : null));
    });
    return { el: ol, manque: () => p.items.some((_, i) => isNaN(val(i))) ? "Écris un nombre dans chaque case (ex : 2,50)." : null, score: () => [p.items.filter((_, i) => ok(i)).length, p.items.length] };
  };

  // redaction : réponse personnelle, non notée, reprise sur le certificat
  P.redaction = (p, d, fini) => {
    const ta = h("textarea", { class: "champ zone-texte", rows: "4", maxlength: "400", disabled: fini, placeholder: "Rédige ta réponse en phrases complètes…" });
    ta.value = d.t || ""; ta.oninput = () => d.t = ta.value;
    return {
      el: h("div", {}, h("p", { class: "q" }, p.question), ta, fini && p.exemple ? h("small", { class: "expl" }, "Exemple de réponse : " + p.exemple) : null),
      manque: () => (d.t || "").trim().length < (p.min || 40) ? `Rédige une réponse d'au moins ${p.min || 40} caractères.` : null,
      score: () => [0, 0], texte: () => (d.t || "").trim()
    };
  };

  // schema : cases positionnées sur une grille ; on clique une étiquette puis une case
  P.schema = (p, d, fini) => {
    d.c = d.c || {};
    let actif = null;
    const sch = h("div", { class: "schema", style: `grid-template-columns:repeat(${p.colonnes || 3},1fr)` });
    const pool = h("div", { class: "etiquettes" });
    const ok = c => c.accepte.includes(d.c[c.id]);
    function dessiner() {
      sch.innerHTML = ""; pool.innerHTML = "";
      (p.decor || []).forEach(x => sch.append(h("div", { class: "decor", style: `grid-column:${x.col};grid-row:${x.lig}` }, x.t)));
      p.cases.forEach(c => sch.append(h("button", { class: "case-sch " + (d.c[c.id] ? "pleine " : "") + cls(fini, ok(c)), style: `grid-column:${c.col};grid-row:${c.lig}`, disabled: fini,
        onclick: () => { if (actif) { for (const k in d.c) if (d.c[k] === actif) delete d.c[k]; d.c[c.id] = actif; actif = null; } else delete d.c[c.id]; dessiner(); } },
        d.c[c.id] || (c.indice || "?"), fini && !ok(c) ? h("small", {}, c.accepte.join(" / ")) : null)));
      if (!fini) p.etiquettes.filter(e => !Object.values(d.c).includes(e)).forEach(e => pool.append(h("button", { class: "pill" + (actif === e ? " on" : ""), onclick: () => { actif = e; dessiner(); } }, e)));
    }
    dessiner();
    return {
      el: h("div", {}, !fini ? h("p", { class: "aide" }, "Clique sur un acteur, puis sur la case où il doit aller. Clique sur une case remplie pour la vider.") : null, pool, sch),
      manque: () => p.cases.some(c => !d.c[c.id]) ? "Place un acteur dans chaque case du schéma." : null,
      score: () => [p.cases.filter(ok).length, p.cases.length]
    };
  };

  // ---------- navigation ----------
  const nav = $("#etapes"), zone = $("#zone");
  const blocs = A.blocs.concat([{ id: "certificat", type: "certificat", titre: "Mon certificat" }]);
  let courant = 0;
  const court = t => t.split(" — ")[0];

  function majNav() {
    nav.innerHTML = "";
    blocs.forEach((b, i) => {
      const r = etat.res[b.id];
      const badge = b.type === "cours" ? (r ? "✓" : "") : r ? (r.max ? `${r.pts}/${r.max}` : "✓") : "";
      nav.append(h("button", { class: "etape" + (i === courant ? " actif" : "") + (r ? " fait" : ""), onclick: () => ouvrir(i) },
        h("span", { class: "n" }, b.type === "certificat" ? "★" : String(i + 1)), h("span", { class: "t" }, court(b.titre)), badge ? h("span", { class: "b" }, badge) : null));
    });
  }

  function ouvrir(i, defile = true) {
    courant = i; majNav();
    const b = blocs[i];
    zone.innerHTML = "";
    zone.append(h("header", { class: "bloc-tete" }, h("h2", {}, b.titre), b.duree ? h("span", { class: "duree" }, "⏱ " + b.duree) : null));
    if (b.consigne) zone.append(h("p", { class: "consigne" }, b.consigne));
    if (b.type === "cours") cours(b); else if (b.type === "certificat") certificat(); else exercice(b);
    if (defile) window.scrollTo({ top: $("#activite").offsetTop - 70, behavior: "smooth" });
  }

  function cours(b) {
    const t = document.getElementById("cours-" + b.id);
    zone.append(h("div", { class: "cours", html: t ? t.innerHTML : "" }));
    const suiv = blocs[courant + 1];
    zone.append(h("div", { class: "pied-bloc" }, h("button", { class: "btn", onclick: () => { etat.res[b.id] = { lu: true }; sauver(); ouvrir(courant + 1); } }, "J'ai lu le cours → " + court(suiv.titre))));
  }

  function exercice(b) {
    const res = etat.res[b.id], fini = !!res;
    const det = fini ? res.detail : b.parties.map(() => ({}));
    const g = 1 + (etat.essais[b.id] || 0);
    const objs = b.parties.map((p, k) => {
      const o = P[p.type](p, det[k], fini, g + k);
      zone.append(h("section", { class: "partie" }, p.titre ? h("h3", { class: "sous" }, p.titre) : null, p.consigne ? h("p", { class: "consigne-p" }, p.consigne) : null, o.el));
      return o;
    });
    const pied = h("div", { class: "pied-bloc" });
    if (fini) {
      const notees = (res.detailParts || []).map((x, k) => x[1] ? `${b.parties[k].titre ? court(b.parties[k].titre) : "Partie " + (k + 1)} : ${x[0]}/${x[1]}` : null).filter(Boolean);
      if (notees.length > 1) zone.append(h("p", { class: "detail-score" }, notees.join(" · ")));
      if (res.max) pied.append(h("p", { class: "score " + (res.pts / res.max >= .7 ? "ok" : "ko") }, `Résultat : ${res.pts} / ${res.max}`));
      pied.append(h("button", { class: "btn sec", onclick: () => { delete etat.res[b.id]; sauver(); ouvrir(courant, false); } }, "↺ Recommencer"),
        h("button", { class: "btn", onclick: () => ouvrir(courant + 1) }, courant + 1 < blocs.length - 1 ? "Activité suivante →" : "Mon certificat →"));
    } else {
      pied.append(h("button", { class: "btn", onclick: () => {
        for (const o of objs) { const m = o.manque(); if (m) return alerte(m); }
        const parts = objs.map(o => o.score());
        etat.essais[b.id] = (etat.essais[b.id] || 0) + 1;
        etat.res[b.id] = { pts: parts.reduce((s, x) => s + x[0], 0), max: parts.reduce((s, x) => s + x[1], 0), detail: det, detailParts: parts,
          textes: objs.map(o => o.texte ? o.texte() : null).filter(Boolean) };
        sauver(); ouvrir(courant, false);
      } }, "Valider mes réponses"));
    }
    zone.append(pied);
  }

  // ---------- certificat ----------
  function code(texte) {
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
    const cible = h("div");
    zone.append(h("div", { class: "pied-bloc" }, h("button", { class: "btn", onclick: () => {
      if (!etat.nom || etat.nom.length < 2) return alerte("Écris ton prénom et l'initiale de ton nom.");
      if (faits.length < notes.length) return alerte(`Il te reste ${notes.length - faits.length} activité(s) à valider avant d'obtenir ton certificat.`);
      const now = new Date(), date = now.toLocaleDateString("fr-FR"), heure = now.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
      const notees = faits.filter(b => etat.res[b.id].max);
      const tot = notees.reduce((s, b) => s + etat.res[b.id].pts, 0), max = notees.reduce((s, b) => s + etat.res[b.id].max, 0);
      const c = code(`${A.id}|${etat.nom}|${notees.map(b => `${b.id}:${etat.res[b.id].pts}/${etat.res[b.id].max}`).join(";")}|${date}`);
      const lignes = faits.map(b => [b.titre, etat.res[b.id].max ? `${etat.res[b.id].pts} / ${etat.res[b.id].max}` : "fait ✓", `${etat.essais[b.id] || 1} essai(s)`]);
      const textes = faits.flatMap(b => etat.res[b.id].textes || []);
      const total = max ? `Total : ${tot} / ${max}  (${Math.round(tot / max * 100)} %)` : "";
      cible.innerHTML = "";
      cible.append(h("div", { class: "certif" },
        h("p", { class: "certif-sur" }, "Seconde EMNB · Lycée des métiers Urbain Vitry"), h("h3", {}, "Certificat de séance"),
        h("p", { class: "certif-seance" }, A.titre), h("p", { class: "certif-nom" }, etat.nom),
        h("table", {}, ...lignes.map(([t, s, e]) => h("tr", {}, h("td", {}, t), h("td", {}, s), h("td", { class: "ess" }, e)))),
        textes.length ? h("div", { class: "certif-textes" }, ...textes.map(t => h("p", {}, "« " + t + " »"))) : null,
        total ? h("p", { class: "certif-total" }, total) : null,
        h("p", { class: "certif-pied" }, `${date} à ${heure} · Code de contrôle : `, h("b", {}, c))),
        h("div", { class: "pied-bloc" }, h("button", { class: "btn", onclick: () => imageCertificat({ lignes, textes, total, pied: `${date} à ${heure}`, code: c }) }, "⬇ Télécharger mon certificat (image)"),
          h("span", { class: "aide" }, "Puis dépose le fichier sur l'ENT.")));
    } }, "Afficher mon certificat")), cible);
  }

  function imageCertificat(d) {
    const W = 1200, F = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif";
    const tmp = document.createElement("canvas").getContext("2d");
    const couper = (t, px, larg) => { tmp.font = `400 ${px}px ${F}`; const out = []; let l = "";
      for (const m of t.split(" ")) { const e = l ? l + " " + m : m; if (tmp.measureText(e).width > larg && l) { out.push(l); l = m; } else l = e; } if (l) out.push(l); return out; };
    const blocsTxt = d.textes.map(t => couper("« " + t + " »", 20, W - 300));
    const H = 700 + d.lignes.length * 56 + blocsTxt.reduce((s, b) => s + b.length * 28 + 14, 0);
    const cv = document.createElement("canvas"); cv.width = W; cv.height = H;
    const x = cv.getContext("2d");
    const txt = (t, px, y, o = {}) => { x.font = `${o.p || 400} ${px}px ${F}`; x.fillStyle = o.c || "#1c2228"; x.textAlign = o.a || "center"; x.fillText(t, o.x ?? W / 2, y); };
    x.fillStyle = "#f4f2ec"; x.fillRect(0, 0, W, H);
    x.strokeStyle = "#c4521f"; x.lineWidth = 6; x.strokeRect(30, 30, W - 60, H - 60); x.lineWidth = 2; x.strokeRect(44, 44, W - 88, H - 88);
    x.fillStyle = "#c4521f"; x.beginPath(); x.roundRect ? x.roundRect(W / 2 - 34, 78, 68, 68, 12) : x.rect(W / 2 - 34, 78, 68, 68); x.fill();
    txt("2de", 30, 124, { p: 800, c: "#fff" });
    txt("SECONDE EMNB · LYCÉE DES MÉTIERS URBAIN VITRY", 20, 186, { p: 600, c: "#5d6670" });
    txt("Certificat de séance", 52, 252, { p: 800, c: "#c4521f" });
    txt(A.titre, 28, 298, { p: 600 });
    txt(etat.nom, 60, 388, { p: 800 });
    let y = 460; x.strokeStyle = "#dedad0"; x.lineWidth = 1.5;
    d.lignes.forEach(([t, s, e]) => { txt(t.length > 52 ? t.slice(0, 50) + "…" : t, 24, y, { a: "left", x: 140 }); txt(s, 26, y, { a: "right", x: 900, p: 700 }); txt(e, 18, y, { a: "right", x: W - 140, c: "#5d6670" });
      x.beginPath(); x.moveTo(140, y + 20); x.lineTo(W - 140, y + 20); x.stroke(); y += 56; });
    blocsTxt.forEach(b => { y += 14; b.forEach(l => { txt(l, 20, y + 10, { c: "#24527a" }); y += 28; }); });
    if (d.total) txt(d.total, 34, y + 46, { p: 800 });
    txt(`${d.pied}  ·  Code de contrôle : ${d.code}`, 22, y + 100, { c: "#5d6670" });
    const fichier = `certificat_${A.id}_${norm(etat.nom).replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}.png`;
    cv.toBlob(blob => { const a = h("a", { href: URL.createObjectURL(blob), download: fichier }); document.body.append(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000); }, "image/png");
  }

  function alerte(msg) {
    let a = $("#alerte"); if (!a) { a = h("div", { id: "alerte", role: "status" }); document.body.append(a); }
    a.textContent = msg; a.classList.add("vu"); clearTimeout(a._t); a._t = setTimeout(() => a.classList.remove("vu"), 3500);
  }

  $("#raz").onclick = () => { if (confirm("Effacer toutes tes réponses de cette séance ?")) { etat = { nom: "", res: {}, essais: {} }; sauver(); ouvrir(0); } };
  ouvrir(0, false);
})();
