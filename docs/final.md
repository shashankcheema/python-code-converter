
# Comprehensive System Design for PCI/CSI Calculations and Data Management

## Overview
This document outlines a comprehensive system design for managing PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations. The design encompasses all aspects of calculation, data management, scheduling, error handling, monitoring, and more, ensuring a robust and scalable solution.

## 1. PCI/CSI Calculations Library

### Overview
The PCI/CSI calculations library is the core component responsible for performing the necessary calculations for PSI and CSI. This library includes post-processing steps to send the calculated data to Snowflake for storage and further analysis.

### Key Features
- **Calculations**: Implements algorithms for calculating PCI/CSI scores.
- **Post-Processing**: Automates the process of sending calculated data to Snowflake.
- **Configuration Management**: Utilizes OpenShift ConfigMaps for managing model-specific settings.
- **Integration with Datadog**: Monitors the entire calculation and post-processing workflow.

### Example Library Structure
```
.
├── src/
│   ├── calculations.py
│   ├── post_processing.py
│   ├── config/
│   │   └── model_configs.yaml
├── tests/
│   └── test_calculations.py
└── README.md
```

## 2. Snowflake Table Design

### Overview
The Snowflake table is designed to store the results of PCI/CSI calculations, providing an efficient structure for querying and analyzing results across multiple models.

### Table Definition (DDL)
```sql
CREATE TABLE PCI_CSI_RESULTS (
    model_id VARCHAR(255),
    value_stream VARCHAR(255),
    calculation_date DATE,
    psi_score FLOAT,
    csi_score FLOAT,
    execution_time TIMESTAMP,
    PRIMARY KEY (model_id, calculation_date)
);
```

### Entity-Relationship Diagram (ERD)
```
+-----------------------------------------------+
|                PCI_CSI_RESULTS                |
+-----------------------------------------------+
| model_id                  : VARCHAR   [PK]    |
| value_stream              : VARCHAR           |
| calculation_date          : DATE      [PK]    |
| psi_score                 : FLOAT             |
| csi_score                 : FLOAT             |
| execution_time            : TIMESTAMP         |
+-----------------------------------------------+
```

## 3. Scheduling Calculations with Kubernetes CronJobs

### Overview
Kubernetes CronJobs are employed to schedule PCI/CSI calculations for different models at specific times, ensuring that calculations are performed regularly and without manual intervention.

### CronJob Example
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

### Monitoring and Alerting with Datadog
Datadog is integrated to monitor the execution of Kubernetes CronJobs, track performance, and alert the team in case of failures, ensuring that the system remains reliable and responsive.

## 4. Configuration Management Using OpenShift ConfigMaps

### Overview
OpenShift ConfigMaps are utilized to centrally manage configuration settings for the PCI/CSI calculations. This approach ensures that configurations are consistent and can be dynamically applied to various models.

### Example ConfigMap
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

### Automation and Maintenance

#### Jenkins Jobs
- **ConfigMap Updates**: Jenkins jobs automate the process of updating ConfigMaps based on changes in the version control system, ensuring that the latest configurations are always applied.
- **Scheduled Jobs**: Periodic updates, such as threshold adjustments, are handled by Jenkins-scheduled jobs.

#### OpenShift Scheduled Jobs
- **Dynamic Updates**: Certain updates, especially those requiring direct interaction with the OpenShift environment, are managed by scheduled jobs within OpenShift, ensuring smooth and timely updates.

## 5. Benchmarking Data Management in EFS

### Overview
Benchmarking data is stored and managed in Amazon Elastic File System (EFS), allowing for efficient and organized data handling. The system is designed to update data for multiple models simultaneously, ensuring that calculations are based on the most recent data.

### EFS Folder Structure
```
/efs
└── value_stream_1/
    ├── model_x/
    │   └── benchmark.csv
    ├── model_y/
    │   └── benchmark.csv
    └── common/
        └── shared_data.csv
```

### Automation with OpenShift Container
OpenShift containers automate the process of fetching, validating, and updating benchmarking data from Snowflake, ensuring that the data stored in EFS is accurate and up-to-date.

### Monitoring with Datadog
Datadog is used to monitor the data update process and alert the team in case of issues, ensuring the reliability and integrity of benchmarking data.

