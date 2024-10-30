from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Initialiser le client BigQuery
client = bigquery.Client()

# Définir les départements Top 4 et Bottom 4 en 2022 pour la pathologie en question
departements_top4 = ['Tarn', 'Creuse', 'Finistère', 'Lot']
departements_bottom4 = ["Mayotte", "Guyane", "La Réunion", "Val-d'Oise"]
departements_cibles = departements_top4 + departements_bottom4

# Définir les paramètres
cancer_id = "CAN_CRE_CAT"  # Catégorie de cancer spécifique
annees = list(range(2015, 2023))  # 2015 à 2022
sexe = 9  # Tous sexes
age = "tsage"  # Tranche d'âge spécifique

# Requête SQL pour les départements Top 4 et Bottom 4
sql_cibles = f"""
SELECT 
    ps.prev,
    fp.libelle AS pathologie,
    d.id AS dept_id,
    d.nom_dept,
    ps.annee,
    ps.sex,
    ps.age
FROM `alien-oarlock-428016-f3.french_cpam.patient_stat` AS ps
JOIN `alien-oarlock-428016-f3.french_cpam.filtered_patho` AS fp
    ON ps.patho_id = fp.id
JOIN `alien-oarlock-428016-f3.french_cpam.dept` AS d
    ON ps.dept_id = d.id
WHERE ps.annee BETWEEN @start_year AND @end_year
    AND ps.age = @age
    AND ps.sex = @sexe
    AND fp.id = @cancer_id
    AND d.nom_dept IN UNNEST(@departements_cibles)
    AND d.id != "999"
ORDER BY ps.annee, d.nom_dept;
"""

# Préparer les paramètres de la requête
job_config_cibles = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("start_year", "INT64", 2015),
        bigquery.ScalarQueryParameter("end_year", "INT64", 2022),
        bigquery.ScalarQueryParameter("age", "STRING", age),
        bigquery.ScalarQueryParameter("sexe", "INT64", sexe),
        bigquery.ScalarQueryParameter("cancer_id", "STRING", cancer_id),
        bigquery.ArrayQueryParameter("departements_cibles", "STRING", departements_cibles)
    ]
)

# Exécuter la requête et récupérer les données dans un dataframe
df_cibles = client.query(sql_cibles, job_config=job_config_cibles).to_dataframe()

# Requête SQL pour la prévalence médiane nationale
sql_moy_med = """
SELECT 
    ps.annee,
    APPROX_QUANTILES(ps.prev, 100)[OFFSET(50)] AS prev_med
FROM `alien-oarlock-428016-f3.french_cpam.patient_stat` AS ps
JOIN `alien-oarlock-428016-f3.french_cpam.filtered_patho` AS fp
    ON ps.patho_id = fp.id
JOIN `alien-oarlock-428016-f3.french_cpam.dept` AS d
    ON ps.dept_id = d.id
WHERE ps.annee BETWEEN @start_year AND @end_year
    AND ps.age = @age
    AND ps.sex = @sexe
    AND fp.id = @cancer_id
    AND d.id != "999"
GROUP BY ps.annee
ORDER BY ps.annee;
"""

# Préparer les paramètres de la requête pour moy_med
job_config_moy_med = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("start_year", "INT64", 2015),
        bigquery.ScalarQueryParameter("end_year", "INT64", 2022),
        bigquery.ScalarQueryParameter("age", "STRING", age),
        bigquery.ScalarQueryParameter("sexe", "INT64", sexe),
        bigquery.ScalarQueryParameter("cancer_id", "STRING", cancer_id)
    ]
)

# Exécuter la requête et récupérer les données dans un DataFrame
df_moy_med = client.query(sql_moy_med, job_config=job_config_moy_med).to_dataframe()

# Fusionner les données des départements ciblés avec les médianes nationales
df_final = df_cibles.merge(df_moy_med, on='annee')

# Ajouter une colonne pour identifier Top 4 et Bottom 4
df_final['groupe'] = df_final['nom_dept'].apply(
    lambda x: 'Top 4' if x in departements_top4 else ('Bottom 4' if x in departements_bottom4 else 'Other')
)

