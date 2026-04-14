from flask import Flask, request, jsonify
from flask_cors import CORS
import math

app = Flask(__name__)
CORS(app)

G0 = 9.80665
R_EARTH = 6371000.0
MU_EARTH = 3.986004418e14
R_AIR = 287.05
GAMMA_AIR = 1.4
K_SG = 1.74153e-4
PI = math.pi
OMEGA_EARTH = 7.2921159e-5
MIN_ALTITUDE = 0.0
MIN_MASS = 1.0e-3


def atmospheric_properties(h: float):
    hb = [0.0, 11000.0, 20000.0, 32000.0, 47000.0, 51000.0, 71000.0, 84852.0]
    tb = [288.15, 216.65, 216.65, 228.65, 270.65, 270.65, 214.65, 186.946]
    pb = [101325.0, 22632.06, 5474.889, 868.0187, 110.9063, 66.93887, 3.956420, 0.3734]
    lb = [-0.0065, 0.0, 0.0010, 0.0028, 0.0, -0.0028, -0.0020, 0.0]

    h = max(h, 0.0)
    h_geo = R_EARTH * h / (R_EARTH + h)

    if h_geo <= hb[-1]:
        i = 0
        while i < len(hb) - 1 and h_geo > hb[i + 1]:
            i += 1
        dh = h_geo - hb[i]
        if abs(lb[i]) > 1e-12:
            T = tb[i] + lb[i] * dh
            p = pb[i] * (tb[i] / T) ** (G0 / (R_AIR * lb[i]))
        else:
            T = tb[i]
            p = pb[i] * math.exp(-G0 * dh / (R_AIR * T))
        rho = p / (R_AIR * T)
    else:
        T = 186.946
        p = pb[-1] * math.exp(-(h_geo - hb[-1]) / 7500.0)
        rho84 = pb[-1] / (R_AIR * T)
        rho = rho84 * math.exp(-(h_geo - hb[-1]) / 7500.0)

    return max(rho, 1e-12), T, p


def dynamic_cd(mach: float, cd_base: float):
    if mach > 5.0:
        cd_dyn = cd_base
    elif mach > 1.2:
        cd_dyn = cd_base * (1.6 - 0.15 * (mach - 1.2))
    elif mach > 0.8:
        cd_dyn = cd_base * (1.0 + 1.5 * (mach - 0.8))
    else:
        cd_dyn = cd_base
    return max(cd_dyn, 0.05)


def auto_condition(params):
    r0 = R_EARTH + max(params["altitude"], 0.0)
    v_circ = math.sqrt(MU_EARTH / r0) if r0 > 0 else 0.0
    speed_ratio = params["velocity"] / v_circ if v_circ > 0 else 0.0
    near_orbital_case = params["altitude"] >= 150000.0 and 0.90 <= speed_ratio <= 1.15

    if near_orbital_case:
        gamma = params["gamma"]
        if gamma > 0:
            gamma = -abs(gamma)
        gamma = min(gamma, -0.08)
        gamma = max(gamma, -0.30)
        params["gamma"] = gamma
        params["t_max"] = max(params["t_max"], 6000.0)


