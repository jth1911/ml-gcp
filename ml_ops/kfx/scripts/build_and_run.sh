#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 -bucket gs://... -pipeline-root my_first_pipeline -pipeline-name my_first_pipeline1 -project-id my_gcp_project_id -bq-source"
   echo -e "\t-bucket gcs bucket formatted as gs://my-bucket"
   echo -e "\t-pipeline-root Where the pipeline artifacts will be stored. gs://my-bucket/pipeline-root"
   echo -e "\t-c Description of what is parameterC"
   exit 1 # Exit script after printing help
}

while getopts "a:b:c:" opt
do
   case "$opt" in
      a ) parameterA="$OPTARG" ;;
      b ) parameterB="$OPTARG" ;;
      c ) parameterC="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# Print helpFunction in case parameters are empty
if [ -z "$parameterA" ] || [ -z "$parameterB" ] || [ -z "$parameterC" ]
then
   echo "Some or all of the parameters are empty";
   helpFunction
fi

# Begin script in case all parameters are correct
echo "$parameterA"
echo "$parameterB"
echo "$parameterC"