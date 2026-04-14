from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np

MU_EARTH = 3.986004418e14
R_EARTH = 6371000.0

# Try to import compiled fortran module, fallback if not compiled yet
try:
    import ablation
    FORTRAN_LOADED = True
except ImportError:
    FORTRAN_LOADED = False

app = Flask("Space Debris Re-entry Ablation Simulator")
CORS(app)  # Enable CORS for all routes

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"status": "Backend Active", "fortran_loaded": FORTRAN_LOADED})

@app.route("/simulate", methods=["POST", "OPTIONS"])
def run_simulation():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    if not FORTRAN_LOADED:
        return jsonify({"detail": "Fortran module not compiled. Jalankan ./compile.sh terlebih dahulu"}), 500
    
    # Get parameters with defaults
    data = request.json or {}
    mass = float(data.get("mass", 100.0))
    area = float(data.get("area", 2.0))
    drag_coeff = float(data.get("drag_coeff", 2.2))
    entry_mode = str(data.get("entry_mode", "auto")).lower()
    requested_ld = data.get("lift_to_drag", None)

    if requested_ld is not None:
        lift_to_drag = float(requested_ld)
    else:
        is_capsule_like = mass >= 1000.0 and area >= 1.5 and drag_coeff <= 1.6
        if entry_mode == "lifting":
            lift_to_drag = 0.1
        elif entry_mode == "auto" and is_capsule_like:
            lift_to_drag = 0.1
        else:
            lift_to_drag = 0.0

    params = {
        "velocity": float(data.get("velocity", 7800.0)),
        "gamma": float(data.get("gamma", -0.05)),
        "altitude": float(data.get("altitude", 120000.0)),
        "mass": mass,
        "area": area,
        "drag_coeff": drag_coeff,
        "heat_of_ablation": float(data.get("heat_of_ablation", 1e7)),
        "dt": float(data.get("dt", 0.1)),
        "t_max": float(data.get("t_max", 1000.0)),
        "shape_factor": float(data.get("shape_factor", 1.0)),
        "initial_lat": float(data.get("initial_lat", 0.0)),
        "initial_lon": float(data.get("initial_lon", 0.0)),
        "lift_to_drag": lift_to_drag,
        "bank_angle_deg": float(data.get("bank_angle_deg", 0.0)),
        "initial_heading_deg": float(data.get("initial_heading_deg", 90.0))
    }

    # Auto de-orbit conditioning to keep simulation in realistic re-entry regime.
    # If object starts near orbital altitude with near-circular orbital speed,
    # enforce a minimum descending flight-path angle to avoid accidental skip-out.
    if entry_mode in ("auto", "reentry"):
        r0 = R_EARTH + max(params["altitude"], 0.0)
        v_circ = np.sqrt(MU_EARTH / r0)
        speed_ratio = params["velocity"] / v_circ if v_circ > 0 else 0.0
        near_orbital_case = params["altitude"] >= 150000.0 and 0.90 <= speed_ratio <= 1.15

        if near_orbital_case:
            gamma = params["gamma"]

            # Normalize sign convention: positive gamma means climb in this solver.
            if gamma > 0:
                gamma = -abs(gamma)

            # Prevent too-shallow entries that lead to frequent skip trajectories.
            gamma = min(gamma, -0.08)
            gamma = max(gamma, -0.30)
            params["gamma"] = gamma

            # Provide enough simulation horizon for high-altitude entries.
            params["t_max"] = max(params["t_max"], 6000.0)

            # Debris-like objects should default to ballistic unless user overrides L/D.
            if requested_ld is None and not (mass >= 1000.0 and area >= 1.5 and drag_coeff <= 1.6):
                params["lift_to_drag"] = 0.0
    
    # Run the Fortran computation
    try:
        res = ablation.trajectory.simulate(
            params["velocity"], 
            params["gamma"], 
            params["altitude"], 
            params["mass"], 
            params["area"], 
            params["drag_coeff"], 
            params["heat_of_ablation"], 
            params["dt"], 
            params["t_max"],
            params["shape_factor"],
            params["initial_lat"],
            params["initial_lon"],
            params["lift_to_drag"],
            params["bank_angle_deg"],
            params["initial_heading_deg"]
        )
        
        n_steps, time_out, h_out, v_out, m_out, q_out, g_out, lat_out, lon_out, mach_out = res
        
        # Trim arrays to actual computed steps
        return jsonify({
            "time": time_out[:n_steps].tolist(),
            "altitude": h_out[:n_steps].tolist(),
            "velocity": v_out[:n_steps].tolist(),
            "mass": m_out[:n_steps].tolist(),
            "heating_rate": q_out[:n_steps].tolist(),
            "g_force": g_out[:n_steps].tolist(),
            "latitude": lat_out[:n_steps].tolist(),
            "longitude": lon_out[:n_steps].tolist(),
            "mach": mach_out[:n_steps].tolist()
        })
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
