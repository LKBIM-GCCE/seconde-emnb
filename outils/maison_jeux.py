"""La maison des jeux : coupe d'une maison où chaque partie ouvre un jeu de découverte."""

# slug -> (emoji, description courte, x, y de la pastille, forme de survol SVG)
ZONES = {
    "couverture": ("☔", "Tuiles, charpente, toiture-terrasse : ce qui protège de la pluie.", 490, 175,
                   '<polygon points="180,262 490,104 800,262 776,262 490,128 204,262"/>'),
    "gros-oeuvre": ("🧱", "Fondations, murs, planchers : le squelette de la maison.", 236, 572,
                    '<path d="M196 528h86v52h-86zM698 528h86v52h-86zM220 250h22v270h-22zM738 250h22v270h-22z"/>'),
    "menuiseries": ("🚪", "Fenêtres et portes : composition, pose, ouvertures.", 231, 448,
                    '<rect x="214" y="410" width="34" height="72" rx="3"/><rect x="732" y="290" width="34" height="60" rx="3"/>'),
    "platrerie": ("🔨", "Cloisons, doublages et plafonds en plaques de plâtre.", 610, 300,
                  '<rect x="496" y="262" width="12" height="110"/><rect x="508" y="262" width="230" height="10"/>'),
    "electricite": ("⚡", "Prises, tableau électrique, salle de bains : les règles du courant.", 545, 440,
                    '<rect x="516" y="420" width="44" height="58" rx="4"/><circle cx="620" cy="410" r="16"/>'),
    "plomberie": ("🚿", "Arrivée d'eau, évacuations, appareils sanitaires.", 330, 318,
                  '<rect x="252" y="320" width="140" height="52" rx="10"/><rect x="408" y="300" width="60" height="72"/>'),
    "sols": ("🟫", "Carrelage, parquet, sol souple : ce qu'il y a sous tes pieds.", 330, 506,
             '<rect x="242" y="500" width="258" height="14"/>'),
    "peinture": ("🎨", "Peintures, enduits, défauts à reconnaître : la finition des murs.", 430, 440,
                 '<rect x="380" y="398" width="104" height="96" rx="4"/>'),
    "lexique": ("📖", "Le vocabulaire du dessinateur : parle comme un pro.", 92, 300,
                '<rect x="40" y="250" width="110" height="140" rx="6"/>'),
    "incendie": ("🧯", "Issues de secours, extincteurs, désenfumage dans un ERP.", 712, 470,
                 '<rect x="696" y="446" width="30" height="58" rx="6"/>'),
    "pmr": ("♿", "Rampes, portes, sanitaires : un bâtiment accessible à tous.", 880, 498,
            '<polygon points="762,520 940,544 940,556 762,532"/>'),
}

