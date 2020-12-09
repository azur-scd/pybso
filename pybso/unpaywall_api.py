#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Module Unpaywall harvesting from a doi list, launched in parallel tasks and concatenate in a resulting dataframe.

Usage:
======
    Unpaywall API : function upw_retrieval(arg1:doi_list,arg2:email)
    doi_list: a list of single doi identifiers (type list)
    email: valid email address to pass to the upw_metadata function (type string)
    Example : upw_retrieval(["10.1051/0004-6361/202037910","10.1016/j.asr.2020.09.009"],"mymail@example.com")
"""

import pandas as pd
import pybso.harvest as harvest
import pybso.utils as utils
from concurrent.futures import ThreadPoolExecutor, as_completed

def upw_retrieval(doi_list,email):
    """Request function upw_metadata from a list of doi,filter result on a few fields and compile in a dataframe"""
    processes = []
    df_collection = []
    fields = ["source_doi","genre","title","published_date","year","publisher","journal_name",
              "journal_issn_l","journal_is_oa","journal_is_in_doaj","is_oa_normalized","oa_status_normalized",
              "oa_host_type_normalized","oa_host_domain"]
    with ThreadPoolExecutor(max_workers=10) as executor:
        processes = {executor.submit(harvest.upw_metadata, doi,email): str(doi) for doi in doi_list}
    for task in as_completed(processes):
        worker_result = task.result()
        df_collection.append(worker_result)
    single_df = pd.concat(df_collection)
    single_df["is_oa_normalized"] = single_df.apply (lambda row: utils.is_oa_normalize(row), axis=1)
    single_df["oa_status_normalized"] = single_df.apply (lambda row: utils.capitalize(row["oa_status"]), axis=1)
    for i in ["host_type","url"]:
        single_df["oa_locations_"+i] = single_df.apply (lambda row:','.join(map(str,[loc[i] for loc in row["oa_locations"]])), axis=1)
    single_df["oa_host_type_normalized"] = single_df.apply (lambda row: utils.oa_host_type_normalize(row), axis=1)
    single_df["oa_host_domain"] = single_df.apply (lambda row: utils.url2domain(row['oa_locations_url']), axis=1)
    return single_df[single_df.columns & fields]