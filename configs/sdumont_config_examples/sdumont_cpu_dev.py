from parsl.config import Config
from parsl.channels import LocalChannel
from parsl.providers import SlurmProvider
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_hostname
# from parsl.addresses import address_by_interface

""" This config uses the HighThroughputExecutor and the SlurmProvider to
run pilot jobs on the nodes. These are controlled by the Parsl from the login
node using SLURM and communication between the workers on nodes and Parsl on
the login node.
"""
config = Config(
    executors=[
#        HighThroughputExecutor(
#            label="sdumont_htex_cpu_dev_24w",
#            address=address_by_hostname(),
#            #address=address_by_interface('ib0'),
#            max_workers=24,          # Set number of workers per node
#            provider=SlurmProvider(
#                cmd_timeout=120,     # Add extra time for slow scheduler responses
#                nodes_per_block=4,
#                walltime='00:20:00',
#                partition='cpu_dev',
#
#                init_blocks=1,
#                min_blocks=1,
#                max_blocks=1,
#
#                # Command to be run before starting a worker, such as:
#                # 'module load Anaconda; source activate parsl_env'.
#                worker_init='module load samtools/1.9; module load bowtie2/2.3; module load bedtools/2.29.0',
#                launcher=SrunLauncher(),
#            ),
#        ),
        HighThroughputExecutor(
            label="sdumont_htex_cpu_dev",
            address=address_by_hostname(),
            #address=address_by_interface('ib0'),
            max_workers=1,          # Set number of workers per node
            provider=SlurmProvider(
                cmd_timeout=120,     # Add extra time for slow scheduler responses
                nodes_per_block=4,
                walltime='00:20:00',
                partition='cpu_dev',
                scheduler_options='#SBATCH --cpus-per-task=24',
                init_blocks=1,
                min_blocks=1,
                max_blocks=1,

                # Command to be run before starting a worker, such as:
                # 'module load Anaconda; source activate parsl_env'.
                worker_init='module load samtools/1.9; module load bowtie2/2.3; module load bedtools/2.29.0; module load R/3.5.2_openmpi_2.0_gnu; module load perl/5.20',
                launcher=SrunLauncher(),
            ),
        )
    ],
    strategy=None,
)
