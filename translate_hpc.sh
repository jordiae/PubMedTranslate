#!/bin/bash
#SBATCH --job-name=back_enpt
#SBATCH --workdir=/gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/BackTranslation
#SBATCH --output=/gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/BackTranslation/PT.out
#SBATCH --error=/gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/BackTranslation/PT.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --time=2-00:00:00
#SBATCH --qos=bsc_ls
#SBATCH --gres=gpu:1

module load cuda/9.1
module load cudnn/7.1.3 atlas/3.10.3 scalapack/2.0.2 fftw/3.3.7 szip/2.1.1 opencv/3.4.1
module load python/3.6.5_ML

export omp_num_threads=40


source /gpfs/projects/bsc88/Environments_P9/OpenNMT-tf/bin/activate


python3 /gpfs/projects/bsc88/Tools/OpenNMT-py/translate.py -gpu 0 -model /gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/model_big_step_330000.pt \
-src /gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/BackTranslation/xaa -replace_unk \
-output /gpfs/scratch/bsc88/bsc88260/WMT_2018_BSC/ENES_PT_PY/BackTranslation/xaa.pt -batch_size 20 &

