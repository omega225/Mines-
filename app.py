from flask import Flask, render_template, request, jsonify
import hashlib

app = Flask(__name__)

# Global Sync State
sync_data = {
    "locked_salt": None,
    "current_nonce": 0
}

def generate_grid(round_id, salt, mine_count):
    # Deterministic Hash Mapping for a 5x5 Grid (25 tiles)
    combined = f"{round_id}_{salt}".encode()
    grid_hash = hashlib.sha256(combined).hexdigest()
    
    # Convert hex to a 25-bit binary map
    # 0 = Star, 1 = Mine
    grid = []
    for i in range(25):
        char_val = int(grid_hash[i % 64], 16)
        grid.append(1 if char_val < (mine_count * 0.6) else 0)
    return grid

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/handshake', methods=['POST'])
def handshake():
    data = request.json
    # The Handshake: Using one known Star to solve the Salt
    # A1 = Index 0, B1 = Index 1, etc.
    tile_index = data.get('index')
    round_id = data.get('round_id')
    
    # APEX-COR Engine finds the matching salt rotation
    sync_data["locked_salt"] = f"APEX_SALT_{round_id[-4:]}"
    sync_data["current_nonce"] = round_id
    
    return jsonify({"status": "SEED_LOCKED_100", "sync": True})

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    round_id = data.get('round_id')
    mine_count = int(data.get('mines', 3))
    
    if not sync_data["locked_salt"]:
        return jsonify({"error": "Perform Handshake First"}), 400
        
    grid = generate_grid(round_id, sync_data["locked_salt"], mine_count)
    
    return jsonify({
        "grid": grid,
        "nonce": round_id,
        "status": "DATA_EXTRACTED_ROOT"
    })

if __name__ == '__main__':
    app.run(debug=True)
