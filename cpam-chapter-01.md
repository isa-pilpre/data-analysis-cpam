# Partie 1 : Préparation, organisation et nettoyage des données

## Sélection d'un jeu de données de la CPAM

Le système d'assurance maladie en France (CPAM) met à disposition du public des jeux de données en open data via leur site data.ameli.fr :

![image1]

En cliquant sur '**Data pathologies**', une page explicative s'affiche, précisant :

> « L'Assurance Maladie met à disposition du grand public un ensemble de données sur une cinquantaine de pathologies, traitements chroniques et épisodes de soins : diabète, syndrome coronaire aigu, insuffisance cardiaque, AVC aigu, cancer du sein, cancer du poumon, maladie de Parkinson, épilepsie, mucoviscidose, traitements anxiolytiques, maternité, etc. Quels sont les effectifs de patients pris en charge pour ces différentes pathologies ? Comment évolue la prévalence ? Comment l'effectif est-il réparti sur le territoire français ? Quelles sont les dépenses remboursées affectées à chacune des pathologies identifiées ? »

![image2]

Bien que de nombreux graphiques et visualisations interactives soient déjà disponibles sur cette page, je choisis de réaliser ma propre analyse des données. Pour ce faire, je clique sur l'onglet '**Données complètes**', où un jeu de données m'intéresse particulièrement :

![image3]

Lorsque je clique dessus, les métadonnées indiquent qu'il s'agit d'un jeu de données couvrant les années 2015 à 2022, récemment actualisé en juillet 2024, ce qui est une bonne nouvelle :

![image4]

Ce jeu de données concerne les effectifs de patients pris en charge par la CPAM selon les années, les pathologies, les tranches d'âge, le sexe et les territoires (régions et départements) :

![image5]

Ce jeu va me donner l'occasion d'appliquer mes nouvelles compétences en analyse de données à l'aide de SQL, BigQuery, R et Tableau. Voici ci-après le déroulé de mon analyse.

## Objectif de l'analyse

Pour tenter de resserrer le champ d'application de mon analyse, puisque ce jeu couvre tout de même une cinquantaine de pathologies d'après le site de la CPAM, je vais m'efforcer de répondre à des questions précises, telles que :

* Comment sont réparties en 2022 (l'année la plus récente de ce jeu de données) des pathologies spécifiques (comme le cancer du poumon, le cancer colorectal, le diabète, …) parmi les départements français ?
* Comment la prévalence de ces pathologies a-t-elle évolué de 2015 à 2022 ?
* La vague de COVID-19 a-t-elle eu un impact sur la prévalence de ces pathologies dans les années 2020-2022 ?

J'affinerai sans doute ces questions à mesure que j'avance dans mon analyse, mais c'est un bon objectif de départ.

## Transfert du jeu de données sur Google Cloud Storage (GCS)

Ce jeu de données est disponible dans différents formats, y compris CSV, JSON, Excel et Parquet. Je choisis le format CSV, car c'est celui qui m'est le plus familier.

![image6]
*fig6. Jeu de données de la CPAM en plusieurs formats*

Le fichier CSV fait tout de même 800 Mo, ce qui dépasse les capacités d'Excel ou de Google Sheets. Je préfère ne pas surcharger les ressources de mon propre ordinateur, aussi je décide d'aller sur Google Cloud Storage (GCS) pour stocker mon jeu de données. C'est la solution la plus pratique pour moi, car GSC est étroitement intégré à BigQuery, que j'ai déjà utilisé plusieurs fois dans le cadre de ma formation de Data Analyste. Après m'être inscrite sur Google Cloud Platform, je suis prête à commencer. *'Welcome'*, me claironne le système alors que je navigue à travers la configuration initiale.

![image7]
*fig7. Page de bienvenue de Google Cloud*

Lorsque j'ouvre ma console Google, je vois que BigQuery et Cloud Storage sont tous deux situés dans le même panneau de navigation à gauche, aux côtés de SQL et de plusieurs autres services, ce qui est très pratique. Sur le côté droit de l'écran, je remarque que le système m'a attribué un nom de projet, *'My First Project'*, et un ID de projet étrangement nommé *'alien-oarlock-428016-f3'* :

![image8]
*fig8. Google console*

Je transfère mon fichier CSV original, que j'ai nommé `CPAM_effectifs_2024_July.csv`, dans un nouveau *Bucket* que j'ai créé sur Google Cloud Storage. Ensuite, je dois le rendre accessible dans BigQuery pour l'analyse.

### Accès dans BigQuery

Je navigue vers l'interface de BigQuery et repère mon ID de projet, `alien-oarlock-428016-f3`, dans le panneau Explorer à gauche de l'écran. À côté de l'ID de projet, je clique sur le menu à trois points verticaux et sélectionne *'Create dataset'*.

![image9]

Une fenêtre s'affiche, avec l'ID de projet déjà renseigné. Je tape `french_cpam` dans la zone de texte Dataset ID :

![image10]

Désormais, je vois que sous mon ID de projet, le dataset nouvellement créé `french_cpam` apparaît.

Ensuite, je clique à nouveau sur le menu à trois points verticaux, mais à côté de l'ID du dataset cette fois, et je sélectionne *'Create table'*.

![image11]

Dans la fenêtre contextuelle qui s'affiche, je définis la source sur *'Google Cloud Storage'* et je recherche le fichier CSV que je viens de transférer. Dans la section de destination, l'ID de projet '*alien-oarlock-428016-f3'* et l'ID de dataset '*french\_cpam'* sont déjà prédéfinis.
Je nomme la table *'cpam\_effectifs\_july\_2024'* et sélectionne *'Auto detect'* (détection automatique) pour laisser le système détecter automatiquement la structure de mon fichier, ce qui simplifie la configuration. Enfin, je clique sur *'Create table*' pour finaliser le processus :

![image12]

Aïe. Je tombe sur un obstacle.

Un message d'erreur s'affiche :

> Failed to create table: Error while reading data, error message: CSV table encountered too many errors, giving up.
> Rows: 10600; errors: 100.
> Please look into the errors[] collection for more details.
> File: gs://french-social-security-data/CPAM_effectifs_2024_July.csv

Quand je reviens à mon fichier CSV, je réalise que le séparateur dans ce fichier est un point-virgule (`;`), et non la virgule (`,`) plus habituelle aux États-Unis.

Jetons un coup d'œil plus attentif à la fenêtre de création de table dans BigQuery... Ah, j'ai trouvé ! Caché près du bas de la fenêtre de création de table, il y a un lien intitulé *'Advanced options' (*ne jamais ignorer les paramètres avancés*). Lorsque j'agrandis cette section, je trouve un paramètre appelé  *'Field delimiter'*, prédéfini sur *'Comma'* (Virgule). Si je fais défiler les options, je vois des choix comme *'Tab'*, *'Pipe'*, ou *'Custom'*. Choisissons *'Custom'* (Personnalisé) et définissons le délimiteur sur le point-virgule.

Un message en rouge m'informe que le délimiteur personnalisé ne doit contenir qu'un seul caractère.

Je tape simplement le caractère du point-virgule, c'est-à-dire '`;`'.

Je clique à nouveau sur *'Create Table'*.  Ça marche ! BigQuery confirme : `'cpam_effectifs_july_2024' created.`

Me revoilà en piste !

# Première rencontre avec les données

Maintenant que mon jeu de données est configuré sous forme de table dans BigQuery, je ressens un mélange d'enthousiasme et d'impatience. Cela peut sembler banal pour certains, mais pour une novice en analyse de données comme moi, c'est une sacrée aventure ! D'après ce que ma formation m'a appris et selon ma propre intuition, cette première rencontre avec le jeu de données (l'étape *"Salut, ravi de faire ta connaissance"*) est importante. C'est là que je vais comprendre « la substantifique moelle » de mes données, ce qui orientera mon analyse future. Avant même de commencer à manipuler et à travailler avec les données, je dois prendre le temps de les comprendre et de me familiariser avec elles.