## 6. Error Handling and Retry Mechanism

### Overview
An error handling and retry mechanism is integrated into the PCI/CSI calculation process to ensure that the system remains reliable even in the face of unexpected errors. The mechanism includes detailed logging, automatic retries, and notifications for critical issues.

### Retry Logic
```python
def perform_calculation(model):
    retries = 3
    delay = 300  # 5 minutes
    for attempt in range(retries):
        try:
            result = calculate_psi_csi(model)
            return result
        except Exception as e:
            log_error(model, e)
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                notify_team(model, e)
                raise e
```

### Monitoring and Alerting with Datadog
Datadog monitors the error handling process and alerts the team if the maximum number of retries is reached or if critical errors occur, ensuring that issues are promptly addressed.


## 7. Logical Architecture Diagram

### Diagram
The following diagram provides a high-level overview of the logical architecture, illustrating the flow of data and control between the various components of the system.

```plaintext
+-----------------------+        +-----------------------+
|                       |        |                       |
|   PCI/CSI Library     |        |   Configurations via  |
|                       |<-------|   ConfigMaps          |
+-----------------------+        +-----------------------+
           |                              |
           v                              |
+-----------------------+                 |
|                       |                 |
|  Kubernetes CronJobs  |                 |
|                       |                 |
+-----------------------+                 |
           |                              |
           v                              v
+-----------------------+        +-----------------------+
|                       |        |                       |
|  EFS (Benchmarking    |        |   Snowflake Table      |
|  Data Management)     +------->|   (Results Storage)    |
|                       |<-------|                       |
+-----------------------+        +-----------------------+
           |                              |
           v                              |
+-----------------------+                 |
|                       |                 |
|  Error Handling and   |                 |
|  Retry Mechanism      |                 |
+-----------------------+                 |
           |                              |
           v                              v
+-----------------------+        +-----------------------+
|                       |        |                       |
|  Monitoring & Alerts  |<-------|    Datadog            |
|                       |        |                       |
+-----------------------+        +-----------------------+
```

## 8. Physical Architecture Diagram

### Diagram
The physical architecture diagram provides a detailed view of the infrastructure components, including servers, storage, and network, and how they interact to support the system's operations.

```plaintext
+-------------------------------------------------------------+
|                          OpenShift Cluster                  |
|                                                             |
|  +-----------------------+      +-----------------------+  |
|  |                       |      |                       |  |
|  |   Kubernetes Pod 1    |      |   Kubernetes Pod 2    |  |
|  |  (PCI/CSI Calc + Post |      |  (Benchmarking Data   |  |
|  |   Processing)         |      |   Management)         |  |
|  +-----------------------+      +-----------------------+  |
|        |                           |                         |
|        v                           v                         |
|  +-----------------------+      +-----------------------+  |
|  |    EFS Storage         |<----|   Snowflake Database   |  |
|  +-----------------------+      +-----------------------+  |
+-------------------------------------------------------------+

+-------------------------------------------------------------+
|                        Jenkins Server                        |
|                                                             |
|  +-----------------------+      +-----------------------+  |
|  |   ConfigMap Updates    |      |  Scheduled Jobs       |  |
|  |    (Jenkins)           |      |   (Jenkins)           |  |
|  +-----------------------+      +-----------------------+  |
|                                                             |
+-------------------------------------------------------------+
```

## 9. Infrastructure Requirements, Design, and Sizing

### Infrastructure Requirements
- **OpenShift Cluster**: Provisioned with sufficient nodes to handle Kubernetes pods responsible for calculations, data management, and monitoring.
- **EFS Storage**: Adequate storage capacity to manage benchmarking data for all models.
- **Snowflake Database**: Configured with the necessary compute resources to efficiently manage data storage and queries.
- **Jenkins Server**: Equipped with resources to handle automated job scheduling and execution.

### Design and Sizing
- **OpenShift Cluster**: Minimum 3-node cluster with autoscaling capabilities to manage load.
- **EFS Storage**: Sizing based on the expected data volume for all models.
- **Snowflake**: Compute warehouse sized according to query load and data volume requirements.
- **Jenkins**: Configured for high job volume with performance optimization.


## 10. 20 Factors

