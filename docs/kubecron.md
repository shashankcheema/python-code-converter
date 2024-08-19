
# System Design: Scheduling PCI/CSI Calculations with Kubernetes CronJobs

## Overview
This document outlines the design for scheduling PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations using Kubernetes CronJobs. The design supports different schedules for each model and ensures scalability and reliability in execution.

## Design Goals
- **Scalability:** Handle scheduling for hundreds of models, each with potentially different execution times.
- **Reliability:** Ensure consistent execution of calculations with proper error handling and retries.
- **Flexibility:** Allow easy adjustments to schedules and configurations as models are added or updated.

## High-Level Workflow Diagram

```plaintext
+-----------------------+
|                       |
|    Kubernetes CronJob  |
|                       |
+-----------------------+
           |
           v
+-----------------------+
|  Model-Specific        |
|  Configuration in      |
|  ConfigMap             |
+-----------------------+
           |
           v
+-----------------------+
|  Container Execution  |
|  (Python Script)      |
+-----------------------+
           |
           v
+-----------------------+            +-----------------------+
|  Load Benchmarking    |            |                       |
|  Data from EFS        +----------->|   Snowflake Table      |
|  Run Calculations     |            |   (Insert Results)     |
|                       |<-----------|                       |
+-----------------------+            +-----------------------+
           |
           v
+-----------------------+
|  Error Handling &     |
|  Retry Mechanism      |
+-----------------------+
           |
           v
+-----------------------+
|  Monitoring & Alerts  |
|  (Datadog)            |
+-----------------------+
```

### 1. Define CronJobs for Each Model
Each model will have its own Kubernetes CronJob, allowing for independent scheduling and execution.

**Example CronJob YAML for Model X (Runs at 2 AM Daily):**
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: model-x-cronjob
spec:
  schedule: "0 2 * * *"  # Executes at 2 AM every day
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: model-x-container
            image: your-image:latest
            volumeMounts:
            - name: efs-storage
              mountPath: /mnt/efs
              subPath: value_stream_1/model_x
            envFrom:
            - configMapRef:
                name: model-x-config
            args: ["python", "run_model_x.py"]
          restartPolicy: OnFailure
      volumes:
      - name: efs-storage
        persistentVolumeClaim:
          claimName: efs-pvc
```

### 2. ConfigMaps for Model-Specific Configurations
Store model-specific configurations, such as thresholds and benchmarking data paths, in OpenShift ConfigMaps.

**Example ConfigMap for Model X:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: model-x-config
data:
  THRESHOLD: "0.05"
  BENCHMARKING_PATH: "/mnt/efs/value_stream_1/model_x/benchmark.csv"
  EMAIL_RECIPIENTS: "team@example.com"
```

### 3. Error Handling and Retry Mechanism

#### Error Handling and Retry Diagram
```plaintext
+-----------------------+
|                       |
|    Job Execution      |
|                       |
+-----------------------+
           |
           v
+-----------------------+
|  Error Occurs?        |
|  (Check Exit Status)  |
+-----------------------+
           |
  +--------+--------+
  |                 |
  | Yes             | No
  |                 |
  v                 v
+-------------------+----+
| Retry Mechanism        |
| (Restart Policy)       |
+------------------------+
           |
           v
+------------------------+
|  Max Retries Reached?  |
+------------------------+
           |
  +--------+--------+
  |                 |
  | Yes             | No
  |                 |
  v                 v
+-------------------+----+
|  Log Error and         |
|  Trigger Alert         |
+------------------------+
```

- **Error Handling:** The container will handle errors within the Python script, such as data loading issues or calculation failures. Errors are logged, and if an error occurs, the job will exit with a non-zero status.
- **Retries:** Kubernetes CronJobs allow specifying a restart policy. If a job fails, Kubernetes will automatically retry it based on the restart policy defined in the CronJob.

### 4. Monitoring and Alerting

#### Using Datadog for Monitoring

- **Infrastructure Monitoring:** Datadog will monitor the Kubernetes infrastructure, tracking resource usage, container performance, and overall health of the cluster.
- **Application Monitoring:** Datadog will also monitor the application-specific metrics, such as job execution times, error rates, and success/failure counts.
- **Alerting:** Set up alerts in Datadog to notify the team in case of job failures, performance degradation, or other critical events.

**Datadog Integration Example:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: datadog-agent
data:
  DD_API_KEY: "<YOUR_DATADOG_API_KEY>"
  DD_TAGS: "env:prod,service:pci-csi"
  DD_LOGS_ENABLED: "true"
  DD_LOG_LEVEL: "info"
```

### 5. Maintenance and Updates

#### Dynamic Schedule Management
Use a management interface or CLI tool to update CronJob schedules without requiring manual edits to YAML files. This could include a scheduling dashboard where authorized users can adjust execution times for different models.

**Example Command for Updating a CronJob Schedule:**
```bash
kubectl patch cronjob model-x-cronjob -p '{"spec":{"schedule":"0 3 * * *"}}'
```

#### ConfigMap Updates
Set up automated jobs or Argo Workflows to update ConfigMaps when there are changes in configuration requirements, such as new thresholds or changes in benchmarking paths.

**Example of a ConfigMap Update Job:**
```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: configmap-update-job
spec:
  template:
    spec:
      containers:
      - name: update-configmap
        image: your-update-image:latest
        command: ["sh", "-c", "python update_configmaps.py"]
      restartPolicy: OnFailure
```

### 6. Scaling and Extending
As new models are introduced or existing models are modified, create new CronJobs or update existing ones to accommodate the changes. This setup can easily be extended to other value streams by duplicating and adjusting CronJob templates as needed.

## Benefits
- **Simplicity and Control:** Each model has its own CronJob, making it easy to manage schedules and configurations individually.
- **Scalability:** New models or changes to existing ones can be accommodated with minimal disruption.
- **Integration with OpenShift and Datadog:** Seamlessly integrates with the OpenShift environment and leverages Datadog for comprehensive monitoring and alerting.

## Conclusion
Using Kubernetes CronJobs for scheduling PCI/CSI calculations provides a scalable, reliable, and flexible solution for managing the execution of different models. With proper monitoring, alerting, and error handling in place, this design ensures that all calculations are performed as scheduled and that any issues are promptly addressed.
