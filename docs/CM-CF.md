
# System Design: Configuration Management Using OpenShift ConfigMaps

## Overview
This document outlines the design for managing configuration files for PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations using OpenShift ConfigMaps. The design ensures that configurations are centralized, easily managed, and dynamically applied to different models.

## Design Goals
- **Centralized Management:** Store and manage configurations centrally using ConfigMaps, allowing for easy updates and consistency across deployments.
- **Dynamic Application:** Ensure that configuration changes are automatically applied to the relevant containers without requiring redeployment.
- **Scalability:** Support configurations for hundreds of models and multiple value streams.

## ConfigMaps Setup

### 1. Define ConfigMaps for Each Model
Each model will have its own ConfigMap, which stores all necessary configuration parameters such as thresholds, benchmarking data paths, email recipients, etc.

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

### 2. Using ConfigMaps in Kubernetes CronJobs
Reference the ConfigMaps in your Kubernetes CronJobs to dynamically load configurations when jobs run.

**Example Usage in CronJob:**
```yaml
spec:
  containers:
  - name: model-x-container
    image: your-image:latest
    envFrom:
    - configMapRef:
        name: model-x-config
```

### 3. Automated Updates and Maintenance

#### Maintenance Workflow Diagram
```plaintext
+-----------------------+
|                       |
|   Configuration       |
|   Repository (Git)    |
|                       |
+-----------------------+
           |
           v
+-----------------------+
|  Update ConfigMap     |
|  YAML Files in Git    |
+-----------------------+
           |
           v
+-----------------------+
|  Jenkins Job          |
|  for Applying         |
|  ConfigMap Changes    |
+-----------------------+
           |
           v
+-----------------------+
|  Apply Updates to     |
|  OpenShift ConfigMaps |
+-----------------------+
           |
           v
+-----------------------+
|  New Configs Applied  |
|  to Running Jobs      |
+-----------------------+
```

#### Automating ConfigMap Updates with Jenkins
Use Jenkins to automate the process of updating ConfigMaps in OpenShift. Jenkins can be triggered by changes in the configuration repository, ensuring that updates are automatically applied.

**Example of a Jenkins Pipeline for ConfigMap Updates:**
```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                git 'https://your-repo-url.git'
            }
        }
        stage('Update ConfigMaps') {
            steps {
                sh 'kubectl apply -f configmaps/'
            }
        }
    }
    post {
        success {
            echo 'ConfigMaps updated successfully!'
        }
        failure {
            echo 'Failed to update ConfigMaps.'
        }
    }
}
```

### 4. Dynamic Configuration Application

#### Version Control Integration
Store the ConfigMap definitions in a version control system (e.g., Git) to track changes over time and ensure that updates can be rolled back if necessary. Use Jenkins to automate the deployment of ConfigMap changes from your version control system to your OpenShift environment.

#### ConfigMap Validation
Implement validation scripts or CI pipelines in Jenkins to ensure that ConfigMaps are correctly formatted and contain valid data before they are applied. This prevents configuration errors from affecting running jobs.

### 5. Monitoring and Alerting

#### Monitoring ConfigMap Changes
Use Datadog to monitor changes to ConfigMaps, ensuring that any updates are applied successfully and that the correct configurations are being used in your jobs.

- **Alerting:** Set up alerts to notify the team if there are any issues with applying ConfigMap changes or if invalid configurations are detected.

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

### 6. Scaling and Extending
As new models are introduced or existing models are modified, create new ConfigMaps or update existing ones to accommodate the changes. This setup can easily be extended to other value streams by duplicating and adjusting ConfigMap templates as needed.

## Benefits
- **Centralized Management:** Configurations are centrally managed, making it easier to update and maintain consistency across all models and deployments.
- **Dynamic Application:** Changes to configurations are automatically picked up by running jobs, reducing downtime and the risk of configuration drift.
- **Scalability:** The setup scales well with the addition of new models or value streams, as each model’s configuration is isolated and managed independently.

## Conclusion
Using OpenShift ConfigMaps for configuration management, combined with Jenkins for automation, provides a robust, scalable, and flexible solution for handling PCI/CSI calculation configurations. With proper automation, validation, and monitoring in place, this design ensures that all configurations are applied consistently and that any issues are promptly addressed.
