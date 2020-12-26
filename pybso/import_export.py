#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Import and export data files with multiples extensions csv, json, Excel
"""

import pandas as pd
import os

def import_data(**kwargs):
    """
    Function to import data from file or dataframe into a dataframe
    Accepted file extensions : csv, json, xls, xlsx
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file with at least a "doi" named column/entry
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe with at least a "doi" named columns

    Return
    -------
    import_data(**kwargs)
        returns a dataframe
        
    Used by
    -------
    All functions in core.py and charts.py modules
    """

    inpath=kwargs.get('inpath', None)
    dataframe=kwargs.get('dataframe', None)
    if (inpath and (dataframe is not None)):
        print("Error : cannot provide 2 sources inpath and dataframe")
    elif (inpath and (dataframe is None)):
        if ".csv" in os.path.basename(inpath):
            df = pd.read_csv(inpath,sep=None,engine = 'python',encoding = 'utf8')
        elif ".json" in os.path.basename(inpath):
            df = pd.read_json(inpath)
        elif (('.xls' in os.path.basename(inpath)) | (".xlsx" in os.path.basename(inpath))):
            df = pd.read_excel(inpath)
        else:
            print("file type not recongnized")
    elif ((dataframe is not None) and not(inpath)):
        df = dataframe
    return df
    
def export_data(out_df,outpath):
    """
    Function to save the results data in a flat file
    Accepted file extensions : csv, json, xls, xlsx
    ...

    Parameters
    ----------
    out_df : object
        a pandas dataframe to save
    outpath : str (optional)
        relative or absolute path to a csv or json or Excel flat file to store the results

    Return
    -------
    export_data(out_df,outpath)
        returns a saved file at the location given by outpath
        
    Used by
    -------
    Functions in core.py module
    """
    
    if ".csv" in os.path.basename(outpath):
        out_df.to_csv(outpath,index = False,encoding='utf8')
    elif ".json" in os.path.basename(outpath):
        out_df.to_json(outpath,orient='records')
    elif (('.xls' in os.path.basename(outpath)) | (".xlsx" in os.path.basename(outpath))):
        out_df.to_excel(outpath,index=False)
    else:
        print("file type not recongnized")

