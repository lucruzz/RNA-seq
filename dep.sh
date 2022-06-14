#!/bin/bash
#SBATCH --nodes=1                #Numero de Nós
#SBATCH --ntasks-per-node=1      #Numero de tarefas por Nó
#SBATCH --ntasks=1               #Numero de tarefas
#SBATCH --cpus-per-task=24       #Numero de threads por tarefa
#SBATCH --partition=nvidia_small #Fila (partition) a ser utilizada
#SBATCH --time=00:05:00          #Tempo maximo de ocupacao da fila
#SBATCH --job-name=dependente    #Nome job
#SBATCH --exclusive              #Uso do nó de forma exclusiva

#Carrega os modulos
module load R/3.5.2_openmpi_2.0_gnu

#Acessa o diretório onde o script está localizado
DIR=$(pwd)
cd $DIR

mkdir -p outputs
mv outputs94/* outputs/
mv outputs95/* outputs/
mv outputs96/* outputs/
mv outputs97/* outputs/
mv outputs98/* outputs/
mv outputs99/* outputs/

DESEQ=$DIR/DESeq.R
INPUTS=$DIR/outputs

echo $SLURM_JOB_ID
$DESEQ $INPUTS
