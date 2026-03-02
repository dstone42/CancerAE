#!/bin/bash
#SBATCH --job-name=cancerae_check
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=data/logs/slurm/%x_%j.out
#SBATCH --error=data/logs/slurm/%x_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=u1025397@utah.edu
##SBATCH --partition=<your_partition>
##SBATCH --account=<your_account>

set -euo pipefail

cd /uufs/chpc.utah.edu/common/home/u1025397/scratch/projects/CancerAE
mkdir -p data/logs/slurm

# Exit code contract from download_FAERS.sh:
#   0  -> new data appears available
#   10 -> no new data
if bash src/prep/download_FAERS.sh --check-only; then
    echo "New data detected. Submitting full pipeline job..."
    sbatch src/slurm/run_pipeline.sbatch
else
    status=$?
    if [ "$status" -eq 10 ]; then
        echo "No new FAERS data. Nothing submitted."
        exit 0
    fi

    echo "Update check failed with status $status"
    exit "$status"
fi
