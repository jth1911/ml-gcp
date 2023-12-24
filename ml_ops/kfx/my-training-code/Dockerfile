FROM gcr.io/deeplearning-platform-release/sklearn-cpu.0-23
WORKDIR /

COPY trainer /trainer

RUN pip install sklearn google-cloud-bigquery joblib pandas google-cloud-storage

ENTRYPOINT ["python","-m","trainer.train"]