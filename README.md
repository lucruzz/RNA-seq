# RNA-seq Scientific Workflow
Workflow for RNA sequencing using the Parallel Scripting Library - Parsl.

**Reference:** Cruz, L., Coelho, M., Terra, R., Carvalho, D., Gadelha, L., Osthoff, C., & Ocaña, K. (2021). *Workflows* Científicos de RNA-Seq em Ambientes Distribuídos de Alto Desempenho: Otimização de Desempenho e Análises de Dados de Expressão Diferencial de Genes. In *Anais do XV Brazilian e-Science Workshop*, p. 57-64. Porto Alegre: SBC. DOI: https://doi.org/10.5753/bresci.2021.15789

## Requirements

In order to use RNA-seq Workflow the following tools must be available:

- [Bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

You can install Bowtie2 by running:

> bowtie2-2.3.5.1-linux-x86_64.zip

Or

> sudo yum install bowtie2-2.3.5-linux-x86_64

- [Samtools](http://www.htslib.org/)

Samtools is a suite of programs for interacting with high-throughput sequencing data.

- [Picard](https://github.com/broadinstitute/picard)

Picard is a set of Java command line tools for manipulating high-throughput sequencing (HTS) data and formats.

- [HTSeq](https://htseq.readthedocs.io/en/master/)

HTSeq is a native Python library that folows conventions of many Python packages. You can install it by running:

> pip install HTSeq

HTSeq uses [NumPy](https://numpy.org/), [Pysam](https://github.com/pysam-developers/pysam) and [matplotlib](https://matplotlib.org/). Be sure this tools are installed.

- [R](https://www.r-project.org/)

To use [DESEq2](https://bioconductor.org/packages/release/bioc/html/DESeq2.html) script make sure R language is also installed. You can install it by running:


> sudo apt install r-base

- [Parsl - Parallel Scripting Library](https://parsl.readthedocs.io/en/stable/index.html)

The recommended way to install Parsl is the suggest approach from Parsl's documentation:


> python3 -m pip install parsl

- [Python (version >= 3.5)](https://www.python.org/)

To use Parsl, you need Python 3.5 or above. You also need Python to use HTSeq, so you should load only one Python version.

## Workflow invocation

First of all, make a Comma Separated Values (CSV) file. So, onto the first line type: ``sampleName,fileName,condition``. **Remember, there must be no spaces between items**. You can use the file *"table.csv"* in this repository as an example. Your CSV file will be like this:

   |    sampleName    |     fileName     |condition|
   |------------------|------------------|---------|
   | tissue control 1 | SRR5445794.fastq | control |
   | tissue control 2 | SRR5445795.fastq | control |
   | tissue control 3 | SRR5445796.fastq | control |
   | tissue wntup 1   | SRR5445797.fastq | wntup   |
   | tissue wntup 2   | SRR5445798.fastq | wntup   |
   | tissue wntup 3   | SRR5445799.fastq | wntup   |

The list of command line arguments passed to Python script, beyond the script's name, must be: the indexed genome; the threads' number for bowtie task, sort task, number of splitted files for split_picard task and number of CPU running in htseq task; path to read fastaq file, which is the path of the input files; directory's name where the output files must be placed;  GTF file; the DESeq script; and, lastly the path to runnable Picard jar. Make sure all the files necessary to run the workflow are in the same directory and the fastaq files in a dedicated folder, as a input directory. The command line will be like this:

> python3 rna-seq.py ../mm9/mm9 6 ../inputs/ ../outputs ../Mus_musculus.NCBIM37.67.gtf ../DESeq.R ../picard/build/libs/picard.jar
