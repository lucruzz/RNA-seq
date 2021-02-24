from parsl.config import Config
#from parsl.monitoring.monitoring import MonitoringHub
from parsl.providers import SlurmProvider
from parsl.executors import HighThroughputExecutor
from parsl.launchers import SrunLauncher
from parsl.addresses import address_by_interface#address_by_hostname
#from parsl.executors.threads import ThreadPoolExecutor
#from parsl.data_provider.file_noop import NoOpFileStaging
#from parsl.data_provider.data_manager import default_staging

config = Config(
    executors=[
        HighThroughputExecutor(
            address=address_by_interface('ib0'),#address_by_hostname(),
            label='htex',
            cores_per_worker=24, # number of cores used by one task
            max_workers=24, # number of cores per node           
            provider=SlurmProvider(
                partition='cpu_small',
                nodes_per_block=6, # number of nodes
                cmd_timeout = 120, # duration for which the provider will wait for a command to be invoked on a remote system
                init_blocks=1,
                launcher=SrunLauncher(overrides='-c 24'),
                max_blocks=1,
                min_blocks=1,
                parallelism=1,
                move_files=False,
                scheduler_options = '#SBATCH -J HTEX\n',
                walltime='01:15:00',
                worker_init='module load bowtie2/2.3\nmodule load python/3.8.2\nmodule load R/3.5.2_openmpi_2.0_gnu\n'
            ),
            #storage_access=default_staging,
        ),
    ],
    strategy='simple'
)
