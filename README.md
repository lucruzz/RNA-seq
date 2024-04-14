# RNA-seq Scientific Workflow
Workflow for RNA sequencing using the Parallel Scripting Library - Parsl.

**Reference:** Cruz, L., Coelho, M., Terra, R., Carvalho, D., Gadelha, L., Osthoff, C., & Ocaña, K. (2021). *Workflows* Científicos de RNA-Seq em Ambientes Distribuídos de Alto Desempenho: Otimização de Desempenho e Análises de Dados de Expressão Diferencial de Genes. In *Anais do XV Brazilian e-Science Workshop*, p. 57-64. Porto Alegre: SBC. DOI: https://doi.org/10.5753/bresci.2021.15789

## Requirements
- [Python >= 3.8.2](https://www.python.org/)
   - [Parsl == 1.0.0)](https://parsl.readthedocs.io/en/stable/index.html)
   - [HTSeq == 0.13.5](https://htseq.readthedocs.io/en/master/)
- [Bowtie2 == 2.3](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)
- [Samtools == 1.10](http://www.htslib.org/)
- [Picard == 2.18](https://github.com/broadinstitute/picard)
- [R >= 3.5.2](https://www.r-project.org/)
   - [DESeq2 >= 1.22.2](https://bioconductor.org/packages/release/bioc/html/DESeq2.html) 



## How to install requirements
In order to use RNA-seq Workflow the following tools must be available:

- [Python (version >= 3.8.2)](https://www.python.org/)

ParslRNA-Seq was tested on Python, version 3.8.2.

- [Parsl - Parallel Scripting Library (version 1.0.0)](https://parsl.readthedocs.io/en/stable/index.html)

The recommended way to install Parsl is the suggest approach from Parsl's documentation:

> python3 -m pip install parsl

- [Bowtie2, version 2.3](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

You can install Bowtie2 by running:

> bowtie2-2.3.5.1-linux-x86_64.zip

Or

> sudo yum install bowtie2-2.3.5-linux-x86_64

- [Samtools, version 1.10](http://www.htslib.org/)

Samtools is a suite of programs for interacting with high-throughput sequencing data.

- [Picard, version 2.18](https://github.com/broadinstitute/picard)

Picard is a set of Java command line tools for manipulating high-throughput sequencing (HTS) data and formats.

- [HTSeq, version 0.13.5](https://htseq.readthedocs.io/en/master/)

HTSeq is a native Python library that folows conventions of many Python packages. You can install it by running:

> pip install HTSeq

HTSeq uses [NumPy](https://numpy.org/), [Pysam](https://github.com/pysam-developers/pysam) and [matplotlib](https://matplotlib.org/). Be sure this tools are installed.

- [R, version 3.5.2](https://www.r-project.org/)

To use [DESEq2](https://bioconductor.org/packages/release/bioc/html/DESeq2.html) script make sure R language is also installed. You can install it by running:

> sudo apt install r-base

## 



## Running the workflow

First of all, make a Comma Separated Values (CSV) file. So, onto the first line type: ``sampleName,fileName,condition``. **Remember, there must be no spaces between items**. You can use the file *"table.csv"* in this repository as an example. Your CSV file will be like this:

   |    sampleName    |     fileName     |condition|
   |------------------|------------------|---------|
   | tissue control 1 | SRR5445794.merge.count | control |
   | tissue control 2 | SRR5445795.merge.count | control |
   | tissue control 3 | SRR5445796.merge.count | control |
   | tissue wntup 1   | SRR5445797.merge.count | wntup   |
   | tissue wntup 2   | SRR5445798.merge.count | wntup   |
   | tissue wntup 3   | SRR5445799.merge.count | wntup   |

The list of command line arguments passed to Python script, beyond the script's name, must be: 

 1. The indexed genome; 
 2. The number of threads or splitted files for `bowtie`, `sort`, `split` and `htseq` tasks; 
 3. Path to read fastaq file, which is the path of the input files; 
 4. Directory's name where the output files must be placed;  
 5. GTF file;
 7. and, lastly the DESeq script. 
 
Make sure all the files necessary to run the workflow are in the same directory and the fastaq files in a dedicated folder, as a input directory. The command line will be like this:

> python3 rna-seq.py ../mm9/mm9 24 ../inputs/ ../outputs ../Mus_musculus.NCBIM37.67.gtf ../DESeq.R

**Remember to adjust the parameter multithreaded and multicore according with your computational environment.** 
Example: If your machine has 8 cores, you should set the parameter on 8.


## Running the workflow in DOCKER

[ParslRNA-Seq](https://hub.docker.com/r/lucruzz/parslrna-seq) is also available on docker. You can push it from [DockerHub](https://hub.docker.com/r/lucruzz/parslrna-seq), running the following command:
```
docker pull lucruzz/parslrna-seq
```
To run it, create a directory on the host machine with the following hierarchy of directories and mount them in the container:

1. inputs
   - input files
2. outputs
3. table.csv
3. gtf
   - file.gtf
4. genomic_base
   - genomic-base-files

To run ParslRNA-Seq in the container, run the following command and keep monitoring the outputs directory:

```
$ sudo docker run -d -v diretorio_maquina_hospedeira:/workdir -e
$ RNASEQ_TABLE_CSV=/workdir/table.csv -e
$ RNASEQ_GENETIC_BASE=/workdir/base_genetica/prefixo_arquivo -e
$ RNASEQ_NUM_THREADS=4 -e RNASEQ_INPUTS=/workdir/inputs/ -e
$ RNASEQ_OUTPUTS=/workdir/outputs/ -e RNASEQ_GTF=/workdir/arquivo.gtf
$ rnaseq:1.0 /RNA-seq/rna-seq.sh
```