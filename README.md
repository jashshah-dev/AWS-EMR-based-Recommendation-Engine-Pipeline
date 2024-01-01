# AWS-EMR-based-Recommendation-Engine-Pipeline
Build and deploy a scalable Recommendation Engine leveraging AWS EMR, enabling efficient processing and analysis for personalized recommendations in large datasets.

# Architecture Diagram

![image](https://github.com/jashshah-dev/AWS-EMR-based-Recommendation-Engine-Pipeline/assets/132673402/b8a4f62c-e18a-4957-b4b8-364107d6e71e)

# Recommendation System

![image](https://github.com/jashshah-dev/AWS-EMR-based-Recommendation-Engine-Pipeline/assets/132673402/aa463365-70bd-4020-8db9-74ca74028c8a)

# Recommendation Systems Overview

## Popularity-Based Recommendation Systems

The popularity-based recommendation system utilizes data from top movie review websites to suggest highly-rated movies, promoting increased content consumption. Despite its simplicity and scalability, this system lacks personalization and may not accurately reflect individual user preferences.

## Association Rule Mining

Association rule mining, also known as Market Basket Analysis, identifies patterns of co-occurrences in basket data. It uncovers if-then associations, offering insights into user choices when preferences are not easily accessible. However, computational expenses may increase with larger datasets.

## Content-Based Filtering

Content-based filtering constructs user preference profiles based on past choices, eliminating the need for direct user-item comparisons. This method aligns recommendations with a user's historical actions, providing a personalized touch.

## Collaborative Filtering

Collaborative filtering examines interactions and similarities between users and items. By analyzing the behavior of multiple customers, this method enhances accuracy in personalized recommendations, contributing to improved user satisfaction and loyalty.

Explore the nuances of recommendation systems, from simple popularity to intricate collaborative filtering, and understand their applications in crafting personalized user experiences.

![image](https://github.com/jashshah-dev/AWS-EMR-based-Recommendation-Engine-Pipeline/assets/132673402/623f0da3-bfc5-40c7-8be4-6cb8f8dd50a5)
![image](https://github.com/jashshah-dev/AWS-EMR-based-Recommendation-Engine-Pipeline/assets/132673402/36c4e316-bfc0-4dab-9c17-7a4cc079c89b)

# Matrix Factorization and ALS (Alternating Least Squares)

## Matrix Factorization

Matrix Factorization is a powerful technique employed in recommendation systems to analyze and decompose a user-item interaction matrix into two lower-dimensional matrices. These matrices represent latent factors, capturing hidden patterns and relationships within the data. Matrix Factorization is widely used for collaborative filtering, providing personalized recommendations based on user-item interactions.

## Alternating Least Squares (ALS)

Alternating Least Squares (ALS) is an iterative optimization algorithm frequently used in Matrix Factorization for recommendation systems. ALS minimizes the difference between the observed and predicted ratings by alternately fixing one matrix and optimizing the other. This iterative process continues until convergence, refining the factorized matrices for improved accuracy in predicting user preferences.

Explore the synergy between Matrix Factorization and ALS, unlocking the potential to enhance recommendation system performance and deliver more accurate and personalized suggestions to users.

## AWS Data Pipeline on Transient EMR Cluster
# Movie Recommendation Airflow Workflow

## Overview

This Airflow workflow automates the process of setting up and running an Amazon EMR cluster for movie recommendation. It includes the following steps:

1. **Create EMR Cluster:** Initiates the creation of an EMR cluster with specified configurations and applications, such as Spark and Hive.

2. **Ingest Layer:** Submits a Spark job to ingest movie data into the EMR cluster, leveraging the script located at `s3://airflowemr/scripts/ingest.py`.

3. **Poll Ingest Layer:** Monitors the status of the ingest layer Spark job and waits for completion before proceeding.

4. **Transform Layer:** Submits a Spark job for transforming movie data, utilizing the script at `s3://airflowemr/scripts/Movie_Recommendation.py`.

5. **Poll Transform Layer:** Monitors the status of the transform layer Spark job and waits for completion before terminating the EMR cluster.

6. **Terminate EMR Cluster:** Terminates the running EMR cluster to ensure cost efficiency.

## Prerequisites

- AWS credentials with the necessary permissions to create and manage EMR clusters.
- Configured EMR cluster settings, including key pair, subnet, and S3 bucket paths for logs and scripts.
- SNS (Simple Notification Service) setup for email notifications.

## Configuration

- Update the `create_emr_cluster` function in the DAG file with your specific EMR cluster configurations.
- Adjust the paths and filenames in the `add_step_emr` calls to point to your specific Spark scripts.

## Usage

1. Ensure that your Airflow environment is properly set up and the necessary plugins are installed.

2. Copy the provided DAG file (`movie_recommendation_airflow_dag.py`) to your Airflow DAGs directory.

3. Trigger the DAG manually or set up a schedule based on your requirements.

4. Monitor the Airflow UI or logs for the progress of each step.

5. Receive email notifications, if configured, through SNS for successful or failed executions.

## Note

This workflow includes the termination of the EMR cluster after processing to manage costs effectively. Make sure that all necessary data is persisted in your S3 bucket before cluster termination.

For questions or issues, contact the workflow owner (specified in the DAG configuration).