DECOR = """
<defs>
  <linearGradient id="mj-ciel" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#d9e8ff"/><stop offset="1" stop-color="#f4f8ff"/></linearGradient>
  <pattern id="mj-tuiles" width="22" height="12" patternUnits="userSpaceOnUse"><rect width="22" height="12" fill="#e2683a"/><path d="M0 11h22M11 0v6" stroke="#b9481f" stroke-width="1.4"/></pattern>
  <pattern id="mj-parquet" width="24" height="8" patternUnits="userSpaceOnUse"><rect width="24" height="8" fill="#c9965a"/><path d="M0 7.5h24M12 0v8" stroke="#a5743d" stroke-width="1"/></pattern>
  <pattern id="mj-carrelage" width="16" height="8" patternUnits="userSpaceOnUse"><rect width="16" height="8" fill="#e9eef3"/><path d="M0 7.5h16M8 0v8" stroke="#b9c4cf" stroke-width="1"/></pattern>
  <pattern id="mj-terre" width="18" height="18" patternUnits="userSpaceOnUse"><rect width="18" height="18" fill="#b98e5f"/><circle cx="4" cy="5" r="1.4" fill="#9c7447"/><circle cx="13" cy="12" r="1.6" fill="#9c7447"/></pattern>
  <pattern id="mj-beton" width="10" height="10" patternUnits="userSpaceOnUse"><rect width="10" height="10" fill="#c7ccd3"/><circle cx="3" cy="3" r="1" fill="#9aa2ad"/><circle cx="8" cy="7" r=".8" fill="#9aa2ad"/></pattern>
</defs>
<rect width="1000" height="640" fill="url(#mj-ciel)"/>
<circle cx="900" cy="80" r="38" fill="#ffc52e"/><g stroke="#ffc52e" stroke-width="4" stroke-linecap="round"><path d="M900 22v-12M900 150v-12M842 80h-12M970 80h-12M859 39l-8-8M949 129l-8-8M859 121l-8 8M949 31l-8 8"/></g>
<g fill="#fff" opacity=".9"><ellipse cx="160" cy="90" rx="48" ry="16"/><ellipse cx="196" cy="80" rx="34" ry="18"/><ellipse cx="640" cy="60" rx="40" ry="13"/></g>
<!-- sol -->
<rect y="540" width="1000" height="100" fill="url(#mj-terre)"/><rect y="532" width="1000" height="10" fill="#7fbf6a"/>
<!-- arbre -->
<rect x="958" y="430" width="12" height="104" fill="#8a5a33"/><circle cx="964" cy="420" r="34" fill="#5fae5b"/>
<!-- fondations -->
<rect x="196" y="528" width="86" height="52" fill="url(#mj-beton)" stroke="#6b7480"/><rect x="698" y="528" width="86" height="52" fill="url(#mj-beton)" stroke="#6b7480"/>
<!-- dallage RDC, plancher R+1 -->
<rect x="220" y="512" width="540" height="16" fill="url(#mj-beton)" stroke="#6b7480"/>
<rect x="220" y="372" width="540" height="14" fill="url(#mj-beton)" stroke="#6b7480"/>
<!-- intérieurs -->
<rect x="242" y="386" width="496" height="126" fill="#fbf7ee"/><rect x="242" y="262" width="496" height="110" fill="#f7fbff"/>
<rect x="242" y="500" width="258" height="12" fill="url(#mj-parquet)"/><rect x="500" y="500" width="238" height="12" fill="url(#mj-carrelage)"/>
<!-- murs extérieurs -->
<rect x="220" y="250" width="22" height="262" fill="#e8d3b5" stroke="#9b8466"/><rect x="738" y="250" width="22" height="262" fill="#e8d3b5" stroke="#9b8466"/>
<!-- menuiseries -->
<rect x="218" y="414" width="26" height="64" fill="#bfe3ff" stroke="#2c5e8f" stroke-width="3"/><path d="M231 414v64" stroke="#2c5e8f" stroke-width="2"/>
<rect x="736" y="294" width="26" height="52" fill="#bfe3ff" stroke="#2c5e8f" stroke-width="3"/>
<rect x="738" y="420" width="22" height="92" fill="#9c6b3d" stroke="#6e4a27"/><circle cx="742" cy="468" r="2.5" fill="#ffd25a"/>
<!-- plafond suspendu + cloison plâtre -->
<rect x="508" y="262" width="230" height="8" fill="#ffffff" stroke="#b9c4cf"/><g stroke="#b9c4cf" stroke-width="1.5"><path d="M540 250v12M600 250v12M660 250v12M720 250v12"/></g>
<rect x="496" y="262" width="12" height="110" fill="#ffffff" stroke="#b9c4cf"/><path d="M502 270v96" stroke="#9aa2ad" stroke-dasharray="4 4"/>
<!-- salle de bains R+1 -->
<rect x="258" y="332" width="128" height="34" rx="12" fill="#ffffff" stroke="#7da6c9" stroke-width="2"/><path d="M270 334h104" stroke="#bfe3ff" stroke-width="6"/>
<path d="M376 300v32" stroke="#8a97a8" stroke-width="3"/><path d="M366 300h20" stroke="#8a97a8" stroke-width="3"/>
<rect x="414" y="330" width="46" height="10" rx="4" fill="#fff" stroke="#7da6c9" stroke-width="2"/><rect x="430" y="340" width="14" height="32" fill="#e9eef3" stroke="#7da6c9"/>
<path d="M437 320v10" stroke="#8a97a8" stroke-width="3"/><path d="M290 372v156M300 372v156" stroke="#3a86c8" stroke-width="3"/><path d="M450 372v156" stroke="#8a97a8" stroke-width="5"/>
<!-- chambre R+1 -->
<rect x="560" y="336" width="120" height="30" rx="5" fill="#9fb7e3"/><rect x="560" y="326" width="34" height="16" rx="5" fill="#fff"/>
<!-- mur peint RDC -->
<rect x="384" y="402" width="96" height="88" fill="#ffd8c2"/><rect x="384" y="402" width="40" height="88" fill="#ffb995"/>
<g transform="translate(452 432) rotate(-25)"><rect width="34" height="12" rx="5" fill="#f2600f"/><path d="M17 12v22" stroke="#555" stroke-width="3"/></g>
<!-- canapé -->
<rect x="262" y="468" width="96" height="32" rx="8" fill="#5f7fb8"/><rect x="262" y="456" width="96" height="16" rx="8" fill="#7895c9"/>
<!-- électricité -->
<rect x="520" y="424" width="36" height="50" rx="4" fill="#ffffff" stroke="#55637e" stroke-width="2"/><g fill="#55637e"><rect x="526" y="432" width="5" height="12"/><rect x="535" y="432" width="5" height="12"/><rect x="544" y="432" width="5" height="12"/><rect x="526" y="452" width="5" height="12"/><rect x="535" y="452" width="5" height="12"/></g>
<path d="M620 386v12" stroke="#55637e" stroke-width="2"/><path d="M606 398h28l-6 14h-16z" fill="#ffc52e" stroke="#c9970f"/>
<!-- escalier -->
<g fill="#d7b98d" stroke="#9b8466"><path d="M590 512h140v-14h-120v-14h-14v-14h-14v-14h-14v-14h-14z" opacity="0"/>
<rect x="640" y="498" width="96" height="14"/><rect x="656" y="484" width="80" height="14"/><rect x="672" y="470" width="64" height="14"/><rect x="688" y="456" width="48" height="14"/>
<rect x="704" y="442" width="32" height="14"/><rect x="720" y="428" width="16" height="14"/></g>
<!-- incendie -->
<rect x="700" y="452" width="20" height="40" rx="7" fill="#d93025"/><rect x="704" y="446" width="12" height="8" fill="#333"/><rect x="664" y="396" width="44" height="18" rx="2" fill="#1f8a5b"/><text x="686" y="409" font-size="10" fill="#fff" text-anchor="middle" font-weight="700">SORTIE</text>
<!-- toiture -->
<polygon points="180,262 490,104 800,262" fill="url(#mj-tuiles)" stroke="#9c3d17" stroke-width="3"/>
<polygon points="232,250 490,126 748,250" fill="#f0e2c8" stroke="#a47d4c" stroke-width="2"/>
<path d="M490 126v124M360 188l130 62M620 188l-130 62" stroke="#a47d4c" stroke-width="5"/>
<rect x="242" y="250" width="496" height="12" fill="#e7d6b8" stroke="#a47d4c"/>
<!-- rampe PMR -->
<polygon points="762,520 940,544 940,556 762,532" fill="#c7ccd3" stroke="#6b7480"/><path d="M770 506 L936 528" stroke="#55637e" stroke-width="3"/><path d="M790 509v15M850 517v15M910 525v15" stroke="#55637e" stroke-width="2"/>
<!-- planche du dessinateur (lexique) -->
<rect x="44" y="254" width="102" height="132" rx="4" fill="#ffffff" stroke="#1f55d6" stroke-width="2"/>
<g stroke="#1f55d6" stroke-width="1.5" fill="none"><rect x="58" y="270" width="74" height="54"/><path d="M58 300h40v24M98 270v30"/><path d="M58 340h74M58 350h50M58 360h64"/></g>
<path d="M70 386l-14 148M120 386l14 148" stroke="#8a5a33" stroke-width="5"/>
<!-- ordinateur (Mission IFC) -->
<rect x="40" y="470" width="110" height="8" fill="#8a5a33"/><path d="M52 478v56M138 478v56" stroke="#8a5a33" stroke-width="5"/>
<rect x="62" y="428" width="66" height="42" rx="3" fill="#13223f"/><rect x="66" y="432" width="58" height="34" fill="#1f55d6"/><path d="M80 456l15-12 15 12z" fill="#ffc52e"/><rect x="54" y="468" width="82" height="5" rx="2" fill="#55637e"/>
"""

IFC = ("💻", "La maquette numérique en jeu (SEQ03) : classes, arborescence, propriétés.", 95, 440, '<rect x="40" y="420" width="110" height="60" rx="6"/>')
