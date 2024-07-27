#!/bin/bash
# run.sh
prep-gas ideal-air.inp ideal-air-gas-model.lua

#mkdir su2_grids
#. mesh.sh

e4shared --prep --job=inlet
#e4shared --run --job=inlet --verbosity=1 --max-cpus=16 --report-residuals 
e4-nk-shared --job=inlet --verbosity=1 --max-cpus=16  
#mpirun -np 8  e4-nk-dist --snapshot-start=last --job=inlet | tee -a 'log.txt'
e4shared --post --job=inlet --tindx-plot=all --vtk-xml --add-vars="mach,pitot,total-p,total-h" 

