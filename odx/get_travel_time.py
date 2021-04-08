'''
MATCH TRIPS
'''
import sqlite3
import geopandas as gpd
import math

input_origins = pd.read_csv("input_origins.csv")
input_dests = pd.read_csv("input_dests.csv")
odx_data = pd.read_csv("1019_trips_filtered.csv")

stops_geo = pd.read_csv("./ODX_files/PT_2017-10-10_stops.csv")
census_tracts = pd.read_csv("census_tracts_bounded.csv")


'''
CREATE AND CONNECT TO LOCAL DATABASE OF ODX TRIP DATA
'''
od_trips_db = "od_trips.db"    # database of filtered ODX trips: origin, destination, depart_time, arr_time, transfers, travel_time
conn = sqlite3.connect(od_trips_db)  # connect to that database (will create if it doesn't already exist)
c = conn.cursor()  # make cursor into database (allows us to execute commands)
c.execute('''CREATE TABLE IF NOT EXISTS od_trips (origin int, dest int, dep_time timestamp, arr_time timestamp, transfers int, travel_time int, UNIQUE(origin, dest, dep_time, arr_time, transfers, travel_time));''') # run a CREATE TABLE command

mylen = odx_data.shape[0]
for i in range(mylen):
    org = int(odx_data['origin'][i])        #must typecast ints in sql or it will be represented as binary
    dest = int(odx_data['dest'][i])

    dep_time = odx_data['dep_time'][i].to_pydatetime()
    arr_time = odx_data['arr_time'][i].to_pydatetime()

    trans = int(odx_data['transfers'][i])
    tt = int(odx_data['travel_time'][i])
    c.execute('''INSERT OR IGNORE into od_trips VALUES (?,?,?,?,?,?);''',(org,dest,dep_time,arr_time,trans,tt))

conn.commit() # commit commands
conn.close() # close connection to database




'''
add column to input OD pairs of geoid of census tract it is in
'''
from shapely.geometry import Point
from shapely import wkt

census_tracts['geometry'] = census_tracts['geometry'].apply(wkt.loads)
cgdf = gpd.GeoDataFrame(census_tracts, geometry = 'geometry')

start_tract_id_col = []
end_tract_id_col = []

mylen = input_origins.shape[0]

for i in range(mylen):
    p_start = Point(input_origins['X'][i], input_origins['Y'][i])
    p_end = Point(input_dests['X'][i], input_dests['Y'][i])
    start_tract = 0
    end_tract = 0

    #loop through census_tracts
    for i in range(801):
        geometry = cgdf['geometry'][i]
        if (p_start.within(geometry)):
            start_tract = cgdf['geoid10'][i]
        if (p_end.within(geometry)):
            end_tract = cgdf['geoid10'][i]

    #append corresponding tract ids to row in OD_pairs dataframe
    start_tract_id_col.append(start_tract)
    end_tract_id_col.append(end_tract)

# cast the two geo_id columns into dataframes and append to OD_pairs
start_col = pd.DataFrame(start_tract_id_col, columns = ['start_tract'])
end_col = pd.DataFrame(end_tract_id_col, columns = ['end_tract'])
input_origins = pd.concat([input_origins, start_col], axis=1)
input_dests = pd.concat([input_dests, end_col], axis=1)



'''
SUPPORTING FUNCTION: CALCULATE LON/LAT MIN&MAX BOUNDS GIVEN A GEO-COORDINATE
- cast coordinate into corresponding census tract bounds calculated by geobounds.py and stored in census_tracts_bounded.csv
'''
def bounds(tract_geoid):
    tract = census_tracts.loc[census_tracts['geoid10'] == tract_geoid]
    if tract.empty:
        return None
    return (tract['minx'].iloc[0], tract['maxx'].iloc[0], tract['miny'].iloc[0], tract['maxy'].iloc[0])



'''
CREATE AND CONNECT A LOCAL DATABASE OF TRANSIT STOPS AND CORRESPONDING LON/LAT
* note: only unique stop_id in the database
** Only need to run this snippet once, comment out later to save time
'''
stops_db = "stops.db"
conn_s = sqlite3.connect(stops_db)
c_s = conn_s.cursor()
c_s.execute('''CREATE TABLE IF NOT EXISTS stops (stop_id int UNIQUE, stop_lat float, stop_lon float);''')

