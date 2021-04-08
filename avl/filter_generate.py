import pandas as pd
import time
import numpy



'''
SECTION 1: Extract all AVL data from specific date into different csv files to optimize future computational complexity
'''
# avl_data = pd.read_csv('October_avl_data.csv')  #2.8GB file, takes 94s to read
# avl_data = avl_data[pd.notnull(avl_data['stop_id'])]
# avl_data = avl_data.reset_index(drop=True)
#
#
# new = avl_data['event_time'].str.partition(" ", True)
# avl_data['date'] = new[0]
# avl_data['time'] = new[2]
#
# date_gp = avl_data.groupby('date')
# oct27 = date_gp.get_group('2017-10-19')
# oct27.to_csv("avl_10_19_17.csv", index=False, header=True)



'''
Uncomment print statements to visualize data attributes
'''
# print(avl_data.head(10))
# print(avl_data.columns)
# print(avl_data.dtypes)
# print(avl_data.shape)



oct19 = pd.read_csv("avl_10_19_17.csv")
gtfs_trips = pd.read_csv("gtfs_trips_oct_17.txt", delimiter=",", usecols=['route_id', "service_id","trip_id", "schd_trip_id"])
grouped_avl = oct19.groupby("trip_id")      #2952 distinct trip_id



'''
SECTION 2:
gtfs_trips: download corresponding CTA gtfs data for the dates in inquiry.
                    Load the 'trips.txt' file. This script will match the service_id
                    provided within the CTA with the trip_id in AVL data.
Output: 'trips.csv' file with three columns: route_id, service_id, trip_id
Notes: We need to manually convert 'trips.csv' into 'trips.txt' by changing the extension
'''
avl_trip_df = {'route_id':[], 'service_id':[], 'trip_id':[]}

for trip_id, group in grouped_avl:
    match_rows = gtfs_trips.loc[gtfs_trips['schd_trip_id']==str(int(trip_id))]
    if not match_rows.empty:
        for i, row in match_rows.iterrows():
            avl_trip_df['route_id'].append(row['route_id'])
            avl_trip_df['service_id'].append(row['service_id'])
            avl_trip_df['trip_id'].append(row['trip_id'])

updated_trips = pd.DataFrame(avl_trip_df)






'''
SECTION 3:
create stop_times.txt, starting with empty dictionary that we will populate and convert to dataframe
'''
valid_stops = pd.read_csv('gtfs-10-22-17/stops.txt')
gtfs_stops = valid_stops.stop_id.unique()
gtfs_stops = set(gtfs_stops)

stop_times = {'trip_id':[], 'arrival_time':[], 'departure_time':[], 'stop_id':[], 'stop_sequence':[]}
#trip_id = int(119867480.0)


for trip_id, group in grouped_avl:
    match_rows = gtfs_trips.loc[gtfs_trips['schd_trip_id']==str(int(trip_id))]
    if not match_rows.empty:
        for i, time_update in group.iterrows():
            if time_update['stop_id'] in gtfs_stops:
                stop_times['trip_id'].append(match_rows['trip_id'].iloc[0])
                arrival_time = time_update['time']
                stop_times['arrival_time'].append(arrival_time)
                stop_times['departure_time'].append(arrival_time)
                stop_times['stop_id'].append(int(time_update['stop_id']))
                stop_times['stop_sequence'].append(time_update['stop_sequence'])

updated_stopTimes = pd.DataFrame(stop_times)




'''
SECTION 4:
Include rail trips and stop_times
'''
rail = gtfs_trips.loc[(gtfs_trips['route_id']=='Red') |
                      (gtfs_trips['route_id']=='Blue') |
                      (gtfs_trips['route_id']=='Brn') |
                      (gtfs_trips['route_id']=='G') |
                      (gtfs_trips['route_id']=='Org') |
                      (gtfs_trips['route_id']=='Pink') |
                      (gtfs_trips['route_id']=='P') |
                      (gtfs_trips['route_id']=='Y')]
rail = rail.drop(['schd_trip_id'], axis=1)

#append rail trips
updated_trips = updated_trips.append(rail, ignore_index=True)
updated_trips.to_csv("trips.csv", index=False, header=True)

#append rail stop_times
original_stopT = pd.read_csv('gtfs_oct19_stop_times.txt', usecols=['trip_id', 'arrival_time', 'departure_time', 'stop_id', 'stop_sequence'])
for i, r in rail.iterrows():
    new = original_stopT.loc[original_stopT['trip_id']==r['trip_id']]
    updated_stopTimes = updated_stopTimes.append(new, ignore_index=True)

updated_stopTimes.to_csv("stop_times.csv", index=False, header=True)

