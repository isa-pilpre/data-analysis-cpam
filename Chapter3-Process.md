# Chapter 3: Process

## 1) Aperçu des données sur le site de la CPAM

Commençons par examiner le modèle de données et les 100 premières lignes de la table sur le site de la CPAM :

![ ](images/cpam_16.png)

Sous le premier onglet `Informations`, si l'on fait défiler la page vers le bas jusqu'à `Modèle de données`, on obtient des informations sur les colonnes de la table et leur type de données.

Si l'on va sur le deuxième onglet `Tableau`, on peut visualiser les premières lignes du jeu de données :

![ ](images/cpam_17.png)

On apprend ainsi que le jeu de données se compose d'une table avec une douzaine de colonnes :

Colonne | Description | Type   |
--------|-------------|--------|
`annee` | les années que couvre cette période d'analyse, qui s'étendent actuellement de 2015 à 2022. | date |
`patho_niv1`, `patho_niv2`, `patho_niv3` | groupe ou sous-groupe de pathologies (ou traitements chroniques ou épisodes de soins). | texte |
`top` | libellé technique de la pathologie. Ex. `CAN_CAT_CAT`. | texte |
`cla_age_5` | classe d'âge (tranche de 5 années). Ex : `30-34`. | texte |
`libelle_classe_age` | classe d'âge en toutes lettres, par ex. `de 30 à 34 ans`. | texte |
`sexe` | `1` pour homme, `2` pour femme, et `9` pour 'tous sexes'. | texte |
`libelle_sexe` | trois options : `homme`, `femme`, `tous sexes`. | texte |
`region` | code INSEE de chaque région française. Le code `99` signifie `toutes régions`. | texte |
`dept` | code INSEE de chaque département. Le code `999` signifie `tous départements`. | texte |
`Ntop` | effectif de patients pris en charge pour la pathologie (ou traitement chronique ou épisode de soins) dont il est question. | entier |
`Npop` | population de référence qui est celle de la cartographie des pathologies et des dépenses de l'Assurance Maladie. | entier |
`prev` | prévalence de patients pris en charge pour la pathologie (ou traitement chronique ou épisode de soins) dont il est question. Ex. `0.867`. | décimal |

### Petit rappel sur la notion de prévalence

La prévalence fait référence à la proportion d'individus dans une population qui ont une maladie ou un problème de santé spécifique, au cours d'une période donnée. La prévalence englobe aussi bien les nouveaux cas que les cas déjà déclarés.

Contrairement à l'incidence (qui mesure uniquement le taux de nouveaux cas), la prévalence dépend de la durée de la maladie.

Dans ce jeu de données, le champ `prev` représente la prévalence, calculée comme le ratio de `Ntop` (le nombre de personnes recevant des soins pour une pathologie spécifique) sur `Npop` (la population de référence pour cette pathologie) :

```math
prévalence=\frac{Ntop}{Npop}
```

C'est pourquoi le champ de prévalence `prev` a un type de données 'float' ou décimal, ce qui signifie qu'il s'agit d'une valeur décimale.

Par exemple, si 3 000 personnes reçoivent des soins pour des troubles psychiatriques au cours d'une année donnée dans une région spécifique avec une population de référence de 100 000 personnes, la prévalence serait :

```math
prev=\frac{3\ 000}{100\ 000}=0,03\ ou\ 3\%
```


## 2) Exploration dans BigQuery avec SQL

Après avoir inspecté les premières lignes du jeu de données sur le site de la CPAM, je continue désormais mon exploration dans BigQuery, pour avoir un meilleur contrôle.

### Comprendre la structure de BigQuery

Pour exécuter des requêtes SQL dans BigQuery et faire des SELECT… FROM…, il faut donner le chemin complet des tables dans la base de données, à savoir :

-  **L'ID du projet** : Chaque projet dans BigQuery possède un identifiant unique. Comme mentionné précédemment, l'ID de projet attribué ici par BigQuery est `alien-oarlock-428016-f3`.
-  **L'ID du dataset** : Au sein de chaque projet, vous pouvez avoir plusieurs ensembles de données (*datasets*). Un *dataset* est comme un conteneur qui stocke vos tables. Pour ce projet, j'ai créé un ensemble de données appelé `french_cpam`.
-  **Le nom de la table** : Au sein du *dataset*, les données sont stockées dans des tables. Ma table s'appelle `cpam_effectifs_july_2024`.

Lorsqu'on lance une requête SQL, il faut ainsi spécifier le chemin complet de la table, à savoir l'ID du projet, l'ID du dataset, et le nom de la table.

### Taille du jeu de données

Voyons la taille du jeu de données :

```sql
SELECT
    COUNT(*) AS `Number of rows`
FROM
    `alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024`;
```

Résultats :

