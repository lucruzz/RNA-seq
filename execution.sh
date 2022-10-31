#!/bin/bash

module load python/3.8.2

DIR=$(pwd)

SCRIPT_PYTHON=$DIR/rna-seq.py
BASE_GENOMICA=$DIR/mm9/mm9
MULTITHREAD=24
INPUTS=$DIR/inputs
OUTPUTS=$DIR/outputs
GTF=$DIR/Mus_musculus.NCBIM37.67.gtf
DESEQ=$DIR/DESeq.R

if [ -d $OUTPUTS ]; then
        rm -r $OUTPUTS
fi

time nohup python3 $SCRIPT_PYTHON $BASE_GENOMICA $MULTITHREAD $INPUTS $OUTPUTS $GTF $DESEQ &
