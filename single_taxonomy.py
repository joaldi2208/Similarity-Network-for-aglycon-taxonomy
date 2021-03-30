#!/usr/bin/env python
# coding: utf-8


from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import venn
from collections import Counter


#--------------------------------------------SELECT AGLYCONS FROM A DIFFERENT DATABANK----------------------------------------

def complete_databank(port="localhost:27017",coconut_database="COCONUT2020-10",sweetcoconut_database="sweetcoconut"):
    """
    Gets user input such as the localhost and the similarity value for the comparision.

    Reads all the ringsugars in the given database and and creates a data frame with aglycons, 
    their coconut_id and taxonomy. The biological names are delete and if  
    there are two different taxonomies for an aglycon, the taxonomy is called 'double'.

    Passes the created data frame.
    """
    client = MongoClient(port)
    db_complete = client[coconut_database]
    collection = db_complete.uniqueNaturalProduct
    db_complete_only_ring_sugars = pd.DataFrame(list(collection.find({"contains_ring_sugars": True})))
    df_complete_tax = pd.DataFrame({"taxonomy": db_complete_only_ring_sugars["textTaxa"],
                        "smiles": db_complete_only_ring_sugars["smiles"],
                        "coconut_id": db_complete_only_ring_sugars["coconut_id"],
                        "no_sugar_smiles": db_complete_only_ring_sugars["sugar_free_smiles"]
                        })
    complete_names = []
    indexes = []
    for i in range(len(df_complete_tax.taxonomy)):
        # some entries are empty lists
        # doubles
        if df_complete_tax.taxonomy[i] != [] and ("plants" in df_complete_tax.taxonomy[i] or "bacteria" in df_complete_tax.taxonomy[i] or "marine" in df_complete_tax.taxonomy[i] or "animals" in df_complete_tax.taxonomy[i] or "fungi" in df_complete_tax.taxonomy[i]):
            indexes.append(i)
            complete_names.append(df_complete_tax.taxonomy[i])
    df_five_tax = df_complete_tax.loc[indexes[:]]
    df_tax_id = pd.DataFrame({"taxonomy": df_five_tax.taxonomy,
                                    "coconut_id": df_five_tax.coconut_id})
    df_tax_id = df_tax_id.reset_index()
    taxonomies = ["plants","bacteria","fungi","marine","animals"]
    biology_names = []
    for row in df_tax_id.taxonomy:
        for name in row:
            if name not in taxonomies:
                biology_names.append(name)
    for biology_name in biology_names:
        for row in df_tax_id.taxonomy:
            if biology_name in row:
                row.remove(biology_name)
    # **------------for tax prediction---------------**
    df_tax_id.to_pickle("output_data/for_predict_doubletriple.pkl")
    # **----------end tax prediction--------------**
    for ind, tax_list in enumerate(df_tax_id.taxonomy):
        if "marine" in tax_list:
            #print(ind, tax_list)
            if len(tax_list) > 1:
                df_tax_id.taxonomy[ind].remove("marine")
            else:
                df_tax_id.taxonomy[ind].append("no")
                df_tax_id.taxonomy[ind].remove("marine")
                #df_tax_id.taxonomy[ind] = ["no"]
    taxonomy_Double = []
    taxonomy_Triple = []
    taxonomy_single_entry = []
    for ind, tax_list in enumerate(df_tax_id.taxonomy):
        #print(ind, tax_list)
        if len(tax_list) == 1:
            taxonomy_single_entry.append(tax_list[0])
        elif len(tax_list) == 2: 
            taxonomy_single_entry.append('double')
            # save original annotation
            taxonomyDouble1 = []
            for tax in tax_list:
                taxonomyDouble1.append(tax)
            taxonomy_Double.append(taxonomyDouble1)
        elif len(tax_list) == 3:
            taxonomy_single_entry.append('triple')
            # save original annotation
            taxonomyTriple1 = []
            for tax in tax_list:
                taxonomyTriple1.append(tax)
            taxonomy_Triple.append(taxonomyTriple1)
        else:
            print('Error: Too many taxonomies for one aglycon','\n','create a new elif statement in line 102 in tanimoto_index.py')
    df_tax_id_fromCompleteDatabank = pd.DataFrame({"taxonomy": taxonomy_single_entry,
                        "coconut_id": df_five_tax.coconut_id})
    sweetcoconut_databank(df_tax_id_fromCompleteDatabank,taxonomy_Double,sweetcoconut_database,port)


#---------------------------------MERGE TWO DATA FRAMES ON COCUNUT ID AND ON SAME SMILES CODE-----------------------------------

