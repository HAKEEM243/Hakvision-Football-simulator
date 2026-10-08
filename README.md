# Hak Vision Football Simulator

Jeu de carrière de football (joueur ou entraîneur) en une seule page web : vrais clubs, vrais joueurs, championnats et coupes du monde entier, matchs en 2D style retransmission TV, finances, vie privée, succès…

- **Jouer en ligne** : https://hakeem243.github.io/Hakvision-Football-simulator/ (après activation de GitHub Pages sur la branche `main`, dossier racine)
- **Sur téléphone** : ouvrir le lien puis « Ajouter à l'écran d'accueil » pour l'installer comme une application.
- La sauvegarde est enregistrée dans le navigateur ; export et import disponibles dans les Réglages.

## Contenu

- Deux carrières : joueur (dès 16 ans, centre de formation, sélection, Ballon d'Or) ou entraîneur (club et sélection nationale).
- Football Manager : fiche joueur détaillée, staff, consignes tactiques, moral individuel, rapport de l'adjoint, mercato complet.
- FIFA Manager / LFP Manager : finances, bilan de saison, vie privée (couple, enfants, bourse, immobilier, loisirs).
- BitLife / New Star Soccer : événements à choix, succès, mini-jeux d'entraînement.

## Images et attribution

- **Joueurs** : 100 portraits réels sous licence CC BY, CC BY-SA, CC0 ou domaine public, dont Messi, Cristiano Ronaldo, Neymar, Mbappé, Vinícius Júnior et Haaland. Les photos sont dans `assets/player-portraits/`; leur correspondance avec les noms du jeu est dans `assets/player-portraits.js`.
- **Écussons** : les 99 écussons déjà embarqués dans le jeu sont conservés; l’écusson d’Estudiantes de La Plata a été ajouté pour compléter la sélection de 100 clubs.
- **Crédits** : consulter [la page des crédits](./credits.html), `assets/player-photo-credits.csv` et `assets/club-crest-credits.csv`.
- Les portraits s’affichent automatiquement pour les joueurs sélectionnés; les autres joueurs conservent le visage généré du jeu et peuvent toujours recevoir une photo personnalisée via l’éditeur.
- Une licence photo ne confère pas automatiquement les droits à l’image/personnalité des joueurs. Les écussons sont des marques; les droits de réutilisation des écussons préexistants sont signalés comme non vérifiés dans le fichier de crédits. Vérifier les autorisations nécessaires avant une distribution commerciale ou sur une boutique d’applications.

## Déploiement

Site statique : `index.html` + `credits.html` + le dossier `assets/` + `manifest.webmanifest` + `sw.js` + icônes. Compatible GitHub Pages et Cloudflare Pages (répertoire de sortie : racine, aucune commande de build).
