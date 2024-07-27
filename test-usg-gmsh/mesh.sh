cd su2_grids
rm block*.su2
ugrid_partition ../inlet.su2 mapped_cells 8 2
mv mapped_cells ../
cd ../
