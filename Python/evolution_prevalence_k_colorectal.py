from google.cloud import bigquery
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# But: tracer l'évolution de la prévalence d'un cancer spécifique de 2015 à 2022

# Cas du cancer colorectal
client = bigquery.Client()
departements_top5 = ['Tarn', 'Creuse', 'Finistère', 'Lot', 'Nièvre'] # Dépts les plus impactés
departements_bottom5 = ["Mayotte", "Guyane", "La Réunion", "Val-d'Oise", "Seine-Saint-Denis"]  # Dépts les moins impactés
departements_cibles = departements_top5 + departements_bottom5
cancer_id = "CAN_CRE_CAT"   # Identifiant du cancer colorectal
age = "tsage"               # tous âges
sexe = 9                    # tous sexes
start_year = 2015
end_year = 2022

def get_cancer_data(client, cancer_id, departements_cibles, start_year, end_year, age="tsage", sexe=9):
    # Requête SQL sans f-strings, paramétrée uniquement avec `query_parameters`
    sql_query = """
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

    # Configuration de la requête avec les paramètres sécurisés
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_year", "INT64", start_year),
            bigquery.ScalarQueryParameter("end_year", "INT64", end_year),
            bigquery.ScalarQueryParameter("age", "STRING", age),
            bigquery.ScalarQueryParameter("sexe", "INT64", sexe),
            bigquery.ScalarQueryParameter("cancer_id", "STRING", cancer_id),
            bigquery.ArrayQueryParameter("departements_cibles", "STRING", departements_cibles)
        ]
    )

    # Exécution de la requête et récupération des données
    return client.query(sql_query, job_config=job_config).to_dataframe()

# Exécution de la fonction pour le cancer spécifique
df_cibles = get_cancer_data(client, cancer_id, departements_cibles, start_year, end_year, age, sexe)

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

# Ajouter une colonne pour identifier Top 5 et Bottom 5
df_final['groupe'] = df_final['nom_dept'].apply(
    lambda x: 'Top 5' if x in departements_top5 else ('Bottom 5' if x in departements_bottom5 else 'Other')
)

# Filtrer uniquement Top 5 et Bottom 5
df_final = df_final[df_final['groupe'].isin(['Top 5', 'Bottom 5'])]

# Préparer les données pour la visualisation
# Inclure les médianes nationales comme lignes supplémentaires
median_median = df_moy_med.copy()
median_median['nom_dept'] = 'Prévalence médiane nationale'
median_median['prev'] = median_median['prev_med']
median_median['groupe'] = 'Médiane'

# Combiner avec Top 5 et Bottom 5
df_visual = pd.concat([df_final, median_median], ignore_index=True)

# Définir une palette de couleurs percutantes
palette = sns.color_palette("Set1", len(departements_cibles))  # Palette vives

# Créer un dictionnaire pour assigner une couleur spécifique à chaque département
color_dict = {dept: palette[i] for i, dept in enumerate(departements_cibles)}

# Ajouter une couleur pour la médiane nationale
color_dict['Prévalence médiane nationale'] = 'black'

# Visualisation avec Seaborn et Matplotlib
plt.figure(figsize=(14, 8))
sns.set(style="whitegrid")

# Tracer les lignes pour les départements Top 5 et Bottom 5
departements_to_plot = df_visual[df_visual['groupe'].isin(['Top 5', 'Bottom 5'])]['nom_dept'].unique()

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
median_data = df_visual[df_visual['nom_dept'] == 'Prévalence médiane nationale']
plt.plot(
    median_data['annee'], 
    median_data['prev'], 
    label='Prévalence médiane nationale', 
    color=color_dict['Prévalence médiane nationale'], 
    linestyle='--', 
    linewidth=2
)

# Ajouter des annotations pour Top 5 et Bottom 5 en 2022 avec un angle plus doux (30 degrés)
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

# Créer une légende pour les départements avec 5 colonnes
legend_depts = plt.legend(
    handles_depts, 
    labels_depts, 
    title='Départements',
    bbox_to_anchor=(0.3, -0.1),  # Positionner la légende en bas à gauche
    loc='upper center',
    ncol=5,  # 5 colonnes pour Top 5 et Bottom 5
    frameon=False
)

# Ajouter une légende séparée pour la médiane
plt.legend(
    handle_med, 
    label_med, 
    # title='Statistiques nationales',
    bbox_to_anchor=(0.8, -0.2),  # Positionner la légende en bas à droite
    loc='upper center',
    frameon=False
)

# Ajouter la légende des départements à l'axe
plt.gca().add_artist(legend_depts)

# Ajouter des labels et titres
plt.xlabel('Année')
plt.ylabel('Prévalence')
plt.title("Prévalence du cancer colorectal dans les départements les plus et les moins affectés, de 2015 à 2022")
plt.xticks(range(start_year, end_year + 1))
plt.grid(True)
plt.tight_layout()

plt.show()