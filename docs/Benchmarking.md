
# System Design: Benchmarking Data Management in EFS

## Overview
This document outlines the design for managing benchmarking data used in PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations, stored in Amazon Elastic File System (EFS). The design ensures that benchmarking data is organized, easily accessible, and efficiently updated for multiple models at the same time.

## Design Goals
- **Organization:** Structure the EFS storage to easily manage and access benchmarking data for different models and value streams.
- **Automation:** Automate the process of updating benchmarking data periodically for multiple models simultaneously, ensuring that calculations use the most recent data.
- **Scalability:** Support data management for hundreds of models, each with its own data storage requirements.

## EFS Folder Structure

### 1. Folder Structure Design
The EFS storage is structured to logically separate data by value streams and models, making it easy to locate and manage benchmarking data.

**Example EFS Folder Structure:**
```plaintext
/efs
└── value_stream_1/
    ├── model_x/
    │   └── benchmark.csv
    ├── model_y/
    │   └── benchmark.csv
    └── common/
        └── shared_data.csv
└── value_stream_2/
    ├── model_a/
    │   └── benchmark.csv
    ├── model_b/
    │   └── benchmark.csv
    └── common/
        └── shared_data.csv
```

### 2. Explanation of Folders and Files
- **`/efs/value_stream_x/`:** Each value stream (e.g., `value_stream_1`, `value_stream_2`) has its own directory.
- **`model_x/`:** Within each value stream, there are directories for individual models (e.g., `model_x`, `model_y`).
  - **`benchmark.csv`:** Contains the benchmarking data for the specific model.
- **`common/`:** A directory for data shared across multiple models within a value stream.

## Automation of Benchmarking Data Updates

### 1. Automation Strategy
To ensure the benchmarking data is up-to-date, automate the process of pulling and replacing the data in EFS on a monthly basis using a container within the OpenShift environment. The container will handle multiple models simultaneously.

#### High-Level Workflow Diagram
```plaintext
+-----------------------+
|                       |
|  Container Job        |
|  (Scheduled Monthly)  |
+-----------------------+
           |
           v
+-----------------------+
|  Fetch Latest         |
|  Benchmarking Data    |
|  (for All Models      |
|   from Snowflake)     |
+-----------------------+
           |
           v
+-----------------------+
|  Validate Data        |
|  (Check Integrity for |
|  Each Model)          |
+-----------------------+
           |
           v
+-----------------------+
|  Replace Old Data     |
|  for All Models in    |
|  EFS                  |
+-----------------------+
           |
           v
+-----------------------+
|  Notify Team          |
|  (Via Email or Slack) |
+-----------------------+
```

### 2. Automating with an OpenShift Container
Instead of using Jenkins, a container within the OpenShift environment will be used to automate the data update process. The container will have the EFS folder mounted, making it easy to directly access and update the benchmarking data for multiple models at once.

**Example OpenShift CronJob for Updating Benchmarking Data:**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: update-benchmarking-data
spec:
  schedule: "0 0 1 * *"  # Executes at midnight on the first day of each month
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: data-update-container
            image: your-update-image:latest
            volumeMounts:
            - name: efs-storage
              mountPath: /mnt/efs
            env:
            - name: SNOWFLAKE_CONN
              valueFrom:
                secretKeyRef:
                  name: snowflake-secret
                  key: connection-string
            envFrom:
            - configMapRef:
                name: model-config
            args: ["sh", "-c", "python update_benchmarking_data.py"]
          restartPolicy: OnFailure
      volumes:
      - name: efs-storage
        persistentVolumeClaim:
          claimName: efs-pvc
```

### 3. Configuration Management via ConfigMaps
Model-specific configurations, such as data processing parameters, will be stored in OpenShift ConfigMaps. The container job will load these configurations dynamically at runtime, allowing it to process and update benchmarking data for multiple models simultaneously.

**Example ConfigMap for Multiple Models:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-config
data:
  MODEL_X_BENCHMARKING_PATH: "/mnt/efs/value_stream_1/model_x/benchmark.csv"
  MODEL_Y_BENCHMARKING_PATH: "/mnt/efs/value_stream_1/model_y/benchmark.csv"
  MODEL_A_BENCHMARKING_PATH: "/mnt/efs/value_stream_2/model_a/benchmark.csv"
  MODEL_B_BENCHMARKING_PATH: "/mnt/efs/value_stream_2/model_b/benchmark.csv"
  VALIDATION_THRESHOLD: "0.05"
```

### 4. Dynamic Updates and Data Validation
- **Validation Scripts:** Implement validation scripts within the container to ensure the integrity and correctness of the benchmarking data before replacing the old data in EFS for each model.
- **Notification:** Automatically notify the team via email or Slack when the data update process is complete, whether successful or not.

### 5. Monitoring and Alerting

#### Using Datadog for Monitoring
Integrate Datadog to monitor the benchmarking data update process, ensuring that any issues are detected and resolved quickly.

- **Alerting:** Set up alerts to notify the team if the benchmarking data update process fails or if the data validation detects any issues.

**Datadog Integration Example:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: datadog-agent
data:
  DD_API_KEY: "<YOUR_DATADOG_API_KEY>"
  DD_TAGS: "env:prod,service:benchmarking-update"
  DD_LOGS_ENABLED: "true"
  DD_LOG_LEVEL: "info"
```

### 6. Scaling and Extending
As new models are introduced or existing models are modified, create new directories in EFS or update existing ones to accommodate the changes. The container job can be easily modified to handle additional data sources or different update schedules, while processing multiple models in parallel.

## Benefits
- **Organization:** The structured EFS folder design ensures that benchmarking data is easily accessible and well-organized for each model and value stream.
- **Automation:** The automated data update process ensures that the latest data is always used in calculations, reducing the risk of errors due to outdated data.
- **Scalability:** The system is designed to scale with the addition of new models and value streams, ensuring that benchmarking data management remains efficient and reliable.

## Conclusion
Managing benchmarking data in EFS with automation through an OpenShift container, utilizing ConfigMaps for model-specific configurations, and monitoring via Datadog provides a robust, scalable, and organized approach to handling data for PCI/CSI calculations. This design ensures that the data is always current, validated, and ready for use, with minimal manual intervention required. The ability to update benchmarking data for multiple models simultaneously further enhances the efficiency and scalability of the system.
