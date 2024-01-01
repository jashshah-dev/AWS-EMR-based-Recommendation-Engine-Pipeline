# Creating spark session 
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql import functions as f
from pyspark.sql.types import *

from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

spark = SparkSession.builder.appName("movierecommender") \
.config(conf=SparkConf([('spark.executor.memory', '16g'), 
                        ('spark.app.name', 'Spark Updated Conf'), 
                        ('spark.executor.cores', '6'), 
                        ('spark.cores.max', '6'), 
                        ('spark.driver.memory','16g')])) \
.getOrCreate()

# Loading data
movies_path = "movie.csv"
ratings_path = "rating.csv"

# Read movie data
movies = spark.read.format("csv").option("header", "true").load(movies_path, inferSchema="true")

# Read ratings data
ratings = spark.read.format("csv").option("header", "true").load(ratings_path, inferSchema="true")

movielens = ratings.join(movies,["movieId"],"left")
# Train set test set split
(train_set,temp) = movielens.randomSplit([8.0,1.0],seed=1)

# Make sure userId and movieId in the validation set are also in the train set (to avoid Cold Start Problem)
validation_set = (temp
    .join(train_set, ["userId"], "left_semi")
    .join(train_set, ["movieId"], "left_semi"))

# Identify and remove entries from the temporary dataset that are not present in the validation set
removed = (temp
    .join(validation_set, ["movieId", "userId"], "left_anti"))

# Update the train_set by removing entries that were identified and removed in the previous step
train_set = train_set.union(removed)

# Basic Model parameters
als = ALS(
        userCol = "userId",
        itemCol = "movieId",
        ratingCol = "rating",
)
# Evaluator
evaluator = RegressionEvaluator(
    metricName = "rmse",
    labelCol = "rating", 
    predictionCol = "prediction"
)
# Fit and Transform
model = als.fit(train_set)
predictions = model.transform(validation_set)
recommend_all_users = model.recommendForAllUsers(10).cache()
recommend_all_users.show(20,False)
USER_ID = 1238
(
    recommend_all_users
    .filter(f"userId == {USER_ID}")
    .withColumn("rec",f.explode("recommendations"))
    .select("userId",
            f.col("rec").movieId.alias("movieId"),
            f.col("rec").rating.alias("rating"),
           )
    .join(movies,"movieId")
    .orderBy("rating",ascending=False)
    .select("movieId","title")
).show(truncate=False)

USER_ID = 1238 

# Movies not rated by the selected user
movies_to_be_rated = (
    ratings
    .filter(f"userId != {USER_ID}")
    .select("movieId").distinct()
    .withColumn("userId",f.lit(USER_ID))
)
# Predictions on unwatched movies only
user_movie_preds = model.transform(movies_to_be_rated)
user_movie_preds.show()

# Movie recommendations for userId - Manually feeding unwatched movies
(user_movie_preds
.dropna()
.orderBy("prediction",ascending = False)
.limit(10)
.join(movies,["movieId"])
.select("userId","movieId","title",f.col("prediction").alias("rating"))
.orderBy("rating",ascending = False)
).show(truncate=False)

pandas_df = user_recommendations.toPandas()

# Create a message body with the movie recommendations
message_body = f"Top Movie Recommendations for User {USER_ID}:\n\n{pandas_df.to_string(index=False)}"

# AWS SNS configurations (replace these with your actual SNS configurations)
aws_access_key = 'YOUR_AWS_ACCESS_KEY'
aws_secret_key = 'YOUR_AWS_SECRET_KEY'
region_name = 'YOUR_AWS_REGION'
sns_topic_arn = 'YOUR_SNS_TOPIC_ARN'

# Initialize SNS client
sns_client = boto3.client('sns', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=region_name)

# Publish the message to the SNS topic
sns_client.publish(
    TopicArn=sns_topic_arn,
    Message=message_body,
    Subject=f"Movie Recommendations for User {USER_ID}"
)

# Stop the Spark session