# Filtrer uniquement Top 4 et Bottom 4
df_final = df_final[df_final['groupe'].isin(['Top 4', 'Bottom 4'])]

# Préparer les données pour la visualisation
# Inclure les médianes nationales comme lignes supplémentaires
median_median = df_moy_med.copy()
median_median['nom_dept'] = 'Prévalence Médiane Nationale'
median_median['prev'] = median_median['prev_med']
median_median['groupe'] = 'Médiane'

# Combiner avec Top 4 et Bottom 4
df_visual = pd.concat([df_final, median_median], ignore_index=True)

# Définir une palette de couleurs percutantes
palette = sns.color_palette("Set1", len(departements_cibles))  # Palette vives

# Créer un dictionnaire pour assigner une couleur spécifique à chaque département
color_dict = {dept: palette[i] for i, dept in enumerate(departements_cibles)}

# Ajouter une couleur pour la médiane nationale
color_dict['Prévalence Médiane Nationale'] = 'black'

# Visualisation avec Seaborn et Matplotlib
plt.figure(figsize=(14, 8))
sns.set(style="whitegrid")

# Tracer les lignes pour les départements Top 4 et Bottom 4
departements_to_plot = df_visual[df_visual['groupe'].isin(['Top 4', 'Bottom 4'])]['nom_dept'].unique()

for dept in departements_to_plot:
    dept_data = df_visual[df_visual['nom_dept'] == dept]
    plt.plot(
        dept_data['annee'], 
        dept_data['prev'], 
        marker='o', 
        label=dept, 
        color=color_dict[dept],
        linewidth=2
    )

# Tracer la ligne de prévalence médiane nationale en noir
median_data = df_visual[df_visual['nom_dept'] == 'Prévalence Médiane Nationale']
plt.plot(
    median_data['annee'], 
    median_data['prev'], 
    label='Prévalence Médiane Nationale', 
    color=color_dict['Prévalence Médiane Nationale'], 
    linestyle='--', 
    linewidth=2
)

# Ajouter des annotations pour Top 4 et Bottom 4 en 2022 avec un angle plus doux (30 degrés)
for dept in departements_to_plot:
    dept_data = df_visual[(df_visual['nom_dept'] == dept) & (df_visual['annee'] == 2022)]
    if not dept_data.empty:
        plt.text(
            dept_data['annee'].values[0], 
            dept_data['prev'].values[0], 
            dept, 
            fontsize=9, 
            ha='center', 
            va='bottom',
            rotation=30,  # Angle plus doux
            bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
        )

# Ajuster l'espace en bas pour la légende
plt.subplots_adjust(bottom=0.3)

# Séparer les handles et labels pour les départements et la médiane
handles, labels = plt.gca().get_legend_handles_labels()
handles_depts = handles[:-1]  # Tous sauf le dernier (médiane)
labels_depts = labels[:-1]
handle_med = handles[-1:]
label_med = labels[-1:]

# Créer une légende pour les départements avec 4 colonnes
legend_depts = plt.legend(
    handles_depts, 
    labels_depts, 
    title='Départements',
    bbox_to_anchor=(0.3, -0.2),  # Positionner la légende en bas à gauche
    loc='upper center',
    ncol=4,  # 4 colonnes pour Top 4 et Bottom 4
    frameon=False
)

# Ajouter une légende séparée pour la médiane
plt.legend(
    handle_med, 
    label_med, 
    title='Statistiques Nationales',
    bbox_to_anchor=(0.7, -0.2),  # Positionner la légende en bas à droite
    loc='upper center',
    frameon=False
)

# Ajouter la légende des départements à l'axe
plt.gca().add_artist(legend_depts)

# Ajouter des labels et titres
plt.xlabel('Année')
plt.ylabel('Prévalence')
plt.title('Évolution de la prévalence du cancer colorectal dans les départements "Top 4" et "Bottom 4" de 2015 à 2022')
plt.xticks(annees)
plt.grid(True)
plt.tight_layout()

plt.show()
