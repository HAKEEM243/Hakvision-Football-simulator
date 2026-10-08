// Blason complémentaire. Ce fichier s’exécute après le script principal, puis rafraîchit l’écran.
(() => {
  const badge = "./assets/club-crests/estudiantes.png";
  CRESTS["Estudiantes"] = badge;
  CRESTS["Estudiantes de La Plata"] = badge;
  if (typeof render === "function") render();
})();
