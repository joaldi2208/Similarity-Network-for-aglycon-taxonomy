#!/usr/bin/python3


from rdkit import Chem
from rdkit.Chem import Draw

import pandas as pd

from rdkit.Chem import AllChem
from rdkit import DataStructs
from rdkit.Chem import Descriptors

import itertools
from collections import Counter

from rdkit import RDLogger
import pickle

#-----------------------------------------MORGAN FINGERPRINTS--------------------------------------

def create_fingerprints(df_Without_Double_or_Triple, similarity_value = 0.95):
    """
    Get a data frame with only a single entry in the taxonomy row
    
    Use RDkit modul to create Morgan-Fingerprints from the smiles code of each aglycon.

    Pass the input of the similarity value, the smiles code of the aglycons, the fingerprint of the aglycons and
    the created data frame with only single entries in the taxonomy row.
    """
    with open(df_Without_Double_or_Triple, "rb") as infile:
        df_Without_Double_or_Triple = pickle.load(infile, encoding="utf-8")

    mol_From_Smiles = []
    index_Mol_Explicit_Valence = []
    index_Mol_Implicit_Valence = []
    index = 0
    RDLogger.DisableLog('rdApp.*')
    for smiles in df_Without_Double_or_Triple.deglycosilated_smiles:
        mol = Chem.MolFromSmiles(smiles)
        if mol == None:
            index_Mol_Explicit_Valence.append(index)
        else:
            mol_From_Smiles.append(mol)
            index_Mol_Implicit_Valence.append(index)
        index += 1    
    #print(index_Mol_Explicit_Valence)
    df_Without_Explicit_Valence = df_Without_Double_or_Triple.iloc[index_Mol_Implicit_Valence[:]]
    df_Without_Explicit_Valence = df_Without_Explicit_Valence.reset_index()
    #df_Without_Explicit_Valence
    fps = [AllChem.GetMorganFingerprint(mol,2,useFeatures=True) for mol in mol_From_Smiles]
    # create combinations of deglycosilated_smiles for indexing
    aglycon_formula_for_indexing = list(df_Without_Explicit_Valence.deglycosilated_smiles)
    aglycon_formulas = [aglycon_pair for aglycon_pair in itertools.combinations(aglycon_formula_for_indexing, 2)]
    #print(len(aglycon_formulas))
    print("MORGAN FINGERPRINTS DONE")
    create_tanimoto_index(similarity_value, aglycon_formulas, fps,df_Without_Double_or_Triple)
    


#-----------------------------------TANIMOTO INDEX BETWEEN TWO DIFFERENT AGLYCONS--------------------------------------

def create_tanimoto_index(similarity_value, aglycon_formulas, fps, df_Without_Double_or_Triple):
    """
    Get the similarity value, the Morgan-Fingerprint of each aglycon and a data frame with only single 
    entries in the taxonomy row.
    
    Check the Tanimito Index for all possible two-pairs of aglycons. If the value of the Tanimoto 
    Index is above the given similarity value, the aglycons and their Tanimoto Index are append to a new data frame.
    
    Pass the new three column data frame with both aglycons and their Tanimoto Index.
    """
    aglycon_pairs = itertools.combinations(fps, 2)
    aglycon1 = []
    aglycon2 = []
    tanimoto = []
    counter = 0
    for pair in aglycon_pairs:
        fingerprint = DataStructs.TanimotoSimilarity(pair[0],pair[1])
        if fingerprint >= similarity_value:
            aglycon1.append(aglycon_formulas[counter][0])
            aglycon2.append(aglycon_formulas[counter][1])
            tanimoto.append(fingerprint)
        counter += 1
    #print(counter)
    df_comparison = pd.DataFrame({
        "aglycon1": aglycon1,
        "aglycon2": aglycon2,
        "tanimoto_index": tanimoto
    })
    create_df_with_tanimoto_index(df_comparison,df_Without_Double_or_Triple)


#-----------------------------------------MERGE DATA FRAME WITH TAXONOMY--------------------------------------------------

def create_df_with_tanimoto_index(df_comparison,df_Without_Double_or_Triple):
    """
    Get a data frame with two aglycons and their Taninmoto Index and a data frame with only single 
    entries in the taxonomy row.
    
    Add the taxonomy of both aglycons to the data frame. Each taxonomy is represented as a 
    string and a number.

    Writing an .csv and an .pkl file for the expanded data frame.
    """
    df_aglycon_taxes_1 = pd.DataFrame({
        "aglycon1": df_Without_Double_or_Triple.deglycosilated_smiles,
        "taxonomy1": df_Without_Double_or_Triple.taxonomy,
    })
    df_aglycon_taxes_2 = pd.DataFrame({
        "aglycon2": df_Without_Double_or_Triple.deglycosilated_smiles,
        "taxonomy2": df_Without_Double_or_Triple.taxonomy,
    })
    df_comparison = pd.merge(df_comparison, df_aglycon_taxes_1, how="left", on="aglycon1")
    df_comparison = pd.merge(df_comparison, df_aglycon_taxes_2, how="left", on="aglycon2")
    df_comparison
    # *change tax-sets to values from 1 to 5*
    tax1_to_value = df_comparison.taxonomy1.replace([{"no"},{"plants"},{"bacteria"},{"animals"},{"fungi"}],[1,2,3,4,5])
    tax2_to_value = df_comparison.taxonomy2.replace([{"no"},{"plants"},{"bacteria"},{"animals"},{"fungi"}],[1,2,3,4,5])
    df_comparison["tax1_as_value"] = tax1_to_value
    df_comparison["tax2_as_value"] = tax2_to_value
    df_comparison.to_csv("output_data/fingerprint_comparison.tsv",sep="\t")
    df_comparison.to_pickle("output_data/fingerprint_comparison.pkl")
    print("TANIMOTO INDEX DONE")
