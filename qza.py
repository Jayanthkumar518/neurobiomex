# =========================================================
# qza_to_csv.py
# FINAL VERSION
#
# CONVERTS:
# 1. table.qza -> feature-table.csv
# 2. data_taxonomy.tsv -> taxonomy.csv
#
# NO QIIME2 REQUIRED
# =========================================================

import os
import zipfile
import biom
import pandas as pd

# =====================================================
# INPUT FILES
# =====================================================

TABLE_QZA = "table.qza"

TAXONOMY_TSV = "data_taxonomy.tsv"

# =====================================================
# OUTPUT FILES
# =====================================================

FEATURE_TABLE_CSV = "feature-table.csv"

TAXONOMY_CSV = "taxonomy.csv"

# =====================================================
# TEMP DIR
# =====================================================

TABLE_EXTRACT_DIR = "table_extracted"

os.makedirs(
    TABLE_EXTRACT_DIR,
    exist_ok=True
)

# =====================================================
# EXTRACT QZA
# =====================================================

def extract_qza(

    qza_path,
    extract_dir
):

    print(f"\nEXTRACTING: {qza_path}")

    with zipfile.ZipFile(
        qza_path,
        'r'
    ) as zip_ref:

        zip_ref.extractall(
            extract_dir
        )

    print("\nEXTRACTION COMPLETE")

# =====================================================
# EXTRACT TABLE.QZA
# =====================================================

extract_qza(
    TABLE_QZA,
    TABLE_EXTRACT_DIR
)

# =====================================================
# FIND BIOM FILE
# =====================================================

biom_path = None

for root, dirs, files in os.walk(
    TABLE_EXTRACT_DIR
):

    for file in files:

        if file.endswith(".biom"):

            biom_path = os.path.join(
                root,
                file
            )

            break

print("\nBIOM FILE FOUND:")
print(biom_path)

# =====================================================
# LOAD BIOM
# =====================================================

table = biom.load_table(
    biom_path
)

# =====================================================
# CONVERT TO DATAFRAME
# =====================================================

feature_df = table.to_dataframe(
    dense=True
)

# =====================================================
# TRANSPOSE
# =====================================================

feature_df = feature_df.T

# =====================================================
# SAVE FEATURE TABLE
# =====================================================

feature_df.to_csv(
    FEATURE_TABLE_CSV
)

print("\nFEATURE TABLE CSV SAVED")

print("\nFEATURE TABLE SHAPE:")
print(feature_df.shape)

print("\nTOP FEATURE TABLE:")
print(feature_df.head())

# =====================================================
# LOAD TAXONOMY TSV
# =====================================================

print("\nLOADING TAXONOMY TSV")

taxonomy_df = pd.read_csv(

    TAXONOMY_TSV,

    sep="\t"
)

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================

taxonomy_df.columns = [

    col.strip()

    for col in taxonomy_df.columns
]

print("\nTAXONOMY COLUMNS:")
print(taxonomy_df.columns)

# =====================================================
# FIND TAXONOMY COLUMN
# =====================================================

taxonomy_column = None

possible_cols = [

    "Taxon",
    "Taxonomy",
    "taxonomy",
    "Consensus.Lineage"
]

for col in possible_cols:

    if col in taxonomy_df.columns:

        taxonomy_column = col
        break

# =====================================================
# ERROR CHECK
# =====================================================

if taxonomy_column is None:

    raise ValueError(

        f"\nNo taxonomy column found.\n"
        f"Available columns: {taxonomy_df.columns}"
    )

print("\nUSING TAXONOMY COLUMN:")
print(taxonomy_column)

# =====================================================
# EXTRACT GENUS
# =====================================================

def extract_genus(taxonomy):

    try:

        taxa = taxonomy.split(";")

        genus = taxa[-1]

        genus = genus.replace(
            "g__",
            ""
        )

        genus = genus.replace(
            "D_5__",
            ""
        )

        genus = genus.replace(
            "__",
            ""
        )

        genus = genus.strip()

        if genus == "":

            genus = "Unknown"

        return genus

    except:

        return "Unknown"

taxonomy_df["Genus"] = taxonomy_df[
    taxonomy_column
].apply(extract_genus)

# =====================================================
# SAVE TAXONOMY CSV
# =====================================================

taxonomy_df.to_csv(

    TAXONOMY_CSV,

    index=False
)

print("\nTAXONOMY CSV SAVED")

print("\nTAXONOMY SHAPE:")
print(taxonomy_df.shape)

print("\nTOP TAXONOMY:")
print(taxonomy_df.head())

# =====================================================
# CREATE TAXONOMY MAP
# =====================================================

feature_id_column = None

possible_feature_cols = [

    "Feature ID",
    "FeatureID",
    "feature-id",
    "#OTU ID"
]

for col in possible_feature_cols:

    if col in taxonomy_df.columns:

        feature_id_column = col
        break

if feature_id_column is not None:

    taxonomy_map = dict(

        zip(

            taxonomy_df[
                feature_id_column
            ],

            taxonomy_df[
                "Genus"
            ]
        )
    )

    print("\nTAXONOMY MAP CREATED")

    print("\nTOP MAPPINGS:")

    for i, (k, v) in enumerate(
        taxonomy_map.items()
    ):

        print(k, "->", v)

        if i >= 5:
            break

else:

    print("\nWARNING:")
    print("No Feature ID column found")

# =====================================================
# COMPLETE
# =====================================================

print("\nQZA CONVERSION COMPLETE")

print("\nFILES CREATED:")

print("1. feature-table.csv")

print("2. taxonomy.csv")