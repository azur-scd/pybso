#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module Crossref harvesting from a doi prefixes list, with a timeout of 1 second between requests and concatenate in a resulting dataframe.

Usage:
======

    Crossref prefix API by DOI: function crf_publisher_metadata(arg1:doi prefix,arg2:email)
    doi prefix: the doi prefix of the publication (type string)  
    email: a valid email (type string)
    Example : crf_publisher_metadata("10.1051","mymail@example.com")
    
    Crossref API for a list of DOI : function crf_publisher_retrieval(arg1:prefix_list,arg2:email)
    prefix_list: a list of single doi prefixes (type list)
    email: valid email address to pass to the upw_metadata function (type string)
    Example : crf_publisher_retrieval(["10.1051","10.1016"],"mymail@example.com")
"""

import pandas as pd
import requests
import json
import time

crfprefix_base_url = "https://api.crossref.org/v1/prefixes/"

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

def crf_publisher_retrieval(doiprefix_list,email):
    """Request function crf_publisher_metadata from a list of doi prefixs and compile in a dataframe"""
    df_result = pd.DataFrame(crf_publisher_metadata(i,email) for i in doiprefix_list)
    return df_result.dropna()
    


