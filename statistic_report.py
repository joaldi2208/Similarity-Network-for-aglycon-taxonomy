#!/usr/bin/env python
# coding: utf-8



import pickle
import json
import pandas as pd


#------------------------------READ AND WRITE STATISTICS----------------------------------------

def statistics_of_analyse(multi_df_cluster_list):
    """
    Read a file with list of data frames inside. The data frames consist of two columns.
    One is the smiles code of the aglycon the other is the taxonomy.

    Pass the list of data frames.
    Write a .txt file from the return value.
    """
    with open(multi_df_cluster_list, "rb") as infile:
        similarity = pickle.load(infile, encoding='utf-8')
    statistic_summary = summary(similarity)
    with open("output_data/statistic_report.json", "w") as outfile:
        json.dump(statistic_summary, outfile, indent = 4)


#-----------------------------------STATISTIC SUMMARY------------------------------------------------

def summary(file):
    """
    Get a list of data frames with the smiles code and the taxonomy of each aglycons.

    Count and analyse statistic parameters like the max and min size of the clusters.
    Create a dictionary with the result of the statistic report.
    
    Return the dictionary.
    """
    cluster_with_tax = 0
    cluster_with_prediction = 0
    size_of_clusters = []
    total_number_of_clusters = 0
    for cluster in file:
        total_number_of_clusters += int(1)
        cluster_shape = cluster.shape
        size_of_clusters.append(cluster_shape[0])
        for tax_list in cluster.taxonomy:
            for tax in tax_list: 
                if 'predict' in tax:
                    cluster_with_prediction += 1
        for tax_list in cluster.taxonomy:
            if "no" not in tax_list:
                cluster_with_tax += 1
                break

            


    size_of_clusters.sort()
    average_size_of_clusters = sum(size_of_clusters)/len(size_of_clusters)
    max_size_of_clusters = int(max(size_of_clusters))
    min_size_of_clusters = int(min(size_of_clusters))
    median_size_of_clusters = int(size_of_clusters[int(len(size_of_clusters)/2)])
    prediction_percent = (cluster_with_prediction/total_number_of_clusters)*100
    annotation_percent = (cluster_with_tax/total_number_of_clusters)*100
    
    statistic_summary = {"total number of clusters":total_number_of_clusters,
                        "average size of clusters":average_size_of_clusters,
                        "max cluster size":max_size_of_clusters,
                        "min cluster size":min_size_of_clusters, 
                        "median cluster size":median_size_of_clusters, 
                        "total number of clusters with annotation":cluster_with_tax,
                        "annotation in %": annotation_percent,
                        "total number of clusters with prediction": cluster_with_prediction,
                        "prediction in %":prediction_percent}
    return statistic_summary






