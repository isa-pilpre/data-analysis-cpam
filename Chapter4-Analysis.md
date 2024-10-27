# Chapter 4: Analysis

Maintenant que mes données sont filtrées et organisées en trois tables dans BigQuery, il est temps de passer à l'analyse. 



## 1) Examen plus approfondi des pathologies répertoriées dans ce jeu de données

Grâce à la division des tables, il est facile désormais d'examiner la liste des patholgies dans la table `patho`.
Pour rappel, cette table contient 77 lignes et 4 colonnes (`id`, `patho_niv1`, `patho_niv2`, `patho_niv3`). Je remarque que les colonnes `id` et `patho_niv1` sont entièrement remplies. En revanche, les colonnes `patho_niv2` et `patho_niv3` contiennent des valeurs nulles, comme observé précédemment.

![](images/cpam_34.png)


Ces valeurs nulles correspondent à des pathologies sans sous-catégories (ce qui est souvent le cas dans les bases de données médicales) et ne reflètent pas un manque de données, mais plutôt l'absence de sous-division. De plus, je remarque que l'identifiant technique dans la colonne `id` inclut la chaîne 'CAT' pour décrire les pathologies de niv2 ou niv3 qui contiennent des valeurs nulles.

Exemples :

Id            |  Libellés |
--------------|-----------|
`CAT_CRE_ACT` | Cancers (niv1) / Cancer colorectal (niv2) / Cancer colorectal actif (niv3) |
`CAN_CAT_CAT` | Cancers (niv1) / Null (niv2) / Null (niv3) |


Pour y voir plus clair, je fais un `Export` / `Explore with Sheets` depuis BigQuery pour ouvrir cette table dans Google Sheets. Là je surligne les pathologies qui m'intéressent ppur mon analyse exploratoire. 

![](images/cpam_50.png)


Pour filtrer encore mes données, je vais mettre à jour la table `patho` pour ne garder que les lignes que j'ai surlignées dans Google Sheets, et qui correspondent à une `patho.id` unique. Je vais ensuite supprimer les colonnes redondantes `patho_niv1`, `patho_niv2` et `patho_niv3`, et ajouter une colonne `libelle` qui contiendra un libellé clair de la pathologie en question.

Les pathologies que je vais garder sont celles-ci, avec leur nouveau libellé dans `libelle` :

| Code        | Libellé                                                   |
|-------------|-----------------------------------------------------------|
| CAN_BPU_CAT | Cancer bronchopulmonaire                                  |
| CAN_SEI_CAT | Cancer du sein de la femme                                |
| CAN_CRE_CAT | Cancer colorectal                                         |
| CAN_PRO_CAT | Cancer de la prostate                                     |
| DIA_CAT_CAT | Diabète                                                   |
| NEU_SEP_IND | Sclérose en plaques                                       |
| NEU_DEM_CAT | Démences (dont Alzheimer)                                 |
| NEU_EPI_IND | Épilepsie                                                 |
| NEU_LME_IND | Lésion médullaire                                         |
| NEU_PRK_IND | Maladie de Parkinson                                      |
| NEU_MMY_IND | Myopathie ou myasthénie                                   |
| PSY_PSC_IND | Troubles psychotiques                                     |
| PSY_ADD_CAT | Troubles addictifs                                        |
| INF_COV_HOS | Hospitalisation pour Covid-19                             |
| MCV_SCO_CAT | Maladie coronaire                                         |
| MCV_AVC_AIG | Accident vasculaire cérébral aigu                         |
| MCV_ICA_AIG | Insuffisance cardiaque aiguë                              |
| MCV_SCO_AIG | Syndrome coronaire aigu                                   |
| MCV_EPU_IND | Embolie pulmonaire                                        |
| MCV_ICA_CAT | Insuffisance cardiaque                                    |
| MCV_MVA_IND | Maladie valvulaire                                        |
| IRT_DCH_CAT | Dialyse chronique                                         |
| TPS_ADR_EXC | Antidépresseurs/régulateurs d’humeur (hors pathologies)   |
| TPS_ANX_EXC | Anxiolytiques (hors pathologies)                          |
| IFL_PRM_IND | Polyarthrite rhumatoïde                                   |
| RAR_MUC_IND | Mucoviscidose                                             |
| IFL_MIC_IND | Maladies inflammatoires chroniques intestinales           |
| RES_CAT_EXC | Maladies respiratoires chroniques (hors mucoviscidose)    |


