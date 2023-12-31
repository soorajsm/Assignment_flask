# -*- coding: utf-8 -*-
"""Assignment_Solution_Sooraj_Moger.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aWW1xktdQ2Euh5XsH2I5OXuQQBQe7g-R
"""

# importing the libraries

import pandas as pd

# choosing the google drive

from google.colab import drive
drive.mount('/content/drive')

# Commented out IPython magic to ensure Python compatibility.
# Navigating to the required directory

# %cd '/content/drive/My Drive/data/'

# Reading the dataset which is in the form of csv file

df = pd.read_csv('HousingDataset.csv',low_memory=False)

# Removing the duplicates from the dataframe

df=df.drop_duplicates()
df

# Remmoving the required columns from the dataframe

df.drop(columns=['ad_type','title','description','l4','l5','l6'],inplace=True)
df

# Removing the null values from the table

df_cleaned = df.dropna(subset=['lon', 'lat', 'price_period', 'bedrooms', 'surface_total', 'rooms', 'price', 'surface_covered'])
df_cleaned

# connecting to the Sqlite database and dividing dataframe into two seperate tables

import sqlite3

conn = sqlite3.connect('property_data.db')

property_details_df = df_cleaned[['id', 'start_date', 'end_date', 'created_on', 'lat', 'lon', 'l1', 'l2', 'l3', 'rooms', 'bedrooms', 'bathrooms', 'surface_total', 'surface_covered']]
property_price_details_df = df_cleaned[['id', 'price', 'currency', 'price_period', 'property_type', 'operation_type']]

# inserting the two tables to the database

property_details_df.to_sql('Property_Details', conn, if_exists='replace', index=False)
property_price_details_df.to_sql('Property_Price_Details', conn, if_exists='replace', index=False)

# 1) Executing the first query which is to get the property details having more than 1M and property location is "Estados Unidos"

import sqlite3
conn = sqlite3.connect('property_data.db')

query='''select a.* from Property_Details a,Property_Price_Details b
        where a.id=b.id and b.price>1000000 and a.l1="Estados Unidos"; ''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result1 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result1)

# 2) Executing the second query which is Categorize properties based on their surface area as 'Small' if it's less than 50 square meters, 'Medium' if it's
# between 50 and 100 square meters, and 'Large' if it's greater than 100 square meters:

import sqlite3
conn = sqlite3.connect('property_data.db')

query='''SELECT pd.*,
    CASE
        WHEN pd.surface_total < 50 THEN 'Small'
        WHEN pd.surface_total >= 50 AND pd.surface_total <= 100 THEN 'Medium'
        ELSE 'Large'
    END AS surface_area_category,pp.*
  FROM
    Property_Details pd,Property_Price_Details pp
  where
    pd.id = pp.id;
 ''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result2 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result2[:1000])

# 3) List all properties (id) in the "Belgrano" neighborhood (l3) that have the same number of bedrooms and bathrooms as another property in the dataset:

import sqlite3
conn = sqlite3.connect('property_data.db')

query= """SELECT id
FROM property_details
WHERE l3 = 'Belgrano'
  AND (bedrooms, bathrooms) IN (
    SELECT bedrooms, bathrooms
    FROM property_details
    GROUP BY bedrooms, bathrooms
    HAVING COUNT(*) > 1
  );""";

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result3 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result3)

# 4) Calculate the average price per square meter (price / surface_total) for each property type (property_type) in the "Belgrano" neighborhood (l3):

import sqlite3
conn = sqlite3.connect('property_data.db')

query='''
SELECT property_type,
       AVG(price / surface_total) AS avg_price_per_sq_meter
FROM property_price_details a,property_details b
WHERE l3 = 'Belgrano' and a.id=b.id
GROUP BY property_type;
''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result4 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result4)

# 5) Identify properties that have a higher price than the average price of properties with the same number of bedrooms and bathrooms.

import sqlite3
conn = sqlite3.connect('property_data.db')

query='''SELECT pd.id, ppd.price
FROM property_details pd
JOIN property_price_details ppd ON pd.id = ppd.id
WHERE ppd.price > (
    SELECT AVG(ppd_avg.price)
    FROM property_details pd_avg
    JOIN property_price_details ppd_avg ON pd_avg.id = ppd_avg.id
    WHERE pd_avg.bedrooms = pd.bedrooms AND pd_avg.bathrooms = pd.bathrooms
);''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result5 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result5[:500])

# 6) Calculate the cumulative price for each property type, ordered by the creation date.

import sqlite3
conn = sqlite3.connect('property_data.db')

query= '''
SELECT
    ppd.property_type,
    pd.created_on,
    ppd.price,
    SUM(ppd.price) OVER (PARTITION BY ppd.property_type ORDER BY pd.created_on) AS cumulative_price
FROM
    property_details pd
JOIN
    property_price_details ppd
ON
    pd.id = ppd.id
ORDER BY
    ppd.property_type, pd.created_on;
''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result6 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result6[:1000])

# 7) Identify the 10 locations (l3) with the highest total surface area (sum of surface_total) of properties listed for sale (operation_type = 'Venta'):

import sqlite3
conn = sqlite3.connect('property_data.db')

query= '''
SELECT pd.l3, SUM(pd.surface_total) AS total_surface_area
FROM property_details pd
JOIN property_price_details ppd ON pd.id = ppd.id
WHERE ppd.operation_type = 'Venta'
GROUP BY pd.l3
ORDER BY total_surface_area DESC
LIMIT 10;
''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result7 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result7)

