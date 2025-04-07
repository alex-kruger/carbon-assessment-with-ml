#!/bin/zsh
LCA_TYPE="process" # either "process" or "eio"
ACTIVITY_FILE="../../flamingo/process/activity_data.csv"
ACTIVITY_COL="['activity_description']"
OUTPUT_FILE="../data/predictions/parakeet_pLCA_activity_data_preds"
export AWS_PROFILE="ParakeetUser" 
export AWS_REGION="us-east-1" 


echo "Running..."
python ../src/generate_ranked_preds.py --verbose --lca_type "$LCA_TYPE" \
--activity_file "$ACTIVITY_FILE" --activity_col "$ACTIVITY_COL" \
--output_file "$OUTPUT_FILE" --paraphrasing False \

