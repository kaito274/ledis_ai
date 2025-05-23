from flask import Flask, request, jsonify
import time
from ledis_core import execute_command
from ledis_ai_translator import init_components

app = Flask(__name__)

# Initialize components
init_components()

@app.route("/", methods=["POST"])
def handle_request():
    command_str = request.get_data(as_text=True)
    response = execute_command(command_str)
    return response 

if __name__ == "__main__":
    # Host 0.0.0.0 makes it accessible from other machines on the network
    app.run(host="0.0.0.0", port=5000, debug=True)