# 8) Find the top 5 most expensive properties (based on price) in the "Palermo" neighborhood (l3) that were listed in August 2020:

import sqlite3
conn = sqlite3.connect('property_data.db')

query= '''
SELECT pd.id, pd.l3, ppd.price, pd.created_on
FROM property_details pd
JOIN property_price_details ppd ON pd.id = ppd.id
WHERE pd.l3 = 'Palermo'
    AND pd.created_on BETWEEN '01/08/2020' AND '31/08/2020'
ORDER BY ppd.price DESC
LIMIT 5;
''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result8 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result8)

# 9) Find the top 3 properties with the highest price per square meter (price divided by surface area) within each property type.

import sqlite3
conn = sqlite3.connect('property_data.db')

query= '''
WITH ranked_properties AS (
    SELECT
        pd.id,
        ppd.property_type,  -- Corrected column name here
        ppd.price / pd.surface_total AS price_per_sq_meter,
        ROW_NUMBER() OVER(PARTITION BY ppd.property_type ORDER BY ppd.price / pd.surface_total DESC) AS rank_within_type
    FROM property_details pd
    JOIN property_price_details ppd ON pd.id = ppd.id
)
SELECT
    rp.id,
    rp.property_type,
    rp.price_per_sq_meter,
    pd.l3 AS neighborhood,
    pd.created_on AS listing_date
FROM ranked_properties rp
JOIN property_details pd ON rp.id = pd.id
WHERE rp.rank_within_type <= 3
ORDER BY rp.property_type, rp.rank_within_type;
''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result9 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result9)

# 10) Find the top 3 locations (l1, l2, l3) with the highest average price per square meter (price / surface_total) for properties listed for sale (operation_type = 'Venta') in the year 2020. Exclude locations with fewer than 10 properties listed for sale in 2020 from the results.


import sqlite3
conn = sqlite3.connect('property_data.db')

query= '''
WITH FilteredProperties AS (
    SELECT
        pd.l1,
        pd.l2,
        pd.l3,
        AVG(ppd.price / pd.surface_total) AS avg_price_per_sq_meter,
        COUNT(*) AS property_count
    FROM
        Property_Details pd
    INNER JOIN
        Property_Price_Details ppd ON pd.id = ppd.id
    WHERE
        ppd.operation_type = 'Venta'
        AND pd.created_on BETWEEN '01/01/2020' AND '12/31/2020'
    GROUP BY
        pd.l1, pd.l2, pd.l3
    HAVING
        COUNT(*) >= 10
)
SELECT
    l1,
    l2,
    l3,
    avg_price_per_sq_meter
FROM
    FilteredProperties
ORDER BY
    avg_price_per_sq_meter DESC
LIMIT 3;

''';

cursor = conn.cursor()
cursor.execute(query)
columns = [column[0] for column in cursor.description]
result10 = [dict(zip(columns, row)) for row in cursor.fetchall()]
cursor.close()

conn.close()
print(result10)

# installing the flask-ngrok

!pip install flask-ngrok
!ngrok update

# downoading ngrok to the googe collab notebook

!curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok

# Adding the autotoken

!ngrok config add-authtoken 2VtjvdSUFv9TkgxjZlKa576QNu7_BMgv2UU3CkpSnC4cLrvx

from flask_ngrok import run_with_ngrok
from flask import Flask,jsonify,request
import threading


index='''"<h1>Hey there !!</h1>"
  "<div><h2>its Sooraj here</h3></div>"
   "<div><h4>To see the results of the 10 queries navigate to the below mentioned paths</h4></div>"
   "<div><ol>
   <li>/question-1</li>
   <li>/question-2</li>
   <li>/question-3</li>
   <li>/question-4</li>
   <li>/question-5</li>
   <li>/question-6</li>
   <li>/question-7</li>
   <li>/question-8</li>
   <li>/question-9</li>
   <li>/question-10</li>
   </ol></div>"
  '''


# Running the flask app
app = Flask(__name__)
app.config['NGROK_PORT'] = 5001

# Starting the ngrok when app is run
run_with_ngrok(app)

#API endpoints the index page
@app.route('/',methods=['GET'])
def indexpage():
   return index


#API endpoints for question-1
@app.route('/question-1',methods=['GET'])
def question1():
   return result1

#API endpoints for question-2
@app.route('/question-2',methods=['GET'])
def question2():
  return result2

#API endpoints for question-3
@app.route('/question-3',methods=['GET'])
def question3():
  return result3

#API endpoints for question-4
@app.route('/question-4',methods=['GET'])
def question4():
  return result4

#API endpoints for question-5
@app.route('/question-5',methods=['GET'])
def question5():
  return result5

#API endpoints for question-6
@app.route('/question-6',methods=['GET'])
def question6():
  return result6

#API endpoints for question-7
@app.route('/question-7',methods=['GET'])
def question7():
  return result7

#API endpoints for question-8
@app.route('/question-8',methods=['GET'])
def question8():
  return result8

#API endpoints for question-9
@app.route('/question-9',methods=['GET'])
def question9():
  return result9

#API endpoints for question-10
@app.route('/question-10',methods=['GET'])
def question10():
  return result10

#error handling : invalid question number
@app.errorhandler(404)
def page_not_found(error):
    return 'Invalid Question Number', 404

if __name__ == '__main__':
    app.run()