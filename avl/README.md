## Data
* `Sept2019_avl_data.csv` is a file of all CTA AVL data from September 2019, it is not uploaded here due to size and access restrictions
* `gtfs_trips_sept2019.txt` is the `trips.txt` file extracted from the CTA GTFS data for corresponding dates. Please extract from the zip file and add to the folder. The full GTFS dataset can be found in the `gtfs` folder as `gtfs-9-19-19.zip`. 
* `stops.txt` is another file found in `gtfs-9-19-19.zip`, extracted to use as a filtering input

Each row of the data represents a GPS location update of a bus with labeled stop_id, route, and event_time. In light of computational complexity, we filter the data for the specific date we want (9/19/2019). Section 1 of `filter_generate.py` accompolishes this and outputs `avl_9_19_19.csv`.

## Generating `trips.txt` and `stop_times.txt`
Run section 2, 3, and 4 to generate `trips.csv` and `stop_times.csv`, then manually convert to `trips.txt` and `stop_times.txt`.

Manual conversion into `.txt` is needed because the pandas to_csv() function does not maintain formating when directly writing to `.txt` files.

## Retrospective GTFS packaging
* Unzip the `gtfs-9-19-19.zip` data into a folder. 
* Replace the original `trips.txt` and `stop_times.txt` files with the ones generated above. 
* Delete `frequencies.txt` from the folder.
* Rezip the folder (make sure it's not a folder within a zipped folder)

## Calculating travel times
We now have a retrospective GTFS package and can follow instructions in the `gtfs` folder to calculate travel times. Use `create_otp_traveltime.py` as the script.