Row   | Number of rows |
----- | -------------- |
 1    | 4636800        |

Il y a donc plus de 4 millions de lignes dans mon jeu de données (précisément 4 636 800 lignes). Ce volume important de données me conforte dans mon choix d'avoir utilisé une plateforme robuste comme BigQuery, qui peut gérer de larges ensembles de données.

La taille imposante de cette table monolithique me fait songer à la diviser en tables plus petites et plus faciles à gérer, dans un souci de normalisation et d'optimisation des requêtes. Mais pour l'instant, terminons les requêtes de base.

### Nombre de colonnes

Voyons le nombre de colonnes de la table `cpam_effectifs_july_2024`, selon la formule :

```sql
SELECT
    COUNT(*)
FROM
    INFORMATION_SCHEMA.COLUMNS
WHERE
    table_name = [my_table_name]
```

Toutefois, comme on l'a vu dans BigQuery, je dois inclure l'ID du projet et l'ID du dataset ID avant `INFORMATION_SCHEMA.COLUMNS` :

```sql
SELECT
    COUNT(*) AS number_of_columns
FROM
    alien-oarlock-428016-f3.french_cpam.INFORMATION_SCHEMA.COLUMNS
WHERE
    table_name = 'cpam_effectifs_july_2024';
```

Résultats :

Row  | number_of_columns |
---- | ---- |
1    | 16 |

La table contient 16 colonnes, ce qui me paraît beaucoup. Pour vérifier, affichons le nom de toutes les colonnes :

```sql
SELECT
    column_name
FROM
    alien-oarlock-428016-f3.french_cpam.INFORMATION_SCHEMA.COLUMNS
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

Ce résultat correspond à ce qui est affiché sur le site de la CPAM, donc tout est correct. 

Cependant, pour mon projet d'analyse, certaines colonnes ne sont pas pertinentes, à savoir :

* `Niveau prioritaire` (Ex : 1, 2, 3) : aucune explication supplémentaire
* `tri` (Ex. 8) : aucune explication supplémentaire sur le site de la CPAM
* `libelle classe age` (Ex. '30 à 34 ans') : cela n'apporte rien par rapport à `cla_age_5` (Ex. '30-34).


### Inspection des premières lignes

```sql
SELECT
    *
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
LIMIT 100;
```

Résultats:

L'aperçu des données révèle des points intéressants. Notamment, les 3 colonnes des pathologies (niveau 1, 2 et 3) contiennent deux valeurs qui attirent mon attention :

* `Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire` : ça semble indiquer des enregistrements où aucune pathologie ni aucun type de traitement n'a été nécessaire.
* `Total consommants tous régimes` : cela semble représenter le total de tous les bénéficiaires du système de santé en France, tous régimes confondus. Cela ne spécifie pas une pathologie particulière, mais semble plutôt agréger les données pour toutes les pathologies. Pour ces entrées, les champs `Ntop` (nombre de patients traités) et `Npop` (population de référence) affichent le même nombre (10 970) pour le groupe d'âge 0-4 ans, aboutissant à un taux de prévalence calculé de 100 %.

De manière similaire à d'autres indicateurs agrégés (comme `9` représentant `tous sexes`, `999` pour `tous départements`, et `99` pour `toutes les régions`), la valeur `Total consommants tous régimes` dans les colonnes de pathologie semble représenter un récapitulatif pour l'ensemble de la population.

Ainsi donc, **certaines lignes agrègent les données** plutôt que d'afficher des enregistrements individuels. C'est important à noter, car il ne faut absolument pas de doublons lors de l'analyse des données, sous peine d'avoir des résultats faussés.

Pour m'assurer que je comprends bien ces entrées, je lance les requêtes SQL suivantes, en mentionnant spécifiquement les valeurs agrégées du sexe (`9`), des départements (`999`), des régions (`99`), des groupes d'âge (`tsage`), ainsi qu'une année donnée (`2022`), afin d'éviter toute duplication de données :

```sql
-- Ntop for 'Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire' for the year 2022 and all ages
SELECT
    SUM(Ntop) AS sum_no_pathology
FROM
    `alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024`
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
    `alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024`
WHERE
    patho_niv1 = 'Total consommants tous régimes'
    AND sexe = 9
    AND dept = '999'
    AND region = 99
    AND cla_age_5 = 'tsage'
    AND annee = 2022;