C'est sans doute plus qu'il n'en faut pour ce projet personnel, mais je pourrai toujours explorer ces pistes plus tard.

- Étape 1 : Création de la table `filtered_patho`

``` sql 
CREATE TABLE `alien-oarlock-428016-f3.french_cpam.filtered_patho` AS
SELECT id
FROM `alien-oarlock-428016-f3.french_cpam.patho`
WHERE id IN (
    'CAN_BPU_CAT', 'CAN_SEI_CAT', 'CAN_CRE_CAT', 'CAN_PRO_CAT', 'DIA_CAT_CAT', 'NEU_SEP_IND',
    'NEU_DEM_CAT', 'NEU_EPI_IND', 'NEU_LME_IND', 'NEU_PRK_IND', 'NEU_MMY_IND', 'PSY_PSC_IND',
    'PSY_ADD_CAT', 'INF_COV_HOS', 'MCV_SCO_CAT', 'MCV_AVC_AIG', 'MCV_ICA_AIG', 'MCV_SCO_AIG',
    'MCV_EPU_IND', 'MCV_ICA_CAT', 'MCV_MVA_IND', 'IRT_DCH_CAT', 'TPS_ADR_EXC', 'TPS_ANX_EXC',
    'IFL_PRM_IND', 'RAR_MUC_IND', 'IFL_MIC_IND', 'RES_CAT_EXC'
);

```

- Étape 2 : Ajout d'une colonne `libelle` et mise à jour des libellés avec Python

Comme il est facile d'intégrer un script Python dans un notebook de Google Query, j'exécute le script suivant pour ajouter et remplir une nouvelle colonne `libelle` dans la table `filtered_patho` :

``` python
from google.cloud import bigquery
import pandas as pd

# Initialiser le client BigQuery
client = bigquery.Client()

# Lire la table BigQuery dans un dataframe
query = """
    SELECT * FROM `alien-oarlock-428016-f3.french_cpam.filtered_patho`
"""
df = client.query(query).to_dataframe()

# Ajouter la colonne `libelle` en fonction des critères
df['libelle'] = df['id'].map({
    "CAN_BPU_CAT": "Cancer bronchopulmonaire",
    "CAN_SEI_CAT": "Cancer du sein de la femme",
    "CAN_CRE_CAT": "Cancer colorectal",
    "CAN_PRO_CAT": "Cancer de la prostate",
    "DIA_CAT_CAT": "Diabète",
    "NEU_SEP_IND": "Sclérose en plaques",
    "NEU_DEM_CAT": "Démences (dont Alzheimer)",
    "NEU_EPI_IND": "Épilepsie",
    "NEU_LME_IND": "Lésion médullaire",
    "NEU_PRK_IND": "Maladie de Parkinson",
    "NEU_MMY_IND": "Myopathie ou myasthénie",
    "PSY_PSC_IND": "Troubles psychotiques",
    "PSY_ADD_CAT": "Troubles addictifs",
    "INF_COV_HOS": "Hospitalisation pour Covid-19",
    "MCV_SCO_CAT": "Maladie coronaire",
    "MCV_AVC_AIG": "Accident vasculaire cérébral aigu",
    "MCV_ICA_AIG": "Insuffisance cardiaque aiguë",
    "MCV_SCO_AIG": "Syndrome coronaire aigu",
    "MCV_EPU_IND": "Embolie pulmonaire",
    "MCV_ICA_CAT": "Insuffisance cardiaque",
    "MCV_MVA_IND": "Maladie valvulaire",
    "IRT_DCH_CAT": "Dialyse chronique",
    "TPS_ADR_EXC": "Antidépresseurs/régulateurs d’humeur (hors pathologies)",
    "TPS_ANX_EXC": "Anxiolytiques (hors pathologies)",
    "IFL_PRM_IND": "Polyarthrite rhumatoïde",
    "RAR_MUC_IND": "Mucoviscidose",
    "IFL_MIC_IND": "Maladies inflammatoires chroniques intestinales",
    "RES_CAT_EXC": "Maladies respiratoires chroniques (hors mucoviscidose)"
})

# Remplacer les valeurs NaN par une chaîne vide si nécessaire
df['libelle'].fillna('', inplace=True)

# Charger les données mises à jour dans BigQuery
table_id = "alien-oarlock-428016-f3.french_cpam.filtered_patho"

job_config = bigquery.LoadJobConfig(
    write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
)

# Charger le dataframe dans la table BigQuery
job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
job.result()  # Attendre la fin de l'upload

print("Table mise à jour avec succès dans BigQuery.")

```

