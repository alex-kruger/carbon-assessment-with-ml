#!/bin/zsh
LCA_TYPE="eio"
ACTIVITY_FILE="../data/raw/api_eio_input.csv"
ACTIVITY_COL="['COMMODITY_DESCRIPTION']"
OUTPUT_FILE="../data/predictions/parakeet_eio_preds"
NAICS_FILE="../data/naics_index.csv"
export AWS_PROFILE="ParakeetUser" 
export AWS_REGION="us-east-1" 



echo "Running..."
python ../src/generate_ranked_preds.py --verbose --lca_type "$LCA_TYPE" \
--naics_file "$NAICS_FILE" \
--activity_file "$ACTIVITY_FILE" --activity_col "$ACTIVITY_COL" \
--output_file "$OUTPUT_FILE" \
--sheet_name "$SHEET_NAME"\
