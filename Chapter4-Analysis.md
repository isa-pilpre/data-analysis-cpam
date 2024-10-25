# Chapter 4: Analysis

Maintenant que mes données ont été nettoyées et organisées dans BigQuery, il est temps de passer à l'analyse proprement dite. 

## Rappel de l'objectif / des trois questions clés

Comme mentionné au départ, voici les trois grandes questions que je souhaite explorer à travers ces données :

* **Quelle est la fréquence/prévalence des pathologies spécifiques (cancer, diabète, etc.) en 2022, selon les départements français ?** Je souhaite identifier comment ces maladies se répartissent à travers les différents départements en France.
* **Comment ces pathologies ont-elles évolué entre 2015 et 2022 ?** Y a-t-il des tendances marquantes au fil des ans ?
* **La vague COVID-19 a-t-elle eu un impact sur certaines pathologies entre 2020 et 2022 ?** Les années 2020 à 2022 pourraient révéler des tendances intéressantes (baisses ou pics) à ce sujet.

**Explication du processus d'analyse à venir**

Comme mes données sont dans BigQuery, je vais continuer à utiliser des requêtes SQL pour explorer les données. Toutefois, je vais aussi automatiser les requêtes à l'aide de scripts R pour rendre tout le processus plus fluide, mieux documenté et surtout reproductible.

Je vais commencer par analyser les données les plus récentes (2022) pour répondre à ma première question. Ensuite, je me pencherai sur les années précédentes pour voir comment ces pathologies ont évolué entre 2015 et 2022, répondant ainsi à ma deuxième question. Enfin, je tenterai de déceler des tendances post-COVID (2020-2022) pour répondre à ma troisième question.

[cpam_01]: images/cpam_01.png
[cpam_02]: images/cpam_02.png
[cpam_03]: images/cpam_03.png
[cpam_04]: images/cpam_04.png
[cpam_05]: images/cpam_05.png
[cpam_06]: images/cpam_06.png
[cpam_07]: images/cpam_07.png
[cpam_08]: images/cpam_08.png
[cpam_09]: images/cpam_09.png
[cpam_10]: images/cpam_10.png
[cpam_11]: images/cpam_11.png
[cpam_12]: images/cpam_12.png
[cpam_13]: images/cpam_13.png
[cpam_14]: images/cpam_14.png
[cpam_15]: images/cpam_15.png
[cpam_16]: images/cpam_16.png
[cpam_17]: images/cpam_17.png
[cpam_18]: images/cpam_18.png
[cpam_19]: images/cpam_19.png
[cpam_20]: images/cpam_20.png
[cpam_21]: images/cpam_21.png
[cpam_22]: images/cpam_22.png
[cpam_23]: images/cpam_23.png
[cpam_24]: images/cpam_24.png
[cpam_25]: images/cpam_25.png
[cpam_26]: images/cpam_26.png
[cpam_27]: images/cpam_27.png
[cpam_28]: images/cpam_28.png
[cpam_29]: images/cpam_29.png
[cpam_30]: images/cpam_30.png