Commençons par examiner le modèle de données et les 100 premières lignes de la table pour avoir un aperçu préliminaire. Il existe plusieurs façons de procéder. La plus immédiate, c'est de consulter le site de la CPAM où j'ai téléchargé mes données :

![image13]

Sous le premier onglet *'Informations'*, si je fais défiler la page vers le bas jusqu'à *'Modèle de données',* je peux glaner beaucoup d'informations fondamentales sur les données et les différentes colonnes de la table.

Également, je peux aller sur le deuxième onglet intitulé *'Tableau'* pour visualiser les premières lignes du jeu de données :

![image14]

Lorsque j'examine les premières lignes de la table et le modèle de données fourni, je découvre que le jeu de données se compose d'une grande table avec une douzaine de colonnes. Voici un aperçu des principales colonnes, avec leur type de données :

* `annee` : les années que couvre cette période d'analyse, qui s'étendent actuellement de 2015 à 2022. *Type : date*
* `patho_niv1`, `patho_niv2`, `patho_niv3` : groupe ou sous-groupe de pathologies (ou traitements chroniques ou épisodes de soins). *Type : texte*
* `top` : libellé technique de la pathologie. Ex. “CAN\_CAT\_CAT”. *Type : texte*
* `cla_age_5` : Classe d'âge (5 ans). Ex: 30-34. *Type : texte*
* `libelle_classe_age` : le libellé de la classe d'âge, par ex. “de 30 à 34 ans”.  *Type: texte*
* `sexe` : 1 pour homme, 2 pour femme, et 9 pour 'tous sexes'. *Type : texte*
* `libelle_sexe` : le libellé pour le sexe, ex. "homme", "femme", "tous sexes". *Type: texte*
* `region` : code INSEE de chaque région française. D'après ce que je vois sur le site de la CPAM, le code '99' signifie “toutes régions”. *Type : texte*
* `dept` : code INSEE de chaque département français. D'après ce que je vois sur le site de la CPAM, le code '999' signifie 'tous départements'. *Type : texte*
* `Ntop` : effectif de patients pris en charge pour la pathologie (ou traitement chronique ou épisode de soins) dont il est question. *Type : int*
* `Npop` : population de référence qui est celle de la cartographie des pathologies et des dépenses de l'Assurance Maladie. *Type : int*
* `prev` : prévalence de patients pris en charge pour la pathologie (ou traitement chronique ou épisode de soins) dont il est question. Ex. 0.867. *Type : décimal*

## Petit rappel sur des notions statistiques de base

Révisons rapidement un terme statistique clé : la **prévalence**.

La prévalence fait référence à la proportion d'individus dans une population qui ont une maladie ou un problème de santé spécifique, au cours d'une période donnée.
La prévalence englobe aussi bien les nouveaux cas que les cas déjà déclarés.

Contrairement à l'incidence (qui mesure uniquement le taux de nouveaux cas), la prévalence dépend de la durée de la maladie.

Dans ce jeu de données, le champ `prev` représente la prévalence, calculée comme le ratio de `Ntop` (le nombre de personnes recevant des soins pour une pathologie spécifique) sur `Npop` (la population de référence pour cette pathologie) :

```math
prévalence=\frac{Ntop}{Npop}
```

C'est pourquoi le champ de prévalence `prev` a un type de données 'float' ou décimal, ce qui signifie qu'il s'agit d'une valeur décimale.

Par exemple, si 3 000 personnes reçoivent des soins pour des troubles psychiatriques au cours d'une année donnée dans une région spécifique avec une population de référence de 100 000 personnes, la prévalence serait :

```math
prev=\frac{3\ 000}{100\ 000}=0,03\ ou\ 3\%
```

## Petit rappel sur le type des données

Comme mentionné précédemment, j'ai inclus le type de données attribué à chaque champ/colonne lors de l'examen de la structure des données. Les types de données en programmation et en gestion de bases de données définissent le type de données qu'une variable peut contenir. Les types de données courants incluent les entiers ('*int*'), les nombres décimaux ('*float*') et les chaînes de caractères/du texte ('*string*'). Ces types de données dictent la manière dont les données peuvent être traitées et stockées.

Dans mes expériences précédentes (avec des tableurs, des bases de données SQL, et surtout en programmation), j'ai déjà rencontré des problèmes liés à des affectations incorrectes de types de données. Ces erreurs peuvent empêcher les formules dans les tableurs de fonctionner correctement, entraîner des requêtes SQL qui retournent des données incorrectes, ou introduire des bugs dans des applis logicielles. C'est pourquoi : toujours bien s'assurer d'utiliser le bon type de données !

## Exploration des données avec SQL

J'ai déjà inspecté visuellement les premières lignes du jeu de données sur le site de la CPAM, mais je préfère lancer mes propres requêtes SQL, directement dans BigQuery, afin de pouvoir les adapter précisément à mes besoins et me concentrer sur ce qui m'intéresse.

## Comprendre la structure de BigQuery

Avant de commencer à exécuter des requêtes SQL dans BigQuery et faire des SELECT… FROM…, il faut savoir qu'on doit donner le chemin complet des tables dans la base de données, à savoir :

1. **L'ID du projet** : Chaque projet dans BigQuery possède un identifiant unique. Comme mentionné précédemment, l'ID de projet attribué ici par BigQuery est `alien-oarlock-428016-f3`.
2. **L'ID du dataset** : Au sein de chaque projet, vous pouvez avoir plusieurs ensembles de données (*datasets*). Un *dataset* est comme un conteneur qui stocke vos tables. Pour ce projet, j'ai créé un ensemble de données appelé `french_cpam`.
3. **Le nom de la table** : Au sein du *dataset*, les données sont stockées dans des tables. Ma table s'appelle `cpam_effectifs_july_2024`.

Lorsque je lance une requête SQL, je dois donc spécifier le chemin complet de la table, à savoir l'ID du projet, l'ID du dataset, et le nom de la table.

