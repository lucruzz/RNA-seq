#!/usr/bin/env python
import sys
import os
from parsl import load, python_app, bash_app
from configs.config import config
from pathlib import Path

load(config)

@bash_app
def bowtie(p, baseGenomica, inputs, stdout=None):
    return 'bowtie2 -p {0} -x {1} -U {2}'.format(p, baseGenomica, inputs)

@bash_app
def htSeq_count(saida, gtf, stdout=None):
    return 'htseq-count --stranded reverse --type=exon --idattr=gene_id --mode=union  {0} {1}'.format(saida, gtf)

# Cleaning head lines of counts files obtained with htseq-count
# @bahs_app
# def grep(file, stdout):
#     return 'grep -vwE "processed" {} > {}'.format(file, stdout)

@bash_app
def DEseq(dseq2, saida, stdout=None):
    return '{0} {1}'.format(dseq2, saida)

# PARÂMETROS DA ATIVIDADE BOWTIE
base_bowtie = sys.argv[1]           # Caminho da base genômica
multithread_bowtie = sys.argv[2]    # Parâmetro multithread da atividade bowtie
inputs_bowtie = sys.argv[3]         # Caminho do diretório dos arquivos de entrada (fastaq)
saida = sys.argv[4]                 # Caminho do diretório de saída onde todos os arquivos gerados por cada atividade do workflow serão inseridos

# "VERIFICAÇÃO" DOS ARQUIVOS DE ENTRADA
p = Path(inputs_bowtie).parent                  # ("./a/b/c").parent -> (".a/b")
pattern = str(Path(inputs_bowtie).name)+'*'     # pega o ultimo componente do caminho (padrão) e inclui o '*'. Ex.: ("a/b/c").name + '*'-> "c*"
fasta = list(p.glob(pattern))                   # cria uma lista com todos os arquivos com o padrão indicado

# INDICAÇÃO DO DIRETÓRIO DE SAÍDA
output = Path(saida) # todos os arquivos gerados pelo workflow serão inseridos nesse diretório

for i in fasta:
    prefix = Path(i).stem # pega o componente final do caminho do arquivo sem o sufixo. Ex.: ("inputs/SRR597499.fastaq.gz").stem -> ("SRR597499.fastaq")
    saida_bowtie = os.path.join(output, prefix+'.sam') # parâmetro da atividade bowtie para indicar onde o arquivo de saída deve ser gerado e que nome ele deve ter
    bow = bowtie(multithread_bowtie, Path(base_bowtie).resolve(), i, stdout=saida_bowtie) # chama a atividade bowtie

bow.result() # Impede que a execução do workflow prossiga sem que as tarefas sejam finalizadas

# PARÂMETROS DA ATIVIDADE HTSEQ
gtf= sys.argv[5] # arquivo GTF
saida = [] # lista para "abrigar todas as execuções" do HTSeq

sam = list(output.glob('*.sam')) # cria uma lista com todos os arquivos gerados pela atividade bowtie

for l in sam:
    prefix = Path(l).stem # pega o componente final do caminho do arquivo sem o sufixo.
    saida_htseq = os.path.join(output, prefix) # parâmetro da atividade htseq para indicar onde o arquivo de saída deve ser gerado e que nome ele deve ter
    exc = htSeq_count(l, Path(gtf).resolve(), stdout=saida_htseq) # chamada a atividade htseq
    saida.append(exc) # armazena em uma lista o estado da atividade

wait_results = [i.result() for i in saida] # Impede que o workflow prossiga sua execução, até que TODAS as tarefas sejam finalizadas

# counts = list(output.glob('*.counts'))
# lista_exe = []
# for i in counts:
#     prefix = Path(i).stem
#     cleanFile = os.path.join(output, prefix + '.clean.counts')
#     exe_grep = grep(i, stdout = cleanFile)
#     lista_exe.append(exe_grep)
# grep_results = [j.results for j in lista_exe]

# PARÂMETRO DA ATIVIDADE DESEQ
exc_dseq2= sys.argv[6] # caminho do script DESeq

saida_DEseq = os.path.join(output, 'teste.deseq') # parâmetro da atividade DESeq para indicar onde o arquivo de saída deve ser gerado e que nome ele deve ter
teste = DEseq(Path(exc_dseq2).resolve(), output, stdout=saida_DEseq) # chamada da atividade DEseq
teste.result() # aguarda até que a atividade DESeq finalize, para terminar a execução do workflow
