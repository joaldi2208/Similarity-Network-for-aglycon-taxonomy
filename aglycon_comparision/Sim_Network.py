#!/usr/bin/env python3

import sys 

from single_taxonomy import complete_databank
from tanimoto_index import create_fingerprints
from predict_annotation import clustering
from statistic_report import statistics_of_analyse


def main():
    try:
        similarity_value = float(sys.argv[1])
        port = sys.argv[2]
        coconut_database = sys.argv[3]
        sweetcoconut_database = sys.argv[4]
        complete_databank(port,coconut_database,sweetcoconut_database)
    except IndexError:
        if len(sys.argv) == 2:
            complete_databank()
        elif len(sys.argv) == 3:
            complete_databank(port)
        elif len(sys.argv) == 4:
            complete_databank(port,coconut_database)
    try:
        create_fingerprints("output_data/df_all_aglycons_with_single_taxonomy.pkl", similarity_value)
    except IndexError:
        create_fingerprints("output_data/df_all_aglycons_with_single_taxonomy.pkl")
    clustering("output_data/fingerprint_comparison.pkl" ,"output_data/df_all_aglycons_with_single_taxonomy.pkl")
    statistics_of_analyse("output_data/multi_df_cluster_list.txt")




if __name__ == "__main__":
    main()
