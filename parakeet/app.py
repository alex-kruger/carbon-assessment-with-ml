from flask import Flask, request, jsonify
import os
import sys
import subprocess
from pathlib import Path
import json

app = Flask(__name__)

@app.route('/eio', methods=['GET'])
def generate_eio_predictions():
    try:
        # Set environment variables
        os.environ["AWS_PROFILE"] = "ParakeetUser"
        os.environ["AWS_REGION"] = "us-east-1"
        
        # Get the absolute path to the src directory and script
        current_dir = Path(__file__).parent
        src_path = current_dir / 'src'
        script_path = src_path / 'generate_ranked_preds.py'
        json_output_path = "data/predictions/parakeet_eio_preds.jsonl"
        
        # Build the command with all the parameters
        cmd = [
            sys.executable,  # Python interpreter
            str(script_path),
            "--lca_type", "eio",
            "--activity_file", request.args.get("activity_file", "data/raw/test_data.csv"),
            "--activity_col", "['COMMODITY_DESCRIPTION']",
            "--output_file", "data/predictions/parakeet_eio_preds",
            "--naics_file", "data/naics_index.csv",
            "--no_progress_bar"
        ]
        
        # Add optional parameters if provided
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
            env=os.environ.copy()
        )
        
        # Check if the command was successful
        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Command failed with exit code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500
        
        try:
            # Read the first line of the JSONL file (assuming we want the first prediction)
            with open(json_output_path, 'r') as jsonl_file:
                json_data = json.loads(jsonl_file.readline().strip())
                
            return jsonify({
                "status": "success",
                "message": "Prediction generated successfully",
                "prediction": json_data
            })
            
        except FileNotFoundError:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but output file {json_output_path} not found",
                "stdout": result.stdout
            })
        except json.JSONDecodeError:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but could not parse JSON from {json_output_path}",
                "stdout": result.stdout
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500
    
@app.route('/process', methods=['GET'])
def generate_process_predictions():
    try:
        # Set environment variables
        os.environ["AWS_PROFILE"] = "ParakeetUser"
        os.environ["AWS_REGION"] = "us-east-1"
        
        # Get the absolute path to the src directory and script
        current_dir = Path(__file__).parent
        src_path = current_dir / 'src'
        script_path = src_path / 'generate_ranked_preds.py'
        json_output_path = "data/predictions/parakeet_pLCA_activity_data_preds.jsonl"
        
        # Build the command with all the parameters
        cmd = [
            sys.executable,  # Python interpreter
            str(script_path),
            "--lca_type", "process",
            "--activity_file", request.args.get("activity_file", "../flamingo/process/activity_data.csv"),
            "--activity_col", "['activity_description']",
            "--output_file", "data/predictions/parakeet_pLCA_activity_data_preds",
            "--paraphrasing", "False"
        ]
        
        # Add optional parameters if provided
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
            env=os.environ.copy()
        )
        
        # Check if the command was successful
        if result.returncode != 0:
            return jsonify({
                "status": "error",
                "message": f"Command failed with exit code {result.returncode}",
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500
        
        try:
            # Read the first line of the JSONL file (assuming we want the first prediction)
            with open(json_output_path, 'r') as jsonl_file:
                json_data = json.loads(jsonl_file.readline().strip())
                
            return jsonify({
                "status": "success",
                "message": "Prediction generated successfully",
                "prediction": json_data
            })
            
        except FileNotFoundError:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but output file {json_output_path} not found",
                "stdout": result.stdout
            })
        except json.JSONDecodeError:
            return jsonify({
                "status": "partial_success",
                "message": f"Process completed but could not parse JSON from {json_output_path}",
                "stdout": result.stdout
            })
        
    except Exception as e:
        import traceback
        return jsonify({
            "status": "error", 
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)