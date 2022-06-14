#!/usr/bin/env python
import sys, os, parsl
from parsl import load, python_app, bash_app
from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_interface
from parsl.data_provider.data_manager import default_staging
from pathlib import Path

base = sys.argv[1]     # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/inputs/mm9
parallel = sys.argv[2] # 24
inputs = sys.argv[3]   # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/94
outputs = sys.argv[4]  # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/outputs94
gtf = sys.argv[5]      # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/inputs/Mus_musculus.NCBIM37.67.gtf
chdir = sys.argv[6]    # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/94
fila = sys.argv[7]     # nvidia_small
namejob = sys.argv[8]  # data-94

partition_queue = fila
total_time = '00:20:00'
nodes = 1
workers=24
over_rides='-c 24'
python='module load python/3.8.2\n'
bowtie='module load bowtie2/2.3\n'
sort='module load samtools/1.10_gnu\n'
picard='module load picard/2.18\n'
modules = python + bowtie + sort + picard
job_name='#SBATCH -J ' + namejob + '\n' + '#SBATCH --chdir=' + chdir + '\n'

config = Config(
    executors=[
        HighThroughputExecutor(
            address=address_by_interface('ib0'),#address_by_hostname(),
            label='htex',
            cores_per_worker=workers,
            max_workers=workers,
            provider=SlurmProvider(
                partition=partition_queue,
                nodes_per_block=nodes,
                cmd_timeout = 240,
                init_blocks=1,
                launcher=SrunLauncher(overrides=over_rides),
                max_blocks=1,
                min_blocks=1,
                parallelism=1,
                move_files=False,
                scheduler_options = job_name,
                walltime=total_time,
                worker_init=modules
            ),
        ),
    ],
)


load(config)

@bash_app
def ssd(ssd_outputs_dir, scratch_outs, inputs=[], outputs=[], stderr=None, stdout=None):
    #import os
    #os.makedirs(ssd_outputs_dir)
    #os.makedirs(scratch_outs)
    return 'mkdir -p {}; mkdir -p {}'.format(ssd_outputs_dir, scratch_outs)

@bash_app
def copy(arquivo, diretorio, inputs=[], outputs=[], stderr=None, stdout=None):
    return 'mkdir -p {} ; cp -r {} {}'.format(diretorio, arquivo, diretorio)

@bash_app
def bowtie(parallel, outfile, inputs=[], outputs=[], stderr=None, stdout=None):
    return 'bowtie2 -p {0} -x {1}/mm9 -U {2} -S {3}'.format(parallel, inputs[1], inputs[0], outfile)

@bash_app
def sort(parallel, sam_file, bam_file, inputs=[], outputs=[], stderr=None, stdout=None):
   return 'samtools sort -@ {0} -o {1} {2}'.format(parallel, bam_file, sam_file)

@bash_app
def split(sort_file, output_dir, split_to_n_files, prefix, inputs=[], outputs=[], stdout=None, stderr=None):
    import os
    os.mkdir(output_dir)
    return 'java -jar $PICARD SplitSamByNumberOfReads I={} OUTPUT={} SPLIT_TO_N_FILES={} CREATE_INDEX=true OUT_PREFIX={}'.format(sort_file, output_dir, split_to_n_files, prefix)

@bash_app
def htseq(gtf, diretorio, nprocesses, outfile, inputs=[], outputs=[], stderr=None):
    from pathlib import Path
    splited_files = list(Path(diretorio).glob('*.bam'))
    all_files = [str(i) for i in splited_files]
    bigstr = ' '.join(all_files)
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union --nprocesses={0} -c {1} {2} {3}'.format(nprocesses, outfile, bigstr, gtf)

@python_app
def merge(n_colummns, infile, outfile, inputs=[], outputs=[], stderr=None):

    import sys

    file_name_in = infile
    file_name_out = outfile
    n_colummns = int(n_colummns)

    HTSeq_file = open(file_name_in, "r")
    HTSeq_new_file = open(file_name_out, "w")

    n_colummns += 1

    for linha in HTSeq_file:
        soma = 0
        valores = linha.split()
        for i in range(1,n_colummns):
            soma = int(valores[i]) + soma
        a = valores[0] + '\t' + str(soma) + '\n'
        HTSeq_new_file.write(a)

    HTSeq_file.close()
    HTSeq_new_file.close()


# DIRETORIO SSD
ssd_dir = '/tmp/rna-seq_ssd/'
ssd_inputs_dir = ssd_dir + 'inputs_ssd/'
ssd_outputs_dir = ssd_dir + 'outputs_ssd'

p = Path(inputs)
fasta = list(p.glob('*.gz'))

bowtie_futures, sort_futures, split_futures, htseq_futures, merge_futures, ssd_futures, scratch_futures = [], [], [], [], [], [], []

fastq_list = list()
ssdfuture = ssd(ssd_outputs_dir, outputs)

# COPY GTF
gtf_future = copy( gtf, ssd_inputs_dir, inputs = [ ssdfuture, gtf ] )

sam_list = list()

# BOWTIE
for j in fasta:
    prefix = Path(Path(j).stem).stem                    # SRR5445797
    outfile = ssd_outputs_dir + '/' + prefix + '.sam'
    sam_list.append(outfile)                            # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sam
    bowtie_futures.append( bowtie( parallel, outfile, inputs=[j, base, ssdfuture] ) )

picard_list = list()

# SORT
for k, v in zip(bowtie_futures, sam_list):
    ssd_sam = v                                                                 # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sam
    prefix = Path(ssd_sam).stem                                                 # SRR5445797.sam -> SRR5445797
    outfile = str(Path(ssd_sam).parent) + '/' + prefix + '.sort.bam'            # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sort.bam
    picard_list.append(outfile)                                                 # /tmp/rna-seq_ssd/outputs_ssd/SRR5445796.sort.bam
    sort_futures.append( sort( parallel, ssd_sam, outfile, inputs=[ k ] ) )

dir_splited = list()

#PICARD
for l, t in zip(sort_futures, picard_list):
    ssd_bam = t                                                     # /tmp/rna-seq_ssd_outputs_ssd/SRR5445797.sort.bam
    prefix = Path(Path(ssd_bam).stem).stem                          # SRR5445797
    split_files_dir = ssd_outputs_dir + '/' + prefix + '_splitted/' # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797_splited/
    dir_splited.append(split_files_dir)
    split_futures.append( split( ssd_bam, split_files_dir, parallel, prefix, inputs = [ l ] ) )

htseq_list = list()

# HTSEQ
for n, a in zip(split_futures, dir_splited):
    copy_gtf = ssd_inputs_dir + Path(gtf).name
    diretorio = a
    prefix = Path(diretorio).name.split('_')[0]
    saida_htseq = ssd_outputs_dir + '/' + prefix + '.count' # '{}/{}.count'.format(dir_outputs, prefix)
    htseq_list.append(saida_htseq)
    htseq_futures.append( htseq( copy_gtf, diretorio, parallel, saida_htseq, inputs=[ n, gtf_future ] ) )

merge_list = list()

# HTSEQ-MERGE
for o, s in zip(htseq_futures, htseq_list):
    ssd_count = s
    prefix = Path(ssd_count).stem
    output_merge = outputs + '/' + prefix + '.merge.count'
    merge_list.append(output_merge)
    merge_futures.append( merge(parallel, ssd_count, output_merge, inputs=[o] ) )

# Waiting for all apps to proceed with the execution of the last activity (DESeq)
[q.result() for q in merge_futures]