def sweetcoconut_databank(df_tax_id_fromCompleteDatabank, taxonomy_Double,sweetcoconut_database,port):
    """
    Gets the created data frame with the three columns aglycon, coconut id and taxonomy

    Merges sweetcocunt data frame with incoming data frame via their coconut id.
    Replaces nan with "no" if there isn't a known taxonomy in the row for the aglycon.
    Summarize all aglycons with the same structure into one row.

    Writes a .pkl file with where all aglycons with the same smiles code are in the same row. 
    Passes a data frame with all the same aglycon structures in one row.
    """
    client2 = MongoClient(port)
    db_s = client2[sweetcoconut_database]
    collection2 = db_s.sweetNaturalProduct
    sweetnp = pd.DataFrame(list(collection2.find({"contains_sugar": True})))
    sweetnp_with_tax = pd.merge(sweetnp, df_tax_id_fromCompleteDatabank, how="left", on="coconut_id")
    df_cutout_sweetnp_with_tax = pd.DataFrame({"coconut_id": sweetnp_with_tax.coconut_id,
                                "taxonomy": sweetnp_with_tax.taxonomy,
                                "all_deglycosilated_smiles": sweetnp_with_tax.all_deglycosilated_smiles
    })
    df_cutout_no_nan = df_cutout_sweetnp_with_tax.fillna('no')
    df_cutout_explode = df_cutout_no_nan.explode("all_deglycosilated_smiles",ignore_index=True)
    #display(df_cutout_explode)
    unique_deglycosilated_smiles = set(df_cutout_explode["all_deglycosilated_smiles"])
    unique_deglycosilated_smiles.pop()
    df_NP = pd.DataFrame(unique_deglycosilated_smiles, columns=["deglycosilated_smiles"])
    df_NP["coconut_id"] = ""
    df_NP["taxonomy"] = ""
    index = 0
    for mol in df_NP.deglycosilated_smiles:
        all_rows = df_cutout_explode[df_cutout_explode["all_deglycosilated_smiles"]==mol]
        df_NP.coconut_id[index] = (all_rows.coconut_id.values)
        df_NP.taxonomy[index] = (all_rows.taxonomy.values)
        index += 1
    #display(df_NP)
    # **-----------------for tax prediction-------------------**
    df_NP.to_pickle("output_data/for_predict_multiple_tax.pkl")
    # **----------------end tax prediction--------------------**
    index = 0
    for tax_list in df_NP.taxonomy:
        df_NP.taxonomy[index] = set(tax_list)
        if len(df_NP.taxonomy[index]) >= 2:
            if 'no' in df_NP.taxonomy[index]:
                df_NP.taxonomy[index].remove('no')
        index += 1
    #display(df_NP)
    bar_plot(df_NP)
    venn_diagram(df_NP,taxonomy_Double)
    aglycon_single_tax(df_NP)


#------------------------------------BAR PLOT-----------------------------------

def bar_plot(df_NP):
    """
    Gets a data frame with all the same aglycon structures in one row.

    Counts all taxonomies and create a barplot. 'Double' is also a taxonomy.

    Saves the bar plot with the numbers of different taxonomies as .png.
    """
    cnt = Counter()
    for tax_list in df_NP.taxonomy:
        for tax in list(tax_list):
            if tax != 'no':
                cnt[tax] += 1
    plt.bar(cnt.keys(),cnt.values())
    plt.xlabel('taxonomic provenance')
    plt.ylabel('number of molecules')
    plt.title('number of aglycons with taxonomies')
    plt.savefig("output_data/Barplot.png")
    print("BAR PLOT DONE")


#-----------------------------------VENN-DIAGRAM--------------------------------------

def venn_diagram(df_NP, taxonomy_Double):
    """
    Gets a data frame with all the same aglycon structures in one row.
   
    Counts all taxonomies and creates a venn diagram with the four taxonomies plants, bacteria,
    animals, fungi. Reads the original taxonmies of the 'Double' entries.
    
    Saves a venn-diagram of the different taxonmies as .png.
    """
    taxonomy_Single = [list(tax) for tax in df_NP.taxonomy if 'double' not in tax]
    taxonomy_All = taxonomy_Single + taxonomy_Double
    plants = set()
    bacteria = set()
    animals = set()
    fungi = set()
    for tax_list in taxonomy_All:
        if "plants" in tax_list:
            for tax in tax_list:
                plants.add(tax.index)
        if "bacteria" in tax_list:
            for tax in tax_list:
                bacteria.add(tax.index)
        if "animals" in tax_list:
            for tax in tax_list:
                animals.add(tax.index)
        if "fungi" in tax_list:
            for tax in tax_list:
                fungi.add(tax.index)     
    dic_for_venn = {"plants": plants, "bacteria": bacteria, "animals": animals, "fungi": fungi}
    fig= venn.venn(dic_for_venn)
    plt.title("venn-diagram from the taxonomy of aglycons")
    plt.savefig("output_data/Venn-Diagram.png")
    print("VENN DIAGRAM DONE")


#--------------------------------SINGLE ENTRY TAXONOMY-------------------------------------------

def aglycon_single_tax(df_NP):
    """
    Gets a data frame with all the same aglycon structures in one row.
    
    Deletes all rows with more than one entry in the taxonomy row.

    Passes a data frame with only one entry (superkingdom or 'no') in the taxonomy row.
    """
    # **seperate aglycons with at least two different entries in taxonomy**
    index_Unique_Tax = [ind for ind, tax_list in enumerate(df_NP.taxonomy) if len(tax_list) == 1]
    df_Without_Double = df_NP.iloc[index_Unique_Tax[:]]
    #df_Without_Double
    # **check for 'double' or 'triple' entries in taxonomy**
    index_double_or_triple = [ind for ind, tax_list in enumerate(df_Without_Double.taxonomy) if 'double' not in tax_list and 'triple' not in tax_list]
    df_Without_Double_or_Triple = df_Without_Double.iloc[index_double_or_triple[:]]
    #df_Without_Double_or_Triple
    # **------for taxonomy prediction------**
    df_Without_Double_or_Triple.to_pickle("output_data/df_all_aglycons_with_single_taxonomy.pkl")
    # **------end for taxonomy prediction------**
   




#complete_databank()