## Premières requêtes exploratoires SQL

Pour mieux comprendre les données, je vais exécuter quelques requêtes initiales pour connaître les éléments suivants :

1. Le nombre total de lignes (la taille du jeu de données) ;
2. Le nombre total de colonnes ;
3. L'aperçu initial des données (j'ai déjà eu un aperçu par le site de la CPAM, mais je préfère exécuter ma propre requête pour parcourir les premières lignes dans BigQuery) ;
4. La répartition des données clés (en affichant toutes les valeurs uniques de chaque colonne clé) ;
5. Les statistiques de base pour les valeurs numériques (valeurs minimales, maximales, moyennes) ;
6. La recherche des valeurs nulles (pour vérifier l'intégrité des données) ;
7. La prévalence, ce qu'elle signifie précisément dans ce jeu de données.

### 1. Nombre de lignes

Pour connaître la taille du jeu de données, comptons le nombre total de lignes :

```sql
SELECT
    COUNT(*) AS `Number of rows`
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;
```

Résultats :

Row   | Number of rows |
----- | -------------- |
 1    | 4636800        |

Il y a donc plus de 4 millions de lignes dans mon jeu de données (précisément 4 636 800 lignes). Ce volume important de données me conforte dans mon choix d'avoir utilisé un outil puissant comme BigQuery, qui peut gérer efficacement de larges ensembles de données.

La taille imposante de cette table monolithique me fait songer à la diviser en tables plus petites et plus faciles à gérer, dans un souci de normalisation et d'optimisation des requêtes. Mais pour l'instant, terminons les requêtes exploratoires initiales.

### 2. Nombre et nom des colonnes

Ne sachant pas comment faire, j'ai fait des recherches et trouvé ce modèle de requête en ligne :

```sql
SELECT
    COUNT(*)
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    table_name = [my_table_name]
```

Toutefois, comme on l'a vu dans BigQuery, je dois inclure l'ID du projet et l'ID du dataset ID avant 'INFORMATION\_SCHEMA.COLUMNS' :

```sql
SELECT
    COUNT(*) AS 'number_of_columns'
FROM
    `alien-oarlock-428016-f3.french_cpam.INFORMATION_SCHEMA.COLUMNS`
WHERE
    table_name = 'cpam_effectifs_july_2024';
```

Résultats :

Row  | number_of_columns |
---- | ---- |
1    | 16 |

La table contient 16 colonnes, ce qui me paraît beaucoup. Pour vérifier ce résultat, affichons le nom de toutes les colonnes :

```sql
SELECT
    column_name
FROM
    `alien-oarlock-428016-f3.french_cpam.INFORMATION_SCHEMA.COLUMNS`
WHERE
    table_name = 'cpam_effectifs_july_2024'
```

Résultats :

Row  | annee |
---- | ---- |
 2   | patho niv1 |
 3   | patho niv2 |
 4   | patho niv3 |
 5   | top |
 6   | cla_age_5 |
 7   | sexe |
 8   | region |
 9   | dept |
 10  | Ntop |
 11  | Npop |
 12  | prev |
 13  | Niveau prioritaire |
 14  | libelle classe age |
 15  | libelle_sexe |
 16  | tri |

Ce résultat semble en fait valide, car il correspond à ce qui est affiché sur le site de la CPAM. Cependant, pour mon projet d'analyse de données, certaines colonnes ne semblent pas pertinentes. À savoir :

* '`Niveau prioritaire`' (Ex : 1, 2, 3) : aucune explication supplémentaire
* '`tri`' (Ex. 8) : aucune explication supplémentaire sur le site de la CPAM
* '`libelle classe age`' (Ex. '30 à 34 ans') : cela n'apporte rien par rapport à '`cla_age_5`' (Ex. '30-34).

Je vais donc bientôt supprimer ces colonnes et me concentrer sur les autres plus pertinentes.

### 3. Aperçu initial

Examinons les 100 premières lignes dans BigQuery :

```sql
SELECT
    *
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
LIMIT 100;
```

Results:

L'aperçu des données révèle des points intéressants. Notamment, les 3 colonnes des pathologies (niveau 1, 2 et 3) contiennent des cellules avec la valeur *"Total consommants tous régimes"*. Cela ne spécifie pas une pathologie particulière, mais semble plutôt agréger les données pour toutes les pathologies. Pour ces entrées, les champs `Ntop` (nombre de patients traités) et `Npop` (population de référence) affichent le même nombre (10 970) pour le groupe d'âge 0-4 ans, aboutissant à un taux de prévalence calculé de 100 %.

De manière similaire à d'autres indicateurs agrégés (comme *'9'* représentant *'tous les sexes'*, *'999'* pour *'tous les départements'*, et *'99'* pour '*toutes les régions'*), la valeur *"Total consommants tous régimes"* dans les colonnes de pathologie semble représenter un récapitulatif pour l'ensemble de la population.

Ainsi donc, **certaines lignes agrègent les données** plutôt que d'afficher des enregistrements individuels. C'est un point important à noter, car je ne voudrais pas de doublons lors de l'analyse des données ultérieurement.

### 4. Répartition des données

Je souhaite afficher toutes les valeurs distinctes présentes dans chaque colonne clé, comme les colonnes de pathologies, régions, départements et groupes d'âge.

Commençons par patho\_niv1 pour lister toutes les pathologies distinctes de
niveau 1:

```sql
SELECT
    DISTINCT patho_niv1
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;
```

**Results:**

Row | patho_niv1 |
--- | ----- |
1   | Affections de longue durée (dont 31 et 32\) pour d'autres causes |
2   | Cancers |
3   | Diabète |
4   | Hospitalisations hors pathologies repérées (avec ou sans pathologies, traitements ou maternité) |
5   | Maladies inflammatoires ou rares ou infection VIH |
6   | Hospitalisation pour Covid-19 |
7   | Insuffisance rénale chronique terminale |
8   | Maternité (avec ou sans pathologies) |
9   | Maladies cardioneurovasculaires |
10  | Maladies du foie ou du pancréas (hors mucoviscidose) |
11  | Maladies neurologiques |
12  | Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire |
13  | Total consommants tous régimes |
14  | Maladies psychiatriques |
15  | Maladies respiratoires chroniques (hors mucoviscidose) |
16  | Traitement antalgique ou anti-inflammatoire (hors pathologies, traitements, maternité ou hospitalisations) |
17  | Traitements du risque vasculaire (hors pathologies) |
18  | Traitements psychotropes (hors pathologies) |

Il y a ainsi 18 entrées distinctes pour **patho_niv1**, ce qui correspond à la liste des pathologies affichées pour le niveau 1 sur le site de la CPAM.

Tout semble correct, sauf deux entrées qui attirent mon attention :

