// Vues et actions de l’Académie et des Légendes. Chargé avant le moteur principal.
const ACADEMY_GROUPS = [
  ["U10", "U10"], ["U12", "U12"], ["U15", "U15"], ["U18", "U18"],
  ["reserve", "Réserve"], ["first", "Première équipe"]
];
let ACAD_GROUP = "U18";
let ACAD_PICK = "";

function academyGroupForAge(age) {
  if (age <= 10) return "U10";
  if (age <= 12) return "U12";
  if (age <= 15) return "U15";
  if (age <= 18) return "U18";
  return "reserve";
}
function academyGroupLabel(key) {
  return (ACADEMY_GROUPS.find(x => x[0] === key) || [key, key])[1];
}
function academyKey(p, i=0) {
  return String(p.key || `${p.name}|${p.age}|${p.nat}|${i}`);
}
function academyAttributes(p) {
  const base = (Number(p.ovr) || 45) / 5 + ((Number(p.age) || 14) - 14) * .06;
  const grp = (POS[p.pos] && POS[p.pos].grp) || "BU";
  const tech = [
    ["Centres", "centres", grp === "LAT" || grp === "AIL" ? 1.5 : 0],
    ["Contrôle de balle", "controle", grp === "AIL" || grp === "MOC" ? 1 : 0],
    ["Corners", "corners", grp === "MOC" ? 1 : 0],
    ["Coups francs", "coups-francs", grp === "MOC" ? 1 : 0],
    ["Dribble", "dribble", grp === "AIL" ? 1.5 : 0],
    ["Finition", "finition", grp === "BU" ? 1.5 : 0],
    ["Passe", "passe", grp === "MIL" || grp === "MOC" ? 1 : 0],
    ["Tirs", "tirs", grp === "BU" ? 1 : 0]
  ];
  const mental = [
    ["Agressivité", "agressivite", grp === "DC" ? 1 : 0],
    ["Anticipation", "anticipation", grp === "DC" || grp === "GB" ? 1 : 0],
    ["Appels de balle", "appels", grp === "BU" || grp === "AIL" ? 1 : 0],
    ["Concentration", "concentration", 0],
    ["Décisions", "decisions", grp === "MIL" ? 1 : 0],
    ["Détermination", "determination", 0],
    ["Jeu collectif", "collectif", grp === "MIL" ? 1 : 0],
    ["Vision", "vision", grp === "MOC" || grp === "MIL" ? 1 : 0]
  ];
  const physical = [
    ["Accélération", "acceleration", grp === "AIL" ? 1.5 : 0],
    ["Agilité", "agilite", grp === "AIL" || grp === "GB" ? 1 : 0],
    ["Équilibre", "equilibre", 0],
    ["Détente", "detente", grp === "GB" || grp === "DC" ? 1 : 0],
    ["Endurance", "endurance", grp === "LAT" || grp === "MIL" ? 1 : 0],
    ["Force", "force", grp === "DC" || grp === "BU" ? 1 : 0],
    ["Vitesse", "vitesse", grp === "AIL" || grp === "LAT" ? 1 : 0]
  ];
  const make = list => list.map(([label, key, bias]) => {
    const h = Math.abs(hashStr(`${p.name}|${key}|${p.age}`));
    const jitter = ((h % 7) - 3) * .48;
    return { label, value: clamp(Math.round(base + jitter + bias), 1, 20) };
  });
  return { tech: make(tech), mental: make(mental), physical: make(physical) };
}
function academyWeightedAverage(attrs) {
  const mean = a => a.reduce((s, x) => s + x.value, 0) / Math.max(1, a.length);
  return (mean(attrs.tech) * .4 + mean(attrs.mental) * .35 + mean(attrs.physical) * .25).toFixed(2);
}
function academyMakeYouth(nat, age, options={}) {
  const club = TEAMS[S.me.club];
  const pool = poolOfCountry(nat || club.country);
  const pos = options.pos || pick(["GB", "DC", "DC", "LAT", "MDC", "MC", "MOC", "AIL", "AIL", "BU", "BU"]);
  const ovr = options.ovr == null
    ? clamp(Math.round(tStr(S.me.club) - 24 + (age - 14) * .45 + Math.random() * 12 - 6), 35, 76)
    : options.ovr;
  const pot = options.pot == null ? clamp(ovr + RI(8, 24), ovr, 96) : options.pot;
  const name = options.name || genName(pool);
  const p = {
    key: `academy-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
    name, pos, ovr, age, pot, nat: nat || club.country, city: club.city || TEAMS[S.me.club].name,
    foot: Math.random() < .22 ? "Gaucher" : "Droitier",
    height: Math.round(104 + age * 3.35 + Math.random() * 5),
    weight: Math.round(14 + age * 1.6 + Math.random() * 5), signed: false
  };
  return p;
}
function academyEnsureData() {
  if (!S || !isCoach() || !S.me.club) return;
  const C = S.coach;
  C.yth = Array.isArray(C.yth) ? C.yth : [];
  C.academyProspects = Array.isArray(C.academyProspects) ? C.academyProspects : [];
  let changed = false;
  if (!C.academySeeded) {
    if (!C.yth.length) {
      [9, 10, 11, 12, 13, 14, 15, 16, 17, 18].forEach(age => C.yth.push(academyMakeYouth(TEAMS[S.me.club].country, age)));
      C.yth.sort((a, b) => b.pot - a.pot);
    }
    if (!C.academyProspects.length) {
      [10, 11, 13, 14, 16, 17, 18].forEach(age => C.academyProspects.push(academyMakeYouth(TEAMS[S.me.club].country, age)));
    }
    C.academySeeded = true;
    changed = true;
  }
  if (changed) save();
}
function academyLauncher() {
  const count = S.coach.yth ? S.coach.yth.filter(y => !y.signed).length : 0;
  return `<div class="card academy-launch"><div><span class="eyebrow">Formation · ${count} jeune${count === 1 ? "" : "s"}</span><h3>Le centre de formation</h3><p class="muted small">Groupes U10 à U18, fiches détaillées et recrutement après observation.</p></div><button class="btn sm gold" data-tab="academy">Ouvrir l’Académie</button></div>`;
}
function academyRows(group) {
  const C = S.coach;
  if (group === "first") {
    return clubReal(S.me.club).map(p => ({kind:"pro", player:p, pid:p.id, token:`pro:${p.id}`})).sort((a,b)=>pOvr(b.player)-pOvr(a.player));
  }
  const youths = (C.yth || []).map((p,i) => ({kind:"youth", player:p, index:i, token:`youth:${encodeURIComponent(academyKey(p,i))}`}));
  const prospects = (C.academyProspects || []).map((p,i) => ({kind:"prospect", player:p, index:i, token:`prospect:${encodeURIComponent(academyKey(p,i))}`}));
  if (group === "reserve") return [...youths.filter(x => x.player.signed || x.player.age > 18), ...prospects.filter(x => x.player.age > 18)].sort((a,b)=>(b.player.ovr||0)-(a.player.ovr||0));
  return [...youths.filter(x => !x.player.signed && academyGroupForAge(x.player.age) === group),
    ...prospects.filter(x => academyGroupForAge(x.player.age) === group)]
    .sort((a,b)=>(b.player.pot||b.player.ovr||0)-(a.player.pot||a.player.ovr||0));
}
function academySelect(token) { ACAD_PICK = token; render(); }
function academySetGroup(group) { ACAD_GROUP = group; ACAD_PICK = ""; render(); }
function academyDiscover() {
  if (!S || !isCoach() || !S.me.club) return;
  const C = S.coach;
  C.academyProspects = C.academyProspects || [];
  if (C.academyProspects.length >= 30) { toast("La liste d’observation est pleine. Fais d’abord une observation."); return; }
  const range = {U10:[9,10], U12:[11,12], U15:[13,15], U18:[16,18], reserve:[19,21], first:[16,18]}[ACAD_GROUP] || [13,17];
  const p = academyMakeYouth(TEAMS[S.me.club].country, RI(range[0], range[1]));
  C.academyProspects.unshift(p); if (ACAD_GROUP === "first") ACAD_GROUP = "U18"; ACAD_PICK = `prospect:${encodeURIComponent(academyKey(p,0))}`;
  save(); render(); toast(`${p.name} ajouté à la liste d’observation.`);
}
function academyObserve(index) {
  if (!S || !isCoach()) return;
  const C = S.coach, p = C.academyProspects && C.academyProspects[index];
  if (!p) return;
  if (p.lastObservedDay != null && S.day - p.lastObservedDay < 7) { toast("Attends une semaine avant une nouvelle observation."); return; }
  const rating = Math.round(clamp(5.15 + ((p.pot || p.ovr) - 60) * .035 + Math.random() * 3.35, 4.5, 9.9) * 10) / 10;
  p.lastObservedDay = S.day;
  p.lastObservedRating = rating;
  if (rating >= 7) {
    const admitted = {...p, signed:false, admittedDay:S.day};
    C.yth = C.yth || []; C.yth.unshift(admitted); C.academyProspects.splice(index, 1);
    ACAD_GROUP = academyGroupForAge(admitted.age);
    ACAD_PICK = `youth:${encodeURIComponent(academyKey(admitted,0))}`;
    addNews(`${admitted.name} intègre l’Académie après une observation notée ${rating.toFixed(1)}/10.`);
    toast(`${admitted.name} entre au centre de formation · ${rating.toFixed(1)}/10`);
  } else {
    toast(`Observation terminée : ${rating.toFixed(1)}/10. Il faudra au moins 7,0 pour intégrer l’Académie.`);
  }
  save(); render();
}
function academyStatsMarkup(items) {
  return items.map(([title, rows]) => `<section class="acad-stat-card"><h3>${title}</h3>${rows.map(x => `<div class="acad-stat"><span>${x.label}</span><i><b style="width:${x.value * 5}%"></b></i><strong>${x.value}</strong></div>`).join("")}</section>`).join("");
}
function academyPortrait(item, large=false) {
  const p = item.player;
  if (item.kind === "pro") return facePlayer(p.name, p.nat).replace('class="face sm"', `class="face ${large ? "academy-face" : "academy-face-sm"}"`);
  return faceImg(faceIdx(p.name, poolOfCountry(p.nat)), large ? "academy-face" : "academy-face-sm");
}
function academyProfile(item) {
  if (!item) return `<div class="card acad-empty"><span class="eyebrow">Fiche du joueur</span><p>Aucun joueur dans ce groupe pour l’instant. Ajoute un talent à observer ou change de catégorie.</p></div>`;
  const p = item.player;
  const isPro = item.kind === "pro";
  const age = isPro ? pAge(p) : p.age;
  const ovr = isPro ? pOvr(p) : p.ovr;
  const attrs = academyAttributes({...p, age, ovr});
  const avg = academyWeightedAverage(attrs);
  const nat = NATIONS[p.nat] || NATIONS[TEAMS[S.me.club].country];
  const position = POS[p.pos] ? POS[p.pos].name : (p.pos || "Joueur");
  const status = item.kind === "prospect" ? "PROFIL · À OBSERVER" : isPro ? "PROFIL · ÉQUIPE PREMIÈRE" : p.signed ? "PROFIL · RÉSERVE" : `PROFIL · ${academyGroupLabel(academyGroupForAge(age))}`;
  const city = p.city || TEAMS[S.me.club].city || TEAMS[S.me.club].name;
  const foot = p.foot || "Droitier";
  const measured = p.height ? `${p.height} cm · ${p.weight || "—"} kg` : "Données physiques à renseigner";
  let action = "";
  if (item.kind === "prospect") {
    const wait = p.lastObservedDay != null && S.day - p.lastObservedDay < 7;
    const previous = p.lastObservedRating == null ? "" : `<p class="acad-observation-result">Dernière observation : <b>${p.lastObservedRating.toFixed(1)}/10</b>${p.lastObservedRating >= 7 ? " · admissible" : " · seuil requis : 7,0"}</p>`;
    action = `<div class="acad-observe"><span class="eyebrow">Une place dans votre Académie</span><p>Observe un match complet. Avec une note finale de <b>7,0/10 ou plus</b>, le joueur rejoint automatiquement le centre.</p>${previous}<button class="btn gold block" data-acadobserve="${item.index}" ${wait ? "disabled" : ""}>${wait ? "Nouvelle observation dans une semaine" : "Observer un match complet"}</button><small>La note est générée par une simulation d’observation et reste enregistrée dans la carrière.</small></div>`;
  } else if (item.kind === "youth" && !p.signed && age >= 16) {
    action = `<button class="btn gold block" style="margin-top:12px" data-ysign="${item.index}">Proposer un contrat professionnel</button>`;
  } else if (item.kind === "youth" && !p.signed) {
    action = `<p class="acad-training-note">En formation — la promotion professionnelle est disponible à partir de 16 ans.</p>`;
  } else if (item.kind === "youth" && p.signed) {
    action = `<span class="status on">Sous contrat au club</span>`;
  }
  return `<article class="card acad-profile"><div class="acad-profile-head">${academyPortrait(item,true)}<div class="acad-player-main"><span class="eyebrow">${status}</span><h2>${esc(p.name)}</h2><p>${esc(TEAMS[S.me.club].name)} · ${esc(position)}</p><div class="acad-facts"><span>${age} ans</span><span>${esc(city)}</span><span>${nat ? nat.flag+" "+esc(nat.name) : ""}</span><span>${esc(foot)}</span><span>${esc(measured)}</span></div></div></div>
    <div class="acad-average"><div><strong>${avg}</strong><span>Moyenne pondérée / 20</span></div><div><strong>${ovr}</strong><span>GEN</span></div><div><strong>${p.pot || (ovr + 4)}</strong><span>Potentiel</span></div></div>
    <div class="acad-skills">${academyStatsMarkup([["Technique",attrs.tech],["Mental",attrs.mental],["Physique",attrs.physical]])}</div>${action}</article>`;
}
function viewAcademy() {
  if (!isCoach() || !S.me.club) return `<section class="view"><div class="card"><h2 class="h2">Centre de formation</h2><p class="muted">L’Académie est disponible dans une carrière entraîneur avec un club.</p></div></section>`;
  academyEnsureData();
  const C = S.coach, club = TEAMS[S.me.club], nat = NATIONS[club.country];
  const lid = teamLeague(S.me.club), league = LG[lid];
  const items = academyRows(ACAD_GROUP);
  const selected = items.find(x => x.token === ACAD_PICK) || items[0] || null;
  ACAD_PICK = selected ? selected.token : "";
  const rows = items.map(item => {
    const p=item.player, age=item.kind==="pro"?pAge(p):p.age, ovr=item.kind==="pro"?pOvr(p):p.ovr;
    const sub=item.kind==="prospect"?"À observer":item.kind==="pro"?"Équipe première":p.signed?"Sous contrat":"Académie · "+academyGroupLabel(academyGroupForAge(age));
    return `<button class="acad-roster-row ${selected&&selected.token===item.token?"selected":""}" data-acadpick="${esc(item.token)}">${academyPortrait(item)}<span class="acad-roster-name"><b>${esc(p.name)}</b><small>${esc(POS[p.pos]?.name||p.pos)} · ${age} ans · ${sub}</small></span><strong>${ovr}</strong></button>`;
  }).join("");
  const enabled = (window.HV_LEGENDS||[]).filter(l=>(S.w.custom||[]).some(c=>c.name===l.name)).length;
  return `<section class="view academy-view"><div class="card acad-title"><div><span class="eyebrow">Formation · ${esc(club.name)}</span><h2 class="h2">Centre de <em>formation</em></h2><p class="muted small">Suis les jeunes, observe des matchs et repère les futurs titulaires.</p></div><button class="btn sm" data-tab="team">Retour à l’équipe</button></div>
    <div class="card"><div class="acad-filters"><label><span>Pays</span><select disabled><option>${nat ? nat.flag+" "+esc(nat.name) : "—"}</option></select></label><label><span>Division</span><select disabled><option>${league ? esc(league.n) : "Championnat"}</option></select></label><label><span>Équipe</span><select data-acadgroup>${ACADEMY_GROUPS.map(([id,label])=>`<option value="${id}" ${ACAD_GROUP===id?"selected":""}>${label}</option>`).join("")}</select></label></div></div>
    <div class="acad-columns"><div class="card acad-roster"><div class="between"><div><span class="eyebrow">${academyGroupLabel(ACAD_GROUP)} · ${items.length} joueur${items.length===1?"":"s"}</span><h3>Effectif</h3></div><button class="btn sm" data-acaddiscover>+ Repérer un jeune</button></div><div class="acad-roster-list">${rows||`<p class="muted small">Aucun joueur dans ce groupe pour l’instant. Utilise « Repérer un jeune » pour lancer une observation.</p>`}</div></div>${academyProfile(selected)}</div>
    <div class="card acad-note"><span class="eyebrow">Progression de l’Académie</span><p>Les jeunes gagnent en potentiel au fil des saisons. Les joueurs de 16 ans et plus peuvent recevoir une proposition de contrat professionnel.</p><div class="acad-footer"><span>${C.yth.filter(y=>!y.signed).length} jeunes en formation</span><span>${C.academyProspects.length} talents à observer</span><span>${enabled} légende${enabled===1?"":"s"} au mercato</span></div></div></section>`;
}
function activateLegends() {
  if (!S || !isCoach() || !S.me.club) { toast("Pour recruter les légendes, ouvre une carrière entraîneur avec un club."); return; }
  const legends = window.HV_LEGENDS || [], C = S.w;
  C.custom = C.custom || [];
  let added = 0;
  legends.forEach(l => {
    if (C.custom.some(p => p.name === l.name)) return;
    const id = PL.length;
    const p = {id, name:l.name, pos:POS[l.position]?l.position:"BU", ovr:clamp(+l.rating||97,90,99), by:C.year-(+l.prime_age||27), nat:NATIONS[l.nation]?l.nation:"bra", team0:null, legend:true};
    C.custom.push(p); PL.push({...p,team0:null,custom:true,legend:true});
    C.pc[id] = null; C.po[id] = p.ovr; C.ret[id] = 0;
    added++;
  });
  if (!added) { toast("Les légendes sont déjà disponibles dans le mercato."); return; }
  refreshSquads(); save(); render();
  toast(`${added} légendes ajoutées aux joueurs libres. Va dans Mercato → Recruter.`);
}
function viewLegends() {
  const legends = (window.HV_LEGENDS || []).slice().sort((a,b)=>b.rating-a.rating);
  const coach = isCoach() && S.me.club;
  const added = coach ? legends.filter(l=>(S.w.custom||[]).some(p=>p.name===l.name)).length : 0;
  const clubs = l => Array.isArray(l.clubs) ? l.clubs.join(" · ") : String(l.clubs || "");
  return `<section class="view legend-view"><div class="card legend-heading"><div><span class="eyebrow">Galerie spéciale · ${legends.length} joueurs</span><h2 class="h2">Les <em>Légendes</em></h2><p class="muted small">R9, Zidane, Ronaldinho, Maradona, Pelé et d’autres icônes, avec leur poste de prédilection et leur GEN de légende.</p></div><div class="legend-actions">${coach ? (added===legends.length ? `<span class="status on">Déjà dans le mercato · ${added}/${legends.length}</span><button class="btn sm gold" data-legendsmarket>Ouvrir le mercato</button>` : `<button class="btn gold" data-legendsenable>⚽ Ajouter les légendes au mercato</button><small>${added}/${legends.length} déjà disponibles</small>`) : `<span class="status">À recruter en carrière entraîneur</span>`}</div></div>
    <div class="legend-grid">${legends.map(l=>`<article class="card legend-card"><img src="${esc(l.image)}" loading="lazy" alt="Portrait de ${esc(l.name)}"><div class="legend-info"><span class="eyebrow">${NATIONS[l.nation]?NATIONS[l.nation].flag+" ":""}${esc(NATIONS[l.nation]?.name||l.nation||"")}</span><h3>${esc(l.nickname||l.name)}</h3>${l.nickname?`<small>${esc(l.name)}</small>`:""}<div class="legend-meta"><span>${esc(POS[l.position]?.name||l.position)}</span><b>GEN ${l.rating}</b></div><small>Âge de pointe : ${l.prime_age} ans</small><small>${esc(clubs(l))}</small><small>${esc(l.era||"")}</small></div></article>`).join("")}</div>
    <div class="card legend-credit-note"><p>Les photos sont accompagnées de leurs sources et licences dans les crédits du jeu. Certains noms, portraits et écussons peuvent rester soumis à des droits à l’image ou à des marques.</p><a href="./credits.html">Voir les crédits des images</a></div></section>`;
}
