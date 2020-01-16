import os

files = sorted([
          'xac', 'xaf', 'xai', 'xal', 'xao', 'xar', 'xau', 'xax', 'xba', 'xbd', 'xbg', 'xbj', 'xbm', 'xbp', 'xbs',
          'xbv', 'xby', 'xcb', 'xce', 'xch', 'xck', 'xcn', 'xcq', 'xct', 'xcw', 'xcz', 'xdc', 'xdf', 'xdi', 'xdl',
          'xdo', 'xdr', 'xdu', 'xaa', 'xad', 'xag', 'xaj', 'xam', 'xap', 'xas', 'xav', 'xay', 'xbb', 'xbe', 'xbh',
          'xbk', 'xbn', 'xbq', 'xbt', 'xbw', 'xbz', 'xcc', 'xcf', 'xci', 'xcl', 'xco', 'xcr', 'xcu', 'xcx', 'xda',
          'xdd', 'xdg', 'xdj', 'xdm', 'xdp', 'xds', 'xab', 'xae', 'xah', 'xak', 'xan', 'xaq', 'xat', 'xaw', 'xaz',
          'xbc', 'xbf', 'xbi', 'xbl', 'xbo', 'xbr', 'xbu', 'xbx', 'xca', 'xcd', 'xcg', 'xcj', 'xcm', 'xcp', 'xcs',
          'xcv', 'xcy', 'xdb', 'xde', 'xdh', 'xdk', 'xdn', 'xdq', 'xdt']
)


def create_script(file):
    return f'''#!/bin/bash
#SBATCH --job-name={file}
#SBATCH --workdir=/gpfs/scratch/bsc88/bsc88251/PubMedTranslate/final
#SBATCH --output=/gpfs/home/bsc88/bsc88251/PubMedTranslate/final/{file}.log
#SBATCH --error=/gpfs/home/bsc88/bsc88251/PubMedTranslate/final/{file}.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40
#SBATCH --time=20:00:00
#SBATCH --gres=gpu:1

module load ffmpeg/4.0.2
module load cuda/9.1
module load cudnn/7.1.3 atlas/3.10.3 scalapack/2.0.2 fftw/3.3.7 szip/2.1.1 opencv/3.4.1
module load python/3.6.5_ML

export omp_num_threads=40


source /gpfs/projects/bsc88/Environments_P9/OpenNMT-tf/bin/activate


python3 /gpfs/projects/bsc88/_old/ExternalTools/OpenNMT-py/translate.py -gpu 0 -model /gpfs/projects/bsc88/_old/Resources/NMT_WMT19/pten_es_model.pt \
-src /gpfs/scratch/bsc88/bsc88251/PubMedTranslate/final/{file} -replace_unk \
-output /gpfs/scratch/bsc88/bsc88251/PubMedTranslate/final/{file}.translated -batch_size 60'''


def main():
    for file in files:
        script = create_script(file)
        with open(os.path.join('scripts', file + '.sh'), 'w') as f:
            f.write(script)


if __name__ == '__main__':
    main()
