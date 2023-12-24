
import os

from kfp.v2.dsl import component, Output, Input, Artifact
from kfx.constants import BASE_KFX_IMAGE
from dotenv import load_dotenv

import logging
logger = logging.getLogger("logger")
logging.basicConfig(level=logging.INFO)

load_dotenv()

logger.info(f"Using {os.getenv(BASE_KFX_IMAGE)} image to build component")

# setting custom machine type settings https://cloud.google.com/vertex-ai/docs/pipelines/machine-types
@component(base_image=os.getenv(BASE_KFX_IMAGE))
def generate_statistics(bq_source: str,
                        bucket: str,
                        job_id: str,
                        project_id : str,
                        network: str,
                        subnet: str,
                        region: str,
                        dataset : Input[Artifact],
                        beam_runner : str,
                        run_as_service_account: str,
                        statistics : Output[Artifact]):

    import inspect
    import os

    import logging
    logger = logging.getLogger("logger")
    logging.basicConfig(level=logging.INFO)

    import tensorflow_data_validation as tfdv
    
    from kfx.utils.bq_utils import bq_table_to_df, bq_table_to_gcs_in_csv
    from kfx.utils.str_utils import write_file
    
    from apache_beam.options.pipeline_options import (
        PipelineOptions, 
        GoogleCloudOptions, 
        StandardOptions, 
        SetupOptions, 
        WorkerOptions)
    
    SETUP_FILE_URI = "/tmp/setup.py"
    output_path = f'{bucket}/{job_id}/statistics/stats.pb'
    logger.info("generating statistics")
    
    SETUP_FILE_CONTENTS = inspect.cleandoc(
            f"""
                import setuptools
                setuptools.setup(
                    install_requires=['tensorflow-data-validation=={tfdv.__version__}'],
                    packages=setuptools.find_packages()
                )
        """
    )
    
    if beam_runner == "direct" or beam_runner == "DirectRunner":
        df = bq_table_to_df(project_id, bq_source)
        stats = tfdv.generate_statistics_from_dataframe(df)
        tfdv.write_stats_text(stats,output_path)
    else:
        destination_uri = bq_table_to_gcs_in_csv(project_id, job_id, bq_source, bucket)
        
        options = PipelineOptions()
        google_cloud_options = options.view_as(GoogleCloudOptions)
        google_cloud_options.project = project_id
        google_cloud_options.job_name = job_id
        google_cloud_options.region = region
        google_cloud_options.service_account_email = run_as_service_account
        
        
        google_cloud_options.staging_location = f"{bucket}/{job_id}/staging"
        google_cloud_options.temp_location = f"{bucket}/{job_id}/tmp"
        options.view_as(StandardOptions).runner = 'DataflowRunner'
        
        worker_options = options.view_as(WorkerOptions)
        worker_options.network = network
        worker_options.subnetwork = f"https://www.googleapis.com/compute/v1/projects/{project_id}/regions/{region}/subnetworks/{subnet}"


        
        setup_options = options.view_as(SetupOptions)
        write_file(SETUP_FILE_CONTENTS, SETUP_FILE_URI)
        setup_options.setup_file = SETUP_FILE_URI
        
        tfdv.generate_statistics_from_csv(
            data_location=destination_uri,
            output_path=output_path,
            pipeline_options=options)
    
    statistics.uri = output_path
        
        