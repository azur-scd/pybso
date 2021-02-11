#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Implementation of Plotly graphs from the csv result files of the core functions (after harvesting)
 
    Usage:
 
    >>> import bso.charts as charts
    >>> charts.oa_rate_by_year(path)
        path : relative or absolute path to a csv flat file resulting from the core Unpaywall functions
    >>> charts.oa_rate_by_publisher(path,publisher_field='publisher_by_doiprefix',n=10)
        path : relative or absolute path to a csv flat file resulting from the core Unpaywall and Crossref functions 
        publisher_field (optional): 2 values 'publisher_by_doiprefix'(default)/'publisher' according to the column to work with, 'publisher_by_doiprefix' the publisher's name from Crossref (prefix owner) or 'publisher' the publisher's name from Unpaywall
        n (optional): filter on the n largest publishers (by number of occurences), default n=10
    >>> charts.oa_rate_by_host(path)
        path : relative or absolute path to a csv flat file resulting from the core Unpaywall functions
    >>> charts.oa_rate_by_type(path)
        path : relative or absolute path to a csv flat file resulting from the core Unpaywall functions
    >>> charts.oa_by_status(path)
        path : relative or absolute path to a csv flat file resulting from the core Unpaywall functions"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import pybso.import_export as ie

__all__ = ['oa_rate','oa_rate_by_year','oa_rate_by_publisher','oa_rate_by_type','oa_by_status']

colors = {'Accès fermé': 'grey',
          'Accès ouvert': '#3288BD',
          'Archive ouverte': 'rgb(122,230,212)',
          'Editeur': 'rgb(241,225,91)',
          'Editeur et archive ouverte':'rgb(211,240,140)'}
list_order = ['Accès fermé','Accès ouvert','Editeur et archive ouverte', 'Archive ouverte', 'Editeur']

def oa_rate(**kwargs):
    """
    Function to plot a nested donut chart
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe
        
    Conditions
    ----------
    The imported file or dataframe must contain the following entry or columns : 
        is_oa_normalized,oa_host_type_normalized
    This is the case when using data processed with the core.py module
    
    Usage
    -------
    fig = oa_rate(**kwargs)
    fig.show

    """
    df = ie.import_data(**kwargs)
    #list_order = ['Accès fermé','Accès ouvert','Editeur et archive ouverte', 'Archive ouverte', 'Editeur']
    g_outer = df["is_oa_normalized"].value_counts()
    g_inner = df["oa_host_type_normalized"].value_counts()
    grouped_outer = g_outer[g_outer.index.isin(list_order)].reindex(list_order).dropna()
    grouped_inner = g_inner[g_inner.index.isin(list_order)].reindex(list_order).dropna()
    labels_outer = grouped_outer.index.tolist()
    values_outer = grouped_outer.values.tolist()
    labels_inner = grouped_inner.index.tolist()
    values_inner = grouped_inner.values.tolist()
    fig = go.Figure()
    fig.add_trace(go.Pie(labels=labels_outer, values=values_outer, hole=.7, direction='clockwise', sort=False,textinfo='label+percent',textposition='outside',marker={'colors': ['grey', '#3288BD']}))
    fig.add_trace(go.Pie(labels=labels_inner, values=values_inner,hole=.7,direction='clockwise', sort=False,domain={'x': [0.15, 0.85], 'y': [0.15, 0.85]},marker={'colors': ['grey', 'rgb(211,240,140)', 'rgb(122,230,212)', 'rgb(241,225,91)']}))
    fig.update_layout(title="Proportion des publications en accès ouvert")
    return fig

def oa_rate_by_year(**kwargs):
    """
    Function to plot a stacked bar chart of OA hosts by year
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe
        
    Conditions
    ----------
    The imported file or dataframe must contain the following entry or columns : 
        year,oa_host_type_normalized
    This is the case when using data processed with the core.py module
    
    Usage
    -------
    fig = oa_rate_by_year(**kwargs)
    fig.show

    """
    df = ie.import_data(**kwargs)
    df.year = df.year.astype(str)
    dc = pd.crosstab(df["year"], df["oa_host_type_normalized"],normalize='index').round(3)*100
    x=sorted(df[df.year.notna()].year.unique().tolist())
    fig = go.Figure()
    for i in dc.columns:
        fig.add_trace(go.Bar(x=x, y=dc[i], name=i,text=dc[i].astype(int),textposition='auto',marker={'color': colors[i]}))
    fig.update_layout(title="Evolution du taux d'accès ouvert aux publications",barmode='stack',uniformtext_minsize=10)
    fig.update_xaxes(categoryorder='category ascending')
    return fig
    
