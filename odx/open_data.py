import pyarrow.parquet as pq
from datetime import datetime
import pandas as pd


'''
Table Description:
All Columns:
    service_dt | transit_account_id | dw_transaction_id | transaction_dtm | trans_status_key
    operator_nm | bus_id | order_in_group | group_size | group_leader_id | order_in_chain
    chain_size | boarding_stop | next_gtfs_stop | next_transaction | avl_bus_route
    boarding_sequence | inferred_alighting_gtfs_stop | alighting_stop_sequence
    alighting_time | distance_in_meters | num_behind_gate_legs | route_sequence
    direction_sequence | boarding_platform_sequence | alighting_platform_sequence
    alighting_time_sequence | transfer_inference | journey_size | last_transaction_in_journey
    time_gap | circuit | od_straightlinedist | insert_dtm
Relevant Columns:
    trans_status_key | boarding_stop | inferred_alighting_gtfs_stop | transfer_inference
    journey_size | transaction_dtm | alighting_time
'''
odx = pq.read_table('October 19/ode.odx_journeys_2017-10-19 03_00_00-2017-10-19 03_00_00-05_00.snappy.parquet')
            # columns = ['trans_status_key', 'boarding_stop', 'inferred_alighting_gtfs_stop', 'transfer_inference',
            #             'journey_size', 'transaction_dtm', 'alighting_time']
pq.write_table(odx, 'tmstp_oct_odx.snappy.parquet', use_deprecated_int96_timestamps=True)


'''
DataFrame Description:
    Beginning: 1,602,696 rows
    Filter out invalid: 1,404,762 rows
'''
odx_formated = pq.read_table('October 19/tmstp_oct_odx.snappy.parquet', columns = ['trans_status_key', 'boarding_stop', 'inferred_alighting_gtfs_stop', 'transfer_inference',
                        'journey_size', 'transaction_dtm', 'alighting_time'])
odx_df = odx_formated.to_pandas()

trips = odx_df.loc[odx_df['trans_status_key']==0]
trips = trips.reset_index(drop=True)


trips['str_transTime'] = trips['transaction_dtm'].astype(str)
new = trips["str_transTime"].str.split(" ", n = 1, expand = True)
trips["trans_date"]= new[0]
trips["trans_time"]= new[1]

trips['str_alightTime'] = trips['alighting_time'].astype(str)
temp = trips["str_alightTime"].str.split(" ", n = 1, expand = True)
trips["alight_date"]= temp[0]
trips["alight_time"]= temp[1]

trips = trips.loc[trips['trans_date']=='2017-10-19']  #data includes both 10/19 and 10/20 - extract for only 10/19


trans_trips = trips.loc[trips['journey_size']>1]
trans_trips = trans_trips.reset_index(drop=True)

direct_trips = trips.loc[trips['journey_size']==1]
direct_trips = direct_trips.loc[direct_trips['alight_date']=='2017-10-19']
direct_trips = direct_trips.loc[direct_trips['transfer_inference']=='Destination']
direct_trips = direct_trips.reset_index(drop=True)


# Direct Trips
ODX_trips = {'origin':[], 'dest':[], 'dep_time':[], 'arr_time':[], 'transfers':[], 'travel_time':[]}

rows = direct_trips.shape[0]
for i in range(rows):
    trans = direct_trips['journey_size'][i]
    trans_inference = direct_trips['transfer_inference'][i]

    #single ride trip: origin -> destination
    if (trans==1 and trans_inference =='Destination'):
        ODX_trips['origin'].append(direct_trips['boarding_stop'][i])
        ODX_trips['dest'].append(direct_trips['inferred_alighting_gtfs_stop'][i])
        ODX_trips['dep_time'].append(direct_trips['transaction_dtm'][i])
        ODX_trips['arr_time'].append(direct_trips['alighting_time'][i])
        ODX_trips['transfers'].append(trans - 1)

        alighting_time = direct_trips['alighting_time'][i]
        trans_time = direct_trips['transaction_dtm'][i]

        if (type(alighting_time) is pd.Timestamp):
            diff = (alighting_time - trans_time).seconds
            ODX_trips['travel_time'].append(diff)
        else:
            ODX_trips['travel_time'].append(None)

    #check for errors:
    if len(ODX_trips['origin'])!=len(ODX_trips['dest']): print(i)




# Transfer Trips
ODX_trans_trips = {'origin':[], 'dest':[], 'dep_time':[], 'arr_time':[], 'transfers':[], 'travel_time':[]}

row = trans_trips.shape[0]
for i in range(row):
    trans = trans_trips['journey_size'][i]
    trans_inference = trans_trips['transfer_inference'][i]

    #trip containing transfers
    if (trans > 1 and i>0):
        dep_time = trans_trips['transaction_dtm'][i]

        if (trans_trips['transfer_inference'][i-1] == 'Destination' and trans_inference == 'Transfer'): #must be a new Origin of trip
            ODX_trans_trips['origin'].append(trans_trips['boarding_stop'][i])
            ODX_trans_trips['dep_time'].append(dep_time)

        if (trans_inference == 'Destination' and trans_trips['transfer_inference'][i-1] == 'Transfer'):
            ODX_trans_trips['dest'].append(trans_trips['inferred_alighting_gtfs_stop'][i])
            ODX_trans_trips['transfers'].append(trans - 1)

            if (trans_trips['alight_date'][i]=='2017-10-19'):
                ODX_trans_trips['arr_time'].append(trans_trips['alighting_time'][i])

                alighting_time = trans_trips['alighting_time'][i]

                if (type(alighting_time) is pd.Timestamp):
                    diff = (alighting_time - dep_time).seconds
                    ODX_trans_trips['travel_time'].append(diff)
                else:
                    ODX_trans_trips['travel_time'].append(None)
            else:
                ODX_trans_trips['arr_time'].append(None)
                ODX_trans_trips['travel_time'].append(None)

    elif (trans>1 and i==0):
        dep_time = trans_trips['transaction_dtm'][i]
        ODX_trans_trips['origin'].append(trans_trips['boarding_stop'][i])
        ODX_trans_trips['dep_time'].append(dep_time)

    #check for errors:
    if len(ODX_trans_trips['origin']) - len(ODX_trans_trips['dest']) >= trans: print(i)


ODX_trips_all = {'origin':[], 'dest':[], 'dep_time':[], 'arr_time':[], 'transfers':[], 'travel_time':[]}

ODX_trips_all['origin'].extend(ODX_trips['origin'])
ODX_trips_all['dest'].extend(ODX_trips['dest'])
ODX_trips_all['dep_time'].extend(ODX_trips['dep_time'])
ODX_trips_all['arr_time'].extend(ODX_trips['arr_time'])
ODX_trips_all['transfers'].extend(ODX_trips['transfers'])
ODX_trips_all['travel_time'].extend(ODX_trips['travel_time'])

ODX_trips_all['origin'].extend(ODX_trans_trips['origin'])
ODX_trips_all['dest'].extend(ODX_trans_trips['dest'])
ODX_trips_all['dep_time'].extend(ODX_trans_trips['dep_time'])
ODX_trips_all['arr_time'].extend(ODX_trans_trips['arr_time'])
ODX_trips_all['transfers'].extend(ODX_trans_trips['transfers'])
ODX_trips_all['travel_time'].extend(ODX_trans_trips['travel_time'])


ODX_final_trips = pd.DataFrame(ODX_trips_all)
ODX_final_trips = ODX_final_trips.dropna()
ODX_final_trips = ODX_final_trips.reset_index(drop=True)
ODX_final_trips.to_csv('1019_trips_filtered.csv')
