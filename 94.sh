#!/bin/bash

# Carrega o modulo
module load python/3.8.2

DIR=/scratch/cenapadrjsd/lucas.silva/rna-seq-ssd

SCRIPT=$DIR/alpha.py
BASE_GENOMICA=$DIR/inputs/mm9
PARALLEL=24
INPUTS=$DIR/94
OUTPUTS=$DIR/outputs94
GTF=$DIR/inputs/Mus_musculus.NCBIM37.67.gtf
CHDIR=$DIR/94
PARTITION=$1
JOBNAME=data-94

nohup python3 $SCRIPT $BASE_GENOMICA $PARALLEL $INPUTS $OUTPUTS $GTF $CHDIR $PARTITION $JOBNAME &