### Critical Factors Considered
1. **Scalability**: Designed to accommodate increasing data volumes and models.
2. **Reliability**: Built-in mechanisms to handle and recover from errors.
3. **Performance**: Optimized to ensure timely execution of calculations and data processing.
4. **Security**: Ensures data protection through encryption and access controls.
5. **Compliance**: Adheres to regulatory standards, including PCI-DSS.
6. **Automation**: Automates key processes using Jenkins and OpenShift.
7. **Monitoring**: Comprehensive monitoring with Datadog to track system health.
8. **Data Integrity**: Validates data at each step to ensure accuracy.
9. **Extensibility**: Modular design supports easy integration of new models.
10. **Cost Efficiency**: Balances performance with cost-effective infrastructure usage.
11. **Data Privacy**: Implements data masking and anonymization as needed.
12. **Maintainability**: Follows best practices for easy system updates and maintenance.
13. **Interoperability**: Compatible with various data sources and formats.
14. **Redundancy**: Incorporates redundancy to prevent single points of failure.
15. **Auditability**: Maintains logs and audit trails for all processes.
16. **Usability**: User-friendly interfaces for monitoring and management.
17. **Latency**: Minimizes delays in data transfer and processing.
18. **Localization**: Adaptable for different regions and data sources.
19. **Compliance**: Ensures adherence to GDPR and other data protection regulations.
20. **Disaster Recovery**: Robust backup and restore processes are in place.

## 11. Cybersecurity Requirements

### Security Measures
- **Data Encryption**: All data is encrypted at rest and in transit.
- **Access Controls**: Role-based access control (RBAC) is implemented in OpenShift and Snowflake.
- **Audit Logs**: Detailed logs of all data access and modifications are maintained.
- **Vulnerability Scanning**: Regular scans are conducted to identify and mitigate vulnerabilities in the PCI/CSI calculation library and related components.
- **Incident Response**: Procedures are in place for detecting and responding to security incidents promptly.

## 12. Non-Functional Requirements

### Key Non-Functional Requirements
- **Performance**: The system must process all scheduled jobs within the designated time windows.
- **Scalability**: Capable of supporting over 100 models with ease.
- **Reliability**: Requires a system uptime of 99.9%.
- **Maintainability**: Updates should not disrupt ongoing operations.
- **Security**: Compliance with PCI-DSS standards and ensuring data integrity are paramount.

## 13. Architecture Decisions and Patterns Referred

### Key Decisions
- **Use of OpenShift**: Chosen for container orchestration due to its enterprise-grade features.
- **EFS for Benchmarking Data**: Selected for its scalability and integration with AWS services.
- **Snowflake for Data Storage**: Chosen for its ability to handle large-scale data analytics.
- **Datadog for Monitoring**: Selected for its comprehensive monitoring and alerting capabilities.

### Patterns
- **Retry Pattern**: Implemented in error handling to increase system resilience.
- **Configuration Management Pattern**: Leveraging ConfigMaps for centralized management of configuration settings.
- **Observer Pattern**: Applied in monitoring and alerting, ensuring timely detection and reporting of issues.

## 14. Trade-offs

### Key Trade-offs
- **Cost vs. Performance**: Prioritized performance, resulting in slightly higher infrastructure costs.
- **Flexibility vs. Security**: Enhanced security measures limit certain flexibilities in data processing.
- **Automation vs. Control**: High levels of automation reduce the need for manual intervention but require more configuration upfront.

## 15. Risks and Controls

### Identified Risks
- **Data Loss**: Potential risk of losing benchmarking data due to errors in data transfer.
- **Security Breach**: Risk of unauthorized access to sensitive data.
- **System Downtime**: Risk of system failures affecting scheduled calculations.

### Controls
- **Backup and Restore**: Regular backups of benchmarking data and Snowflake tables.
- **Encryption**: Data encryption ensures unauthorized access is prevented.
- **Redundancy**: Redundant systems ensure high availability.
- **Monitoring and Alerts**: Continuous monitoring with immediate alerts for critical issues.

## Conclusion
This comprehensive design integrates various components to ensure reliable and scalable PCI/CSI calculations. Each component is designed with scalability, reliability, and monitoring in mind, ensuring the overall system is robust and adaptable to future needs.
