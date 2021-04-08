## GTFS travel time methodology
This repository allows the user to reproduce the Origin-Destination travel time matrices generated in our CTA project with GTFS data, using Open Trip Planner (OTP) and Python.

**Inputs**
* An Open Street Map of the geographic region of interest in `.pbf` format 
* GTFS dataset in a `.zip` format
* OTP java application `.jar` file
* Jython standalone application `.jar` file
* `.csv` file with coordinates of interest (lon, lat)
* python script to generate matrices

**Output**
* A `.csv` file with the travel time between pairs of points. The travel time matrix will look something like this:
```
Departure_Time    Origin_ID     Destination_ID    walking_distance    travel_time     boardings
      17:30:00            1                 1                    0              0             0
      17:30:00            1                 2                   10           1234             1
      17:30:00            1                 3                   20           1234             2
      17:30:00            2                 1                   10           1234             1
      17:30:00            2                 2                    0              0             0
      17:30:00            2                 3                   30           1234             1
      17:30:00            3                 1                   20           1234             2
      17:30:00            3                 2                   30           1234             1
      17:30:00            3                 3                    0              0             0
```

* The point-to-point travel time output will look like this:
```
Departure_Time    Origin_ID     Destination_ID    walking_distance    travel_time     boardings
      17:30:00            1                 5                    0              0             0
      17:30:00            2                 6                   10           1234             1
      17:30:00            3                 7                   20           1234             2
      17:30:00            4                 8                   10           1234             1

```

#### Step 1: Install Jython 2.7 in your computer
[Here](http://www.jython.org/downloads.html) you find the executable jar for installing Jython

#### Step 2: Download files to your folder

Most of the files you need are in this repository already. The other files you can download from here:

* [jython-standalone.jar](http://search.maven.org/remotecontent?filepath=org/python/jython-standalone/2.7.0/jython-standalone-2.7.0.jar)
* [otp-1.3.0-shaded.jar](https://repo1.maven.org/maven2/org/opentripplanner/otp/1.3.0/otp-1.3.0-shaded.jar)
* chicago.pbf (replace with own `.pbf` file)

Make sure to download the above versions of OTP and Jython as the newer versions are not compatible when running step 3

#### Step 3: Build Graph.obj
Open your Command Prompt and run this line to set the directory where you've saved the files

`cd C:\Users\ting\Documents\otp-travel-time-matrix-chicago`

Now run this line to build the Graph.obj. Once OTP has built the Graph.obj, move it to the subdirectory `chicago`.

`java –Xmx10G -jar otp-1.3.0-shaded.jar --cache C:\Users\ting\Documents\otp-travel-time-matrix-chicago --basePath C:\Users\ting\Documets\otp-travel-time-matrix-chicago --build C:\Users\ting\Documents\otp-travel-time-matrix-chicago`


#### Step 4: Run the Python script

**4.1** The script `create_matrix.py` will return a travel time matrix for one single departure time (e.g. at 10:00:00 on  15-October-2018)

`c:\jython2.7.0\bin\jython.exe -J-XX:-UseGCOverheadLimit -J-Xmx10G -Dpython.path=otp-1.3.0-shaded.jar create_matrix.py`


**4.2** The script `create_ptp_traveltime.py` takes two separate input origin file and destination files and outputs the travel time between each iterative OD pair, rather than the combination of all origin destinations points.


More information about how to automate OTP [here](http://docs.opentripplanner.org/en/latest/Scripting/).


This code is adapted from:
[![DOI](https://zenodo.org/badge/44453629.svg)](https://zenodo.org/badge/latestdoi/44453629)
 
```
Pereira, R. H. M.; Grégoire, L.; Wessel, N.; Martins, J. (2019). Tutorial with reproducible example to estimate a travel time matrix
using OpenTripPlanner and Python. Retrieved from https://github.com/rafapereirabr/otp-travel-time-matrix. 
doi:10.5281/zenodo.3242134
```

