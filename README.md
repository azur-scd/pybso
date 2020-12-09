pybso - Générateur de baromètre Open Access local
========================================================

Ce module automatise la récupération des données et la production des graphiques pour la constitution d'un baromètre local de l'Open Access sur le modèle du baromètre national de la science ouverte développé par le MESRI

## Installation
Vous pouvez l'installer avec pip:

    pip install pybso

## Remarques

Le package ne traite pas la question des affiliations des publications et ne prend pas en charge la constitution du set de publications de départ, vous devez vous constituer en amont votre corpus de DOI à analyser.

Ce package est optimisé pour une utilisation dans le cadre d'un Jupyter Notebook.

[Voir le notebook de démo]("demo/demo_pybso.ipynb")

## Fonctionnement

Vous disposez de deux types de fonctions pour produire un baromètre local

### Fonctions de requêtages d'API pour l'enrichissement du jeu de DOI

#### Interrogation de l'API d'Unpaywall

*Documentation sur le format de données Unpaywall : https://unpaywall.org/data-format*

1. Métadonnées bibliographiques moissonnés sans modification : "title","genre" (type de document),"published_date","year","publisher","journal_name","journal_issn_l","journal_is_oa","journal_is_in_doaj"
   
2. Champs relatifs à l'analyse OA avec post-traitement

   - "is_oa" : valeurs True/False deviennent Accès ouvert/Accès fermé
   - "oa_status" : Green, Gold, Hybrid...
   - champs "host_type" de l'object "oa_locations" (fournit tous les types d'hébergement des différentes versions de la publication) : les valeurs possibles publisher/repository sont concaténées et converties en libellé unifié : "Archive ouverte" si pas de mention publisher, "Editeur" si pas de mention repository, "Editeur et archive ouverte" si les 2 mentions sont présentes, "Accès fermé" si le champ "is_oa" est False.

#### Interrogation de l'API Metadata de Crossref

*Documentation : https://github.com/CrossRef/rest-api-doc*

Elle permet d'homogénéiser le nom de l'éditeur fourni par Unpaywall en récupérant le libellé de l'éditeur propriétaire (le "prefix owner") lors de l'attribution du DOI, identifiable par le préfixe de chaque DOI.

La liste des prefix owner membres de Crossref est disponible ici https://www.crossref.org/06members/50go-live.html 

L'API utilisé est https://api.crossref.org/prefixes/{doi}

### Fonctions de mise en forme graphique des indicateurs d'ouverture des publications 

La librairie graphique utilisée est Plotly, notamment pour ses fonctionnalités interactives de rendu (légende cliquable, export, annotations, sélection, zoom...).
Les anayses graphiques reprises du baromètre national sont celles relatives : 

- au taux global d'accès ouvert,
- à l'évolution annuelle de ce taux (si le set de données couvre plusieurs années) 
- au taux d'accès ouvert par éditeur
- au taux d'accès ouvert par type de publication

