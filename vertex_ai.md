+ ## Train the AutoML model

```
from google.cloud import aiplatform

aiplatform.init(project="projectid", location="us-central1")

MODEL_DISPLAY_NAME = "diamonds_price_model"

training_job = aiplatform.AutoMLTabularTrainingJob(
    display_name=MODEL_DISPLAY_NAME,
    optimization_prediction_type="regression"
)

model = training_job.run(
    dataset=dataset,
    target_column="price",
    budget_milli_node_hours=1000  # 1 hour
)
```


+ ## Deploy the trained model to an endpoint
for predictions, you need an endpoint:

```
endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=1,
)
```

 + ## Send online prediction requests
 
 ```
 instances = [
    {
        "carat": 1.0,
        "cut": "Ideal",
        "color": "H",
        "clarity": "VS2",
        "depth": 61.5,
        "table": 55.0,
        "x": 6.5,
        "y": 6.5,
        "z": 4.0
    }
]

prediction = endpoint.predict(instances=instances)

print("Prediction:", prediction)
```

+ ## Batch Predict
```
batch_prediction_job = model.batch_predict(
    job_display_name="diamonds_batch_predict",
    bigquery_source="bq://PRJECT_ID.sales_dw.diamonds_full",
    bigquery_destination_prefix="bq://projectid.sales_dw.diamonds_predictions",
    machine_type="n1-standard-4",
    sync=True
)
```




