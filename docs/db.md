
# System Design: Snowflake Table for PCI/CSI Calculation Results

## Overview
This document outlines the design of a Snowflake table to store the results of PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations. The table is designed to handle data from multiple models and value streams, ensuring scalability and ease of access.

## Design Goals
- **Scalability:** Support storing results for hundreds of models and multiple value streams.
- **Efficiency:** Ensure fast querying and retrieval of calculation results.
- **Security:** Protect sensitive data and ensure compliance with data handling standards.

## Table Structure
The table will store the results of PCI/CSI calculations for each model, along with metadata about the calculation.

### Table Definition (DDL)
```sql
CREATE TABLE PCI_CSI_RESULTS (
    model_id VARCHAR(255),
    value_stream VARCHAR(255),
    calculation_date DATE,
    psi_score FLOAT,
    csi_score FLOAT,
    error_flag BOOLEAN,
    error_details STRING,
    benchmarking_period_start DATE,
    benchmarking_period_end DATE,
    execution_time TIMESTAMP,
    PRIMARY KEY (model_id, calculation_date)
);
```

### Explanation of Columns
- **`model_id`**: Identifies the model for which the PCI/CSI calculation was performed.
- **`value_stream`**: Specifies the value stream (e.g., fraud detection) to which the model belongs.
- **`calculation_date`**: The date when the PCI/CSI calculation was executed.
- **`psi_score`** and **`csi_score`**: These fields store the calculated PSI and CSI scores, respectively.
- **`error_flag`**: A boolean flag indicating whether an error occurred during the calculation process.
- **`error_details`**: A string field that provides details about any errors that occurred during the calculation.
- **`benchmarking_period_start`** and **`benchmarking_period_end`**: These fields capture the date range of the benchmarking data used for the calculations.
- **`execution_time`**: The timestamp indicating when the calculation was completed.

## Entity-Relationship Diagram (ERD)

Below is a simple representation of the entity-relationship diagram (ERD) for the `PCI_CSI_RESULTS` table:

```plaintext
+-----------------------------------------------+
|                PCI_CSI_RESULTS                |
+-----------------------------------------------+
| model_id                  : VARCHAR   [PK]    |
| value_stream              : VARCHAR           |
| calculation_date          : DATE      [PK]    |
| psi_score                 : FLOAT             |
| csi_score                 : FLOAT             |
| error_flag                : BOOLEAN           |
| error_details             : STRING            |
| benchmarking_period_start : DATE              |
| benchmarking_period_end   : DATE              |
| execution_time            : TIMESTAMP         |
+-----------------------------------------------+
```

**Primary Key:**
- The combination of `model_id` and `calculation_date` forms the primary key (`[PK]`), ensuring that each record in the table is unique.

**Foreign Key:**
- There is no explicit foreign key relationship defined in this table, but it assumes that `model_id` corresponds to models defined elsewhere in the system.

### Indexing and Performance Optimization
- **Primary Key (`PRIMARY KEY (model_id, calculation_date)`):** This key ensures that each combination of `model_id` and `calculation_date` is unique, enabling fast lookups and preventing duplicate entries.
- **Clustering:** Consider clustering the table on `calculation_date` to optimize query performance for time-based queries.
- **Data Partitioning:** If the table grows significantly, consider partitioning the data by `value_stream` or `calculation_date` to further improve query performance.

### Data Ingestion and Integration
- **Integration with PCI/CSI Library:**
  - The PCI/CSI calculations library will automatically insert results into this table after each calculation is completed.
  - The library will handle connection setup, data formatting, and error handling during the insertion process.

### Security and Compliance
- **Access Controls:** Implement role-based access controls (RBAC) to restrict access to sensitive data within the table.
- **Data Encryption:** Ensure that data is encrypted at rest and in transit, using Snowflake’s built-in encryption features.
- **Audit Logging:** Enable audit logging to track access and modifications to the table for compliance purposes.

### Query Examples
**Example 1: Retrieve All Results for a Specific Model**
```sql
SELECT * FROM PCI_CSI_RESULTS
WHERE model_id = 'model_x'
ORDER BY calculation_date DESC;
```

**Example 2: Retrieve Results Where Errors Occurred**
```sql
SELECT * FROM PCI_CSI_RESULTS
WHERE error_flag = TRUE
ORDER BY calculation_date DESC;
```

**Example 3: Retrieve Results for a Specific Value Stream Over a Date Range**
```sql
SELECT * FROM PCI_CSI_RESULTS
WHERE value_stream = 'fraud_detection'
AND calculation_date BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY calculation_date DESC;
```

## Maintenance and Monitoring
- **Data Purging:** Implement a data retention policy to periodically archive or purge old data based on business requirements.
- **Monitoring:** Set up monitoring and alerts for data ingestion processes to ensure timely and accurate data updates.

### Example Data Insertion
The following example demonstrates how data would be inserted into the table after a PCI/CSI calculation:

```sql
INSERT INTO PCI_CSI_RESULTS (
    model_id, value_stream, calculation_date, psi_score, csi_score, error_flag, error_details, benchmarking_period_start, benchmarking_period_end, execution_time
) VALUES (
    'model_x', 'fraud_detection', '2024-08-19', 0.045, 0.037, FALSE, NULL, '2024-07-01', '2024-07-31', '2024-08-19T02:00:00Z'
);
```

## Conclusion
The Snowflake table for PCI/CSI calculation results is designed to be scalable, secure, and efficient, providing a reliable repository for storing and querying calculation results across multiple models and value streams. By integrating this table with the PCI/CSI calculations library, organizations can ensure seamless data flow and maintain high standards of data quality and compliance.
