
# System Design: PCI/CSI Calculations Library

## Overview
This document outlines the design for a new Python library to perform PCI (Population Stability Index) and CSI (Characteristic Stability Index) calculations. The library is built with a focus on security, maintainability, and scalability, using Poetry for dependency management and distribution.

## Design Goals
- **Security:** Ensure the library is free from vulnerabilities.
- **Modularity:** Structure the codebase to allow easy updates and maintenance.
- **Scalability:** Support calculations for an increasing number of models.
- **Integration:** Seamlessly integrate with Snowflake for data storage and OpenShift for deployment.
- **Automation:** Automate testing, building, and deployment using CI/CD pipelines.

## Project Setup
- **Language:** Python 3.x
- **Package Manager:** Poetry

### Directory Structure
The project follows a standard Python project structure, organized for clarity and maintainability.

\`\`\`plaintext
pci_csi_library/
├── pyproject.toml           # Poetry configuration file
├── README.md                # Project overview
├── src/
│   ├── pci_csi/
│   │   ├── __init__.py      # Initialize the package
│   │   ├── calculations.py  # Core calculation logic
│   │   ├── data_processing.py # Data loading and transformation
│   │   ├── post_processing.py # Sending results to Snowflake
│   │   └── utils.py         # Utility functions
│   └── tests/
│       ├── test_calculations.py  # Unit tests for calculations
│       ├── test_data_processing.py # Unit tests for data processing
│       └── test_post_processing.py # Unit tests for post-processing
└── docs/
    └── index.rst            # Sphinx documentation index
\`\`\`

### Core Modules
- **\`calculations.py\`:** Contains the core logic for PCI and CSI calculations.
- **\`data_processing.py\`:** Handles data loading, cleaning, and transformation.
- **\`post_processing.py\`:** Handles the process of sending the calculated results to the Snowflake table.
- **\`utils.py\`:** Provides helper functions for logging, error handling, and configuration management.

### Post-Processing: Sending Data to Snowflake
After the PCI/CSI calculations are complete, the results are automatically sent to a Snowflake table. This step is handled by the \`post_processing.py\` module.

**Steps Involved:**
1. **Connection Setup:** Establish a secure connection to the Snowflake database.
2. **Data Preparation:** Format the calculation results into a structure suitable for insertion into the Snowflake table.
3. **Data Insertion:** Insert the prepared data into the appropriate Snowflake table.
4. **Error Handling:** Implement error handling to log any issues during the data insertion process.

**Example Code for \`post_processing.py\`:**
\`\`\`python
import snowflake.connector
import logging

def send_to_snowflake(data, config):
    try:
        # Establish Snowflake connection
        conn = snowflake.connector.connect(
            user=config["user"],
            password=config["password"],
            account=config["account"]
        )
        cursor = conn.cursor()

        # Prepare insert statement
        insert_stmt = """
        INSERT INTO PCI_CSI_RESULTS (model_id, value_stream, calculation_date, psi_score, csi_score, error_flag, error_details, benchmarking_period_start, benchmarking_period_end, execution_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Execute insert
        cursor.execute(insert_stmt, (
            data["model_id"],
            data["value_stream"],
            data["calculation_date"],
            data["psi_score"],
            data["csi_score"],
            data["error_flag"],
            data["error_details"],
            data["benchmarking_period_start"],
            data["benchmarking_period_end"],
            data["execution_time"]
        ))

        conn.commit()
    except Exception as e:
        logging.error(f"Failed to send data to Snowflake: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
\`\`\`

### Dependency Management
Poetry is used to manage project dependencies and environments, ensuring that the library is isolated from system packages and can be easily deployed.

**Example \`pyproject.toml\` Configuration:**

\`\`\`toml
[tool.poetry]
name = "pci-csi-library"
version = "0.1.0"
description = "A library for PCI/CSI calculations"
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.8"
pandas = "^1.3.0"
numpy = "^1.21.0"
snowflake-connector-python = "^2.4.6"

[tool.poetry.dev-dependencies]
pytest = "^6.2.4"
flake8 = "^3.9.2"
black = "^21.6b0"
\`\`\`

### Security Best Practices
- **Input Validation:** Ensure all input data is validated and sanitized before processing.
- **Error Handling:** Implement robust error handling to capture and log errors without exposing sensitive information.
- **Dependency Management:** Regularly update dependencies to patch vulnerabilities.

### CI/CD Pipeline
- **Testing:** Use pytest for unit testing and ensure all tests pass before merging code.
- **Linting:** Enforce code style using flake8 and black.
- **Build and Deploy:** Use GitHub Actions or another CI/CD tool to automate the testing, building, and publishing process.

### Integration with Other Systems
- **Snowflake:** The library will be integrated with Snowflake to store PCI/CSI calculation results.
- **OpenShift:** The library will be deployed on OpenShift as part of a larger system, where it will be used by Kubernetes CronJobs.

### Documentation
Use Sphinx to generate comprehensive documentation, including usage examples and API references.

\`\`\`plaintext
docs/
└── index.rst  # Sphinx documentation
\`\`\`

### Example Usage
\`\`\`python
from pci_csi import calculations, post_processing

# Load data
data = load_data("input.csv")

# Perform calculations
pci_score, csi_score = calculations.calculate_pci_csi(data)

# Prepare data for Snowflake
calculated_data = {
    "model_id": "model_x",
    "value_stream": "fraud_detection",
    "calculation_date": "2024-08-19",
    "psi_score": pci_score,
    "csi_score": csi_score,
    "error_flag": False,
    "error_details": None,
    "benchmarking_period_start": "2024-07-01",
    "benchmarking_period_end": "2024-07-31",
    "execution_time": "2024-08-19T02:00:00Z"
}

# Send results to Snowflake
post_processing.send_to_snowflake(calculated_data, config)
\`\`\`
