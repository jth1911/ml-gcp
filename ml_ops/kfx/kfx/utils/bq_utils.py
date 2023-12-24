from google.cloud import bigquery
from kfx.utils.str_utils import remove_prefix

import pandas as pd

def bq_table_to_df(project_id: str, bq_table_uri: str) -> pd.DataFrame:

    bqclient = bigquery.Client(project=project_id)

    bq_table_uri = remove_prefix(bq_table_uri,"bq://")
    table = bigquery.TableReference.from_string(bq_table_uri)
    rows = bqclient.list_rows(
        table,
    )
    return rows.to_dataframe(create_bqstorage_client=False)

# TODO - shard table
def bq_table_to_gcs_in_csv(project_id : str, job_id: str, bq_table_uri: str, bucket : str) -> str:
    
    bqclient = bigquery.Client(project=project_id)
    
    bq_table_uri = remove_prefix(bq_table_uri,"bq://")
    destination_uri = f"{bucket}/tmp/{job_id}/dataset.csv"
    tbl_info = bq_table_uri.split(".")
    project_id = tbl_info[0]
    dataset_id = tbl_info[1]
    table_id = tbl_info[2]
    dataset_ref = bigquery.DatasetReference(project_id, dataset_id)
    table_ref = dataset_ref.table(table_id)
    
    extract_job = bqclient.extract_table(
        table_ref,
        destination_uri,
        location="US"
    )
    extract_job.result() # waits for job to complete
    return destination_uri