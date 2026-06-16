from scripts.spark_session import get_spark_session


def run_smoke_test() -> None:
    spark = get_spark_session("PySparkSmokeTest")

    data = [
        ("CUST001", "Rohith", "Bengaluru"),
        ("CUST002", "Anil", "Kolar"),
    ]

    columns = ["customer_id", "name", "city"]

    df = spark.createDataFrame(data, columns)

    print("PySpark DataFrame created successfully")
    df.show()

    spark.stop()


if __name__ == "__main__":
    run_smoke_test()