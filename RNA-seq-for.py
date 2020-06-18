#!/usr/bin/env python
import sys
import os
from parsl import load, python_app, bash_app
from parsl.configs.local_threads import config
from parsl.data_provider.files import File
from pathlib import Path
load(config)

@bash_app
def bowtie(p, baseGenomica, inputs, stdout=None):
    return 'bowtie2 -p {0} -x {1} -U {2}'.format(p, baseGenomica, inputs)

@bash_app
def htSeq_count(saida, gtf, stdout=None):
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union  {0} {1}'.format(saida, gtf)

@bash_app
def DEseq(dseq2, saida, stdout=None):
    return '{0} {1}'.format(dseq2, saida)

# Parâmetros bowtie2
base_bowtie, inputs_bowtie, saida = sys.argv[1], sys.argv[2], sys.argv[3]

p = Path(inputs_bowtie)
fasta = list(p.glob('*.gz'))
output = Path(saida)

# Parâmetros htSeq-count
gtf = sys.argv[4]

# Parâmetros DEseq
exc_dseq2 = sys.argv[5]

for i in fasta:
    prefix = Path(i).stem
    saida_bowtie = os.path.join(output, prefix+'.sam')
    exec_bowtie = bowtie(1, Path(base_bowtie).resolve(), i, stdout=saida_bowtie)
    exec_bowtie.result()

    prefix = Path(saida_bowtie).stem
    saida_htseq = os.path.join(output, prefix+'.counts')
    exec_htseq = htSeq_count(saida_bowtie, Path(gtf).resolve(), stdout=saida_htseq)
    exec_htseq.result()

saida_DEseq = os.path.join(output, 'teste.deseq')
teste = DEseq(Path(exc_dseq2).resolve(), output, stdout=saida_DEseq)
teste.result()
