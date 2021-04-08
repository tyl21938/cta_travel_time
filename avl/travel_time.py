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

#set times {AVL and corresponding GTFS for 08/27/2019 and 08/28/2019}
year = 2017
month = 10
day = 19
h = 8
m = 00
s = 00

# Create a default request for a given departure time
req = otp.createRequest()
req.setDateTime(year, month, day, h, m, s)  # set departure time
req.setMaxTimeSec(50000)                   # set a limit to maximum travel time (seconds)
req.setModes('WALK,BUS,RAIL,TRAM,TRANSIT,SUBWAY')             # define transport mode ("WALK,CAR, TRANSIT, TRAM,RAIL,SUBWAY,FUNICULAR,GONDOLA,CABLE_CAR,BUS")
req.setClampInitialWait(0)                # clamp the initial wait time to zero


# Read Points of Destination - The file points.csv contains the columns GEOID, X and Y.
points = otp.loadCSVPopulation('input_origins.csv', 'Y', 'X')
destinations = otp.loadCSVPopulation('input_dests.csv', 'Y', 'X')


# Create a CSV output
matrixCsv = otp.createCSVOutput()
matrixCsv.setHeader([ 'date','depart_time', 'origin', 'destination', 'AVL_found', 'walk_distance', 'travel_time', 'boardings' ])

origin_list = []
dest_list = []

for origin in points:
    origin_list.append(origin)
for dest in destinations:
    dest_list.append(dest)

invalid_spts_first_round = 0

for i in range(len(origin_list)):
  print("Processing origin: ", i)
  req.setOrigin(origin_list[i])
  spt = router.plan(req)
  if spt is None:
      continue

  #Evaluate the SPT for each OD pair
  result = spt.eval(dest_list[i])

  #Add a new row of result in the CSV output
  if result is None:
      invalid_spts_first_round += 1
      matrixCsv.addRow([str(month)+"/"+str(day)+"/"+str(year), str(h) + ":" + str(m) + ":00", origin_list[i].getStringData('GEOID'), dest_list[i].getStringData('GEOID'), "false", None, None, None])

  if result is not None:
      matrixCsv.addRow([str(month)+"/"+str(day)+"/"+str(year), str(h) + ":" + str(m) + ":00", origin_list[i].getStringData('GEOID'), dest_list[i].getStringData('GEOID'), "true", result.getWalkDistance(), result.getTime(), result.getBoardings()])

# Save the result
matrixCsv.save('jobs_avl_traveltime_'+ str(month) + "." + str(day) + "-" + str(h) + "." + str(m) + '.csv')

print("Error rate of given date", invalid_spts_first_round, len(origin_list))

# Stop timing the code
print("Elapsed time was %g seconds" % (time.time() - start_time))
