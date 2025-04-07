#!/bin/zsh
LCA_TYPE="eio"
ACTIVITY_FILE="../data/raw/test_data.csv"
ACTIVITY_COL="['COMMODITY_DESCRIPTION']"
OUTPUT_FILE="../data/predictions/parakeet_eio_preds"
export AWS_PROFILE="ParakeetUser" 
export AWS_REGION="us-east-1" 



echo "Running..."
python ../src/generate_ranked_preds.py --verbose --lca_type "$LCA_TYPE" \
--activity_file "$ACTIVITY_FILE" --activity_col "$ACTIVITY_COL" \
--output_file "$OUTPUT_FILE" \
--sheet_name "$SHEET_NAME"\
