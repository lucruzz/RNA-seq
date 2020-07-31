from parsl.config import Config
from parsl.executors.threads import ThreadPoolExecutor

config = Config(
	app_cache=True,
	checkpoint_files=None,
	checkpoint_mode=None,
	checkpoint_period=None,
	data_management_max_threads=10,
	executors=[
		ThreadPoolExecutor(
			label='threads',
			managed=True,
			max_threads=12,
			storage_access=None,
			thread_name_prefix='',
			working_dir=None
		)
	],
	initialize_logging=True,
	max_idletime=120.0,
	monitoring=None,
	retries=0,
	run_dir='runinfo',
	strategy='simple',
	usage_tracking=False
)