```

**Résultats:**

Résultats    | Valeurs |
-----------|----|
37 919 240 | `sum_no_pathology` |
68 729 230 | `sum_total_consumers` |

La valeur des `total consommants tous régimes` semble exacte, car le site de la CPAM rapporte « 68,7 millions de bénéficiaires de soins de santé en France pour 2022 ».

La valeur de quasi 38 millions de personnes sans pathologie en 2022 (c'est-à-dire plus d'une personne sur deux en France) semble plausible, bien que cela me surprenne quelque peu. Je pourrais avoir besoin d'approfondir cette analyse plus tard pour valider cette conclusion.

Globalement, les résultats des données semblent cohérents.

### Recherche des valeurs nulles

Voyons s'il y a des valeurs nulles dans la table `cpam_effectifs_july_2024`:

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

**Résultats** :

Je trouve des valeurs nulles principalement dans les colonnes `patho_nov2` (483 840 occurrences) et `patho_nov3` (1 048 320 occurrences), ce qui suggère que certaines `patho_niv1` ne se divisent pas en sous-catégories.

La colonne `Ntop` (nombre de patients) contient également de nombreux nulls : précisément 1 238 024 nulls. Ce grand nombre m'interpelle. Pour en savoir plus, je lance la requête suivante pour examiner les 100 premières lignes où `Ntop` est nul, et vérifie les valeurs des autres colonnes dans ces lignes :

```sql
SELECT
    *
FROM
    alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024
WHERE
    Ntop IS NULL
LIMIT 100
```

**Résultats:**

Les résultats sont révélateurs. Les cent premières lignes avec une valeur nulle dans la colonne `Ntop` (indiquant l'absence de patients) correspondent au groupe d'âge très jeune de 0 à 4 ans, sans cas de cancer enregistrés. Cela reflète la réalité que certaines pathologies sont absentes ou extrêmement rares dans certaines tranches démographiques, comme certains groupes d'âge ou sexes. Cela a du sens et me rassure sur le fait que ces valeurs nulles indiquent probablement une faible prévalence ou l'absence de ces pathologies, plutôt que des données manquantes.

Pour confirmer mon hypothèse et obtenir une vue plus large, je lance la requête suivante :

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

![](images/cpam_22.png)

Les résultats montrent des tendances pour lesquelles certains groupes d'âge, comme les très jeunes ou les très âgés, n'ont aucun cas enregistré pour certaines pathologies, telles que des maladies inflammatoires ou des cancers. De plus, certains sexes n'ont pas de cas enregistrés pour des conditions spécifiques, comme les patients masculins pour le cancer du sein féminin. Ces résultats renforcent mon idée que les valeurs nulles dans `Ntop` (nombre de patients) sont cohérentes avec les tendances démographiques attendues de la prévalence des maladies.

Pour garantir l'intégrité des données, je vérifie que le nombre total de valeurs nulles identifiées dans la requête précédente correspond bien aux 1 238 024 valeurs nulles de `Ntop` que nous avons trouvées plus tôt. Au passage, cela me permet d'utiliser une sous-requête imbriquée dans une requête :

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

Le résultat est conforme aux attentes :

Row | Total_Null_Ntop |
----|---------|
1   | 1238024 |

Comme prévu, nous obtenons 1 238 024 valeurs nulles pour `Ntop`. L'intégrité des données semble assurée.

## 4) Nettoyage de la table `cpam.cpam_effectifs_july_2024`

Avant de procéder à l'analyse, je vais donc filtrer les données non pertinentes que nous avons identifiées précédemment, à savoir les colonnes `Niveau prioritaire`, `Tri` et `Libellé classe d'âge`. 
Aussi, comme on l'a vu, certaines lignes de la colonne `patho_niv1` contiennent les valeurs `Pas de pathologie repérée, traitement, maternité, hospitalisation ou traitement antalgique ou anti-inflammatoire` et `Total consommants tous régimes` qui ne sont pas pertinentes pour mon analyse et vont aussi être exclues.

Voici ma requête SQL sur BiqQuery pour nettoyer la table `cpam.cpam_effectifs_july_2024` et créer la table `cleaned_cpam` à la place :

```sql
-- Création de la table 'cleaned_cpam'

CREATE OR REPLACE
TABLE `alien-oarlock-428016-f3.french_cpam.cleaned_cpam` AS

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
    `alien-oarlock-428016-f3.french_cpam.cpam_effectifs_july_2024`
WHERE
    patho_niv1 NOT LIKE "%Pas de patho%"
    AND patho_niv1 NOT LIKE "%Total conso%"
```

La table `cleaned_cpam` est bien créée :

![](images/cpam_25.png)

La table `cleaned_cpam` ne possède effectivement que les colonnes qui m'intéressent.

Quand je clique sur `Preview`, je vois que le nombre de mes rangées est désormais de 4.515.840, inférieur au nombre initial de 4.636.840 (soit environ cent mille rangées en moins).

Je vérifie quand même que les lignes contenant `Total consommants` ou `Pas de pathologies` dans la colonne `patho_niv1` ont bien été exclues :

![](images/cpam_27.png)

J'obtiens désormais la table `cleaned_cpam`, plus petite et filtrée. Les données sont désormais prêtes pour l'analyse.
