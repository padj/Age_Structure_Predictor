#%% MORTALITY PREDICTOR

# This script takes in ONS male/female mortalities for 1981-2018, and uses 
# exponential regression to predict male/female mortalities per age up to 2100.

#%% imports
import pandas as pd
import numpy as np
import scipy.optimize
import matplotlib.pyplot as plt

#%% Preamble

# Import mortalities from ONS data. Drop the last entry as this is artifically
# set to 1 for an age of 101 as an artefact from using these datasets for 
# a health economics model.
maleMortality = pd.read_csv('../data/ONS_mortalities_male_parsed.csv')
maleMortality = maleMortality.drop(101)
femaleMortality = pd.read_csv('../data/ONS_mortalities_female_parsed.csv')
femaleMortality = femaleMortality.drop(101)

# years is the years for ONS data, future_years is for predictions.
years = np.arange(1981,2019)
future_years = np.arange(1981,2101)

# Function definitions
# This fitting function is the driving force for the prediction model. 
# Generalised exponential decay equation.
def fittingFunc(x, a, b):
    return a * np.exp(-b * x)

#def fittingFunc2(x, )
#%% Prediction

# Define lists to write to
predictedMaleMortalities = []
predictedMaleMortalitiesResiduals = []
predictedFemaleMortalities = []
predictedFemaleMortalitiesResiduals = []

# For each age
for i in range(len(maleMortality['Age'])):
    # set mortalityData to the relevant male mortalities for the age. Then
    # calculate coeffs for fitting function, calculate future data and residual.
    # Add fitted data and average residuals to lists. Repeat for female data.
    mortalityData = maleMortality[i:i+1].values[0,1:]
    mortalityData = mortalityData[::-1]
    [coeffs,covars] = scipy.optimize.curve_fit(fittingFunc,years-1980,mortalityData,check_finite=True)
    fittedData = fittingFunc(future_years-1980,*coeffs)
    #print(coeffs)
    #print(np.min(fittedData))
    #plt.scatter(years,mortalityData)
    #plt.plot(future_years,fittedData)
    residualAvg = np.mean(np.abs(mortalityData-fittedData[0:38]))
    predictedMaleMortalities.append(fittedData)
    predictedMaleMortalitiesResiduals.append(residualAvg)
    
    mortalityData = femaleMortality[i:i+1].values[0,1:]
    mortalityData = mortalityData[::-1]
    [coeffs,covars] = scipy.optimize.curve_fit(fittingFunc,years-1980,mortalityData,check_finite=True)
    fittedData = fittingFunc(future_years-1980,*coeffs)
    #print(coeffs)
    #print(np.min(fittedData))
    #plt.scatter(years,mortalityData)
    #plt.plot(future_years,fittedData)
    residualAvg = np.mean(np.abs(mortalityData-fittedData[0:38]))
    predictedFemaleMortalities.append(fittedData)
    predictedFemaleMortalitiesResiduals.append(residualAvg)
    
maleMortalityPredicted = pd.DataFrame(predictedMaleMortalities)
maleMortalityPredicted.columns = [future_years]

femaleMortalityPredicted = pd.DataFrame(predictedFemaleMortalities)
femaleMortalityPredicted.columns = [future_years]

maleMortalityPredicted.to_csv('../data/mortalities_male_predicted_parsed.csv')
femaleMortalityPredicted.to_csv('../data/mortalities_female_predicted_parsed.csv')
