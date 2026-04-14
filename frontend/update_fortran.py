import re

with open('/home/tirr/project/re-entry/backend/fortran_src/trajectory.f90', 'r') as f:
    code = f.read()

# Add Coriolis
coriolis_code = "lon = lon + (d_dist * sin(gamma)) / (R_EARTH * cos(lat)) - (7.2921159D-5 * dt)"
code = re.sub(r'lon = lon \+ \(d_dist \* sin\(gamma\)\) / \(R_EARTH \* cos\(lat\)\)', coriolis_code, code)

with open('/home/tirr/project/re-entry/backend/fortran_src/trajectory.f90', 'w') as f:
    f.write(code)