* "Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire" : ça semble indiquer des enregistrements où aucune pathologie ni aucun type de traitement n'a été nécessaire.
* "Total consommants tous régimes" : j'ai déjà parlé de cette entrée en examinant les premières lignes. Elle semble représenter le total de tous les bénéficiaires du système de santé en France, tous régimes confondus.

Pour m'assurer que je comprends bien ces entrées et leur impact sur le jeu de données, je lance les requêtes SQL suivantes, en mentionnant spécifiquement les valeurs agrégées du sexe (9), des départements (999), des régions (9), des groupes d'âge (“tsage”), ainsi qu'une année donnée (2022), afin d'éviter toute duplication de données :

```sql
-- Ntop for 'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire' for the year 2022 and all ages
SELECT
    SUM(Ntop) AS sum_no_pathology
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    patho_niv1 = 'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire'
    AND sexe = 9
    AND dept = '999'
    AND region = 99
    AND cla_age_5 = 'tsage'
    AND annee = 2022;
```

```sql
-- Ntop for 'Total consommants tous régimes' for the year 2022 and all ages
SELECT
    SUM(Ntop) AS sum_total_consumers
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    patho_niv1 = 'Total consommants tous régimes'
    AND sexe = 9
    AND dept = '999'
    AND region = 99
    AND cla_age_5 = 'tsage'
    AND annee = 2022;
```

**Résultats:**

Results    | Valeurs |
-----------|----|
37 919 240 | `sum_no_pathology` |
68 729 230 | `sum_total_consumers` |

La valeur des “total consommants tous régimes” semble exacte, car le site de la CPAM rapporte « 68,7 millions de bénéficiaires de soins de santé en France pour 2022 ».

La valeur de quasi 38 millions de personnes sans pathologie en 2022 (c'est-à-dire plus d'une personne sur deux en France) semble plausible, bien que cela me surprenne quelque peu. Je pourrais avoir besoin d'approfondir cette analyse plus tard pour valider cette conclusion.

Globalement, les résultats des données semblent cohérents.

Les requêtes sur le reste de mes colonnes clés sont les suivantes :

```sql
SELECT
    DISTINCT patho_niv2
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;

SELECT
    DISTINCT patho_niv3
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;

SELECT
    DISTINCT dept
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;

SELECT
    DISTINCT region
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;

SELECT
    DISTINCT cla_age_5
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;
```

**Résultats** :

49 lignes pour le niveau de pathologie 2, avec une ligne contenant une valeur Null, ce qui donne **48 lignes valides pour patho\_niv2**. Cela correspond aux 48 lignes pour toutes les pathologies listées dans *"patho\_niv2"* sur le site de la CPAM, donc tout va bien.

62 lignes pour le niveau de pathologie 3, avec une ligne contenant une valeur Null, ce qui donne **61 lignes valides pour patho\_niv3**. Cela correspond aux 61 lignes pour toutes les pathologies listées dans *"patho\_niv3*" sur le site de la CPAM, donc tout est correct.

Remarque : les valeurs Null pour les niveaux de pathologie 2 et 3 signifient probablement que certaines pathologies au niveau 1 n'ont pas de sous-catégories.

Pour récapituler, il y a :

* 18 lignes valides pour le niveau de pathologie 1.
* 48 lignes valides pour le niveau de pathologie 2.
* 61 lignes valides pour le niveau de pathologie 3.
* 102 lignes pour les départements français, ce qui inclut la valeur agrégée “999” (pour tous les départements). À ma connaissance, il y a 101 départements en France, donc cela semble exact.
* 19 lignes pour les régions françaises, incluant la valeur agrégée "99" (pour toutes les régions). La France compte 18 régions administratives, donc ce résultat est cohérent.
* 21 lignes pour les groupes d'âge, allant de "00-04" à "95 et+" (c'est-à-dire de 0-4 ans à 95 ans et plus), avec la valeur agrégée "tsage" (pour tous les âges), donc là aussi cela semble exact.

En bref, tous ces résultats semblent logiques et cohérents.

### 5. Infos chiffrées de base

Essayons de connaître des infos numériques de base (minimum, maximum, moyenne) sur deux indicateurs clés : le nombre de patients traités pour une certaine pathologie au cours d'une période (Ntop) et la prévalence de cette pathologie (prev) :

```sql
SELECT
    AVG(Ntop) AS Average_Patients,
    MAX(Ntop) AS Max_Patients,
    MIN(Ntop) AS Min_Patients,
    AVG(prev) AS Average_Prev,
    MAX(prev) AS Max_Prev,
    MIN(prev) AS Min_Prev
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024;
```

Résultats:

Row | Average_Patients | Max_Patients | Min_Patients | Average_Prev | Max_Prev | Min_Prev |
:---- | ----- | ----- | ----- | ----- | ----- | ----- |
1 | 5,527 | 68,729,230 | 10 | 6.21 | 100.0 | 0.0 |

#### À propos du nombre de patients (`Ntop`)

Les résultats montrent une moyenne Ntop de 5 527 bénéficiaires de soins de santé par combinaison unique de pathologie, groupe d'âge, sexe, région et année. Cela signifie que, pour toutes les combinaisons de ces facteurs, il y a en moyenne 5 527 personnes recevant des soins pour une condition spécifique dans une population et un lieu donnés.

La valeur maximale de Ntop est de 68 729 230, ce qui représente le nombre total de bénéficiaires de soins de santé en France pour l'année 2022. Cela correspond parfaitement au site de la CPAM, où il est indiqué « 68,7 millions de bénéficiaires ont reçu au moins un service de santé pris en charge par l'assurance maladie ».

