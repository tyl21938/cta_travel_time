import pandas as pd
import csv
import numpy


#census tracts origin
census_tracts = "ODpoints_tracts.csv"

#load census tracts OD points into a pandas dataframe
ODtracts_df = pd.read_csv(census_tracts)

#sample in increments of 10% and write to excel file
for percentage in range(10, 110, 10):
    mysample = ODtracts_df.sample(frac = percentage/100)
    mysample.to_csv('{}%ODpoints.csv'.format(percentage), index=None, header=True)
