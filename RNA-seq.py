#!/usr/bin/env python
import sys, os, parsl
from parsl import load, python_app, bash_app
#from configs.config_ThreadPool import config
from configs.config_HTEx import config
from parsl.data_provider.files import File
from pathlib import Path

load(config)

@bash_app
def bowtie(p, base, infile, outputs=[], stderr=None):
    return 'bowtie2 -p {0} -x {1} -U {2} -S {3}'.format(p, base, infile, outputs[0])

@bash_app
def sort(multithread, inputs=[], outputs=[], stderr=None):
   return 'samtools sort -@ {} -o {} {}'.format(multithread, outputs[0], inputs[0])

@bash_app
def picard_split(picard_path, infile, output_dir, split_n_files, prefix, inputs=[], outputs=[], stdout=None, stderr=None):
    import os
    os.mkdir(output_dir)
    return 'java -jar {} SplitSamByNumberOfReads I={} OUTPUT={} SPLIT_TO_N_FILES={} CREATE_INDEX=true OUT_PREFIX={}'.format(picard_path, infile, output_dir, split_n_files, prefix)

@bash_app
def htSeq_count(gtf, diretorio, n_splited_files, inputs=[], outputs=[], stderr=None):
    from pathlib import Path
    splited_files = list(Path(diretorio).glob('*.bam'))
    all_files = [str(i) for i in splited_files]
    bigstr = ' '.join(all_files)
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union --nprocesses={0} -c {1} {2} {3}'.format(n_splited_files, outputs[0], bigstr, gtf)

@bash_app
def HTSeq_Merge(merge_path, n_colummns, inputs=[], outputs=[], stderr=None):
    return 'python3 {0} {1} {2}'.format(merge_path, inputs[0], outputs[0], n_colummns)

@bash_app
def DESeq(scriptR, pathInputs, inputs=[], outputs=[], stdout = None, stderr=None):
    return '{0} {1}'.format(scriptR, pathInputs)

base_bowtie = sys.argv[1]
multithread = sys.argv[2]
inputs_bowtie = sys.argv[3]
dir_outputs = sys.argv[4]
gtf = sys.argv[5]
script_DESeq2 = sys.argv[6]
picard_path_file = sys.argv[7]
merge_path = sys.argv[8]

p = Path(inputs_bowtie)
fasta = list(p.glob('*'))

bow_apps, sort_apps, split_apps, htseq_apps, merge_apps = [], [], [], [], []

# BOWTIE
for i in fasta:
    prefix = Path(Path(i).stem).stem
    output_bowtie = '{}/{}.sam'.format(dir_outputs, prefix)
    stderr_bowtie = '{}/stderr/{}.bowtie'.format(dir_outputs, prefix)
    infile = str(i)
    bow_apps.append(bowtie(multithread, base_bowtie, infile, outputs=[File(output_bowtie)], stderr=stderr_bowtie))

# SORT
for k in bow_apps:
    prefix = Path(k.outputs[0].filename).stem
    output_sort = '{}/{}.sort.bam'.format(dir_outputs, prefix)
    stderr_sort = '{}/stderr/{}.sort'.format(dir_outputs, prefix)
    sort_apps.append(sort(multithread, inputs=[k.outputs[0]], outputs=[File(output_sort)], stderr=stderr_sort))

dir_splited = list()

# PICARD
for p in sort_apps:
    prefix = str(Path(Path(p.outputs[0].filename).stem).stem)
    split_files_dir = '{}/{}_splited/'.format(dir_outputs, prefix)
    dir_splited.append(split_files_dir)
    stderr_split = '{}/stderr/{}.picard'.format(dir_outputs, prefix)
    split_apps.append(picard_split(picard_path_file, p.outputs[0], split_files_dir, multithread, prefix, stderr=stderr_split))

dir_splited.reverse()

# HTSeq
for l in split_apps:
    diretorio = dir_splited.pop()
    prefix = Path(diretorio).name.split('_')[0]
    saida_htseq = '{}/{}.count'.format(dir_outputs, prefix)
    stderr_htseq = '{}/stderr/{}.htseq_count'.format(dir_outputs, prefix)
    htseq_apps.append(htSeq_count(gtf, diretorio, multithread, inputs=[l], outputs=[File(saida_htseq)], stderr = stderr_htseq))

# HTSeq-Merge
for m in htseq_apps:
    prefix = Path(m.outputs[0].filename).stem
    output_merge = '{}/{}.merge.count'.format(dir_outputs, prefix)
    stderr_merge = '{}/stderr/{}.merge_htseq'.format(dir_outputs, prefix)
    merge_apps.append(HTSeq_Merge(merge_path, inputs=[m.outputs[0]], outputs=[File(output_merge)], multithread, stderr = stderr_merge))

[j.result() for j in merge_apps]

# DESeq
saida_DEseq = '{}/teste.deseq'.format(dir_outputs)
stderr_DESeq = '{}/stderr/all.deseq'.format(dir_outputs)
teste = DESeq(File(script_DESeq2), dir_outputs, stdout=saida_DEseq, stderr = stderr_DESeq)
teste.result()
