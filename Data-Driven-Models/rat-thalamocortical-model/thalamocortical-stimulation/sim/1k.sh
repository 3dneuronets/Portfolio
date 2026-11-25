#!/bin/bash

#SBATCH --job-name=v7_batch7_0_0
#SBATCH -A TG-IBN140002
#SBATCH -t 4:00:00
#SBATCH --nodes=8
#SBATCH --ntasks-per-node=128
#SBATCH -o ../data/v7_batch7/v7_batch7_0_0.run
#SBATCH -e ../data/v7_batch7/v7_batch7_0_0.err
#SBATCH --mail-user=fernandodasilvaborges@gmail.com
#SBATCH --mail-type=end

#SBATCH --mem=240G
#SBATCH --export=ALL
#SBATCH --partition=compute

source ~/.bashrc
cd /home/fborges/Thalamocortical_model/sim/
mpirun -n 1024 nrniv -python -mpi init.py simConfig=../data/v7_batch7/v7_batch7_0_0_cfg.json netParams=../data/v7_batch7/v7_batch7_netParams.py
mpirun -n 1024 nrniv -python -mpi init.py simConfig=../data/v7_batch7/v7_batch7_0_0_cfg.json netParams=../data/v7_batch7/v7_batch7_netParams.py
wait
