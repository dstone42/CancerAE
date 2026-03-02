#!/bin/bash
#SBATCH --job-name=cancerae_pipeline
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=48G
#SBATCH --time=3:00:00
#SBATCH --output=data/logs/slurm/%x_%j.out
#SBATCH --error=data/logs/slurm/%x_%j.err
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=u1025397@utah.edu
##SBATCH --partition=notchpeak-freecycle
##SBATCH --qos=notchpeak-freecycle
##SBATCH --account=actan

#SBATCH --partition=kingspeak
#SBATCH --qos=kingspeak
#SBATCH --account=actan

set -euo pipefail

cd /uufs/chpc.utah.edu/common/home/u1025397/scratch/projects/CancerAE
mkdir -p data/logs/slurm

source ~/scratch/miniconda3/bin/activate

conda activate cancer-ae

# Encourage threaded libraries to stay inside the Slurm CPU allocation
export OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export OPENBLAS_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export MKL_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}
export NUMEXPR_NUM_THREADS=${SLURM_CPUS_PER_TASK:-1}

bash src/run_all.sh
