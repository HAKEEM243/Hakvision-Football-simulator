# Hak Vision Football Simulator

Jeu de carrière de football en une page web : carrière joueur ou entraîneur, clubs et championnats, matchs animés, finances et progression.

- **Version Cloudflare Workers** : https://hakvision-football-simulator.arenalse22.workers.dev/
- **Version GitHub Pages** : https://hakeem243.github.io/Hakvision-Football-simulator/
- **Sur téléphone** : ouvrir le lien puis « Ajouter à l’écran d’accueil » pour l’installer comme une application.
- Les sauvegardes restent dans le navigateur ; export et import sont disponibles dans les Réglages.

## Nouveautés de cette version

- **150 portraits réels** de joueurs, dont Messi, Cristiano Ronaldo, Neymar, Mbappé, Vinícius Júnior et Haaland. Les fichiers sont dans `assets/player-portraits/`; le script `assets/player-portraits.js` relie les noms du jeu aux photos.
- **15 légendes** avec portrait, poste, nationalité, âge de pointe et notes de 97 à 99 : Ronaldo Nazário (R9), Zidane, Ronaldinho, Maradona, Pelé, Cruyff, Beckenbauer, Eusébio, Garrincha, Platini, George Best, Maldini, Puskás, Yashin et Thierry Henry. En carrière entraîneur, l’onglet **Légendes** permet de les ajouter aux joueurs libres du mercato.
- **Centre de formation enrichi** : filtres par groupe U10, U12, U15, U18, Réserve et équipe première; fiches de jeunes avec taille, poids, pied préféré, moyenne pondérée et attributs techniques, mentaux et physiques. L’observation simulée d’un match complet recrute automatiquement un prospect si sa note finale atteint **7/10**.
- **102 écussons de clubs** documentés, dont des écussons séparés d’Estudiantes de La Plata, Botafogo et Al Ahli.
- La navigation conserve l’avatar personnalisé de Hakeem Jr ; les portraits réels s’affichent dans les fiches et listes de joueurs.

## Images, sources et attribution

La page `credits.html` réunit les crédits, liens et licences des portraits, des légendes et des écussons. Les manifestes source sont dans `assets/player-photo-credits.csv`, `assets/legend-photo-credits.csv` et `assets/club-crest-credits.csv`. Les licences ne règlent pas automatiquement les droits à l’image des joueurs ou les marques des clubs ; vérifier les autorisations nécessaires avant toute diffusion commerciale.

Pour régénérer les crédits, le cache hors ligne et la version statique servie par Cloudflare :

```sh
python3 scripts/build_asset_credits.py
python3 scripts/build_service_worker.py
python3 scripts/sync_public.py
```

## Déploiement

Le jeu utilise Cloudflare Workers Static Assets, configuré par `wrangler.jsonc` pour servir le dossier `public/`. Le synchroniseur copie le code et les médias testés de la racine dans `public/`. GitHub Pages peut également servir la version statique depuis la racine.
