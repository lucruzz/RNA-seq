# RNA-seq Scientific Workflow
Workflow for RNA sequencing using the Parallel Scripting Library - Parsl.

## Requirements

In order to use RNA-seq Workflow the following tools must be available:

- [Bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)

You can install Bowtie2 by running:

> bowtie2-2.3.5.1-linux-x86_64.zip

Or

> sudo yum install bowtie2-2.3.5-linux-x86_64

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

The list of command line arguments passed to Python script, beyond the script's name, must be: the indexed genome, the threads' number for bowtie task, read fastaq file, directory's name where the output files must be placed,  GTF file and lastly the DESeq script. Make sure all the files necessary to run the workflow are in the same directory and the fastaq files in a dedicated folder, as a input directory. The command line will be like this:

> python3 rna-seq.py ../mm9/mm9 6 ../inputs/SRR ../outputs ../Mus_musculus.NCBIM37.67.gtf ../DESeq.R

On this first version the workflow search, on the input files' directory, for a pattern on the prefix in the files' name. So, for running this workflow you need pass this pattern. In the table, as you can see, the pattern is ``"SRR"``.
