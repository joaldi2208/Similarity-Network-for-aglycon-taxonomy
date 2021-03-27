#!/usr/bin/env python
# coding: utf-8


import igraph 
from igraph import Graph, Plot
import pandas as pd

from collections import Counter
import pickle


#------------------------------------------CLUSTERS-----------------------------------------------------------

def clustering(df_fingerprint_comparison,df_single_taxonomy):
    """
    Get two data frames. One with only single entries in the taxonomy row and the other with
    the two aglycons, their Tanimoto Index.

    Create clusters for the data frame with the Tanimoto Index by using the igraph modul.

    Pass a data frame with single taxonomy entries and the created cluster object and the cluster nodes.
    """
    df_all_aglycons_with_single_taxonomy = pd.read_pickle(df_single_taxonomy)
    fpc = pd.read_pickle(df_fingerprint_comparison)
    fpc_graph = Graph.DataFrame(fpc, directed=False)
    fpc_cluster = Graph.components(fpc_graph)
    fpc_nodes = fpc_graph.get_vertex_dataframe()
    with open("output_data/clustered_similarity_network.txt", "wb") as outfile:
        pickle.dump(fpc_cluster, outfile)
    cluster_in_lists(fpc_cluster, fpc_nodes, df_all_aglycons_with_single_taxonomy)


#---------------------------------------LIST OF CLUSTERS------------------------------------------------------------

def cluster_in_lists(fpc_cluster, fpc_nodes, df_all_aglycons_with_single_taxonomy):
    """
    Get a data frame with single taxonomy entries and the created cluster object and the cluster nodes.
    
    Create a list of of clusters. Each aglycon is represented by their smiles code and their taxonomy.
    
    Pass a list of lists, where each list represents a cluster of aglycons.
    """
    multi_cluster_list = []
    for index_list in fpc_cluster:
        single_cluster_list = []
        for index in index_list:
            for ind, aglycon in enumerate(df_all_aglycons_with_single_taxonomy.deglycosilated_smiles):
                try:
                    if aglycon == fpc_nodes.name[index]:
                        aglycon_tax_pair = {aglycon: list(df_all_aglycons_with_single_taxonomy.taxonomy[ind])[0]}          
                except KeyError:
                    #print(index, ind, aglycon, KeyError)
                    pass
            single_cluster_list.append(aglycon_tax_pair)
        multi_cluster_list.append(single_cluster_list)
    predict_annotation(multi_cluster_list)


#--------------------------------------PREDICT ANNOTATION------------------------------------------------------

def predict_annotation(multi_cluster_list):
    """
    Get a list of lists with aglycons and their taxonomy as key-value-pair.

    If the size of the cluster is greater than two and more of the half aglycons
    have a known taxonomy, all other aglycons get this taxonomy as predict taxonomy.
    When the taxonomy of one aglycon is unknown, the new taxonomy is named predict_$new taxonomy$
    When the taxonomy of one aglycon is different, the new taxonomy is named $old taxonomy$/predict_$new taxonomy$

    Pass a list of lists with customized key-value-pairs
    """
    cnt = Counter()
    for ind1, aglycon_tax_list in enumerate(multi_cluster_list):
        cnt.clear()
        len_aglycon_tax_list = len(aglycon_tax_list)
        if len_aglycon_tax_list > 2:
            for aglycon_tax in aglycon_tax_list:
                for tax in aglycon_tax.values():
                    if tax != 'no':
                        cnt[tax] += 1
            try:
                name_of_tax = max(cnt)
                quantity_of_tax = max(cnt.values())
                if quantity_of_tax >= len_aglycon_tax_list/2:
                    for ind2, aglycon_tax in enumerate(aglycon_tax_list):
                        for aglycon in aglycon_tax:
                            for tax in aglycon_tax.values():
                                if tax == 'no':
                                    multi_cluster_list[ind1][ind2][aglycon] = 'predict'+ '_' + name_of_tax
                                elif tax != name_of_tax:
                                    multi_cluster_list[ind1][ind2][aglycon] = tax + '/' + 'predict' + "_" + name_of_tax
            except ValueError:
                pass
    create_dataframe(multi_cluster_list)


#---------------------------------------------LIST OF DATAFRAMES----------------------------------------------

def create_dataframe(multi_cluster_list):
    """
    Get a list of lists with customized key-value-pairs

    Every cluster become a data frame with two columns, one is the smiles code and the 
    other one is the taxonomy

    Write a .txt file with the lists of dataframes.
    """
    multi_df_cluster_list = []
    for aglycon_tax_list in multi_cluster_list:
        df_cluster = pd.DataFrame(index=range(len(aglycon_tax_list)))
        df_cluster["aglycon"] = ""
        df_cluster["taxonomy"] = ""
        counter = 0
        for aglycon_tax in aglycon_tax_list:
            df_cluster.aglycon[counter] = list(aglycon_tax.keys())
            df_cluster.taxonomy[counter] = list(aglycon_tax.values())
            counter += 1
        multi_df_cluster_list.append(df_cluster)

    with open("output_data/multi_df_cluster_list.txt", "wb") as outfile:
        pickle.dump(multi_df_cluster_list, outfile)
    print("CLUSTERS DONE")


#clustering("output_data/fingerprint_comparison095.pkl" ,"output_data/df_all_aglycons_with_single_taxonomy.pkl")







