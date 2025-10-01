# My Project

- [Vertex AI Guide](vertex_ai.md)


# GoogleCloudETL_ML_Deployment
### GoogleCloud_ETL_VertexAi
+ Google Cloud ETL Pipeline with Machine Learning Model Deployment
+ cloud project setup and role assign
+ Google Cloud ETL data pipelines with Airflow Orchestration using Directed Acyclic Graphs (DAGs)
+ Cloud Composer, Cloud Sql, Google BigQuery, VertexAi Endpoints
 🏗️ Admin vs Developer in Composer Setup
## 🔹 1. Admin Responsibilities

Cloud Admin / Platform Team has Owner or Project IAM Admin.


Create the Composer environment.

Set up networking, VPC, subnets, firewall rules.

Assign IAM roles to developers and service accounts.

Enable all required APIs (Composer, GKE, Cloud SQL, BigQuery, Storage, etc.).

👉 IAM roles for Admin:
```
roles/owner (or) combination of:

roles/composer.admin

roles/compute.admin

roles/storage.admin

roles/serviceusage.serviceUsageAdmin

roles/resourcemanager.projectIamAdmin
```
## 🔹 2. Developer Responsibilities (Airflow / ETL Engineers)

Developers don’t create the Composer environment. Instead, they:

Write DAGs (Python workflows).

Upload DAGs to GCS bucket linked to Composer.

Manage ETL jobs (BigQuery, Cloud SQL, Dataproc, Vertex AI, etc.).

Monitor DAG runs in Airflow UI.

👉 IAM roles for Developer (user account or ETL SA):
```
roles/composer.user → Access Airflow UI.

roles/composer.worker → Run DAG tasks.

roles/bigquery.dataEditor + roles/bigquery.jobUser → Work with BigQuery.

roles/cloudsql.client → Connect to Cloud SQL.

roles/storage.objectAdmin → Access DAGs/logs bucket.

roles/dataproc.editor → If using Dataproc jobs.

roles/aiplatform.user → If using Vertex AI from DAGs.
```
## ⚡ Example IAM Setup
```gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:admin@company.com" \
  --role="roles/composer.admin"

ETL Service Account (etl-sa@...)

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:etl-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/composer.worker"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:etl-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:etl-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

# 🚀 Flow of How You Onboard as an ETL Engineer in GCP with Composer
## 🔹 1. Admin Onboarding

The Cloud Admin / IT team owns the Google Cloud project(s).

the project with the right roles:

```
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:your.email@company.com" \
  --role="roles/composer.user"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:your.email@company.com" \
  --role="roles/bigquery.jobUser"
```
## 🔹 2. Access Composer Environment

Admin gives the Composer environment name + region.

You log in with:
```
gcloud composer environments describe ENV_NAME \
  --location=REGION
```

This shows details like:

The GCS DAG bucket path (e.g. gs://us-central1-composer-bucket-xyz/dags/)

The Airflow Web UI URL

## 🔹 3. Service Accounts for DAGs

Your DAGs won’t run as your user, but as a Service Account (SA).

Admins create a dedicated ETL Service Account (e.g. etl-sa@PROJECT_ID.iam.gserviceaccount.com)

They assign it roles like:
```
roles/bigquery.dataEditor (to write/query BQ)

roles/cloudsql.client (to read Cloud SQL input data)

roles/storage.objectAdmin (for staging/intermediate files)

roles/aiplatform.user (if calling Vertex AI models)
```
This way your DAGs can run safely without using your personal account.

## 🔹 4. Developing DAGs

As an engineer, your main job is:

Write DAGs in Python (dags/ folder).

Test them locally (optional with airflow standalone).

Upload DAGs to GCS:
```
gsutil cp my_dag.py gs://COMPOSER_BUCKET/dags/
```

Once uploaded → Composer automatically syncs DAGs → visible in Airflow UI.

## 🔹 5. Running Workflows

You monitor DAGs in the Airflow UI.

You check logs (stored in GCS).

You debug failed tasks and re-run them.

## 🔹 6. Day-to-Day Communication

If you need new permissions (e.g. access to another dataset, or Vertex AI),
→ You raise a request to the Admin team (they use Jira / ITSM tickets in enterprise).

Example request:

"Please grant etl-sa@PROJECT_ID.iam.gserviceaccount.com the role roles/aiplatform.user in project ml-project-456 so our Composer DAGs can trigger Vertex AI training jobs."

# ✅ Summary: Your Lifecycle

Admin adds you to GCP with roles/composer.user.

You access Composer and the DAG bucket.

DAGs run via a Service Account (etl-sa) with specific roles.

You request more permissions via Admin when needed.


