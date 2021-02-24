#!/usr/bin/env python
import sys, os, parsl
from parsl import load, python_app, bash_app
from configs.config_HTEx import config
from parsl.data_provider.files import File
from pathlib import Path

load(config)

@bash_app
def bowtie(p, base, infile, outputs=[], stderr=None):
    return 'bowtie2 -p {0} -x {1} -U {2} -S {3}'.format(p, base, infile, outputs[0])

@bash_app
def htSeq_count(gtf, inputs=[], outputs=[], stderr=None):
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union --nprocesses=24 {0} {1} > {2}'.format(inputs[0], gtf, outputs[0])

@bash_app
def DESeq(inputs=[], outputs=[], stdout = None):
    return '{0} {1}'.format(inputs[0], outputs[0])

base_bowtie, multithread_bowtie, inputs_bowtie, saida, gtf, exc_dseq2 = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]

p = Path(inputs_bowtie).parent
pattern = str(Path(inputs_bowtie).name)+'*'
fasta = list(p.glob(pattern))

output = str(Path(saida))

stop, bow_files = [], []

for i in fasta:
    prefix = str(Path(i).stem)
    saida_bowtie = output + '/' + prefix + '.sam'
    outfile = saida_bowtie
    infile = str(i)
    bow_files.append(bowtie(multithread_bowtie, base_bowtie, infile, outputs=[File(outfile)], stderr='./outputs2/stderr/{}.bowtie'.format(prefix)))

for i in bow_files:
    prefix = str(Path(i.outputs[0].filename).stem)
    saida_htseq = output + '/' + prefix
    stderr_htseq = './outputs2/stderr/' + prefix + '.htseq_count'
    exc = htSeq_count(gtf, inputs=[i.outputs[0]], outputs=[File(saida_htseq)], stderr = stderr_htseq)
    stop.append(exc)
[j.result() for j in stop]

saida_DEseq = output + '/teste.deseq'
teste = DESeq(inputs = [File(exc_dseq2)], outputs=[File(output)], stdout=saida_DEseq)
teste.result()
