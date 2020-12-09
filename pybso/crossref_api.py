#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module Crossref harvesting from a doi prefixes list, with a timeout of 1 second between requests and concatenate in a resulting dataframe.

Usage:
======
    Crossref API : function crf_publisher_retrieval(arg1:prefix_list,arg2:email)
    prefix_list: a list of single doi prefixes (type list)
    email: valid email address to pass to the upw_metadata function (type string)
    Example : crf_publisher_retrieval(["10.1051","10.1016"],"mymail@example.com")
"""

import pandas as pd
import pybso.harvest as harvest

def crf_publisher_retrieval(doiprefix_list,email):
    """Request function crf_publisher_metadata from a list of doi prefixs and compile in a dataframe"""
    df_result = pd.DataFrame(harvest.crf_publisher_metadata(i,email) for i in doiprefix_list)
    return df_result.dropna()
    


