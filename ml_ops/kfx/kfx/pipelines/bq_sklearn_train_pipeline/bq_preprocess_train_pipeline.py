import argparse
from dotenv import load_dotenv

from kfx.utils.container_utils import build_container, push_container
from kfx.constants import BASE_KFX_IMAGE

import logging
logger = logging.getLogger("logger")
logging.basicConfig(level=logging.INFO)

load_dotenv() 

def build_pipeline(args):
    
    import os
    import kfp
    from kfp.v2 import compiler, dsl
    import kfp.dsl as dsl
    from kfp.v2.dsl import pipeline
    from google.cloud import aiplatform
    import google_cloud_pipeline_components as gcpc
    from google_cloud_pipeline_components import aiplatform as gcc_aip
    from google_cloud_pipeline_components.experimental import vertex_notification_email
    from datetime import datetime
    from kfx.components.statistics_gen import bq_statistics_gen
    
    container_uri = os.getenv(BASE_KFX_IMAGE)
    logger.info(f"container_uri: {container_uri}")
    if args.build_pipeline_container:
        build_container(container_uri)
        push_container(container_uri)
    os.environ[BASE_KFX_IMAGE] = container_uri
    
    #Trainer component container
    training_container_uri = f"gcr.io/{args.project_id}/scikit:v1"
    build_container(training_container_uri,'./my-training-code/')
    push_container(training_container_uri)
    
    logger.info(f"kfp version: {kfp.__version__}")
    logger.info(f"gcpc version: {gcpc.__version__}")
    
    TIMESTAMP = datetime.now().strftime("%Y%m%d%H%M%S")
    
    bucket = args.bucket
    bucket_name = bucket[5:]
    
    job_id = f"{args.job_id}-{TIMESTAMP}"

    service_account = args.service_account
    
    pipeline_root = f"{bucket}/{args.pipeline_root}"
    
    @pipeline(name=args.pipeline_name, pipeline_root=pipeline_root)
    def bq_preprocess_train_pipeline(
        bq_source: str = args.bq_source,
        bucket: str = args.bucket,
        project: str = args.project_id,
        job_id: str = job_id,
        region: str = "us-central1",
        run_as_servince_account: str = service_account
    ):
        
        notify_email_task = vertex_notification_email.VertexNotificationEmailOp(
                recipients=args.recipients)
            
        with dsl.ExitHandler(notify_email_task):
            
            dataset_create_op = gcc_aip.TabularDatasetCreateOp(
                display_name="tabular-beans-dataset",
                bq_source=bq_source,
                project=project,
                location=region
            )
            bq_statistics_gen.generate_statistics(bq_source=args.bq_source, 
                                                         dataset=dataset_create_op.outputs["dataset"],
                                                         bucket=args.bucket, 
                                                         job_id=job_id, 
                                                         project_id=args.project_id,
                                                         network=args.network,
                                                         subnet=args.subnetwork,
                                                         region=region,
                                                         beam_runner=args.beam_runner,
                                                         run_as_service_account=service_account)
            
            gcc_aip.CustomContainerTrainingJobRunOp(
                display_name="pipeline-beans-custom-train",
                container_uri=training_container_uri,
                project=project,
                location=region,
                dataset=dataset_create_op.outputs["dataset"],
                staging_bucket=bucket,
                training_fraction_split=0.8,
                validation_fraction_split=0.1,
                test_fraction_split=0.1,
                bigquery_destination=args.bq_dest,
                model_serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest",
                model_display_name="scikit-beans-model-pipeline",
                environment_variables={"GCS_BUCKET" : bucket_name},
                machine_type="n1-standard-4",
            )
        
            
    
    compiler.Compiler().compile(pipeline_func = bq_preprocess_train_pipeline, package_path="custom_train_pipeline.json")
    
    pipeline_job = aiplatform.PipelineJob(
        display_name="custom-train-pipeline",
        template_path="custom_train_pipeline.json",
        job_id=job_id,
        enable_caching=False
    )
    pipeline_job.submit(service_account=service_account)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket',
                        required=True,
                        help='gcs bucket formatted as gs://my-bucket')
    parser.add_argument('--pipeline-root',
                        required=True,
                        help='name of pipeline')
    parser.add_argument('--pipeline-name',
                        required=True,
                        help="name of pipeline")
    parser.add_argument('--project-id',
                        required=True,
                        help="project id")
    parser.add_argument("--bq-source",
                        required=True,
                        help="source table")
    parser.add_argument("--bq-dest",
                        required=True,
                        help="destination table")
    parser.add_argument("--recipients",nargs='+',
                       required=True,
                       help="email recipients when pipeline exists")
    parser.add_argument("--job-id",
                        required=True,
                        help="job id of your pipeline")
    parser.add_argument("--service-account",
                        required=True,
                        help="service account email to run this pipeline")
    parser.add_argument("--network",
                        required=True,
                        help="Name of network")
    parser.add_argument("--subnetwork",
                        required=True,
                        help="Name of subnetwork.")
    parser.add_argument("--beam-runner",
                        required=True,
                        help="Beam runner name. direct or DirectRunner or DataFlowRunner only supported")
    parser.add_argument("--build-pipeline-container",
                        required=False,
                        default=False,
                        help="If set to true, it will build the docker container required for the components.")
    parser.add_argument("--pipeline-container-version",
                        required=True,
                        default="v1",
                        help="pipeline container version")
    args = parser.parse_args()
    build_pipeline(args)