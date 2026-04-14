#!/bin/bash
# Script untuk mengompilasi Fortran sources yang kompleks
cd /home/tirr/project/re-entry/backend

# Bersihkan file modul pre-compiled lama (jika ada)
rm -f *.mod
rm -f ablation*.so

# Modul dipanggil berurutan dari dependensi terendah sampai tertinggi (trajectory paling terakhir)
# Ini adalah hal wajib di Fortran supaya module usage tersambung (Gunakan f2py)
echo "Mengompilasi Sub-Modules Fortran dengan F2PY..."
# Gunakan python environment jika ada, jika tidak revert ke python
PYTHON_BIN="python"
if [ -f "./venv/bin/python" ]; then
    PYTHON_BIN="./venv/bin/python"
    export PATH="$(pwd)/venv/bin:$PATH"
fi

$PYTHON_BIN -m numpy.f2py -c -m ablation fortran_src/constants.f90 fortran_src/atmosphere.f90 fortran_src/aerodynamics.f90 fortran_src/thermodynamics.f90 fortran_src/trajectory.f90


echo "Kompilasi Selesai! Modul 'ablation' berbentuk .so siap diimport."