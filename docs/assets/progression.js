/* Affiche l'avancement de l'élève (enregistré dans son navigateur) sur les pages de séquence et de séance. */
(function () {
  function lire(id) { try { return JSON.parse(localStorage.getItem("emnb-" + id)) || null; } catch (e) { return null; } }
  function bilan(id, nb) {
    const st = lire(id); if (!st || !st.res) return null;
    const faits = Object.entries(st.res).filter(([k, r]) => !r.lu);
    let pts = 0, max = 0; faits.forEach(([k, r]) => { pts += r.pts || 0; max += r.max || 0; });
    return { faits: faits.length, nb: nb, pts, max };
  }
  document.querySelectorAll("[data-act]").forEach(el => {
    const b = bilan(el.dataset.act, +el.dataset.nb || 0); if (!b || !b.faits) return;
    if (b.faits >= b.nb) { el.textContent = "Terminée" + (b.max ? ` · ${Math.round(b.pts / b.max * 100)} %` : ""); el.classList.add("fini"); }
    else { el.textContent = `En cours · ${b.faits}/${b.nb}`; el.classList.add("encours"); }
  });
  document.querySelectorAll("[data-acts]").forEach(el => {
    const l = el.dataset.acts.split(" ").filter(Boolean).map(x => x.split(":"));
    const fin = l.filter(([id, nb]) => { const b = bilan(id, +nb); return b && b.faits >= b.nb; }).length;
    const deb = l.filter(([id, nb]) => { const b = bilan(id, +nb); return b && b.faits; }).length;
    if (!deb) return;
    el.innerHTML = `<i style="width:${Math.round(fin / l.length * 100)}%"></i><span>${fin} séance${fin > 1 ? "s" : ""} terminée${fin > 1 ? "s" : ""} sur ${l.length}</span>`;
    el.classList.add("vu");
  });
})();