def simulate_python(params):
    v = params["velocity"]
    gamma = params["gamma"]
    h = params["altitude"]
    m = params["mass"]
    area = params["area"]
    cd_base = params["drag_coeff"]
    q_star = params["heat_of_ablation"]
    dt = params["dt"]
    t_max = params["t_max"]
    shape_factor = params["shape_factor"]
    lat = math.radians(params["initial_lat"])
    lon = math.radians(params["initial_lon"])
    ld_ratio = max(params["lift_to_drag"], 0.0)
    bank_rad = math.radians(params["bank_angle_deg"])
    psi = math.radians(params["initial_heading_deg"])

    r_nose = math.sqrt(max(area, 1e-8) / PI) * max(shape_factor, 1e-3)
    max_steps = min(int(t_max / max(dt, 1e-4)), 100000)

    time_out, h_out, v_out, m_out = [], [], [], []
    q_out, g_out, lat_out, lon_out, mach_out = [], [], [], [], []

    t = 0.0
    step = 0
    while t <= t_max and h > MIN_ALTITUDE and m > MIN_MASS and step < max_steps:
        rho, T, _ = atmospheric_properties(h)
        a_sound = math.sqrt(GAMMA_AIR * R_AIR * T)
        mach = abs(v) / max(a_sound, 1e-6)

        cd_dyn = dynamic_cd(mach, cd_base)
        D = 0.5 * rho * (abs(v) ** 2) * cd_dyn * max(area, 0.0)
        L = ld_ratio * D

        q_dot = K_SG * math.sqrt(max(rho, 1e-12) / max(r_nose, 1e-3)) * (max(abs(v), 0.0) ** 3)
        m_dot = (q_dot * max(area, 0.0)) / q_star if q_star > 1.0 else 0.0

        aero_acc = math.sqrt(D * D + L * L) / max(m, MIN_MASS)
        g_force = aero_acc / G0

        time_out.append(t)
        h_out.append(h)
        v_out.append(v)
        m_out.append(m)
        q_out.append(q_dot)
        g_out.append(g_force)
        lat_out.append(math.degrees(lat))
        lon_out.append(math.degrees(lon))
        mach_out.append(mach)

        r_cur = R_EARTH + max(h, 0.0)
        g_local = G0 * (R_EARTH / r_cur) ** 2
        v_safe = max(abs(v), 1.0)
        cos_gamma_safe = max(abs(math.cos(gamma)), 1e-6)
        cos_lat_safe = max(abs(math.cos(lat)), 1e-6)

        v_dot = -(D / max(m, MIN_MASS)) - g_local * math.sin(gamma)
        gamma_dot = (L * math.cos(bank_rad)) / (max(m, MIN_MASS) * v_safe) + math.cos(gamma) * (v_safe / r_cur - g_local / v_safe)
        psi_dot = (L * math.sin(bank_rad)) / (max(m, MIN_MASS) * v_safe * cos_gamma_safe)
        h_dot = v_safe * math.sin(gamma)
        lat_dot = (v_safe * math.cos(gamma) * math.cos(psi)) / r_cur
        lon_dot = (v_safe * math.cos(gamma) * math.sin(psi)) / (r_cur * cos_lat_safe) - OMEGA_EARTH

        v = max(v + v_dot * dt, 0.0)
        gamma = gamma + gamma_dot * dt
        psi = psi + psi_dot * dt
        h = h + h_dot * dt
        lat = max(min(lat + lat_dot * dt, 0.5 * PI), -0.5 * PI)
        lon = lon + lon_dot * dt
        if lon > PI:
            lon -= 2.0 * PI
        if lon < -PI:
            lon += 2.0 * PI
        if psi > PI:
            psi -= 2.0 * PI
        if psi < -PI:
            psi += 2.0 * PI
        if h < MIN_ALTITUDE:
            h = MIN_ALTITUDE
        m = max(m - m_dot * dt, MIN_MASS)

        t += dt
        step += 1

    return {
        "time": time_out,
        "altitude": h_out,
        "velocity": v_out,
        "mass": m_out,
        "heating_rate": q_out,
        "g_force": g_out,
        "latitude": lat_out,
        "longitude": lon_out,
        "mach": mach_out,
        "engine": "python-fallback"
    }


@app.route("/api/simulate", methods=["POST", "OPTIONS"])
def simulate():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    data = request.get_json(silent=True) or {}

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
        "dt": max(float(data.get("dt", 0.1)), 1e-4),
        "t_max": float(data.get("t_max", 1000.0)),
        "shape_factor": float(data.get("shape_factor", 1.0)),
        "initial_lat": float(data.get("initial_lat", 0.0)),
        "initial_lon": float(data.get("initial_lon", 0.0)),
        "lift_to_drag": lift_to_drag,
        "bank_angle_deg": float(data.get("bank_angle_deg", 0.0)),
        "initial_heading_deg": float(data.get("initial_heading_deg", 90.0)),
    }

    if entry_mode in ("auto", "reentry"):
        auto_condition(params)

    result = simulate_python(params)
    return jsonify(result)
