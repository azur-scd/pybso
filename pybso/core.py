#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Implementation of the Unpaywall and Crossref harvesting modules from a source cvs file
 
    Usage:
 
    >>> import bso.core as core
    >>> core.unpaywall_data(inpath,outpath,email)
        inpath : relative or absolute path to a csv flat file with at least a doi named column
        outpath : relative or absolute path to a new csv flat file with results
        email : a valid email address needed by the Unpaywall API
        Return a dataframe and save the results in csv file
    >>> core.crossref_publisher_normalized(inpath,outpath,email)
        inpath : relative or absolute path to a csv flat file with at least a doi named column
        outpath : relative or absolute path to a new csv flat file with results
        email : a valid email address needed by the Crossref API  
        Return a dataframe and save the results in csv file"""
        
import pybso.crossref_api as crf
import pybso.unpaywall_api as upw
import pandas as pd
from os import path
#from pkg_resources import resource_filename

__all__ = ['unpaywall_data','crossref_publisher_normalized']

#sample = resource_filename('data', 'sample.csv')
my_path = path.abspath(path.dirname(__file__))
sample = path.join(my_path, "data/sample.csv")

def unpaywall_data(inpath,outpath):
    df_source = pd.read_csv(inpath,sep=None,engine = 'python',encoding = 'utf8')
    list_source = df_source.drop_duplicates(subset=['doi'], keep='last')["doi"].to_list()
    df_upw = upw.upw_retrieval(list_source)
    list_result = df_upw["source_doi"].tolist()
    df_result = pd.merge(df_source,df_upw, left_on='doi', right_on='source_doi',how="right").drop(columns=['source_doi'])
    print("Pourcentage de doi reconnus par Unpaywall : "+ "{:.2f}".format(df_upw.shape[0]/df_source.shape[0] * 100) + "%")
    print("DOI non reconnus : " + ",".join(set(list_source) - set(list_result)))
    df_result.to_csv(outpath,index = False,encoding='utf8')
    return df_result
    
def crossref_publisher_normalized(inpath,outpath,email):
    df_source = pd.read_csv(inpath,sep=None,engine = 'python',encoding = 'utf8')
    df_source["doi_prefix"] = df_source.apply (lambda row: row["doi"].partition("/")[0], axis=1)
    list_source = df_source.drop_duplicates(subset=['doi_prefix'], keep='last')["doi_prefix"].tolist()
    df_prefix_result = crf.crf_publisher_retrieval(list_source,email)
    list_result = df_prefix_result["prefix"].tolist()
    df_result = df_source.merge(df_prefix_result, left_on='doi_prefix', right_on='prefix',how='left').drop(columns=['prefix']) 
    print("Pourcentage de préfixes de DOI reconnus par Crossref : "+ "{:.2f}".format(len(list_result)/len(list_source) * 100) + "%")
    print("Préfixes de DOI non reconnus : " + ",".join(set(list_source) - set(list_result)))
    df_result.to_csv(outpath,index = False,encoding='utf8') 
    return df_result
    
    
if __name__ == "__main__":
    unpaywall_data(),crossref_publisher_normalized()