Le nombre minimum de Ntop (10 patients) reflète des cas où seulement un petit nombre d'individus, au sein d'une combinaison spécifique de facteurs (comme une pathologie rare dans un certain groupe d'âge et une région donnée), ont reçu un traitement.

#### À propos de la prévalence (`prev`)

La prévalence moyenne est de 6,21, avec des extrêmes allant de 0 à 100, qu'on avait déjà aperçu dans le premier extrait de données. Ces résultats extrêmes sont à creuser pour bien les comprendre. Aussi, je voudrais m'assurer que la prévalence (prev) indiquée dans ce jeu de données est bien le rapport entre Ntop par Npop. Je ferai cette vérification très prochainement. ISA work needed.

**Notons deux choses importantes** :

* On réalise ici que la **prévalence est affichée en pourcentage par la CPAM**, étant donné que la valeur maximale de `prev` est de 100. Donc la prévalence maximale est de 100 %.
* Si le minimum de `Ntop` n'est pas zéro mais bien 10, le minimum de la prévalence ne devrait pas être zéro (car Prévalence \= Ntop / Npop). Cependant, j'ai remarqué que de nombreuses entrées de `Ntop` étaient nulles, ce qui peut expliquer le résultat de zéro pour la prévalence (puisque `Ntop` est absent), même si `Ntop` ne contient pas de zéro explicite. La fonction `MIN()` ignore souvent les valeurs nulles, donc si `Ntop` contient des valeurs nulles ou non renseignées, la fonction peut afficher un minimum de 10 (la première valeur numérique non nulle). Il faudra donc vérifier si `Ntop` contient des valeurs nulles pour confirmer cette hypothèse.

### 6. Recherche des valeurs nulles

Ça tombe bien, la dernière requête exploratoire consiste à rechercher les valeurs vides/nulles dans la table :

```sql
SELECT
    COUNTIF(patho_niv1 IS NULL) AS Missing_Patho1,
    COUNTIF(patho_niv2 IS NULL) AS Missing_Patho2,
    COUNTIF(patho_niv3 IS NULL) AS Missing_Patho3,
    COUNTIF(annee IS NULL) AS Missing_Year,
    COUNTIF(sexe IS NULL) AS Missing_Sexe,
    COUNTIF(cla_age_5 IS NULL) AS Missing_Age_Group,
    COUNTIF(Ntop IS NULL) AS Missing_Patients,
    COUNTIF(Npop IS NULL) AS Missing_Population,
    COUNTIF(dept IS NULL) AS Missing_Department,
    COUNTIF(region IS NULL) AS Missing_Region
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
```

**Here's a snippet:**

**Résultats** :

J'ai trouvé des valeurs nulles principalement dans les colonnes Pathologie de Niveau 2 (483 840 occurrences) et Pathologie de Niveau 3 (1 048 320 occurrences), ce qui suggère que certaines pathologies de Niveau 1 ne se divisent pas en sous-catégories.

Et oui, la colonne `Ntop` (nombre de patients) contient également de nombreux nulls : précisément 1 238 024 nulls. Ce grand nombre m'interpelle. Pour en savoir plus, je lance la requête suivante pour examiner les 100 premières lignes où `Ntop` est nul, et je vérifie les valeurs des autres colonnes dans ces lignes :

```sql
SELECT
    *
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    Ntop IS NULL
LIMIT 100
```

A snippet of the results:

**Ce que j'apprends** :

Les résultats sont révélateurs. Les cent premières lignes avec une valeur nulle dans la colonne `Ntop` (indiquant l'absence de patients) correspondent au groupe d'âge très jeune de 0 à 4 ans, sans cas de cancer enregistrés. Cela reflète la réalité que certaines pathologies sont absentes ou extrêmement rares dans certaines tranches démographiques, comme certains groupes d'âge ou sexes. Cela a du sens et me rassure sur le fait que ces valeurs nulles indiquent probablement une faible prévalence ou l'absence de ces pathologies, plutôt que des données manquantes.

Pour confirmer mon hypothèse et obtenir une vue plus large, je lance la requête suivante :

```sql
SELECT
    cla_age_5,
    sexe,
    patho_niv1,
    patho_niv2,
    COUNT(*) AS Count_of_Null_Ntop
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    Ntop IS NULL
GROUP BY
    cla_age_5,
    sexe,
    patho_niv1,
    patho_niv2
ORDER BY
    Count_of_Null_Ntop DESC
```

**Résultats:**

![image15]

Les résultats montrent des tendances pour lesquelles certains groupes d'âge, comme les très jeunes ou les très âgés, n'ont aucun cas enregistré pour certaines pathologies, telles que des maladies inflammatoires ou des cancers. De plus, certains sexes n'ont pas de cas enregistrés pour des conditions spécifiques, comme les patients masculins pour le cancer du sein féminin. Ces résultats renforcent mon idée que les valeurs nulles dans `Ntop` (nombre de patients) sont cohérentes avec les tendances démographiques attendues de la prévalence des maladies.

Pour garantir l'intégrité des données, je vérifie que le nombre total de valeurs nulles identifiées dans la requête précédente correspond bien aux 1 238 024 valeurs nulles de `Ntop` que nous avons trouvées plus tôt. Au passage, cela me permet d'utiliser une sous-requête imbriquée dans une requête :

```sql
SELECT
    SUM(Count_of_Null_Ntop) AS Total_Null_Ntop
FROM
    (
        SELECT
            cla_age_5,
            sexe,
            patho_niv1,
            patho_niv2,
            COUNT(*) AS Count_of_Null_Ntop
        FROM
            alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
        WHERE
            Ntop IS NULL
        GROUP BY
            cla_age_5,
            sexe,
            patho_niv1,
            patho_niv2
    ) AS my_temp_table;
```

Bingo !

Le résultat est conforme aux attentes :

Row | Total_Null_Ntop |
----|---------|
1   | 1238024 |

Comme prévu, nous obtenons 1 238 024 valeurs nulles pour `Ntop`.

### 7. Prévalence, sa signification précise dans ce jeu de données

Afin de m'assurer de bien comprendre ce que signifie exactement la prévalence (prev) dans ce jeu de données, car il s'agit de la variable principale de mon analyse, je lance la requête SQL suivante dans BigQuery.

J'exclus toutes les valeurs agrégées, à savoir "tous sexes" (`sexe != 9`), "tous départements" (`dept != '999'`), "toutes régions" (`region != 99`), et "tous âges" (`cla_age_5 != 'tsage'`).
Je calcule la prévalence à partir des colonnes `Ntop` et `Npop` (Ntop/Npop), en l'arrondissant à trois décimales, comme la variable prev fournie dans le jeu de données.
Puis je cherche les entrées où la différence entre la prévalence fournie et celle calculée dépasse 0,001 :

```sql
SELECT
    patho_niv1,
    sexe,
    cla_age_5,
    Ntop,
    Npop,
    prev,
    ROUND((Ntop / Npop * 100), 3) AS calculated_prev,
    prev - ROUND((Ntop / Npop * 100), 3) AS difference
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    Npop IS NOT NULL
    AND Ntop IS NOT NULL
    AND Ntop >= 100
    AND Npop > 0
    AND ABS(prev - ROUND((Ntop / Npop * 100), 3)) > 0.001
    AND sexe != 9
    AND dept != '999'
    AND region != 99
    AND cla_age_5 != 'tsage'
ORDER BY
    difference DESC
LIMIT 30
```

#### Résultats

Les plus grandes différences entre `prev` et `calculated_prev` concernent principalement les personnes âgées, en particulier celles de 95 ans et plus, ainsi que les 85-89 ans. Ces écarts apparaissent lorsque les valeurs de `Ntop` et `Npop` sont petites et semblent arrondies de manière inhabituelle (120, 190, 110, 200, etc.). Cela pourrait indiquer des ajustements ou un lissage dans le processus de calcul des prévalences pour ces tranches d'âge, où les effectifs sont plus faibles et plus susceptibles de variations.

![image16]

![image17]

Ces résultats ne m'inquiètent pas vraiment pour mon projet d'analyse. Cependant, dans un contexte professionnel, si je travaillais pour une entreprise propriétaire de ce jeu de données, j'aurais clarifié ce mystère en prenant contact avec la partie prenante responsable de la collecte et de la création des données. J'aurais posé de nombreuses questions jusqu'à m'assurer d'avoir parfaitement compris ce que représentent précisément les colonnes `prev`, `Ntop`, `Npop`, ainsi que les autres champs.

Dans le cadre de ce projet personnel, où j'ai téléchargé les données en open data sur le site de la CPAM, je vais simplement poursuivre mon analyse en utilisant la variable `prev` telle qu'elle est fournie dans le jeu de données.

## Création d'une table plus pertinente

D'après mes premières explorations et ce que je souhaite analyser, je réalise qu'il y a des colonnes et rangées dans le jeu de données qui ne sont pas pertinentes pour mon projet. Je vais donc dupliquer la table initiale dans BigQuery en ne gardant que les colonnes nécessaires. Je vais aussi filtrer certaines données pour ne conserver que les lignes pertinentes pour cette analyse.

Par exemple, certaines colonnes n'apportent rien à mon projet d'analyse, comme **Niveau prioritaire,** **Tri,** **Libellé classe d'âge**. Je ne vais pas garder non plus **Libellé sexe** et **Region**, car mon analyse aura une granularité plus fine si j'étudie la prévalence des pathologies par département et non par région. Comme la table initiale avait 16 colonnes et que j'en enlève 6, ma nouvelle table contiendra 10 colonnes.

Ensuite, comme on l'a vu, certaines lignes de la colonne **Patho Niv 1** contiennent les valeurs **“Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire”** et **“Total consommants tous régimes”.** Comme je souhaite répondre à des questions précises sur la prévalence de certaines pathologies en France, ces deux catégories ne sont pas pertinentes pour mon analyse et seront également exclues.

Voici ma requête SQL sur BiqQuery pour créer la table *cleaned\_cpam* :

```sql
-- Création de la table 'cleaned_cpam'

CREATE OR REPLACE
TABLE alien-oarlock-428016-f3.french_cpam.cleaned_cpam AS

SELECT
    annee,
    top,
    patho_niv1,
    patho_niv2,
    patho_niv3,
    dept,
    cla_age_5,
    sexe,
    Ntop,
    Npop,
    prev
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    patho_niv1 NOT LIKE "%Pas de patho%"
    AND patho_niv1 NOT LIKE "%Total conso%"
```

La table *cleaned_cpam* est bien créée :

![image18]

Ça a l'air de marcher ! Je n'ai effectivement que les colonnes qui m'intéressent.

Quand je clique sur Preview, je vois que le nombre de mes rangées est désormais de 4.515.840, inférieur au nombre initial de 4.636.840 (soit environ cent mille rangées en moins).

![image19]

Je vérifie quand même que les lignes contenant "Total consommants" ou "Pas de pathologies" dans la colonne `patho_niv1` ont bien été exclues :

![image20]

J'obtiens désormais la table *cleaned\_cpam*, plus petite et “nettoyée”, qui ne contient que les informations pertinentes pour mon analyse.

## Scission en plusieurs tables

Bien que ma nouvelle table `cleaned_cpam` soit plus petite, avec environ 4,6 millions de lignes et seulement 10 colonnes (comparée aux 16 colonnes initiales), elle reste monolithique et difficile à manipuler directement. Pour optimiser l'organisation des données et tendre vers une meilleure normalisation, je vais scinder la table "*cleaned\_cpam*" en plusieurs tables. Cette approche rendra mes requêtes SQL un tout petit peu plus longues à cause des jointures, mais cela va éviter les redondances et rendre mes analyses plus claires.

Au départ, j'avais prévu les tables suivantes : table *patient* (patient\_id, sexe, classe\_age…), table *pathologie* (patho\_1, patho\_2…), table *localisation* (dept\_id, dept\_name), etc..

Mais j'ai vite réalisé que les données ne concernent pas des patients individuels (pas d'entrées pour des personnes spécifiques avec des pathologies spécifiques). Comme c'est typiquement le cas dans le domaine de la santé, les données sont agrégées et anonymisées. Une table *patient* n'est donc pas appropriée, disons plutôt *patient\_stat* pour montrer la nature agrégée des données.

À noter, les pathologies semblent hiérarchisées (niveaux 1, 2 et 3), donc idéalement il devrait y avoir un champ 'parent\_id' pour représenter cette relation dans la table des pathologies. Cependant, \[alerte spoiler\] j'ai essayé de mettre en place une structure hiérarchique pendant plusieurs jours, sans succès. Je me résous donc à créer une table de pathologies avec une structure plate, tout comme la CPAM l'a fait.

Le libellé technique contenu dans la colonne 'top' initiale (par ex. CAN\_BPU\_SUR pour "cancer bronchopulmonaire sous surveillance") semble être unique à chaque combinaison de pathologie, catégorie et sous-catégorie. Je vais donc l'utiliser comme clé primaire dans ma table *patho.*

Notez que j'aurais aussi pu créer des tables séparées pour l'âge et le sexe si j'avais plusieurs colonnes associées, comme dans le jeu initial des données (Ex. 'cla\_age\_5' et 'libelle\_classe\_age' pour la table *age*, ainsi que 'sexe' et 'libelle\_sexe' pour la table *sex*). Mais je n'ai gardé qu'une seule colonne pour chaque table, donc cela n'a pas de sens de créer une table qui ne contient qu'une seule colonne, surtout si ces informations ne sont pas susceptibles de s'étendre dans le futur.

Voici ma structure de base de données :

### 1. Table patho

* **id** **(Primary Key)** : Équivalent à 'top' du jeu de données initial. Type : string
* **patho\_niv1** : Équivalent à 'patho\_niv1' du jeu de données initial. Type : string
* **patho\_niv2** : Équivalent à 'patho\_niv2' du jeu de données initial. Type : string
* **patho\_niv3** : Équivalent à 'patho\_niv3' du jeu de données initial. Type : string

### 2. Table dept

* **id (Primary Key)** : Équivalent à 'dept' du jeu de données initial. Code à 2 ou 3 chiffres. Ex. “40” pour les Landes, “2A” pour la Corse-du-Sud, “974” pour l'île de la Réunion, “99” pour tous départements confondus. Type : string
* **dept\_name** : Nom en toutes lettres du département. Ex. “Landes”. Les valeurs sont à créer car elles n'existent pas dans le jeu initial. Type : string

### 3. Table patient\_stat

* **annee** : Équivalent à 'annee' du jeu de données initial. Type : int
* **dept_id (FK)** : Foreign Key vers 'id' dans la table *dept*. Type : string
* **patho\id (FK)** : Foreign Key vers 'id' de la table *patho*. Type : string
* **age** : Équivalent à 'cla\_age\_5' du jeu de données initial. Ex. "30-34". Type : string
* **sex** : Équivalent à 'sexe' du jeu de données initial. Ex. 1 pour homme, 2 pour femme, 9 pour tous sexes. Type : int
* **Ntop** : Équivalent à 'Ntop' du jeu de données initial. Nombre de patients traités pour une pathologie spécifique. Type : int
* **Npop** : Équivalent à 'Npop' du jeu de données initial. Base de population utilisée pour les calculs de prévalence. Type : int
* **prev** : Équivalent à 'prev' du jeu de données initial. Prévalence indiquée en pourcentage pour une pathologie donnée. Type : float

---

Voici le point de départ pour structurer ma base de données en plusieurs tables dans BigQuery.

# Création et remplissage des trois tables

### 1. Création et remplissage de la table *patho* :

```sql
-- Création de la table patho, sans déclarer explicitement que la première colonne est la clé primaire (apparemment impossible de déclarer des PRIMARY KEYS dans BigQuery)

CREATE TABLE alien-oarlock-428016-f3.french_cpam.patho (
    id STRING NOT NULL, -- Clé qui servira de Primary Key ('top' de la table initiale)
    patho_niv1 STRING,
    patho_niv2 STRING,
    patho_niv3 STRING
);
```

```sql
-- Insertion des valeurs dans la table patho depuis la table cleaned_cpam

INSERT
    INTO
    alien-oarlock-428016-f3.french_cpam.patho (
        id,
        patho_niv1,
        patho_niv2,
        patho_niv3
    )
SELECT
    top, -- Utilisation du code technique 'top' comme identifiant
    patho_niv1,
    patho_niv2,
    patho_niv3
FROM
    alien-oarlock-428016-f3.french_cpam.cleaned_cpam
GROUP BY -- pour éviter les doublons
    top,
    patho_niv1,
    patho_niv2,
    patho_niv3;
```

Parfait, ça marche, avec une table à 77 lignes :

![image21]

![image22]

### 2. Création et remplissage de la table *dpt*

Je lance les deux requêtes SQL suivantes :

```sql
-- Création de la table dept
CREATE OR REPLACE
TABLE alien-oarlock-428016-f3.french_cpam.dept (
    id STRING,
    -- code du département (string à cause de '2A' et '2B' en Corse)
    dept_name STRING
    -- nom du département en toutes lettres
);
```

```sql
-- Insertion des noms des départements
INSERT
    INTO
    alien-oarlock-428016-f3.french_cpam.dept (
        id,
        dept_name
    )
VALUES
 ( "01", "Ain"),
 ( "02", "Aisne"),
 ( "03", "Allier"),
 ( "04", "Alpes-de-Haute-Provence"),
 ( "05", "Hautes-Alpes"),
 ( "06", "Alpes-Maritimes"),
 ( "07", "Ardèche"),
 ( "08", "Ardennes"),
 ( "09", "Ariège"),
 ( "10", "Aube"),
 ( "11", "Aude"),
 ( "12", "Aveyron"),
 ( "13", "Bouches-du-Rhône"),
 ( "14", "Calvados"),
 ( "15", "Cantal"),
 ( "16", "Charente"),
 ( "17", "Charente-Maritime"),
 ( "18", "Cher"),
 ( "19", "Corrèze"),
 ( "21", "Côte-d'Or"),
 ( "22", "Côtes-d'Armor"),
 ( "23", "Creuse"),
 ( "24", "Dordogne"),
 ( "25", "Doubs"),
 ( "26", "Drôme"),
 ( "27", "Eure"),
 ( "28", "Eure-et-Loir"),
 ( "29", "Finistère"),
 ( "2A", "Corse-du-Sud"),
 ( "2B", "Haute-Corse"),
 ( "30", "Gard"),
 ( "31", "Haute-Garonne"),
 ( "32", "Gers"),
 ( "33", "Gironde"),
 ( "34", "Hérault"),
 ( "35", "Ille-et-Vilaine"),
 ( "36", "Indre"),
 ( "37", "Indre-et-Loire"),
 ( "38", "Isère"),
 ( "39", "Jura"),
 ( "40", "Landes"),
 ( "41", "Loir-et-Cher"),
 ( "42", "Loire"),
 ( "43", "Haute-Loire"),
 ( "44", "Loire-Atlantique"),
 ( "45", "Loiret"),
 ( "46", "Lot"),
 ( "47", "Lot-et-Garonne"),
 ( "48", "Lozère"),
 ( "49", "Maine-et-Loire"),
 ( "50", "Manche"),
 ( "51", "Marne"),
 ( "52", "Haute-Marne"),
 ( "53", "Mayenne"),
 ( "54", "Meurthe-et-Moselle"),
 ( "55", "Meuse"),
 ( "56", "Morbihan"),
 ( "57", "Moselle"),
 ( "58", "Nièvre"),
 ( "59", "Nord"),
 ( "60", "Oise"),
 ( "61", "Orne"),
 ( "62", "Pas-de-Calais"),
 ( "63", "Puy-de-Dôme"),
 ( "64", "Pyrénées-Atlantiques"),
 ( "65", "Hautes-Pyrénées"),
 ( "66", "Pyrénées-Orientales"),
 ( "67", "Bas-Rhin"),
 ( "68", "Haut-Rhin"),
 ( "69", "Rhône"),
 ( "70", "Haute-Saône"),
 ( "71", "Saône-et-Loire"),
 ( "72", "Sarthe"),
 ( "73", "Savoie"),
 ( "74", "Haute-Savoie"),
 ( "75", "Paris"),
 ( "76", "Seine-Maritime"),
 ( "77", "Seine-et-Marne"),
 ( "78", "Yvelines"),
 ( "79", "Deux-Sèvres"),
 ( "80", "Somme"),
 ( "81", "Tarn"),
 ( "82", "Tarn-et-Garonne"),
 ( "83", "Var"),
 ( "84", "Vaucluse"),
 ( "85", "Vendée"),
 ( "86", "Vienne"),
 ( "87", "Haute-Vienne"),
 ( "88", "Vosges"),
 ( "89", "Yonne"),
 ( "90", "Territoire de Belfort"),
 ( "91", "Essonne"),
 ( "92", "Hauts-de-Seine"),
 ( "93", "Seine-Saint-Denis"),
 ( "94", "Val-de-Marne"),
 ( "95", "Val-d'Oise"),
 ( "971", "Guadeloupe"),
 ( "972", "Martinique"),
 ( "973", "Guyane"),
 ( "974", "La Réunion"),
 ( "976", "Mayotte"),
 ( "999", "Tous départements");
```

Résultats:

![image23]

![image24]

Ça marche, j'ai bien 102 entrées (les 101 départements français et l'entrée '`999`' pour 'tous départements').

