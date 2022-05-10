#!/usr/bin/env python
import sys, os, parsl
from parsl import load, python_app, bash_app
from configs.config_HTEx import config
#from configs.config_ThreadPool import config
from parsl.data_provider.files import File
from pathlib import Path

load(config)

@bash_app
def ssd(ssd_dir, ssd_inputs_dir, ssd_outputs_dir, inputs=[], outputs=[], stderr=None):
    create_directories = 'mkdir {0} ; mkdir {1} ; mkdir {2} ;'.format(ssd_dir, ssd_inputs_dir, ssd_outputs_dir)
    open_directory = create_directories + 'cd {} ;'.format(ssd_dir) 
    command = open_directory +  'cp {} {} -r ; cp {} {} ; cp {} {} ;'
    return command.format( inputs[0], outputs[0], inputs[1], outputs[1], inputs[2], outputs[2])

#@python_app
#def ssd2(ssd_inputs_dir, ssd_outputs_dir, entrada):
#    import shutil    
#    shutil.copytree(entrada, ssd_inputs_dir)

@bash_app
def bowtie(parallel, inputs=[], outputs=[], stderr=None, stdout=None):
    return 'bowtie2 -p {0} -x {1}/mm9 -U {2} -S {3}'.format(parallel, inputs[0], inputs[1], outputs[0])

@bash_app
def sort(parallel, inputs=[], outputs=[], stderr=None):
   return 'samtools sort -@ {0} -o {1} {2}'.format(parallel, outputs[0], inputs[0])

@bash_app
def split_picard(output_dir, split_to_n_files, prefix, inputs=[], outputs=[],stdout=None, stderr=None):
    import os
    os.mkdir(output_dir)
    return 'java -jar $PICARD SplitSamByNumberOfReads I={} OUTPUT={} SPLIT_TO_N_FILES={} CREATE_INDEX=true OUT_PREFIX={}'.format(inputs[0], output_dir, split_to_n_files, prefix)

@bash_app
def htseq_count(gtf, diretorio, nprocesses, inputs=[], outputs=[], stderr=None):
    from pathlib import Path
    splited_files = list(Path(diretorio).glob('*.bam'))
    all_files = [str(i) for i in splited_files]
    bigstr = ' '.join(all_files)
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union --nprocesses={0} -c {1} {2} {3}'.format(nprocesses, outputs[0], bigstr, gtf)

@python_app
def htseq_merge(n_colummns, inputs=[], outputs=[], stderr=None):

    import sys

    file_name_in = inputs[0]
    file_name_out = outputs[0]
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

@bash_app
def scratch(directory, inputs=[], outputs=[], stderr=None):
    import os
    os.mkdir(directory)
    return 'cp {} {}'.format(inputs[0], outputs[0])


@bash_app
def deseq2(scriptR, pathInputs, stdout = None, stderr=None):
    return '{0} {1}'.format(scriptR, pathInputs)


base = sys.argv[1]          # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/inputs/mm9/mm9
parallel = sys.argv[2]      # 24
inputs = sys.argv[3]        # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/inputs
outputs = sys.argv[4]       # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/outputs
gtf = sys.argv[5]           # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/inputs/Mus_musculus.NCBIM37.67.gtf
script_deseq2 = sys.argv[6] # /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/DESeq.R

# DIRETORIO SSD
ssd_dir = '/tmp/rna-seq_ssd/'
ssd_inputs_dir = ssd_dir + 'inputs_ssd/'
ssd_outputs_dir = ssd_dir + 'outputs_ssd'

p = Path(inputs)
fasta = list(p.glob('*.gz'))

bowtie_futures, sort_futures, split_futures, htseq_futures, merge_futures, ssd_futures, scratch_futures = [], [], [], [], [], [], []

print(fasta)

# COPY INDIVIDUAL FILES TO EACH NODE
for i in fasta:
    copy_base = ssd_inputs_dir + Path(base).stem
    copy_gtf = ssd_inputs_dir + Path(gtf).name
    copy_input = ssd_inputs_dir + i.name # SRR5445797.fastq.gz
    print(copy_base, copy_gtf, copy_input)
    print(base, gtf, str(i))
    infile = str(i)
    ssd_futures.append(ssd( ssd_dir, 
                            ssd_inputs_dir, 
                            ssd_outputs_dir, 
                            inputs = [ File(base), File(gtf), File(infile) ], 
                            outputs=[ File(copy_base), File(copy_gtf), File(copy_input) ] ) )

# [k.result() for k in ssd_futures]

