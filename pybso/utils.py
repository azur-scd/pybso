#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""A few utils functions for post-processing the Unpaywall fields
"""

import numpy as np
from urllib.parse import urlparse

def try_join(list):
    try:
        return ','.join(map(str, list))
    except TypeError:
        return np.nan 
    
def get_substring (row,column,sep,part):
    if isinstance(row[column], str):
        return row[column].partition(sep)[part]
    else:
        return row[column].str.partition(sep)[part]

def is_oa_normalize(row):
    if row['is_oa'] is False :
        return 'Accès fermé'
    if row['is_oa'] is True :
        return 'Accès ouvert'
    
def oa_host_type_normalize(row):
    if ("publisher" in row['oa_locations_host_type']) and ("repository" in row['oa_locations_host_type'])  :
        return 'Editeur et archive ouverte'
    if ("publisher" in row['oa_locations_host_type']) and ("repository" not in row['oa_locations_host_type'])  :
        return 'Editeur'
    if ("publisher" not in row['oa_locations_host_type']) and ("repository" in row['oa_locations_host_type'])  :
        return 'Archive ouverte'
    if row['is_oa_normalized'] == "Accès fermé" :
        return 'Accès fermé'

def oa_hostdomain_count (row):
    list = row.split(",")
    return {"hal":sum('hal' in s for s in list),"arXiv":sum('arxiv' in s for s in list),"Autres":sum(('hal' not in s) and ('arxiv' not in s) for s in list)}

def oa_repo_normalize (row):
    r = row
    list = []
    if (r["hal"] != 0):
        list.append("Hal")
    if (r["arXiv"] != 0):
        list.append("arXiv")
    if (r["Autres"] != 0):
        list.append("Autres")
    return ",".join(list)

def oa_url_normalize(row):
    list = row['oa_locations_url'].split(",")
    l = []
    for k in list:
        o = urlparse(k).netloc
        l.append(o)
    return ",".join(l)

def doi_prefix(row):
    return row["doi"].str.partition("/")[0]

def url2domain(row):
    #list = row['oa_locations_url'].split(",")
    list = row.split(",")
    l = []
    for k in list:
        o = urlparse(k).netloc
        l.append(o)
    return ",".join(l)

def capitalize(row):
    return row.capitalize() 

def parse_list_of_dict(data,k):
    c = []
    for item in data:
        for key,value in item.items():
            if key == k:
                c.append(value)
    return c