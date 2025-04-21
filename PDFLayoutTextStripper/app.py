import subprocess
import os
import shutil
import pandas as pd
import json
import sys
from pathlib import Path

def check_maven_installation():
    """Check if Maven is installed and accessible"""
    try:
        # Using shell=True for Windows compatibility with 'where' command
        if sys.platform == "win32":
            result = subprocess.run('where mvn', shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(['which', 'mvn'], capture_output=True, text=True)
        
        return result.returncode == 0
    except Exception as e:
        return False

def run_maven_command(command, cwd=None):
    """Run Maven command with proper error handling"""
    try:
        # On Windows, we need to use mvn.cmd instead of mvn
        maven_exec = 'mvn.cmd' if sys.platform == "win32" else 'mvn'
        
        # Convert command list to use the correct Maven executable
        if isinstance(command, list):
            command[0] = maven_exec
        
        # Add shell=True for Windows compatibility
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=sys.platform == "win32",
            cwd=cwd
        )
        return process
    except Exception as e:
        print(f"Error executing Maven command: {str(e)}")
        return None
    
def json_to_csv(json_data):
    """Convert JSON data to CSV format"""
    try:
        flat_data = [item for sublist in json_data for item in sublist]
        df = pd.DataFrame(flat_data)
        return df
    except Exception as e:
        print(f"Error converting JSON to CSV: {str(e)}")
        return None

def ocrFromJava(file_path):
    """Process PDF file using Java OCR"""
    # Verify Maven installation
    if not check_maven_installation():
        print("Maven is not installed or not in PATH. Please install Maven.")
        return False
    
    # Check/create target directory
    if not os.path.exists('target/classes'):
        print("Compiling Java classes...")
        
        compile_result = run_maven_command(['mvn', 'clean', 'compile'])
        
        if compile_result is None or compile_result.returncode != 0:
            print("Maven compilation failed. Please check your Java configuration.")
            return False
        
        print("Compilation completed.")

    # Run Java application
    print("Processing OCR...")
    exec_command = f'mvn exec:java -Dexec.mainClass=io.github.jonathanlink.test -Dexec.args="{file_path}"'
    
    exec_result = run_maven_command(exec_command)
    
    if exec_result is None or exec_result.returncode != 0:
        print("OCR processing failed. Please check the file and try again.")
        return False
    
    print("OCR processing completed successfully.")
    return True

if __name__ == "__main__":
    ocrFromJava(str("PDFs/370_paper.pdf"))