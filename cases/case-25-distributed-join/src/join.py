from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.getOrCreate()
clicks = spark.read.parquet('/data/clicks')
catalog = spark.read.parquet('/data/catalog')

joined = clicks.join(catalog, 'product_id')
rows = joined.collect()
lookup = {r.product_id: r.category for r in rows}
result = clicks.rdd.map(lambda r: (r.user_id, lookup.get(r.product_id))).toDF()
result.write.mode('overwrite').parquet('/output/features')
