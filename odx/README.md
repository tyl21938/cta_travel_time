## origin destination inference (ODX) data


**Inputs**
* `input_origins.csv` and `input_dests.csv`, which can be found in the main directory
* ODX dataset
    * Raw data from 9/19/2019 cannot be uploaded due to size and access restrictions.
* A set of geographical bounds to determine to nearest transit stops to an origin or destination
    * `CT2010.geojson` represents the geometry of Chicago census tracts from the 2010 census count
    * `census_tracts_bounded.csv` extracts the information from `CT2010.geojson` into a `csv` dataframe format
* `PT_2017-10-10_stops.csv` maps stop_ids to their geographical latitude and longitudes


**Output**
* A sqlite table `results_travel_time.db` whose contents resemble:
```
time_start  time_end  start_lat   start_lon   end_lat   end_lon   start_stop    end_stop    transfers   median_tt   quartile_tt
8:00:00     8:20:05   -87.6673    42.0179     -87.6903  42.0023   501           35          0           1000        1250
7:56:35     8:15:45   -87.6561    41.9886     -87.6456  41.9247   794           1102        1           200         300
```
* A histogram of travel times
![alt text](https://github.mit.edu/jtl-transit/cta-travel-time/blob/master/odx/ODX_quartileTT_histogram.png "Logo Title Text 1")


### **Methodology**
=====================

**`geobounds.py`** - Prestep: Bounds Processing
    * To delineate the realm of possible trips between an origin-destination, we specify a boundary around it so that only trips within the origin boundary and subsequent destination boundary will be considered a valid trip.
    * The boundaries are represented by census tracts, whose raw data format is `CT2010.geojson`
    * `geobounds.py` takes `CT2010.geojson` as input and outputs `census_tracts_bounded.csv` to represent geometry in a more efficient format for processing.

**`ODX_filter_data.ipynb`** - Filter ODX data, match trips, get result table, and visualize results
  
  *Note: The Jupyter notebook is the amalgamation of `open_data.py`, `get_travel_time.py`, and `visualize_results.py`. It is more efficient to use the Jupyter notebook implementation for debugging to avoid excessive data processing*
  1. Filter ODX data - **`open_data.py`**
      * The ODX data comes in a `snappy.parquet` file. We read its relevant columns into a pandas dataframe
      * The first steps involve filtering out all trips with invalid status ids, and eliminating trips falling outside of our desired date, 10/19/2017.
      * We divide these trips into direct trips and trips that require one or more transfers.
      * Both sets are filtered and delineated into individual trips specified by the following fields : `origin`, `destination`, `departure_time`, `arrival_time`, `transfers`, `travel_time`.
      * All trips are combined into a singular dataframe
  2. Match trips - **`get_travel_time.py`**
      * Insert all filtered ODX trips into a sqlite database `od_trips.db`
      * Match each input OD pair to its respective census tractid using `census_tracts_bounded.csv` as input
      * Create a database of transit stops and their lon/lat in `stops.db` using `PT_2017-10-10_stops.csv` as input
      * For each OD pair, get all stops in the same census tract as the origin, and all stops in the same census tract as the destination
      * For all combinations of possible origin-stop to destination-stop trips, find matching trips in the ODX database 
      * For all matching trips, find the median and 75th quartile trip
      * Insert the 75th quartile trip in a database `results_travel_time.db`
  3. Visualizing results - **`visualize_results.py`**
      * Connect to the database, see descriptive characteristics, and visualize with histogram
