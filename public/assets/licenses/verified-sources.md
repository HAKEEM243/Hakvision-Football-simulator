# Sources vérifiées des médias du jeu

Les crédits détaillés, les auteurs, les liens et les licences sont conservés dans `assets/player-photo-credits.csv` (150 joueurs), `assets/legend-photo-credits.csv` (15 légendes) et `assets/club-crest-credits.csv` (102 écussons). Les images sont stockées localement pour l’affichage et le cache hors ligne.

## Portraits des joueurs

Les 150 correspondances entre les noms du jeu et les portraits sont dans `assets/player-portraits.js`. Les licences Creative Commons et les crédits exacts restent dans le manifeste; les adaptations concernées par une licence CC BY-SA doivent conserver une licence compatible et signaler les modifications éventuelles.

## Portraits des légendes

Les quinze portraits et leurs fiches source sont définis dans `assets/legend-photo-credits.csv`; les pages Commons, auteurs et licences y sont indiqués individuellement. Le tableau HTML public des crédits est généré par `scripts/build_asset_credits.py`.

## Nouveaux écussons

- **Estudiantes de La Plata** — [fichier Commons](https://commons.wikimedia.org/wiki/File:Escudo_de_Estudiantes_de_La_Plata.svg), rendu local `assets/club-crests/estudiantes.png`. Commons invoque le seuil d’originalité pour ce logo; des droits de marque peuvent subsister.
- **Botafogo de Futebol e Regatas** — [fichier Commons](https://commons.wikimedia.org/wiki/File:Botafogo_de_Futebol_e_Regatas_logo.svg), copie locale `assets/club-crests/botafogo-fr.svg`. Commons le classe comme texte/logo simple du domaine public au titre du seuil d’originalité; sa page avertit explicitement que la marque peut rester protégée.
- **Al Ahli Saudi** — [fichier Commons](https://commons.wikimedia.org/wiki/File:Alahlilogo.svg), copie locale `assets/club-crests/al-ahli-saudi.svg`. La page indique une dédicace CC0 par son téléverseur et cite le site `alahlifc.sa`; elle porte aussi une proposition de suppression (depuis le 28 juin 2026) liée à l’incertitude sur le seuil d’originalité en Arabie saoudite. La marque du club peut subsister : conserver cette réserve et vérifier avant une diffusion publique/commerciale.

## Limites d’utilisation

Une licence de droit d’auteur n’accorde pas automatiquement les droits à l’image, le droit de la personnalité, le droit des marques ou l’autorisation d’un club. Les 99 écussons intégrés auparavant et les nouveaux fichiers sont documentés dans le manifeste; leur réutilisation doit être contrôlée selon le territoire et l’usage envisagé.

## Vérification des sources de badges supplémentaires

Les conditions de TheSportsDB (https://www.thesportsdb.com/docs_terms_of_use.php, consultées le 9 octobre 2026) demandent de vérifier la licence de chaque image. Leur champ `strCreativeCommons` n’est qu’un indicateur : `Yes` exige encore l’identification de la licence, du créateur et de la source; les statuts vides, `Unknown` ou non vérifiés ne sont pas autorisés pour un usage public. Lors d’un test sur plusieurs clubs absents, l’API n’a renvoyé aucun statut Creative Commons. Ces badges n’ont donc pas été ajoutés. Les nouveaux écussons ajoutés à cette version proviennent des fichiers Commons consignés ci-dessus; des droits de marque peuvent néanmoins subsister.