mylen = stops_geo.shape[0]
for i in range(mylen):
    id = int(stops_geo['stop_id'][i])
    lat = stops_geo['stop_lat'][i]
    lon = stops_geo['stop_lon'][i]
    c_s.execute('''INSERT OR IGNORE into stops VALUES (?,?,?);''',(id, lat, lon))

conn_s.commit()
conn_s.close()




'''
OD PAIR -> ODX TRIP MATCHING
1. For each Origin-Destination pair, get all stops in same tract as the origin,
    and another set of stops in same tract as the destination coordinate
2. Find all trips in ODX database that match origin and destination id
3. Sort matching trips by travel time and calculate 75th percentile and median travel time
4. Store in results_travel_time local database (can easily be extracted and converted to pandas dataframe/csv)
'''
conn_s = sqlite3.connect(stops_db)
c_s = conn_s.cursor()

conn = sqlite3.connect(od_trips_db)
c = conn.cursor()

results_db = "results.db"
conn_results = sqlite3.connect(results_db)
c_r = conn_results.cursor()
c_r.execute('''CREATE TABLE IF NOT EXISTS results_travel_time (time_start int, time_end int, start_lat float, start_lon float, end_lat float, end_lon float, start_stop int, end_stop int, transfers int, median_tt int, quartile_tt int, UNIQUE(time_start, time_end, start_lat, start_lon, end_lat, end_lon, start_stop, end_stop, transfers, median_tt, quartile_tt));''')


OD_pairs_len = input_origins.shape[0]

#Iterate through each desired Origin-Destination pair
for i in range(OD_pairs_len):
    print(i)

    #extract origin and destination lat/lon in geo coordinates
    or_lat = input_origins['Y'][i]
    or_lon = input_origins['X'][i]
    dest_lat = input_dests['Y'][i]
    dest_lon = input_dests['X'][i]
    start_id = input_origins['start_tract'][i]
    end_id = input_dests['end_tract'][i]

    # get min&max bounds on lat/lon given desired radius (lat_min, lat_max, lon_min, lon_max)
    origin_bounds = bounds(start_id)
    dest_bounds = bounds(end_id)

    # case where origin or destination coordinates are not in a census tract
    if origin_bounds is None or dest_bounds is None:
        c_r.execute('''INSERT OR IGNORE into results_travel_time VALUES (?,?,?,?,?,?,?,?,?,?,?);''',(28800, 28800, or_lat, or_lon, dest_lat, dest_lon, None, None, None, None, None))
    else:
        query = (
            '''
            SELECT * FROM stops WHERE
                (stop_lon > ? AND stop_lon < ?) AND (stop_lat > ? AND stop_lat < ?);
            '''
            )

        # get a list of stops within census tract
        or_neighbors = c_s.execute(query, origin_bounds).fetchall()
        dest_neighbors = c_s.execute(query, dest_bounds).fetchall()


        # Find all possible trips in ODX database that match neighboring origin and destination id
        matching_trips = []
        for origin in or_neighbors:
            for dest in dest_neighbors:
                matching_OD = c.execute(
                    '''SELECT * FROM od_trips WHERE origin = ? AND dest = ?;''',
                    (origin[0], dest[0])).fetchall()

                if matching_OD:
                    for trip in matching_OD:
                        dep_dt = datetime.strptime(trip[2], '%Y-%m-%d %H:%M:%S')
                        if abs(dep_dt.hour - 8) < 2:
                            matching_trips.append(trip)

        conn.commit()
        conn_s.commit()


        if (len(matching_trips)>0):
            matching_trips.sort(key = lambda x: x[5])
            quartile_index = math.floor(0.75*len(matching_trips))   #75th percentile index
            median_index = math.floor(0.5*len(matching_trips))      #median index
            q_trip = matching_trips[quartile_index]
            m_trip = matching_trips[median_index]

            c_r.execute('''INSERT OR IGNORE into results_travel_time VALUES (?,?,?,?,?,?,?,?,?,?,?);''',(q_trip[2], q_trip[3], or_lat, or_lon, dest_lat, dest_lon, q_trip[0], q_trip[1], q_trip[4], m_trip[5], q_trip[5]))


        conn_results.commit()


# Uncomment to visualize results
# res = c_r.execute('''SELECT * FROM results_travel_time''').fetchall()
# for trip in res:
#    print('mytrip', i, trip)



conn_results.close()
conn.close()
conn_s.close()
