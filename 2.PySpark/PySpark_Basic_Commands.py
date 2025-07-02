# Databricks notebook source
# MAGIC %md
# MAGIC ## Spark Code using Python and SQL

# COMMAND ----------

# MAGIC %md
# MAGIC ### Command to find the file path

# COMMAND ----------

dbutils.fs.ls('FileStore/tables/')

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Importing the files

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.1. Reading the file (.csv)

# COMMAND ----------

df = spark.read.format('csv')\
    .option('inferSchema',True)\
    .option('header',True)\
    .load('/FileStore/tables/customer_order_data.csv')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.2. Display the records
# MAGIC 2 ways to display:
# MAGIC
# MAGIC     1.  df.show()
# MAGIC     2.  df.display()

# COMMAND ----------

df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.3. Reading the JSON file

# COMMAND ----------

df_json = spark.read.format('json')\
    .option('inferSchema',True)\
    .option('headers',True)\
    .option('multiline',False)\
    .load('/FileStore/tables/restaurants.json')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 1.4. Display the JSON data

# COMMAND ----------

df_json.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Print Schema Definition
# MAGIC - This will print the column names, their data types and nullable.

# COMMAND ----------

df.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Manually define the column data types in the schema

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.1. Using SQL Schema method

# COMMAND ----------

#1. Define the schema with column name and data types
my_schema = '''
customer_ID integer 
,customer_Name string 
,Customer_email string 
,Customer_Contact_Number string 
,DOB date 
,order_type string 
,order_Qty integer 
,order_date date 
,Shipment_Date date 
,price_per_unit double 
,total_order_amount double
'''

# 2. Import the data with custom created schema
df_my_schema = spark.read.format('csv')\
  .schema(my_schema)\
  .option('header',True)\
  .load('/FileStore/tables/customer_order_data.csv')

# 3. Display records
df_my_schema.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 3.2. Using StructType() schema

# COMMAND ----------

#1. Import Libraries
from pyspark.sql.types import *
from pyspark.sql.functions import *

#2. Define custom Schema
my_struct_schema = StructType([
 StructField('customer_ID', IntegerType(), True) 
,StructField('customer_Name', StringType(), True) 
,StructField('Customer_email', StringType(), True) 
,StructField('Customer_Contact_Number', StringType(), True) 
,StructField('DOB', DateType(),True) 
,StructField('order_type', StringType(), True) 
,StructField('order_Qty', IntegerType(), True) 
,StructField('order_date', DateType(),True) 
,StructField('Shipment_Date', DateType(),True) 
,StructField('price_per_unit', DoubleType(), True)  
,StructField('total_order_amount', DoubleType(), True)
])

#3. Import file using custom schema
df_struct_schema = spark.read.format('csv')\
  .schema(my_struct_schema)\
  .option('header',True)\
  .option('dateFormat','dd-mm-yyyy')\
  .load('/FileStore/tables/customer_order_data.csv')

#4. Display Records
df_struct_schema.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4. Transformations

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.1. Select() only the required columns

# COMMAND ----------

#1. Simple option
df.select('customer_id','Customer_name','Customer_email').display()

# COMMAND ----------

