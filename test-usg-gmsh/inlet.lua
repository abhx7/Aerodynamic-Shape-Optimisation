-- cone20.lua
-- Unstructured Grid Example -- for use with Eilmer4
-- PJ & RG
-- 2015-11-08 -- adapted from cone20-simple

job_title = "Scramjet Inlet"
print(job_title)

-- We can set individual attributes of the global data object.
config.dimensions = 2
config.title = job_title
config.axisymmetric = true

p_inf = 701.4 -- Pa
u_inf = 1221.8 -- m/s
T_inf = 67.85 -- degree K

nsp, nmodes, gm = setGasModel('ideal-air-gas-model.lua')
print("GasModel set to ideal air. nsp= ", nsp, " nmodes= ", nmodes)
initial = FlowState:new{p=p_inf, T=T_inf}
inflow = FlowState:new{p=p_inf, velx=u_inf, T=T_inf}


-- Demo: Verify Mach number of inflow.
Q = GasState:new{gm}
Q.p = 701.4 
Q.T = 67.85
print("T", Q.T)
Q.massf = {air=1.0}
gm:updateSoundSpeed(Q)
print("Sound speed= ", Q.a)
print("Inflow Mach number= ", 1000.0/Q.a)

-- Define the flow domain using an imported grid.
grid0 = UnstructuredGrid:new{filename="inlet.su2", fmt="su2text",scale=1}
--[[nblocks=8
grids={}
for i=0,nblocks-1 do
        fileName = string.format("su2_grids/block_%d_inlet.su2", i)
        grids[i] = UnstructuredGrid:new{filename=fileName, fmt="su2text", scale=1}
end]]--

-- FluidBlock:new
boundary_conditions = { outlet=OutFlowBC_Simple:new{},
                        body=WallBC_NoSlip_FixedT:new{Twall=300.0, group="body"},
                        inlet=InFlowBC_Supersonic:new{flowCondition=inflow},
                        top=WallBC_WithSlip:new{},
                        invis=WallBC_WithSlip:new{},
                        METIS_INTERIOR = ExchangeBC_MappedCell:new{cell_mapping_from_file=true,
                        list_mapped_cells=false}
                       }
                                 
blks = {}
--[[for i=0,nblocks-1 do
        blks[i] = FluidBlock:new{grid=grids[i], bcList=boundary_conditions, bcDict=boundary_conditions, fillCondition=inflow}
end]]--
blks[0] = FluidBlock:new{grid=grid0, bcList=boundary_conditions, bcDict=boundary_conditions, fillCondition=inflow}
 
--identifyBlockConnections() --what is this for?

---- loads settings --causes error
--config.boundary_groups_for_loads = "body"
--config.write_loads = true

--convective flux settings
config.interpolation_order = 2
config.flux_calculator = "ausmdv"
config.freeze_limiter_on_step = 4000

config.extrema_clipping = false
config.apply_limiter = true
config.unstructured_limiter = "venkat"
config.smooth_limiter_coeff = 0.5  --config.venkat_K_value = 0.5
config.thermo_interpolator = "rhop"

-- viscous flux settings
config.viscous = true
config.spatial_deriv_locn = "cells"
config.spatial_deriv_calc = "least_squares"
config.diffuse_wall_bcs_on_init = false
config.number_init_passes = 25


-- output settings
config.print_count = 50

SteadyStateSolver{
   use_preconditioner = true,
   precondition_matrix_type = "ilu",
   ilu_fill = 0,
   frozen_preconditioner_count = 20,
   
   use_scaling = true,
   use_complex_matvec_eval = true,
   use_physicality_check = true,
   
   number_total_steps = 50000,
   stop_on_relative_global_residual = 1.0e-12,

   -- Settings for FGMRES iterative solver
   max_outer_iterations = 80,
   max_restarts = 4,

   residual_based_cfl_scheduling = true,
   cfl_max = 1e4,

   -- Settings for start-up phase
   number_start_up_steps = 100,
   cfl0 = 0.5,
   eta0 = 0.01,
   sigma0 = 1.0e-50,

   -- Settings for inexact Newton phase
   cfl1 = 1.0,
   sigma1 = 1.0e-50,
   eta1 = 0.01,
   tau1 = 0.5,
   p1 = 0.7,

   -- Settings control write-out
   snapshots_count = 50,
   number_total_snapshots = 10,
   write_diagnostics_count = 20,
   write_loads_count = 20,
}

