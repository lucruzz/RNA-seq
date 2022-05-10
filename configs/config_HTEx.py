from parsl.config import Config
from parsl.providers import SlurmProvider
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_interface
from parsl.data_provider.data_manager import default_staging

partition_queue = 'cpu_dev'
total_time = '00:20:00'
nodes = 1
workers=24
over_rides='-c 24'
python='module load python/3.8.2\n'
bowtie='module load bowtie2/2.3\n'
sort='module load samtools/1.10_gnu\n'
picard='module load picard/2.18\n'
r='module load R/3.5.2_openmpi_2.0_gnu\n'
modules = python + bowtie + sort + picard + r
job_name='#SBATCH -J SSD\n'

config = Config(
    executors=[
        HighThroughputExecutor(
            address=address_by_interface('ib0'), # address_by_hostname(),
            label='htex',
            cores_per_worker=workers, # number of cores used by one task
            max_workers=workers, # number of cores per node
            provider=SlurmProvider(
                partition=partition_queue,
                nodes_per_block=nodes, # number of nodes
                cmd_timeout = 240,
                init_blocks=1,
                launcher=SrunLauncher(overrides=over_rides),
                max_blocks=1,
                min_blocks=1,
                parallelism=1,
                move_files=False,
                scheduler_options = job_name,
                walltime=total_time,
                worker_init=modules
            ),
            storage_access=default_staging,
            working_dir='tmp/'
        ),
    ],
    strategy='simple'
)