La table `filtered_patho` est bien créée et remplie comme il faut, avec 2 colonnes et 28 rangées : 

![](images/cpam_51.png)

![](images/cpam_52.png)




## 2) Prévalence des pathologies selon les départements

Puisque l'obectif de cette analyse exploratoire des données est de répondre à trois questions : 1) analyser la prévalence des pathologies selon les départements en 2022, 2) voir l'évolution de ces pathologies de 2015 à 2022, et 3) voir si la vague Covid 2019-2020 a eu un impact sur ces pathologies, commençons par analyser la prévalence de certaines pathologies spécifiques en 2022.


### Prévalence du cancer du poumon en France en 2022

``` sql 
SELECT 
    ps.prev,
    fp.libelle,
    d.id,
    d.nom_dept,
    
FROM `alien-oarlock-428016-f3.french_cpam.patient_stat` as ps
JOIN `alien-oarlock-428016-f3.french_cpam.filtered_patho` as fp
ON ps.patho_id = fp.id
JOIN `alien-oarlock-428016-f3.french_cpam.dept` as d
ON ps.dept_id = d.id

WHERE ps.annee = 2022
AND   ps.age = "tsage"
AND   ps.sex = 9
AND   fp.id = "CAN_BPU_CAT" -- code pour le cancer bronchopumonaire
AND   d.id != "999" 

ORDER BY ps.prev DESC
LIMIT 10 ;
```

Résultat :

| Row | prev | libelle                | id | nom_dept           |
|-----|------|-------------------------|----|---------------------|
| 1   | 0.411| Cancer bronchopulmonaire | 2A | Corse-du-Sud       |
| 2   | 0.406| Cancer bronchopulmonaire | 2B | Haute-Corse        |
| 3   | 0.351| Cancer bronchopulmonaire | 08 | Ardennes           |
| 4   | 0.340| Cancer bronchopulmonaire | 58 | Nièvre             |
| 5   | 0.338| Cancer bronchopulmonaire | 09 | Ariège             |
| 6   | 0.337| Cancer bronchopulmonaire | 55 | Meuse              |
| 7   | 0.331| Cancer bronchopulmonaire | 54 | Meurthe-et-Moselle |
| 8   | 0.329| Cancer bronchopulmonaire | 57 | Moselle            |
| 9   | 0.323| Cancer bronchopulmonaire | 83 | Var                |
| 10  | 0.322| Cancer bronchopulmonaire | 29 | Finistère          |



### Prévalence du cancer colorectal en France en 2022

``` sql 
SELECT 
    ps.prev,
    fp.libelle,
    d.id,
    d.nom_dept,
    
FROM `alien-oarlock-428016-f3.french_cpam.patient_stat` as ps
JOIN `alien-oarlock-428016-f3.french_cpam.filtered_patho` as fp
ON ps.patho_id = fp.id
JOIN `alien-oarlock-428016-f3.french_cpam.dept` as d
ON ps.dept_id = d.id

WHERE ps.annee = 2022
AND   ps.age = "tsage"
AND   ps.sex = 9
AND   fp.id = "CAN_CRE_CAT" -- code pour le cancer colorectal
AND   d.id != "999" 

ORDER BY ps.prev DESC
LIMIT 10 ;
```


Résultat:

| Row | prev | libelle           | id | nom_dept       |
|-----|------|--------------------|----|----------------|
| 1   | 0.929| Cancer colorectal | 81 | Tarn           |
| 2   | 0.810| Cancer colorectal | 23 | Creuse         |
| 3   | 0.795| Cancer colorectal | 29 | Finistère      |
| 4   | 0.793| Cancer colorectal | 46 | Lot            |
| 5   | 0.773| Cancer colorectal | 58 | Nièvre         |
| 6   | 0.747| Cancer colorectal | 11 | Aude           |
| 7   | 0.737| Cancer colorectal | 36 | Indre          |
| 8   | 0.734| Cancer colorectal | 10 | Aube           |
| 9   | 0.729| Cancer colorectal | 03 | Allier         |
| 10  | 0.728| Cancer colorectal | 12 | Aveyron        |






















#### À propos du nombre de patients (`Ntop`)

