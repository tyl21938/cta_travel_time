## cta-travel-time
MIT JTL CTA travel time project: This repository aims to allow the user to reproduce the Origin-Destination travel time methodologies generated in our CTA project with GTFS, AVL, and ODX data, using Open Trip Planner (OTP) and Python.

**General Data File Descriptions**
* `.csv` file with coordinates of interest (lon, lat)
* python script to open filter input OD data

**References**
```
Pereira, R. H. M.; Grégoire, L.; Wessel, N.; Martins, J. (2019). Tutorial with reproducible example to estimate a travel time matrix
using OpenTripPlanner and Python. Retrieved from https://github.com/rafapereirabr/otp-travel-time-matrix. 
doi:10.5281/zenodo.3242134
```



## Our Methodology

### Origin Destination Input Pairs: 
The origin-destination coordinate pairs were downloaded directly from the [LEDH Origin-Destination Employment Statistics](https://lehd.ces.census.gov/data/) (LODES) database (Version: LODES7, State/Territory: Illinois, Type: Origin-Destination, file name: `il_od_main_JT00_2017.csv.gz`). Click here for a [description](https://lehd.ces.census.gov/data/lodes/LODES7/LODESTechDoc7.4.pdf) of data fields. This dataset consists of all OD pairs in Illinois in 2017 that emcompasses all jobs with both workplace and residence in the state. 

#### Data filtering - `filter_OD.py` 
* Inputs: `il_od_main_JT00_2017.csv.gz` and `ODpoints_blocks.csv` 
* Outputs
     * Section 1: `all_Chicago_pairs.csv` is only the Chicago OD pairs from the Illinois dataset
     * Section 2: `geocoord_gt3jobs_chicago_lodes.csv` of all Chicago OD pairs representing more than 3 jobs
     * Section 3: `input_origins.csv` and `input_dests.csv` with only fields `GEOID`, `X`, and `Y` to use as inputs to running OTP travel times

### GTFS
We used Chicago Transportation Authority's scheduled GTFS public transit data found [here](https://transitfeeds.com/p/chicago-transit-authority/165), particularly the data file named `22 October 2017`, which contains the GTFS feed from 19 October 2017 - 31 December 2017. 

After generating `input_origins.csv` and `input_dests.csv` from above, follow the `README.md` instructions in the `gtfs` folder to calculate travel times. 

### AVL 
Next, we use Automatic Vehicle Location (AVL) data to create a "retrospective" GTFS feed based on real time bus arrivals. We then run the GTFS through the same OTP methodology used to calculate GTFS travel times.

Using the same `input_origins.csv` and `input_dests.csv` files, follow the `README.md` instructions in the `avl` folder to calculate travel times. 

### ODX
Finally, we leverage Origin Destination Inference (ODX) data, which is recorded per transaction as a singular trip made by an individual, including transfers. The public transit station 'tap-in' time is recorded, and the 'transfer' and 'tap-out' time is inferred.

Using the same `input_origins.csv` and `input_dests.csv` files, follow the `README.md` instructions in the `odx` folder to calculate travel times. 
