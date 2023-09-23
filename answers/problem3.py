# Problem 3 - Data Analysis
# -------------------------
# For every year, for every weather station, calculate:
# * Average maximum temperature (in degrees Celsius)
# * Average minimum temperature (in degrees Celsius)
# * Total accumulated precipitation (in centimeters)

# Ignore missing data when calculating these statistics.
# Design a new data model to store the results. Use NULL for statistics that cannot be calculated.
# Your answer should include the new model definition as well as the code used to calculate the new values and store them in the database.


# Import required modules and functions from psycopg2
import psycopg2
from psycopg2 import sql

# Establish a connection to the PostgreSQL database
connection = psycopg2.connect(
    dbname="weather_data",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
cursor = connection.cursor()

# Query to fetch distinct station IDs and years from weather_data table
cursor.execute("""
    SELECT DISTINCT station, EXTRACT(YEAR FROM date)
    FROM weather_data
""")
# Store the fetched data for further processing
stations_and_years = cursor.fetchall()

# Create a new table `weather_stats` to store aggregated weather statistics
# This table includes average max and min temperatures and total precipitation for each station per year
cursor.execute('''
CREATE TABLE IF NOT EXISTS weather_stats (
    id SERIAL PRIMARY KEY,         # Auto-incrementing ID
    station VARCHAR(255),         # Station identifier
    year INT,                      # Year of the recorded data
    avg_max_temp FLOAT,            # Average of maximum temperatures
    avg_min_temp FLOAT,            # Average of minimum temperatures
    total_precipitation FLOAT      # Total precipitation (scaled)
)
''')

# Loop through each unique combination of station and year
for station, year in stations_and_years:
    
    # For each combination, calculate the following statistics:
    # - Average of maximum temperatures (excluding invalid readings represented by -9999)
    # - Average of minimum temperatures (excluding invalid readings represented by -9999)
    # - Total precipitation (excluding invalid readings and scaled by dividing by 10)
    cursor.execute(sql.SQL("""
        INSERT INTO weather_stats (station, year, avg_max_temp, avg_min_temp, total_precipitation)
        SELECT 
            %s,            # Current station
            %s,            # Current year
            AVG(max_temp) FILTER (WHERE max_temp > -9999),  # Filter out invalid max temperatures
            AVG(min_temp) FILTER (WHERE min_temp > -9999),  # Filter out invalid min temperatures
            SUM(precipitation) FILTER (WHERE precipitation > -9999) / 10  # Filter and scale precipitation
        FROM 
            weather_data 
        WHERE 
            station = %s AND EXTRACT(YEAR FROM date) = %s  # Filter by current station and year
    """), (station, year, station, year))

# Commit the database changes
connection.commit()

# Close the cursor and connection to free up resources
cursor.close()
connection.close()
