#!/bin/env python
"""
Created on Saturday March 21, 2020 at 8:39 PM
@author: kong44

Program Description: 
    This script is a modified template. It performs an automated data quality 
    checking by using functions. First, an error check for invalid, no data entries. 
    Then values outside a threshold for the data is replaced with NaN. 
    Some entries for min and max temp are in the wrong column, so those are swapped. 
    Finally, the difference in high and low temp for the day is calculated to 
    determine if it is outside the acceptable difference. 
    Raw and processed data is plotted to show the results. 

References: 
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
    https://stackoverflow.com/questions/29530232/how-to-check-if-any-value-is-nan-in-a-pandas-dataframe
    https://stackoverflow.com/questions/46168450/replace-a-specific-range-of-values-in-a-pandas-dataframe
    https://stackoverflow.com/questions/40159763/how-to-replace-a-range-of-values-with-nan-in-pandas-data-frame
    https://stackoverflow.com/questions/38901563/pandas-swap-columns-based-on-condition/38903431
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import figure

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "Date", "Precip", "Max Temp", "Min Temp", "Wind Speed". Function
    returns the completed DataFrame, and a dictionary designed to contain all 
    missing value counts."""
    
    # define column names
    colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

    # open and read the file
    DataDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
    DataDF = DataDF.set_index('Date')
    
    # define and initialize the missing data dictionary
    # Included other indexes
    ReplacedValuesDF = pd.DataFrame(0, index=["1. No Data","2. Gross Error","3. Swapped","4. Range Fail"], columns=colNames[1:])
     
    return( DataDF, ReplacedValuesDF )
 
def Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF ):
    """This check replaces the defined No Data value with the NumPy NaN value
    so that further analysis does not use the No Data values.  Function returns
    the modified DataFrame and a count of No Data values replaced."""

    # add your code here
    DataDF = DataDF.replace(-999, np.NaN) # replace -999 with NaN
    
    # isolate columns of the full DF, find all NaN values and sum the count
    # assign that summed count to the other DF
    ReplacedValuesDF.iloc[0,0]=DataDF['Precip'].isna().sum()
    ReplacedValuesDF.iloc[0,1]=DataDF['Max Temp'].isna().sum()
    ReplacedValuesDF.iloc[0,2]=DataDF['Min Temp'].isna().sum()
    ReplacedValuesDF.iloc[0,3]=DataDF['Wind Speed'].isna().sum()

    return( DataDF, ReplacedValuesDF )
    
def Check02_GrossErrors( DataDF, ReplacedValuesDF ):
    """This function checks for gross errors, values well outside the expected 
    range, and removes them from the dataset.  The function returns modified 
    DataFrames with data the has passed, and counts of data that have not 
    passed the check."""
 
    # add your code here
    # replace values in column of DF with NaN if outside of range
    DataDF['Precip'] = DataDF['Precip'].mask((DataDF['Precip'] > 25) | (DataDF['Precip'] < 0), np.NaN) 
    DataDF['Max Temp'] = DataDF['Max Temp'].mask((DataDF['Max Temp'] > 35) | (DataDF['Max Temp'] < -25), np.NaN)
    DataDF['Min Temp'] = DataDF['Min Temp'].mask((DataDF['Min Temp'] > 35) | (DataDF['Min Temp'] < -25), np.NaN)
    DataDF['Wind Speed'] = DataDF['Wind Speed'].mask((DataDF['Wind Speed'] > 10) | (DataDF['Wind Speed'] < 0), np.NaN)
    
    # The count from the gross error check is equal to the number of NaNs in the DF minus the number of previously counted NaNs
    ReplacedValuesDF.loc['2. Gross Error',:] = DataDF.isna().sum() - ReplacedValuesDF.sum()
    
    return( DataDF, ReplacedValuesDF )
    
def Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture is less than
    minimum air temperature, and swaps the values when found.  The function 
    returns modified DataFrames with data that has been fixed, and with counts 
    of how many times the fix has been applied."""
    
    # add your code here
    instances = len(DataDF.loc[DataDF['Min Temp'] > DataDF['Max Temp']]) # see where max temp is less than min temp, by row. Record how many times this happens
    
    # swap values inside the min and max temp column if Min > Max at that row
    DataDF["Min Temp"], DataDF["Max Temp"] = np.where(DataDF['Min Temp'] > DataDF['Max Temp'], [DataDF["Max Temp"], DataDF["Min Temp"]], [DataDF["Min Temp"], DataDF["Max Temp"] ])
    
    ReplacedValuesDF.loc['3. Swapped',:] = [0, instances, instances, 0] # new DF index accounts for the temperature error
    
    return( DataDF, ReplacedValuesDF )
    
def Check04_TmaxTminRange( DataDF, ReplacedValuesDF ):
    """This function checks for days when maximum air temperture minus 
    minimum air temperature exceeds a maximum range, and replaces both values 
    with NaNs when found.  The function returns modified DataFrames with data 
    that has been checked, and with counts of how many days of data have been 
    removed through the process."""
    
    # add your code here
    # see where max temp minus min temp is greater than 25, by row. Record how many times this happens
    instances2 = len(DataDF.loc[ (DataDF['Max Temp'] - DataDF['Min Temp']) > 25])
    
    # replace values inside the temp columns with NaN if the difference between between max and min for the day is > 25
    DataDF.loc[(DataDF['Max Temp'] - DataDF['Min Temp'] > 25), ['Max Temp','Min Temp']] = np.NaN

    ReplacedValuesDF.loc['4. Range Fail',:] = [0, instances2, instances2, 0] # new DF index accounts for the temperature range error
    return( DataDF, ReplacedValuesDF )

# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    fileName = "DataQualityChecking.txt"
    DataDF, ReplacedValuesDF = ReadData(fileName)
    
    print("\nRaw data.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check01_RemoveNoDataValues( DataDF, ReplacedValuesDF )
    
    print("\nMissing values removed.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check02_GrossErrors( DataDF, ReplacedValuesDF )
    
    print("\nCheck for gross errors complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check03_TmaxTminSwapped( DataDF, ReplacedValuesDF )
    
    print("\nCheck for swapped temperatures complete.....\n", DataDF.describe())
    
    DataDF, ReplacedValuesDF = Check04_TmaxTminRange( DataDF, ReplacedValuesDF )
    
    print("\nAll processing finished.....\n", DataDF.describe())
    print("\nFinal changed values counts.....\n", ReplacedValuesDF)
    
########################## Plotting and saving data to new file #############################################

# getting the raw data 
colNames = ['Date','Precip','Max Temp', 'Min Temp','Wind Speed']

RawDF = pd.read_csv("DataQualityChecking.txt",header=None, names=colNames,  
                         delimiter=r"\s+",parse_dates=[0])
RawDF = RawDF.set_index('Date')

# before and after plot of precip 
figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(DataDF.index, RawDF['Precip'],'b*', label = 'Before correction')
plt.plot(DataDF.index, DataDF['Precip'],'r*', label = 'After correction', markersize = 1.5)
plt.xlabel('Date')
plt.ylabel('Precipitation (mm)')
plt.title('Precipitation Before and After Correction')
plt.legend()
plt.savefig('Precipitation.png')
plt.close()
    
# before and after plot of max temp
figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(DataDF.index, RawDF['Max Temp'],'b*', label = 'Before correction')
plt.plot(DataDF.index, DataDF['Max Temp'],'r*', label = 'After correction', markersize = 1.5)
plt.xlabel('Date')
plt.ylabel('Temperature (C)')
plt.title('Max Air Temperature Before and After Correction')
plt.legend()
plt.savefig('Max Temp.png')
plt.close()
    
# before and after plot of min temp
figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(DataDF.index, RawDF['Min Temp'],'b*', label = 'Before correction')
plt.plot(DataDF.index, DataDF['Min Temp'],'r*', label = 'After correction', markersize = 1.5)
plt.xlabel('Date')
plt.ylabel('Temperature (C)')
plt.title('Minimum Air Temperature Before and After Correction')
plt.legend()
plt.savefig('Min Temp.png')
plt.close()
    
# before and after plot of wind speed
figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
plt.plot(DataDF.index, RawDF['Wind Speed'],'b*', label = 'Before correction')
plt.plot(DataDF.index, DataDF['Wind Speed'],'r*', label = 'After correction', markersize = 1.5)
plt.xlabel('Date')
plt.ylabel('Wind Speed (m/s)')
plt.title('Wind Speed Before and After Correction')
plt.legend()
plt.savefig('Wind Speed.png')
plt.close()

# output info on data that passed checks to a new file, with the same format as the original 
DataDF.to_csv('Passed_Checks.txt', header=None, sep=" ")
    
# output info on data that failed checks to a Tab delimited file 
ReplacedValuesDF.to_csv('Failed_Checks.txt', sep="\t")