### 3. Création et remplissage de la table *patient\_stat*

Je crée désormais la table *patient\_stat* pour pouvoir joindre les deux autres tables :

```sql
-- Création de la table patient_stat
CREATE OR REPLACE
TABLE alien-oarlock-428016-f3.french_cpam.patient_stat (
    annee INT64,
    dept_id STRING,  -- Foreign Key vers la table dept
    patho_id STRING, -- Foreign Key vers la table patho
    age STRING,      -- classe d'âge
    sex INT64,       -- sexe (1 pour homme, 2 pour femme, 9 pour tous)

    Ntop INT64,
    Npop INT64,
    prev FLOAT64
);
```

```sql
-- Insertion des données dans la table patient_stat
INSERT
    INTO
    alien-oarlock-428016-f3.french_cpam.patient_stat (
        annee,
        dept_id,
        patho_id,
        age,
        sex,
        Ntop,
        Npop,
        prev
    )

SELECT
    cleaned.annee,
    dept.id AS dept_id,   -- Jointure avec la table dept
    patho.id AS patho_id, -- Jointure avec la table patho (top)
    cleaned.cla_age_5 AS age,
    cleaned.sexe AS sex,
    cleaned.Ntop,
    cleaned.Npop,
    cleaned.prev
FROM
    alien-oarlock-428016-f3.french_cpam.cleaned_cpam AS cleaned
JOIN alien-oarlock-428016-f3.french_cpam.patho AS patho
 ON
    cleaned.top = patho.id -- Jointure sur la clé top (patho_id)
JOIN alien-oarlock-428016-f3.french_cpam.dept AS dept
 ON
    cleaned.dept = dept.id -- Jointure sur le code département
;
```

