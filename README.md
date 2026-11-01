# E-Commerce Data Engineering Pipeline

An end-to-end data engineering project built using **Python, Snowflake, SQL, Snowpark and Pandas**. This project demonstrates data ingestion, layered data transformations, incremental loading, data quality validation and analytical data modelling.

## 1. Project Overview

The objective is to build a scalable e-commerce data pipeline that processes synthetic customer, product, order and order-item datasets and transforms them into analytics-ready data.

The project follows a layered architecture:

- **RAW:** Stores source data ingested from CSV files.
- **STAGING:** Cleans and standardizes source datasets.
- **CORE:** Builds dimensional and fact tables.
- **ANALYTICS:** Produces business-oriented aggregated datasets.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Pipeline orchestration and ingestion |
| Snowflake | Cloud data warehouse |
| Snowflake SQL | Data transformation and modelling |
| Snowpark Python | Python-based Snowflake transformations |
| Pandas | Local data processing |
| Snowflake Connector | Python-to-Snowflake connectivity |
| Git & GitHub | Version control |

## 3. Architecture

```text
              Synthetic CSV Data
                      |
                      v
              Python Ingestion
                      |
                      v
               SNOWFLAKE RAW
                      |
                      v
                 STAGING
             Cleaning and Standardization
                      |
                      v
                   CORE
             Dimensional Modelling
                      |
                      v
                ANALYTICS
              Business Aggregations
                      |
                      v
             Analytics-ready Data
```

## 4. Dataset Details

The pipeline processes four synthetic e-commerce datasets.

| Dataset | Records |
|---|---:|
| Customers | 1,000 |
| Products | 200 |
| Orders | 5,000 |
| Order Items | 12,479 |
| **Total** | **18,679** |

## 5. Snowflake Data Model

### RAW Schema
- CUSTOMERS
- PRODUCTS
- ORDERS
- ORDER_ITEMS

### STAGING Schema
- STG_CUSTOMERS
- STG_PRODUCTS
- STG_ORDERS
- STG_ORDER_ITEMS

### CORE Schema
- DIM_CUSTOMER
- DIM_PRODUCT
- FACT_ORDER
- FACT_ORDER_ITEM

### ANALYTICS Schema
- DAILY_SALES
- CUSTOMER_SALES
- PRODUCT_PERFORMANCE
- CATEGORY_PERFORMANCE

The project contains 16 Snowflake tables across the four layers.

## 6. Key Features

### Data Ingestion
- Python-based CSV ingestion into Snowflake.
- Internal Snowflake staging using PUT and COPY INTO.
- Temporary tables and row-count verification.
- Full refresh of RAW tables.

### Data Transformation
- Layered RAW, STAGING, CORE and ANALYTICS architecture.
- Data cleaning and standardization using Pandas.
- Dimensional and fact table creation.
- Business-level aggregations.
- Snowpark-based transformation implementation.

### Incremental Loading
- Customer-level incremental ingestion using Snowflake MERGE.
- Updates existing customer records when attributes change.
- Inserts new customer records.
- Avoids unnecessary updates when records are unchanged.
- Validates target record uniqueness.

**Note:** The current implementation uses snapshot-based incremental loading with CUSTOMER_ID as the matching key. It does not implement timestamp-based CDC or source-driven deletion handling.

### Data Quality and Validation
- Record-count validation.
- Duplicate customer-key checks.
- Referential integrity checks.
- Sales amount reconciliation.
- Revenue and quantity reconciliation across CORE and ANALYTICS.

### Pipeline Orchestration and Logging
- Sequential execution of transformation and validation scripts.
- Execution status and duration tracking.
- Pipeline logging.
- Final execution summary.

## 7. Validation Results

The following results were verified during project execution.

| Validation | Result |
|---|---|
| RAW ingestion | 18,679 records loaded |
| STAGING transformations | Passed |
| CORE transformations | Passed |
| ANALYTICS transformations