Les résultats montrent une moyenne `Ntop` de 5 527 bénéficiaires de soins de santé par combinaison unique de pathologie, groupe d'âge, sexe, région et année. Cela signifie que, pour toutes les combinaisons de ces facteurs, il y a en moyenne 5 527 personnes recevant des soins pour une condition spécifique dans une population et un lieu donnés.

La valeur maximale de `Ntop` est de 68 729 230, ce qui représente le nombre total de bénéficiaires de soins de santé en France pour l'année 2022. Cela correspond parfaitement au site de la CPAM, où il est indiqué « 68,7 millions de bénéficiaires ont reçu au moins un service de santé pris en charge par l'assurance maladie ».

Le nombre minimum de `Ntop` (10 patients) reflète des cas où seulement un petit nombre d'individus, au sein d'une combinaison spécifique de facteurs (comme une pathologie rare dans un certain groupe d'âge et une région donnée), ont reçu un traitement.

#### À propos de la prévalence (`prev`)

La prévalence moyenne est de 6,21, avec des extrêmes allant de 0 à 100, qu'on avait déjà aperçu dans le premier extrait de données. Ces résultats extrêmes sont à creuser pour bien les comprendre. Aussi, je voudrais m'assurer que la prévalence (`prev`) indiquée dans ce jeu de données est bien le rapport entre Ntop par Npop. Je ferai cette vérification très prochainement. ISA work needed.

**Notons deux choses importantes** :

* On réalise ici que la **prévalence est affichée en pourcentage par la CPAM**, étant donné que la valeur maximale de `prev` est de 100. Donc la prévalence maximale est de 100 %.
* Si le minimum de `Ntop` n'est pas zéro mais bien 10, le minimum de la prévalence ne devrait pas être zéro (car Prévalence \= Ntop / Npop). Cependant, j'ai remarqué que de nombreuses entrées de `Ntop` étaient nulles, ce qui peut expliquer le résultat de zéro pour la prévalence (puisque `Ntop` est absent), même si `Ntop` ne contient pas de zéro explicite. La fonction `MIN()` ignore souvent les valeurs nulles, donc si `Ntop` contient des valeurs nulles ou non renseignées, la fonction peut afficher un minimum de 10 (la première valeur numérique non nulle). Il faudra donc vérifier si `Ntop` contient des valeurs nulles pour confirmer cette hypothèse.


## 2) Prévalence, sa signification précise dans ce jeu de données

Afin de m'assurer de bien comprendre ce que signifie exactement la prévalence (prev) dans ce jeu de données, car il s'agit de la variable principale de mon analyse, je lance la requête SQL suivante dans BigQuery.

J'exclus toutes les valeurs agrégées, à savoir "tous sexes" (`sexe != 9`), "tous départements" (`dept != '999'`), "toutes régions" (`region != 99`), et "tous âges" (`cla_age_5 != 'tsage'`).
Je calcule la prévalence à partir des colonnes `Ntop` et `Npop` (Ntop/Npop), en l'arrondissant à trois décimales, comme la variable prev fournie dans le jeu de données.
Puis je cherche les entrées où la différence entre la prévalence fournie et celle calculée dépasse 0,001 :

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

### Résultats

Les plus grandes différences entre `prev` et `calculated_prev` concernent principalement les personnes âgées, en particulier celles de 95 ans et plus, ainsi que les 85-89 ans. Ces écarts apparaissent lorsque les valeurs de `Ntop` et `Npop` sont petites et semblent arrondies de manière inhabituelle (120, 190, 110, 200, etc.). Cela pourrait indiquer des ajustements ou un lissage dans le processus de calcul des prévalences pour ces tranches d'âge, où les effectifs sont plus faibles et plus susceptibles de variations.

![ ](images/cpam_23.png)

![ ](images/cpam_24.png)

Ces résultats ne m'inquiètent pas pour mon projet d'analyse. Cependant, dans un contexte professionnel, si je travaillais pour une entreprise propriétaire de ce jeu de données, j'aurais clarifié ce mystère en prenant contact avec la partie prenante responsable de la collecte et de la création des données. J'aurais posé toutes les questions requises jusqu'à m'assurer d'avoir parfaitement compris ce que représentent précisément les colonnes `prev`, `Ntop`, `Npop`, ainsi que les autres champs.

Dans le cadre de ce projet personnel d'analyse exploratoire, où j'ai téléchargé les données en open data sur le site de la CPAM, je vais simplement poursuivre mon analyse en utilisant la variable `prev` telle qu'elle est fournie dans le jeu de données.


