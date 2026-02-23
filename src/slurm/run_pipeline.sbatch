#!/bin/bash
#SBATCH --job-name=cancerae_pipeline
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=24:00:00
#SBATCH --output=data/logs/slurm/%x_%j.out
#SBATCH --error=data/logs/slurm/%x_%j.err
##SBATCH --partition=<your_partition>
##SBATCH --account=<your_account>

set -euo pipefail

cd /uufs/chpc.utah.edu/common/home/u1025397/scratch/projects/CancerAE
mkdir -p data/logs/slurm

# Optional: activate environment later
# source .venv/bin/activate
# or: module load python/3.x

# Encourage threaded libraries to stay inside the Slurm CPU allocation
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export NUMEXPR_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}

bash src/run_all.sh
