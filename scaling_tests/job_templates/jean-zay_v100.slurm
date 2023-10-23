#!/bin/sh
#SBATCH --account=een@v100          # obtained with idrproj
#SBATCH --constraint=v100-16g       # limit to 16GB nodes
#SBATCH --job-name={job_name}       # GENERATED
#SBATCH --nodes={n_nodes}            # GENERATED
#SBATCH --ntasks-per-node=4         # nombre de tache MPI par noeud (=nb de GPU)
#SBATCH --gres=gpu:4                # nombre de GPU par noeud
#SBATCH --cpus-per-task=10          # nombre de coeurs CPU par tache (un quart du noeud ici)

# /!\ Attention, "multithread" fait reference à l'hyperthreading dans la terminologie Slurm
#SBATCH --hint=nomultithread        # hyperthreading desactive
#SBATCH --time=00:10:00
#SBATCH --output=%j.out
#SBATCH --error=%j.err

set -euxo pipefail

module purge
module load cuda/12.1.0
module load gcc/12.2.0
module load openmpi/4.1.1-cuda
module load cmake/3.18.0

# Changement du dossier de scratch pour nvidia system (sinon pas assez d'espace disque)
export TMPDIR=$JOBSCRATCH
ln -s $JOBSCRATCH /tmp/nvidia

srun ./idefix -dec {decomposition}