# BOWTIE
for j in ssd_futures:
    ssd_base = j.outputs[0].filepath + '/mm9' # /tmp/rna-seq_ssd/inputs_ssd/mm9
    ssd_gtf = j.outputs[1].filepath           # /tmp/rna-seq_ssd/inputs_ssd/Mus_musculus.NCBIM37.67.gtf
    ssd_fastq = j.outputs[2].filepath         # /tmp/rna-seq_ssd/inputs_ssd/SRR5445797.fastq.gz
    
    prefix = Path(Path(j.outputs[2].filename).stem).stem # SRR5445797.fastq.gz -> SRR5445797
    outfile = str(Path(j.outputs[2].filepath).parent.parent) + '/outputs_ssd/' + prefix + '.sam' # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sam
    print('OUTPUT: ' + outfile)
    bowtie_futures.append( bowtie( parallel, inputs=[j.outputs[0], j.outputs[2]], outputs=[File(outfile)] ) )

# [k.result() for k in bowtie_futures]

# SORT
for k in bowtie_futures:
    print('SORT: ' + k.outputs[0].filepath)
    ssd_sam = k.outputs[0].filepath           # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sam

    prefix = Path(k.outputs[0].filepath).stem # SRR5445797.sam -> SRR5445797
    outfile = str(Path(k.outputs[0].filepath).parent) + '/' + prefix + '.sort.bam'
    print('OUTPUT: ' + outfile)               # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.sort.bam
    sort_futures.append( sort( parallel, inputs=[ k.outputs[0] ], outputs=[File(outfile)] ) )

# [l.result() for l in sort_futures]

dir_splited = list()

#PICARD
for l in sort_futures:
    print('SPLIT_PICARD: ' + l.outputs[0].filepath)                 # /tmp/rna-seq_ssd_outputs_ssd/SRR5445797.sort.bam
    prefix = Path(Path(l.outputs[0].filename).stem).stem            # SRR5445797
    split_files_dir = ssd_outputs_dir + '/' + prefix + '_splitted/' # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797_splited/
    print(split_files_dir)
    dir_splited.append(split_files_dir)

    files = list()
    for i in range(24):
        base = '000'
        if i < 9:
            files.append(split_files_dir + prefix + '_' + base + str(i+1) + '.bam')
        if i >= 9:
            files.append(split_files_dir + prefix + '_' + base[1:] + str(i+1) + '.bam')

    print(files)
    split_futures.append(split_picard( split_files_dir, 
                                       parallel, 
                                       prefix, 
                                       inputs=[l.outputs[0]], 
                                       outputs=[File(files[0]),File(files[1]), File(files[2]), File(files[3]), File(files[4]), File(files[5]), 
                                                File(files[6]),File(files[7]), File(files[8]), File(files[9]), File(files[10]), File(files[11]), 
                                                File(files[12]),File(files[13]), File(files[14]), File(files[15]), File(files[16]), File(files[17]), 
                                                File(files[18]),File(files[19]), File(files[20]), File(files[21]), File(files[22]), File(files[23])] ) )

# [k.result() for k in split_futures]

dir_splited.reverse()

# HTSEQ
for m in split_futures:
    diretorio = dir_splited.pop()
    prefix = Path(diretorio).name.split('_')[0]
    outfile = '{}/{}.count'.format(ssd_outputs_dir, prefix)
    ssd_gtf = '{}{}'.format(ssd_inputs_dir, Path(gtf).name) 
    print('OUTPUT: ' + outfile)  # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.count
    print('GTF: ' + ssd_gtf)     # /tmp/rna-seq_ssd/inputs_ssd/Mus_musculus.NCBIM37.67.gtf
    htseq_futures.append( htseq_count( ssd_gtf, diretorio, parallel, inputs=[m], outputs=[File(outfile)] ) )
    

# HTSEQ-MERGE
for n in htseq_futures:
    prefix = Path(n.outputs[0].filename).stem
    outfile = '{}/{}.merge.count'.format(ssd_outputs_dir, prefix)
    print('OUTPUT: ' + outfile)  # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797.merge.count
    merge_futures.append( htseq_merge( parallel, inputs=[n.outputs[0]], outputs=[File(outfile)] ) )

# Saída no scratch
# Caminho: /scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/ssd-outputs
out = '/scratch/cenapadrjsd/lucas.silva/rna-seq-ssd/ssd-outputs'

for p in merge_futures:
    print('OUTPUT: ' + str(p.outputs[0].filepath)) # /tmp/rna-seq_ssd/outputs_ssd/SRR5445797_splited.sort.bam
    filename = Path(p.outputs[0].filepath).name
    outfile = '{}/{}'.format(out, filename)
    print('SCRATCH: ' + outfile)
    scratch_futures.append( scratch( out, inputs=[ p.outputs[0] ], outputs=[ File(outfile)]) )


# Waiting for all apps to proceed with the execution of the last activity (DESeq)
[q.result() for q in scratch_futures]

# DESEQ2
#saida_DEseq = '{}/teste.deseq'.format(out)
#deseq_future = deseq2(File(script_deseq2), out, stdout=saida_DEseq)
#deseq_future.result()
