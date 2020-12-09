#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Unpaywall and Crossref data harvesting functions by DOI

Usage:
======
    Unpaywall API : function upw_metadata(arg1:doi,arg2:email)
    doi: the doi identifier of the publication (type string)
    email: a valid email (type string)
    Example : upw_metadata("10.1051/0004-6361/202037910","mymail@example.com")
    
    Crossref prefix API : function crf_publisher_metadata(arg1:doi prefix,arg2:email)
    doi prefix: the doi prefix of the publication (type string)  
    email: a valid email (type string)
    Example : crf_publisher_metadata("10.1051","mymail@example.com")
"""

import requests
import json
import time
import pandas as pd

upw_base_url = "https://api.unpaywall.org/v2/"
crfprefix_base_url = "https://api.crossref.org/v1/prefixes/"

def upw_metadata(doi,email):
    """Get all Unpaywall metadata from a single doi"""       
    if doi is None:
        raise ValueError('DOI cannot be None')
    df_temp = pd.DataFrame()
    params = {'email': email}    
    try:
        requests.get(upw_base_url+str(doi),params=params)
        if requests.get(upw_base_url+str(doi),params=params).status_code == 200:
            response = requests.get(upw_base_url+str(doi),params=params).text
            df_temp = pd.json_normalize(json.loads(response),max_level=6,errors='ignore')
            df_temp["source_doi"] = doi
    except requests.exceptions.RequestException:
        pass
    return df_temp

def crf_publisher_metadata(prefix,email):
    """Get the homogeneous publisher's name from a prefix doi"""
    if prefix is None:
        raise ValueError('prefix cannot be None')
    params = {'mailto': email}
    result = {}
    result["prefix"] = prefix
    try:
        requests.get(crfprefix_base_url+str(prefix),params=params)
        if requests.get(crfprefix_base_url+str(prefix),params=params).status_code == 200:
            response = requests.get(crfprefix_base_url+str(prefix),params=params).text
            result["publisher_by_doiprefix"] = json.loads(response).get("message")["name"]
        else:
            pass
    except:
        pass
    time.sleep(1)
    return result