def oa_rate_by_publisher(**kwargs):
    """
    Function to plot a horizontal stacked bar chart of OA hosts by most represented publishers
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe
    publisher_field : str, optional, default "publisher" (the Unpaywall value)
        Can be changed to publisher_field="publisher_by_doiprefix" if the Crossref value has been harvested.
    n : int, optional, default 10
        number of most represented publisher in descending order
        
    Conditions
    ----------
    The imported file or dataframe must contain at least the entry or columns "publisher" and
        possibly the entry or column "publisher_by_doiprefix"
    This is the case when using data processed with the core.py module
    
    Usage
    -------
    fig = oa_rate_by_publisher(**kwargs)
    fig.show

    """
    publisher_field=kwargs.get('publisher_field', "publisher")
    n=kwargs.get('n', 10)
    df = ie.import_data(**kwargs)
    filter_sort_index = df[publisher_field].value_counts().nlargest(n).keys()
    topten_list = filter_sort_index.tolist()
    grouped = df[df[publisher_field].isin(filter_sort_index)]
    dc = pd.crosstab(grouped[publisher_field], grouped["oa_host_type_normalized"],normalize='index').round(3)*100
    y=sorted(grouped[publisher_field].unique().tolist(), key=lambda x: topten_list.index(x),reverse=True)
    dd = dc.reindex(y, axis="index")
    fig = go.Figure()
    for i in dd.columns:
        fig.add_trace(go.Bar(y=y, x=dd[i], name=i,text=dd[i].astype(int),textposition='auto',marker={'color': colors[i]},orientation='h'))
    fig.update_layout(title="Taux d'accès ouvert aux publications par éditeur",barmode='stack',uniformtext_minsize=10)
    return fig
    
def oa_rate_by_type(**kwargs):
    """
    Function to plot a stacked bar chart of OA hosts by type of publication (journal-article, book chapter etc...)
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe
        
    Conditions
    ----------
    The imported file or dataframe must contain the following entry or columns : 
        genre,oa_host_type_normalized
    This is the case when using data processed with the core.py module
    
    Usage
    -------
    fig = oa_rate_by_type(**kwargs)
    fig.show

    """
    df = ie.import_data(**kwargs)
    dc = pd.crosstab(df["is_oa_normalized"], df["genre"],normalize='index').round(3)*100
    x=df["is_oa_normalized"].unique().tolist()
    fig = go.Figure()
    for i in dc.columns:
        fig.add_trace(go.Bar(x=x, y=dc[i], name=i,text=dc[i].astype(int),textposition='auto'))
    fig.update_layout(title="Répartition des publications par type de publications et par accès",barmode='stack',uniformtext_minsize=10)
    fig.update_xaxes(categoryorder='category ascending')
    return fig
    
def oa_by_status(**kwargs):
    """
    Function to plot a line chart of OA type by year
    ...

    Parameters
    ----------
    inpath : str, mutually exclusive with dataframe
        relative or absolute path of a csv or json or Excel flat file
    dataframe : object, mutually exclusive with inpath
        name of a pandas dataframe
        
    Conditions
    ----------
    The imported file or dataframe must contain the following entry or columns : 
        year,oa_status_normalized
    This is the case when using data processed with the core.py module
    
    Usage
    -------
    fig = oa_by_status(**kwargs)
    fig.show

    """
    df = ie.import_data(**kwargs)
    df.year = df.year.astype(str)
    dc = pd.crosstab(df["year"], df[df["oa_status_normalized"] != "Closed"]["oa_status_normalized"])
    x=sorted(df[df.year.notna()].year.unique().tolist())
    fig = go.Figure()
    for i in dc.columns:
        fig.add_trace(go.Scatter(x=x, y=dc[i], name=i,text=dc[i].astype(int), mode="lines"))
    fig.update_layout(title="Part Open Access : Evolution du type d'accès ouvert",uniformtext_minsize=10)
    fig.update_xaxes(categoryorder='category ascending',type="category")
    return fig
    
if __name__ == "__main__":
    oa_rate(),oa_rate_by_year(),oa_rate_by_publisher(),oa_rate_by_type(),oa_by_status()