L'analyse du taux d'accès ouvert par disciplines n'est pas pris en charge dans la mesure où cette donnée n'est pas présente dans les métadonnées Unpaywall (elle l'est dans cette autre API Crossref mais de manière inexploitable car très lacunaire), et nécessiterait par exemple la constitution d'un modèle de Machine Learning de classification supervisée qui s'appuierait sur la classification par apprentissage déjà effectuée pour le baromètre comme set d'entrainement, ce qui dépasse le cadre du package.

## Usage

### Moissonnage des données

    import pybso.core as core

#### Données Unpaywall

    core.unpaywall_data(inpath,outpath,email)

Les 3 arguments à fournir sont
- inpath : le chemin (relatif ou absolu) du fichier csv source. Celui-ci doit contenir au minimum une colonne nommée "doi", si d'autres colonnes sont présentes elles seront conservées dans le fichier résultat
- outpath : le chemin (relatif ou absolu) pour la sauvegarde du fichier produit en résultat
- email : une adress mail valide pour l'utilisation de l'API Unpaywall. Aucune création de compte n'est demandée pour son utilisation mais ce paramètre permet aux producteurs du service de suivre son usage

Exemple

    source_path = "source_doi.csv"
    result_path = "/result_files/upw_output.csv"
    mail = "une_adresse_mail_valide"  
    core.unpaywall_data(source_path,result_path,mail)

**Remarques**

Bien que l'API Unpaywall réponde plutôt bien et que les requêtes soient parallélisées (multithread), le temps d'exécution peut être plus ou moins long selon le nombre de DOI à traiter.

La fonction renvoie un dataframe qu'il est possible d'assigner à une variable pour d'autres traitements éventuels.

    df = core.unpaywall_data(source_path,result_path,mail)

Attention : le nombre d'enregistrements peut être inférieur au total initial car seuls les DOI reconnus sont conservés.

Sont également fournis le pourcentage de DOI connus d'Unpaywall (code réponse http 200) dans le set de départ et la liste des DOI non traités car non reconnus. 

#### Données Crossref (mention éditeur à partir du préfixe de DOI)

    core.crossref_publisher_normalized(inpath,outpath,email)

Les 3 arguments à fournir sont
- inpath : le chemin (relatif ou absolu) du fichier csv source. L'idée du package étant de faciliter et fluidifer l'obtention des données nécessaires, le fichier en entrée est idéalement le fichier résultat de l'étape précédente. Quoi qu'il en soit, celui-ci doit contenir au minimum une colonne nommée "doi", et si d'autres colonnes sont présentes elles seront conservées dans le fichier résultat
- outpath : le chemin (relatif ou absolu) pour la sauvegarde du fichier produit en résultat
- email : une adress mail valide pour l'utilisation de l'API Crossref. Pas d'authentification requise pour l'utilisation gratuite de l'API Crossref mais son usage est encadré, et un requêtage abusif (selon Crossref) peut conduire à un blocage d'IP. Une bonne pratique recommandée consiste à ajouter une adresse mail en paramètre et à espacer les requêtes (1 seconde ici).

Exemple

    source_path = "/result_files/upw_output.csv"
    result_path = "/result_files/upw_crf_output.csv"
    mail = "une_adresse_mail_valide"   
    core.crossref_publisher_normalized(source_path,result_path,mail)

**Remarques**

Selon le nombre de DOI à traiter il faut être patient, le temps de réponse de l'API Crossref peut être assez long (voire très long... voire pénible)!

La fonction renvoie un dataframe qu'il est possible d'assigner à une variable pour d'autres traitements éventuels.

    df = core.crossref_publisher_normalized(source_path,result_path,mail)

Sont également fournis le pourcentage de DOI présents dans la base Crossref (code réponse http 200) dans le fichier en entrée et la liste des DOI non traités car non valides.

### Visualisations

    import pybso.charts as charts

#### Taux global d'accès ouvert

    charts.oa_rate(filepath)

En argument, fournir le chemin (relatif ou absolu) vers un fichier issu des traitements précédents contenant les métadonnées d'Unpaywall retraitées.

#### Evolution du taux d'accès ouvert

    charts.oa_rate_by_year(filepath)

En argument, fournir le chemin (relatif ou absolu) vers un fichier issu des traitements précédents contenant les métadonnées d'Unpaywall retraitées.

#### Taux d'accès ouvert par éditeur

    charts.oa_rate_by_publisher(filepath,publisher_field='publisher_by_doiprefix',n=10)

Les 3 arguments sont :
- path (obligatoire):  le chemin (relatif ou absolu) vers un fichier issu des traitements précédents contenant les métadonnées OA retraitées.
- publisher_field (optionnel, valeur par défaut publisher_field="publisher_by_doiprefix") : prend au choix 2 valeurs selon la variable (ie colonne du fichier csv) à prendre en compte pour la création du graphique
  - "publisher_by_doiprefix" : le nom de l'éditeur issu de Crossref à partir du préfixe de DOI
  - "publisher" : le nom de l'éditeur fourni par Unpaywall
- n (optionnel, valeur par défaut n=10) : pour plus de lisibilité du graphique, filtre sur les 10 éditeurs les plus representés (rendus par ordre décroissant).

Exemple sans personnalisation :

    charts.oa_rate_by_publisher("votre_fichier.csv")

Exemple customisé (Les 5 éditeurs les plus immportants à partir de la donnée "publisher" d'Unpaywall): 

    charts.oa_rate_by_publisher("votre_fichier.csv",publisher_field="publisher",n=5)

#### Exemple complet
    
Paramètres de localisation des fichiers

    mail = "votre_email" 
    source_path = "votre_fichier_source_doi.csv"
    upw_result_path = "/result_files/upw_output.csv"
    
API Unpaywall

    core.unpaywall_data(source_path,upw_result_path,mail)   
![](assets/unpaywall_data1.png) ![](assets/unpaywall_data2.png)

Graphiques données OA

    charts.oa_rate(upw_result_path)
![](assets/graph_oa_rate.png)

    charts.oa_rate_by_year(upw_result_path)
![](assets/graph_oa_by_year.png)

    charts.oa_rate_by_publisher(upw_result_path,publisher_field="publisher")
![](assets/graph_oa_by_pub_upw.png)

    charts.oa_rate_by_type(upw_result_path)
![](assets/graph_oa_by_type.png)
    
Paramètre nouveau fichier
    upw_crf_result_path = "/result_files/upw_crf_output.csv"   
    
API Crossref

    core.crossref_publisher_normalized(upw_result_path,upw_crf_result_path,mail)
![](assets/crossref_data.png)
    
Graphique avec les noms éditeurs normalisés

    charts.oa_rate_by_publisher(upw_crf_result_path)
![](assets/graph_oa_by_pub_crf.png)

Avant de vous lancer avec vos propres données, vous pouvez tester le package avec sur un fichier exemple inclus. Pour lancer le test : 

    core.unpaywall_data(core.sample,"votre_resultfile.csv","votre_email") 

[Voir le notebook de démo]("demo/demo_pybso.ipynb")

## Licence

Ce code est sous licence MIT.