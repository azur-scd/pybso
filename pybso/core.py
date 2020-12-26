#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Implementation of the Unpaywall and Crossref harvesting modules from a source cvs file
"""
        
import pybso.crossref_api as crf
import pybso.unpaywall_api as upw
import pybso.import_export as ie
import pandas as pd
import os

__all__ = ['unpaywall_data','crossref_publisher_data']

#sample file variable
my_path = os.path.abspath(os.path.dirname(__file__))
sample = os.path.join(my_path, "data/sample.csv")

def unpaywall_data(**kwargs):
    """
    Function to harvest the Unpaywall API, process the data and returns a dataframe with structured OA data
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file with at least a "doi" named column/entry
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe with at least a "doi" named columns
    outpath : str (optional)
        relative or absolute path to a csv or json or Excel flat file to store the results

    Return
    -------
    unpaywall_data(**kwargs)
        returns a dataframe with the following additional columns : 
            * API data without process : title,genre,published_date,year,
            journal_name,journal_issn_l,journal_is_oa,journal_is_in_doaj,publisher
            * Processed and normalized data : is_oa_normalized,oa_status_normalized,
            oa_host_type_normalized,oa_host_domain
                   
    Uses
    -------
    * import_export.py module by passing the **kwards arguments
    * unpaywall_api.py module for requesting the API

    """
    outpath=kwargs.get('outpath', None)
    df_source = ie.import_data(**kwargs)
    list_source = df_source.drop_duplicates(subset=['doi'], keep='last')["doi"].to_list()
    df_upw = upw.upw_retrieval(list_source)
    list_result = df_upw["source_doi"].tolist()
    df_result = pd.merge(df_source,df_upw, left_on='doi', right_on='source_doi',how="right").drop(columns=['source_doi'])
    print("Pourcentage de doi reconnus par Unpaywall : "+ "{:.2f}".format(df_upw.shape[0]/df_source.shape[0] * 100) + "%")
    print("DOI non reconnus : " + ",".join(set(list_source) - set(list_result)))
    if (outpath):
        ie.export_data(df_result,outpath)
    return df_result
    
def crossref_publisher_data(**kwargs):
    """
    Function to harvest the Crossref prefixes API, process the data and returns a dataframe with a normalized publisher label
    ...

    Parameters
    ----------
    inpath : str, , mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file with at least a "doi" named column/entry
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe with at least a "doi" named columns
    email : str
        valid email needed by the Crossref API
    outpath : str (optional)
        relative or absolute path to a csv or json or Excel flat file to store the results

    Return
    -------
    crossref_publisher_data(**kwargs)
        returns a dataframe with the following additional columns : doi_prefix,publisher_by_doiprefix
        
    Uses
    -------
    * import_export.py module by passing the **kwards arguments
    * crossref_api.py module for requesting the API

    """
    outpath=kwargs.get('outpath', None)
    email=kwargs.get('email', None)
    if (not(email)):
        print("Error : missing a valid email parameter")
    df_source = ie.import_data(**kwargs)
    df_source["doi_prefix"] = df_source.apply (lambda row: row["doi"].partition("/")[0], axis=1)
    list_source = df_source.drop_duplicates(subset=['doi_prefix'], keep='last')["doi_prefix"].tolist()
    df_prefix_result = crf.crf_publisher_retrieval(list_source,email)
    list_result = df_prefix_result["prefix"].tolist()
    df_result = df_source.merge(df_prefix_result, left_on='doi_prefix', right_on='prefix',how='left').drop(columns=['prefix']) 
    print("Pourcentage de préfixes de DOI reconnus par Crossref : "+ "{:.2f}".format(len(list_result)/len(list_source) * 100) + "%")
    print("Préfixes de DOI non reconnus : " + ",".join(set(list_source) - set(list_result))) 
    if (outpath):
        ie.export_data(df_result,outpath)
    return df_result
    
    
if __name__ == "__main__":
    unpaywall_data(),crossref_publisher_data()
