// Associe les portraits licenciés des légendes aux noms utilisés par les fiches du jeu.
(() => {
  const photos = window.HV_PLAYER_PHOTOS || {};
  for (const legend of (window.HV_LEGENDS || [])) {
    if (legend.name && legend.image) photos[legend.name] = legend.image;
  }
  window.HV_PLAYER_PHOTOS = photos;
})();
