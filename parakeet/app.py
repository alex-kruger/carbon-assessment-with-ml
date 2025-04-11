from flask import Flask, request, jsonify
import os
import sys
import subprocess
from pathlib import Path
import json
import pandas as pd

app = Flask(__name__)

from enum import Enum
class LCAType(Enum):
    PROCESS = "process"
    EIO = "eio"

PARAKEET_PATH = Path(__file__).parent.absolute()
SRC_PATH = PARAKEET_PATH / 'src'
DATA_PATH = PARAKEET_PATH / 'data'
SCRIPT_PATH = SRC_PATH / 'generate_ranked_preds.py'
NAICS_PATH = DATA_PATH / 'naics_index.csv'
PREDICTIONS_PATH = DATA_PATH / 'predictions'
RAW_PATH = DATA_PATH / 'raw'
INPUT_CSV_PATH_EIO = RAW_PATH / 'api_eio_input.csv'
OUTPUT_PATH_EIO = PREDICTIONS_PATH / 'parakeet_eio_preds'
JSONL_OUTPUT_PATH_EIO = OUTPUT_PATH_EIO.absolute().with_suffix('.jsonl')
INPUT_CSV_PATH_PROCESS = RAW_PATH / 'api_process_input.csv'
OUTPUT_PATH_PROCESS = PREDICTIONS_PATH / 'parakeet_process_preds'
JSONL_OUTPUT_PATH_PROCESS = OUTPUT_PATH_PROCESS.absolute().with_suffix('.jsonl')
ACTIVITY_COL_EIO = "['COMMODITY_DESCRIPTION']"
ACTIVITY_COL_PROCESS = "['activity_description']"
REQUIRED_COLUMNS_EIO = ["COMMODITY", "COMMODITY_DESCRIPTION", "EXTENDED_DESCRIPTION", "CONTRACT_NAME"]
REQUIRED_COLUMNS_PROCESS = ["COMMODITY", "COMMODITY_DESCRIPTION", "EXTENDED_DESCRIPTION", "CONTRACT_NAME"]

def generate_predictions(lca_type: LCAType):
    if lca_type == LCAType.EIO:
        input_csv_path = INPUT_CSV_PATH_EIO
        output_path = OUTPUT_PATH_EIO
        jsonl_output_path = JSONL_OUTPUT_PATH_EIO
        activity_col = ACTIVITY_COL_EIO
        required_columns = REQUIRED_COLUMNS_EIO
    else:
        input_csv_path = INPUT_CSV_PATH_PROCESS
        output_path = OUTPUT_PATH_PROCESS
        jsonl_output_path = JSONL_OUTPUT_PATH_PROCESS
        activity_col = ACTIVITY_COL_PROCESS
        required_columns = REQUIRED_COLUMNS_PROCESS
    
    try:
        # Check if request contains JSON data
        if not request.is_json:
            return jsonify({
                "status": "error",
                "message": "Missing JSON data in request"
            }), 400
            
        # Get the JSON data from the request
        data = request.get_json()
        
        # Check if it's a list
        if not isinstance(data, list):
            return jsonify({
                "status": "error",
                "message": "Expected a JSON array of objects"
            }), 400
        
        # Set environment variables
        os.environ["AWS_PROFILE"] = "ParakeetUser"
        os.environ["AWS_REGION"] = "us-east-1"
        
        for directory in [DATA_PATH, PREDICTIONS_PATH, RAW_PATH]:
            directory.mkdir(parents=True, exist_ok=True)
                
        # Convert JSON array to DataFrame
        df = pd.DataFrame(data)

        # Convert all column names to uppercase
        df.columns = [col.upper() if lca_type == LCAType.EIO else col.lower() for col in df.columns]

        # Ensure all required columns exist (now with uppercase names)
        for col in required_columns:
            if col not in df.columns:
                df[col] = ""  # Add empty column if missing
        
        # Save as CSV
        df.to_csv(input_csv_path, index=False)
        print(f"Created input CSV at {input_csv_path} with {len(df)} rows")
            
        # Build relative paths
        rel_activity_file = os.path.relpath(input_csv_path, PARAKEET_PATH)
        
        # Build the command
        cmd = [
            sys.executable,
            str(SCRIPT_PATH),
            "--lca_type", "eio",
            "--activity_file", rel_activity_file,
            "--activity_col", activity_col,
            "--output_file", str(output_path),
            "--naics_file", str(NAICS_PATH),
            "--no_progress_bar"
        ]
        if lca_type == LCAType.PROCESS:
            cmd = [
                sys.executable,
                str(SCRIPT_PATH),
                "--lca_type", "process",
                "--activity_file", rel_activity_file,
                "--activity_col", activity_col,
                "--output_file", str(output_path),
                "--paraphrasing", "False"
            ]
        
        # Add optional parameters
        if request.args.get("sheet_name"):
            cmd.extend(["--sheet_name", request.args.get("sheet_name")])
            
        if request.args.get("verbose", "").lower() == "true":
            cmd.append("--verbose")
            
        # Execute the command
        print(f"Executing command: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PARAKEET_PATH,
            env=os.environ.copy()
        )
        
        # Check if successful
        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Command failed with exit code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout,
                "command": ' '.join(cmd)
            }), 500
        
        results = []
        
        try:
            # Read the JSONL file line by line
            with open(jsonl_output_path, 'r') as jsonl_file:
                for line in jsonl_file:
                    results.append(json.loads(line.strip()))
                
            return jsonify({
                "status": "success",
                "message": f"Successfully processed {len(results)} items",
                "predictions": results
            })
            
        except FileNotFoundError:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but output files not found",
                "stdout": result.stdout
            })
        except json.JSONDecodeError as e:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but could not parse JSON: {str(e)}",
                "stdout": result.stdout
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

@app.route("/healthcheck", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Parakeet API is running."}), 200

@app.route('/eio', methods=['POST'])
def generate_eio_predictions():
    return generate_predictions(LCAType.EIO)

@app.route('/process', methods=['POST'])
def generate_process_predictions():
    return generate_predictions(LCAType.PROCESS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)