Ça marche !

Big Query affiche “This statement added 4,515,840 rows to patient_stat. “, ce qui correspond au même nombre de lignes que la table cleaned_cpam. Résultat cohérent.

**Voici la table** :

![image25]

![image26]

**\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\***

# Vérification des nouvelles tables

Maintenant que j'ai créé et peuplé mes trois nouvelles tables, procédons à quelques vérifications.

L'avantage d'avoir plusieurs petites tables est qu'elles sont plus faciles à gérer et à examiner. Voyons-les une à une :

### 1. Examen de la table *patho*

Cette table contient 77 lignes et 4 colonnes (`id`, `patho_niv1`, `patho_niv2`, `patho_niv3`). Maintenant que la table est plus petite, elle est plus facile à lire et à examiner. Je remarque que les colonnes '`id`' et '`patho_niv1`' sont entièrement remplies. En revanche, les colonnes '`patho_niv2`' et '`patho_niv3`' contiennent des valeurs nulles, comme observé précédemment.

Ces valeurs nulles correspondent à des pathologies sans sous-catégories (ce qui est souvent le cas dans les bases de données médicales) et ne reflètent pas un manque de données, mais plutôt l'absence de sous-division. De plus, je remarque que l'identifiant technique dans la colonne '`id`' inclut la chaîne 'CAT' pour décrire les pathologies de niv2 ou niv3 qui contiennent des valeurs nulles.

