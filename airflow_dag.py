import boto3
import logging
import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
# from airflow.contrib.operators.snowflake_operator import SnowflakeOperator
# from airflow.contrib.hooks.snowflake_hook import SnowflakeHook
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from time import sleep

# Setting up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Airflow DAG configuration
args = {"owner": "Airflow"}
dag = DAG(
    dag_id="Emr_automation_dag",
    default_args=args,
    schedule_interval=None,
    start_date=airflow.utils.dates.days_ago(2)  # Move start_date to DAG constructor
    
)


# Boto3 client for EMR
client = boto3.client('emr', region_name='us-west-2', aws_access_key_id='AKIATFYN2XYJLP6P2HLY', aws_secret_access_key='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')

def create_emr_cluster():
    """
    Creates an EMR cluster.

    Returns:
        str: The ID of the created EMR cluster.
    """
    cluster_id = client.run_job_flow(
        Name="transient_demo_testing",
        Instances={
            'InstanceGroups': [
                {
                    'Name': "Master",
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'MASTER',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 1,
                },
                {
                    'Name': "Slave",
                    'Market': 'ON_DEMAND',
                    'InstanceRole': 'CORE',
                    'InstanceType': 'm5.xlarge',
                    'InstanceCount': 2,
                }
            ],
            'Ec2KeyName': 'emrwest',
            'KeepJobFlowAliveWhenNoSteps': True,
            'TerminationProtected': False,
            'Ec2SubnetId': 'subnet-006f2c9fde171ce6d',
        },
        LogUri="s3://airflowemr/logs/",
        ReleaseLabel='emr-7.0.0',
        BootstrapActions=[],
        VisibleToAllUsers=True,
        JobFlowRole="emr_ec2",
        ServiceRole="emr",
        Applications=[{'Name': 'Spark'}, {'Name': 'Hive'}]
    )
    print("The cluster started with cluster id: {}".format(cluster_id))
    return cluster_id

def add_step_emr(cluster_id, jar_file, step_args):
    """
    Adds a step to an existing EMR cluster.

    Args:
        cluster_id (str): The ID of the EMR cluster.
        jar_file (str): The JAR file for the EMR step.
        step_args (list): List of arguments for the EMR step.

    Returns:
        str: The ID of the added EMR step.
    """
    response = client.add_job_flow_steps(
        JobFlowId=cluster_id,
        Steps=[
            {
                'Name': 'test12',
                'ActionOnFailure': 'CONTINUE',
                'HadoopJarStep': {
                    'Jar': jar_file,
                    'Args': step_args
                }
            },
        ]
    )
    print("The EMR step is added")
    return response['StepIds'][0]

def get_status_of_step(cluster_id, step_id):
    """
    Gets the status of an EMR step.

    Args:
        cluster_id (str): The ID of the EMR cluster.
        step_id (str): The ID of the EMR step.

    Returns:
        str: The status of the EMR step.
    """
    response = client.describe_step(
        ClusterId=cluster_id,
        StepId=step_id
    )
    return response['Step']['Status']['State']

def wait_for_step_to_complete(cluster_id, step_id):
    """
    Waits for an EMR step to complete.

    Args:
        cluster_id (str): The ID of the EMR cluster.
        step_id (str): The ID of the EMR step.
    """
    print("The cluster id : {}".format(cluster_id))
    print("The EMR step id : {}".format(step_id))
    while True:
        try:
            status = get_status_of_step(cluster_id, step_id)
            if status == 'COMPLETED':
                break
            else:
                print("The step is {}".format(status))
                sleep(40)
        except Exception as e:
            logging.info(e)

def terminate_cluster(cluster_id):
    """
    Terminates an EMR cluster.

    Args:
        cluster_id (str): The ID of the EMR cluster.
    """
    try:
        client.terminate_job_flows(JobFlowIds=[cluster_id])
        logger.info("Terminated cluster %s.", cluster_id)
    except ClientError:
        logger.exception("Couldn't terminate cluster %s.", cluster_id)
        raise

# Snowflake Operator to load data into Snowflake
# snowflake_load = SnowflakeOperator(
#     task_id="snowflake_load",
#     sql="""ALTER EXTERNAL TABLE s3_to_snowflake.PUBLIC.Iris_dataset REFRESH""",
#     snowflake_conn_id="snowflake_conn"
# )

# Define Airflow tasks
with dag:
    create_emr_cluster_task = PythonOperator(
        task_id='create_emr_cluster',
        python_callable=create_emr_cluster,
        dag=dag,
    )

    ingest_layer_task = PythonOperator(
        task_id='ingest_layer',
        python_callable=add_step_emr,
        op_args=[
            '{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}',
            'command-runner.jar',
            ['spark-submit',
             '--master', 'yarn',
             '--deploy-mode', 'cluster',
             's3://airflowemr/scripts/ingest.py']
        ],
        dag=dag,
    )

    poll_step_layer_task = PythonOperator(
        task_id='poll_step_layer',
        python_callable=wait_for_step_to_complete,
        op_args=['{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}', '{{ ti.xcom_pull("ingest_layer")}}'],
        dag=dag,
    )

    transform_layer_task = PythonOperator(
        task_id='transform_layer',
        python_callable=add_step_emr,
        op_args=[
            '{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}',
            'command-runner.jar',
            ['spark-submit',
             '--master', 'yarn',
             '--deploy-mode', 'cluster',
             's3://airflowemr/scripts/Movie_Recommendation.py']
        ],
        dag=dag,
    )

    poll_step_layer2_task = PythonOperator(
        task_id='poll_step_layer2',
        python_callable=wait_for_step_to_complete,
        op_args=['{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}', '{{ ti.xcom_pull("transform_layer")}}'],
        dag=dag,
    )

    terminate_emr_cluster_task = PythonOperator(
        task_id='terminate_emr_cluster',
        python_callable=terminate_cluster,
        op_args=['{{ ti.xcom_pull("create_emr_cluster")["JobFlowId"]}}'],
        dag=dag,
    )

# Set up task dependencies
create_emr_cluster_task >> ingest_layer_task >> poll_step_layer_task >> transform_layer_task >> poll_step_layer2_task >> terminate_emr_cluster_task 
# >> snowflake_load