# Second Option
df.select(col('customer_id'),col('Customer_name'),col('Customer_email')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.2. Alias() to rename the column names in the select

# COMMAND ----------

df.select(col('Customer_name').alias('Customer Full Name')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.3. Filter() / Where() to filter the records

# COMMAND ----------

#Filter on single columnsamples.tpch.customer
df.filter(col('Order_type') == 'Online').display()

# COMMAND ----------

#Filter on multiple columns
df.filter((col('Order_type') == 'Online') & (col('total_order_amount') >= 500)).display()

# COMMAND ----------

#Using isNull() and isin() functions
df.filter((col('shipment_date').isNull() & col('order_type').isin('Online','Phone Order'))).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.4. withColumnRenamed(): to rename the column at DataFrame level

# COMMAND ----------

df.withColumnRenamed('DOB','Birth Date').display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.5. withColumn(): To add new column to the DataFrame

# COMMAND ----------

#Import the data from csv file and store in a variable
df2 = spark.read.format('csv')\
.option('inferSchema',True)\
.option('header',True)\
.load('/FileStore/tables/customer_order_data.csv')

from pyspark.sql.functions import *
#Adding a New column with a constant value using lit() function
df2 = df2.withColumn('DiscountRate',lit(0.1))

df2.display()

# COMMAND ----------

# Deriving a new column from existing columns
df2 = df2.withColumn('Discounted_price_per_unit',bround(col('price_per_unit') - (col('price_per_unit') * col('DiscountRate')),2))

df2.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.6. withColumn().Regex(): Replace the column content using Regex

# COMMAND ----------

df2 = df2.withColumn('Order_type',regexp_replace(col('Order_type'),'Online','Online order'))\
    .withColumn('Order_type',regexp_replace(col('Order_type'),'In-Store','In-Store order'))
df2.display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.7. withColumn().cast(): For Type Casting the column type

# COMMAND ----------

df2.withColumn('DOB',col('DOB').cast(StringType())).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.8. Sort(): Sort the dataset

# COMMAND ----------

#Sorting on single column
df2.sort(col('Order_Qty').desc()).display()

# COMMAND ----------

#Sorting on multiple colums: By order qty desc and customer name asc
df2.sort(['Order_Qty','customer_name'],ascending=[0,1]).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.9. Limit(): To limit the number of records

# COMMAND ----------

df2.limit(10).display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.10. Drop(): To drop one or multiple columns

# COMMAND ----------

# Drop a single column
df2.drop('Discounted_price_per_unit').display()

# COMMAND ----------

# Drop multiple columns
df2.drop('DiscountRate','Discounted_price_per_unit').display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.11. Drop_duplicates(): To remove the duplicates from data

# COMMAND ----------

# Drop all duplicates
df2.dropDuplicates().display()

# COMMAND ----------

# Drop based on subset of columns
df2.drop_duplicates(subset=['Order_Type','Order_qty']).display()

# COMMAND ----------

# Drop duplicates by considering all the columns
df2.distinct().display()

# COMMAND ----------

# MAGIC %md
# MAGIC #### 4.12. Union() and Union_ByName()

# COMMAND ----------

# MAGIC %md
# MAGIC ##### 4.12.1. union()

# COMMAND ----------

# Prepare the data for Union operation
data1 = [(1,'Name1'),
         (2,'Name2')]

data2 = [(1,'Name1'),
         (3,'Name3'),
         (4,'Name4')]

# Create a schema with Data types
schema = 'id Int, name String'

# Convert the data into a DataFrame
d1 = spark.createDataFrame(data1,schema)
d2 = spark.createDataFrame(data2,schema)

d1.display()
d2.display()
# Union operation
d1.union(d2).display()


# COMMAND ----------

# MAGIC %md
# MAGIC ##### 4.12.1. unionByName()

# COMMAND ----------

# Prepare the data for Union operation
data1 = [('Name1',1),
         ('Name2',2)] #Order of both data columns are different

data2 = [(1,'Name1'),
         (3,'Name3'),
         (4,'Name4')]

# Create a schema with Data types
schema1 = 'name String, id String'
schema2 = 'id String, name String'

# Convert the data into a DataFrame
d1 = spark.createDataFrame(data1,schema1)
d2 = spark.createDataFrame(data2,schema2)

d1.display()
d2.display()
# Union by name operation
d1.unionByName(d2).display()


# COMMAND ----------

# MAGIC %md
# MAGIC ### 5. String Functions
# MAGIC
# MAGIC -   INITCAP()
# MAGIC -   UPPER()
# MAGIC -   LOWER()

# COMMAND ----------

#Prepare the data
# Prepare the data for Union operation
data = [('Name1',1),
         ('namE2',2),
         ('name3',3)]

schema = 'name string, id int'
dd = spark.createDataFrame(data,schema)

# INITCAP
dd.select(initcap('name')).display()

# UPPER
dd.select(upper('name').alias('NameUpper')).display()

# LOWER
dd.select(lower('name')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 6. Date Functions
# MAGIC
# MAGIC - CURRENT_DATE()
# MAGIC - DATE_ADD()
# MAGIC - DATE_SUB()
# MAGIC - DATEDIFF()
# MAGIC - DATE_FORMAT()

# COMMAND ----------

# Curr_date()
df2 = df.withColumn('Curr_date',current_date())

# Date_add()
df2 = df2.withColumn('Week_after',date_add('Curr_date',7))

# Date_sub()
df2 = df2.withColumn('Week_before',date_sub('Curr_date',7))

# Datediff()
df2 = df2.withColumn('Date_diff',datediff('week_after','week_before'))

# Date_format()
df2 = df2.withColumn('Format_date',date_format('week_after','dd-MM-yyyy'))

df2.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 7. Handling Nulls
# MAGIC
# MAGIC - dropna()
# MAGIC - fillna()

# COMMAND ----------

# Dropping Nulls using dropna():
# Parameters: Any -> Drop records (rows) if Any column values with Null
#             All -> Drop records (rows) Only if all columns are Null

# Create the Dataframe
data = [(1, 'Value1', 'Desc123'),
         (2, 'Value2', None),
         (3, None, 'desc134'),
         (4, None, None),
         (None, None, None)
         ]
schema3 = 'id string, value string, desc string'

d3 = spark.createDataFrame(data, schema3)

print('Drop using Any:\n',d3.display())

# Drop rows using All
print('Drop using All:\n')
d3.dropna('all').display()

# Drop rows using Any
print('Drop using Any:\n')
d3.dropna('any').display()

# Drop rows using Subset say Value
print('Drop using Subset:\n')
d3.dropna(subset=['value']).display()

# COMMAND ----------

# Filling Nulls using fillna()

# fillna() for all the Nulls
print('fillna() for All values:\n')
d3.fillna('NA').display()

# fillna() for  Subset of values
print('fillna() for  Subset of values:\n')
d3.fillna('NA',subset=['desc']).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 8. Split(), Indexing and Explode()

# COMMAND ----------

# Split()
print('Split: \n')
df2.withColumn('customer_name',split('customer_name', ' ')).display()

# Indexing
print('Indexing: \n')
df2.withColumn('customer_name',split('customer_name', ' ')[1]).display()

# Explode(): Split the rows into multiple rows based on the column selected
print('Explode (Row level): \n')
df2.withColumn('customer_name',explode(split('customer_name',' '))).display()

# Split the string and populate into multiple columns
print('Split (Column level / New column creation based on split) 1st Method: \n')
df2.withColumn('FirstName',split('customer_name',' ')[0])\
    .withColumn('LastName',split('customer_name',' ')[1])\
        .display()
#OR
print('Split (Column level / New column creation based on split) 2nd Method: \n')
df3 = df2.withColumn('FirstName',split('customer_name',' ').getItem(0))\
    .withColumn('LastName',split('customer_name',' ').getItem(1))
df3.display()


# COMMAND ----------

# MAGIC %md
# MAGIC ### 9. Array_contains()
# MAGIC
# MAGIC - To find a text within a array

# COMMAND ----------

# Split the customer name column and create an array
df4 = df2.withColumn('Split_customer_name',split('customer_name', ' '))

# Find the text Dr. in the array
df4.withColumn('array_text_flag',array_contains('Split_customer_name','Dr.')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 10. Group_by()

# COMMAND ----------

# Group by on single column
df2.groupBy('order_type').agg(count('order_Qty').alias('Order_qty_count'),\
    round(sum('total_order_amount'),2).alias('Order_amount'))\
        .display()

# Group by on multiple columns
df2.groupBy('order_type',year('order_date')).agg(count('order_Qty').alias('Order_qty_count'),\
    round(sum('total_order_amount'),2).alias('Order_amount'))\
        .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 11. Collect_list()
# MAGIC
# MAGIC - Group the data into a list

# COMMAND ----------

# Prepare the data
data = [('user1', 'value1'),
        ('user1', 'value2'),
        ('user2', 'value1'),
        ('user2', 'value2'),
        ('user3', 'value3')
        ]

schema = 'user string, value string'

d = spark.createDataFrame(data,schema)

d.groupBy('user').agg(collect_list('value')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 12. Pivot()

# COMMAND ----------

df2.groupBy(year('order_date').alias('order_year'))\
    .pivot('order_type')\
    .agg(sum('order_Qty'))\
    .sort('order_year')\
    .display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 13. When-Otherwise()

# COMMAND ----------

# With single condition
df2.withColumn('Bulk_normal',when(col('order_Qty') <= 10, 'Normal').otherwise('Bulk')).display()

# With multiple condition
df2.withColumn('Bulk_order_type', when((col('order_Qty') <=10) & (col('order_type').isin('Online','Phone Order')), 'Online-Normal')\
                                .when((col('order_Qty') <=10) & (col('order_type').isin('In-Store')), 'Offline-Normal')\
                                .when((col('order_Qty') > 10) & (col('order_type').isin('In-Store')), 'Offline-Bulk')\
                                .otherwise('Online-Bulk')).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 14. Joins()
# MAGIC
# MAGIC - INNER Join
# MAGIC - LEFT Join
# MAGIC - RIGHT Join
# MAGIC - FULL Join
# MAGIC - ANTI Join

# COMMAND ----------

# Prepare data
data1 = [
    (1, 'Name1', 'Desc123'),
    (2, 'Name2', 'Desc234'),
    (3, 'Name3', 'Desc345'),
    (4, 'Name4', 'Desc456'),
    (5, 'Name5', 'Desc789')
]

data2 = [
    (1, 10000.00, 'HR'),
    (2, 15000.00, 'Manager'),
    (3, 8000.00, 'Assistant'),
    (6, 25000.00, 'HOD')
]

schema1 = 'id INT, name string, desc string'
schema2 = 'id INT, sal double, designation string'

d1 = spark.createDataFrame(data1,schema1)
d2 = spark.createDataFrame(data2,schema2)

d1.display()
d2.display()

# Inner join
print('Inner join Results:\n')
d1.join(d2,d1['id']==d2['id'],'inner').display()

# Left join
print('Left join Results:\n')
d1.join(d2,d1['id']==d2['id'],'left').display()

# Right join
print('Right join Results:\n')
d1.join(d2,d1['id']==d2['id'],'right').display()

# Full join
print('Full join Results:\n')
d1.join(d2,d1['id']==d2['id'],'full').display()

# Anti join
print('Anti join Results:\n')
d1.join(d2,d1['id']==d2['id'],'anti').display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 15. Window Functions()
# MAGIC
# MAGIC - Row_number()
# MAGIC - RANK()
# MAGIC - DENSE_RANK()
# MAGIC - Cumulative_sum()

# COMMAND ----------

# Import the window library
from pyspark.sql.window import Window

# Row_number()
print('Row Number: \n')
df3.withColumn('row_num', row_number().over(Window.orderBy('customer_ID'))).display()

#Rank()
print('Rank: \n')
df3.withColumn('rank',rank().over(Window.orderBy('order_type'))).display()

#Dense_Rank()
print('Dense Rank: \n')
df3.withColumn('dense_rank',dense_rank().over(Window.orderBy(col('order_type').desc()))).display()

# Cumulative_sum()
# Define specification
cumsum_spec = Window.orderBy('order_type').rowsBetween(Window.unboundedPreceding,Window.currentRow)
# Calculate Cumulative Sum
print('Cumulative Sum: \n')
df.withColumn('CumSum',round(sum('total_order_amount').over(cumsum_spec),2)).display()

# COMMAND ----------

# MAGIC %md
# MAGIC ### 16. Writing the Data to CSV, Table and Parquet format

# COMMAND ----------

# MAGIC %md
# MAGIC #### 16.1.1. Write Data to CSV

# COMMAND ----------

# Write to CSV
df.write.format('csv')\
  .mode('overwrite')\
  .save('/FileStore/tables/CSV/data.csv')
print('File Saved!')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 16.1.2. Write Data to parquet
# MAGIC

# COMMAND ----------

# Write to Parquet
df.write.format('parquet')\
  .mode('overwrite')\
  .save('/FileStore/tables/CSV/data.parquet')
print('File Saved!')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 16.1.3. Write Data to table

# COMMAND ----------

# Write to Table
df.write.format('csv')\
    .mode('overwrite')\
    .option('header', True)\
    .saveAsTable('my_table_new')
print('Table Created!')

# COMMAND ----------

# MAGIC %md
# MAGIC #### 16.2. Data Writing Modes
# MAGIC
# MAGIC - Append()
# MAGIC - Overwrite()
# MAGIC - Error()
# MAGIC - Ignore()

# COMMAND ----------

# Append()
df.write.format('csv')\
  .mode('append')\
  .save('/FileStore/tables/CSV/data.csv')
print('File Appended Successfully!')

# Overwrite()
df.write.format('csv')\
  .mode('overwrite')\
  .save('/FileStore/tables/CSV/data.csv')
print('File overwritten Successfully!')

# Ignore()
df.write.format('csv')\
  .mode('ignore')\
  .save('/FileStore/tables/CSV/data.csv')
print('File Writing Successful ignoring Errors!')

# Error()
print('Error writing File')
df.write.format('csv')\
  .mode('error')\
  .save('/FileStore/tables/CSV/data.csv')

# COMMAND ----------

# MAGIC %md
# MAGIC ## SPARK SQL

# COMMAND ----------

# Create a Temporary View
df.createTempView('my_temp_view')

# Now in next cell change the language to SQL

# COMMAND ----------

# MAGIC %sql
# MAGIC select * from my_temp_view where order_type = 'Online'

# COMMAND ----------

df_sql = spark.sql("select * from my_temp_view where order_type = 'Online'")

df_sql.display()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Managed vs External tables

# COMMAND ----------

# MAGIC %md
# MAGIC In **PySpark** (and Apache Spark in general), there are two types of tables you can work with when storing data in a **Spark SQL** environment:
# MAGIC
# MAGIC 1. **Managed Tables**
# MAGIC 2. **External Tables**
# MAGIC
# MAGIC Both types of tables are part of the **Hive metastore** (or equivalent storage management system) in Spark, but they differ in terms of data storage and how the data is managed.
# MAGIC
# MAGIC ### 1. **Managed Tables**
# MAGIC A **managed table** is a table where both the **metadata** (the table schema and structure) and the **data** (the actual content) are managed by Spark or the underlying cluster.
# MAGIC
# MAGIC #### Key Characteristics of Managed Tables:
# MAGIC - **Data & Metadata**: Spark handles both the **data** and **metadata** (schema, table name, columns, etc.).
# MAGIC - **Location**: The data for a managed table is stored **inside the default Spark warehouse** (usually the `spark.sql.warehouse.dir` location). This is typically a directory within the system’s storage, and Spark manages it automatically.
# MAGIC - **Deletion of Data**: If you **drop a managed table**, both the **metadata** and the **data** are deleted from the system.
# MAGIC - **Use Case**: Ideal for when you want Spark to fully manage the lifecycle of both the table and its data.
# MAGIC
# MAGIC #### Example of Creating a Managed Table:
# MAGIC ```python
# MAGIC # Create a managed table (data and metadata are stored by Spark)
# MAGIC df.write.mode('overwrite').saveAsTable('my_managed_table')
# MAGIC
# MAGIC # Drop the table (data and metadata are deleted)
# MAGIC spark.sql("DROP TABLE my_managed_table")
# MAGIC ```
# MAGIC
# MAGIC - **`saveAsTable('my_managed_table')`** stores both the data and metadata in Spark’s default location.
# MAGIC - When you drop the table using **`DROP TABLE`**, the underlying data is also deleted.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### 2. **External Tables**
# MAGIC An **external table** is a table where the **metadata** is managed by Spark, but the **data** resides in an external location (like **HDFS**, **Azure Data Lake**, **Amazon S3**, or other external storage systems). Spark doesn’t manage the actual data directly; it just references the data stored outside of its default warehouse.
# MAGIC
# MAGIC #### Key Characteristics of External Tables:
# MAGIC - **Data**: The actual data resides in an **external location** (outside the Spark-managed storage, like HDFS, S3, or Azure Data Lake).
# MAGIC - **Metadata**: Spark still manages the **metadata** (the schema, table structure, etc.).
# MAGIC - **Location**: The data for an external table is stored in a user-defined location (e.g., a path in HDFS or cloud storage). Spark references this location but does not manage the data itself.
# MAGIC - **Deletion of Data**: If you drop an external table, only the **metadata** (schema) is deleted from the metastore. The actual **data** in the external location remains intact.
# MAGIC - **Use Case**: Ideal for when you want Spark to manage only the metadata but keep the data outside Spark's control, especially when you're working with shared data sources.
# MAGIC
# MAGIC #### Example of Creating an External Table:
# MAGIC ```python
# MAGIC # Create an external table (data is stored externally, not managed by Spark)
# MAGIC df.write.option("path", "/path/to/external/storage").mode("overwrite").saveAsTable("my_external_table")
# MAGIC
# MAGIC # Drop the table (only metadata is deleted; data remains intact)
# MAGIC spark.sql("DROP TABLE my_external_table")
# MAGIC ```
# MAGIC
# MAGIC - **`saveAsTable('my_external_table')`**: The data is stored in the specified external location (`/path/to/external/storage`), and only the metadata is stored in the Hive metastore.
# MAGIC - When you drop the table, Spark removes the **metadata** but **does not delete the data** in the external storage.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Key Differences Between Managed and External Tables:
# MAGIC
# MAGIC | **Feature**            | **Managed Table**                                    | **External Table**                                 |
# MAGIC |------------------------|------------------------------------------------------|----------------------------------------------------|
# MAGIC | **Data Management**     | Data is managed by Spark (both data and metadata).   | Data is stored externally; Spark manages only metadata. |
# MAGIC | **Storage Location**    | Data is stored in the default Spark warehouse.       | Data is stored at a user-defined location (e.g., HDFS, S3). |
# MAGIC | **Dropping Table**      | Both data and metadata are deleted when dropped.     | Only metadata is deleted; data remains in the external location. |
# MAGIC | **Use Case**            | Suitable for when Spark manages both the data and metadata. | Suitable when the data is shared or external and Spark should only manage metadata. |
# MAGIC
# MAGIC ### When to Use Managed vs. External Tables:
# MAGIC
# MAGIC - **Managed Table**: Use a managed table if you want Spark to take care of both **data** and **metadata**, and you don’t mind the data being stored in Spark’s internal storage.
# MAGIC   - Example Use Case: Storing data that is purely for Spark processing and doesn’t need to be shared with external systems.
# MAGIC
# MAGIC - **External Table**: Use an external table if you have data that is stored externally (e.g., in **HDFS**, **Azure Data Lake**, **S3**, or another cloud storage system), and you want Spark to manage the **metadata** without affecting the actual data.
# MAGIC   - Example Use Case: Data that is shared with multiple systems, or data that exists outside of Spark’s control but you want to query it using Spark SQL.
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Example Scenarios
# MAGIC
# MAGIC 1. **Managed Table Example:**
# MAGIC    - You have a dataset in Spark that you want to store in a **Parquet** format, and Spark manages both the metadata and the data. You don’t need to share the data externally.
# MAGIC    ```python
# MAGIC    df.write.format('parquet').mode('overwrite').saveAsTable('my_managed_table')
# MAGIC    ```
# MAGIC
# MAGIC 2. **External Table Example:**
# MAGIC    - You have data in **Amazon S3** that you want to query with Spark. Spark only manages the metadata, and the actual data stays in **S3**.
# MAGIC    ```python
# MAGIC    df.write.format('parquet').mode('overwrite').option('path', 's3a://bucket/path/to/data').saveAsTable('my_external_table')
# MAGIC    ```
# MAGIC
# MAGIC ---
# MAGIC
# MAGIC ### Conclusion:
# MAGIC - **Managed Tables** are best when you want Spark to handle both the metadata and data.
# MAGIC - **External Tables** are useful when you want to store the data externally but still manage the schema with Spark.
# MAGIC
# MAGIC Both types of tables are valuable depending on your data storage and management needs in the Spark ecosystem. Let me know if you need more details!

# COMMAND ----------


