#!/usr/bin/jython
from org.opentripplanner.scripting.api import OtpsEntryPoint

# Instantiate an OtpsEntryPoint
otp = OtpsEntryPoint.fromArgs(['--graphs', '.',
                               '--router', 'chicago'])

# Start timing the code
import time
start_time = time.time()

# Get the default router
router = otp.getRouter('chicago')

#set times {GTFS data from 4 October 2018 to 31 December 2018}
year = 2017
month = 10
day = 19
h = 8
m = 00
s = 00

# Create a default request for a given departure time
req = otp.createRequest()
req.setDateTime(year, month, day, h, m, s)                # set departure time
req.setMaxTimeSec(50000)                                  # set a limit to maximum travel time (seconds)
req.setModes('WALK,BUS,RAIL,TRAM,TRANSIT,SUBWAY')         # define transport mode ("WALK,CAR, TRANSIT, TRAM,RAIL,SUBWAY,FUNICULAR,GONDOLA,CABLE_CAR,BUS")
req.setClampInitialWait(0)                                # clamp the initial wait time to zero

# Read Points of Destination - The file points.csv contains the columns GEOID, X and Y.
points = otp.loadCSVPopulation('ODpoints_tracts.csv', 'Y', 'X')
dests = otp.loadCSVPopulation('ODpoints_tracts.csv', 'Y', 'X')

# Create a CSV output
matrixCsv = otp.createCSVOutput()
matrixCsv.setHeader([ 'depart_time', 'origin', 'destination', 'walk_distance', 'travel_time', 'boardings' ])


# Start Loop
for origin in points:
  #print "Processing origin: ", origin
  req.setOrigin(origin)
  spt = router.plan(req)
  if spt is None:
      continue

  # Evaluate the SPT for all points
  result = spt.eval(dests)

  # Add a new row of result in the CSV output
  for r in result:
    matrixCsv.addRow([str(h) + ":" + str(m) + ":00", origin.getStringData('GEOID'), r.getIndividual().getStringData('GEOID'), r.getWalkDistance() , r.getTime(), r.getBoardings()])



# Save the result
matrixCsv.save('traveltime_matrix_'+ str(month) + "." + str(day) + "-" + str(h) + "." + str(m) + '.csv')

# Stop timing the code
print("Elapsed time was %g seconds" % (time.time() - start_time))
