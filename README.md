pybso - Générateur de baromètre Open Access local
========================================================

Ce package automatise la récupération des données et la production des graphiques pour la constitution d'un baromètre local de l'Open Access sur le modèle du [baromètre national de la science ouverte](https://ministeresuprecherche.github.io/bso/) développé par le M.E.S.R.I.

## Installation
Vous pouvez l'installer avec [pip](https://pypi.org/project/pybso/):

    pip install pybso
    
## Import

    import pybso.core as core
    import pybso.charts as charts

## Remarques

Le package ne traite pas la question des affiliations des publications et ne prend pas en charge la constitution du set de publications de départ, vous devez vous constituer en amont votre corpus de DOI à analyser.

Ce package est optimisé pour une utilisation dans le cadre d'un Jupyter Notebook.

[Voir le notebook de démo]("https://mybinder.org/v2/gh/gegedenice/pybso/master?filepath=%2Fdemo%2FDemo_pybso.ipynb")

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/gegedenice/pybso/master?filepath=%2Fdemo%2FDemo_pybso.ipynb)

## Fonctionnement

Le package propose un ensemble de fonctions prenant toutes en entrée un fichier csv et produisant parfois (pour les fonctions de récupération de données externes) un autre fichier csv de résultats à stocker sur votre PC.

Ce mode de fonctionnement a été pensé pour :
- archiver automatiquement les données moissonnées et donner la possibilité de les analyser autrement ou les intégrer dans des applications tierces ;
- ne pas figer le tableau de bord sur une source unique et pouvoir moduler les graphiques à partir de fichiers différents ;
- potentiellement pouvoir historiciser les données et afficher sur un même notebook des états différents d'OA pour le même corpus.

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
- à l'évolution annuelle de ce taux
- au taux d'accès ouvert par éditeur
- au taux d'accès ouvert par type de publication