Exemples :

Id            |  Libellés |
--------------|-----------|
`CAT_CRE_ACT` | Cancers (niv1) / Cancer colorectal (niv2) / Cancer colorectal actif (niv3) |
`CAN_CAT_CAT` | Cancers (niv1) / Null (niv2) / Null (niv3) |

![image27]

### 2. Examen de la table *dpt*

Cette table possède 2 colonnes ('id' qui est le code du département, et 'dept\_name' qui est le nom en toutes lettres du département). La table contient 102 rangées (96 départements de la France métropolitaine, plus 5 départements d'Outre-mer, et 1 département fictif '99' agrégeant tous les départements).

Pour voir les départements dans l'ordre :

```sql
SELECT
    *
FROM
    alien-oarlock-428016-f3.french_cpam.dept
ORDER BY
    id;
```

![image28]

Petite vérification pour s'assurer que les deux départements de Corse sont bien inclus:

![image29]

Ainsi que les cinq départements d'Outre-mer:

![image30]

### 3. Examen de la table *patient\_stat*

Il s'agit de la table la plus large, avec 8 colonnes et plus de 4,5 millions de rangées (4 515 840).

Elle contient des valeurs Null dans les colonnes `Ntop` et `prev`, comme attendu.

![image26]

Comme on l'a déjà évoqué, les valeurs Null dans les colonnes `Ntop` et `prev` semblent indiquer des situations où il n'y a pas de patients traités pour une pathologie donnée dans une tranche d'âge ou un sexe spécifique. Par exemple, un groupe démographique peut ne pas être affecté par une pathologie particulière, d'où les valeurs Null dans `Ntop` (nombre de patients) et `prev` (prévalence).

Je décide de garder ces valeurs, mais je pourrai les filtrer ultérieurement dans mes analyses où leur présence pourrait fausser les résultats ou les visualisations.

# Il est temps pour l'analyse proprement dite

Maintenant que mes données ont été nettoyées et organisées dans BigQuery, il est temps de passer à l'analyse proprement dite. Comme mentionné au début de cet article, voici les trois grandes questions que je souhaite explorer à travers ces données :

* **Quelle est la fréquence/prévalence des pathologies spécifiques (cancer, diabète, etc.) en 2022, selon les départements français ?** Je souhaite identifier comment ces maladies se répartissent à travers les différents départements en France.
* **Comment ces pathologies ont-elles évolué entre 2015 et 2022 ?** Y a-t-il des tendances marquantes au fil des ans ?
* **La vague COVID-19 a-t-elle eu un impact sur certaines pathologies entre 2020 et 2022 ?** Les années 2020 à 2022 pourraient révéler des tendances intéressantes (baisses ou pics) à ce sujet.

**Explication du processus d'analyse à venir**

Comme mes données sont dans BigQuery, je vais continuer à utiliser des requêtes SQL pour explorer les données. Toutefois, je vais aussi automatiser les requêtes à l'aide de scripts R pour rendre tout le processus plus fluide, mieux documenté et surtout reproductible.

Je vais commencer par analyser les données les plus récentes (2022) pour répondre à ma première question. Ensuite, je me pencherai sur les années précédentes pour voir comment ces pathologies ont évolué entre 2015 et 2022, répondant ainsi à ma deuxième question. Enfin, je tenterai de déceler des tendances post-COVID (2020-2022) pour répondre à ma troisième question.

Tout ceci sera documenté dans la **Partie 2 de mon article** (lien).

[image1]: images/image01.png
[image2]: images/image2.png
[image3]: images/image3.png
[image4]: images/image4.png
[image5]: images/image5.png
[image6]: images/image6.png
[image7]: images/image7.png
[image8]: images/image8.png
[image9]: images/image9.png
[image10]: images/image10.png
[image11]: images/image11.png
[image12]: images/image12.png
[image13]: images/image13.png
[image14]: images/image14.png
[image15]: images/image15.png
[image16]: images/image16.png
[image17]: images/image17.png
[image18]: images/image18.png
[image19]: images/image19.png
[image20]: images/image20.png
[image21]: images/image21.png
[image22]: images/image22.png
[image23]: images/image23.png
[image24]: images/image24.png
[image25]: images/image25.png
[image26]: images/image26.png
[image27]: images/image27.png
[image28]: images/image28.png
[image29]: images/image29.png
[image30]: images/image30.png