L'analyse du taux d'accès ouvert par disciplines n'est pas pris en charge dans la mesure où cette donnée n'est pas présente dans les métadonnées Unpaywall (on peut retrouver une indexation sujet par DOI via [cette API Crossref](https://api.crossref.org/works/10.1155/2014/413629) mais inexploitable car très lacunaire). 

L'analyse par disciplines nécessiterait, par exemple, la constitution d'un modèle de Machine Learning de classification supervisée qui s'appuierait sur la classification par apprentissage déjà effectuée pour l'année 2018 dans le cadre du baromètre national comme set d'entrainement, ce qui dépasse le cadre du package.

## Usage

**Le séparateur de votre fichier csv source est détecté automatiquement à l'import, vous pouvez donc par exemple utiliser comme séparateur la virgule, le point-virgule ou la tabulation**

### Moissonnage des données

#### Données Unpaywall

    core.unpaywall_data(inpath,outpath)

Les 2 arguments à fournir à la fonction sont :
- inpath : le chemin (relatif ou absolu) du fichier csv source. Celui-ci doit contenir au minimum une colonne nommée "doi", si d'autres colonnes sont présentes elles seront conservées dans le fichier résultat ;
- outpath : le chemin (relatif ou absolu) pour la sauvegarde du fichier produit en résultat.

Exemple

    core.unpaywall_data("source_doi.csv","upw_output.csv")
    
ou

    source_path = "source_doi.csv"
    result_path = "upw_output.csv" # ou "C:/Users/xxxx/mon_barometre/upw_output.csv"
    
    core.unpaywall_data(source_path,result_path)

**Remarques**

Bien que l'API Unpaywall réponde plutôt bien et que les requêtes soient parallélisées (multithread), le temps d'exécution peut être plus ou moins long selon le nombre de DOI à traiter.

La fonction renvoie un dataframe qu'il est possible d'assigner à une variable pour d'autres traitements éventuels.

    df = core.unpaywall_data(source_path,result_path)

Attention : le nombre d'enregistrements des résultats peut être inférieur au total initial car seuls les DOI reconnus sont conservés.

Sont également fournis dans la réponse le pourcentage de DOI connus d'Unpaywall (code réponse http 200) dans le set de départ ainsi que la liste des DOI non traités car non reconnus. 

#### Données Crossref (mention éditeur à partir du préfixe de DOI)

    core.crossref_publisher_normalized(inpath,outpath,email)

Les 3 arguments à fournir sont
- inpath : le chemin (relatif ou absolu) du fichier csv source. L'idée du package étant de faciliter et fluidifer l'obtention des données nécessaires, le fichier en entrée est idéalement le fichier résultat de l'étape précédente. Quoi qu'il en soit, celui-ci doit contenir au minimum une colonne nommée "doi", et si d'autres colonnes sont présentes elles seront conservées dans le fichier résultat ;
- outpath : le chemin (relatif ou absolu) pour la sauvegarde du fichier produit en résultat ;
- email : une adress mail valide pour l'utilisation de l'API Crossref. Pas d'authentification requise pour l'utilisation de l'API Crossref gratuite mais son usage est surveillé, et un requêtage abusif (selon Crossref) peut conduire à un blocage d'IP. Une bonne pratique recommandée consiste à ajouter une adresse mail en paramètre et à espacer les requêtes (1 seconde ici).

Exemple

    core.crossref_publisher_normalized("upw_output.csv","upw_crf_output.csv","une_adresse_mail_valide")
    
ou

    source_path = "upw_output.csv"
    result_path = "upw_crf_output.csv"
    mail = "une_adresse_mail_valide"   
    
    core.crossref_publisher_normalized(source_path,result_path,mail)

**Remarques**

Selon le nombre de DOI à traiter il faut être patient, le temps de réponse de l'API Crossref peut être assez long (voire très long... voire pénible)!

La fonction renvoie un dataframe qu'il est possible d'assigner à une variable pour d'autres traitements éventuels.

    df = core.crossref_publisher_normalized(source_path,result_path,mail)

Sont également fournis le pourcentage de DOI présents dans la base Crossref (code réponse http 200) dans le fichier en entrée et la liste des DOI non traités car non reconnus.

### Visualisations

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

#### Focus sur la part en OA : évolution des types d'Open Access (Gold, Green etc...)

    charts.oa_by_status(path)
    
En argument, fournir le chemin (relatif ou absolu) vers un fichier issu des traitements précédents contenant les métadonnées d'Unpaywall retraitées.

#### Exemple complet
    
Paramètres de localisation des fichiers

    source_path = "votre_fichier_source_doi.csv"
    upw_result_path = "upw_output.csv"
    
API Unpaywall

    core.unpaywall_data(source_path,upw_result_path)   
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

    charts.oa_by_status(upw_result_path)
![](assets/graph_oa_by_status.png)
    
Ajout données Crossref
    
    mail = "votre_email" 
    upw_crf_result_path = "upw_crf_output.csv"   
    
API Crossref

    core.crossref_publisher_normalized(upw_result_path,upw_crf_result_path,mail)
![](assets/crossref_data.png)
    
Graphique avec les noms éditeurs normalisés

    charts.oa_rate_by_publisher(upw_crf_result_path)
![](assets/graph_oa_by_pub_crf.png)

On remarque que la clusterisation effectuée en prenant en compte le préfixe de DOI comme source de la mention d'éditeur peut conduite à modifier à la fois l'ordre d'importance des éditeurs et l'analyse des politiques OA par éditeur.

### Données de démo

Le package est livré avec un jeu de données de démo d'une cinquantaine de DOI.

Avant de vous lancer avec vos propres données, vous pouvez tester le package sur ce petit dataset en l'appellant avec la variable core.sample : 

    core.unpaywall_data(core.sample,"votre_resultfile.csv") 
    
## ToDo

**Sur la forme**

- permettre d'embedder les graphiques dans des iframes html
- dash app basée sur le package

**Sur le fond**

- Enrichir les données OA avec d'autres sources : par exemple Dissemin via l'API mise à disposition
- Compléter les données bibliographiques des publications avec les métadonnées Crossref, notamment 
  - pour ré-évaluer la notion de date de publication qui n'est pas claire dans Unpaywall
  - pour compléter les possibilités d'analyse avec les données des organismes de financement (registre funders de Crossref issu du référentiel Scopus) 

## Licence

Ce code est sous licence MIT.