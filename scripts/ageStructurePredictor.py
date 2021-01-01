#%% ageStructurePredictor.py

# This script calculates takes the age structure of the UK from 1991 and the 
# ONS life tables and uses these to predict the change in the age structure 
# over time. 

# The values determined for 2018 are compared to official data. 

# Life tables for future years are predicted based on historical data, and the
# age structure is predicted up to the year 2041, and then compared to ONS 
# predictions. 


#%% preamble

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation

PLOT = True
ANIMATE = True

#%% initial data

# Import the parsed mortalities of males and females for age groups of 1 year
# taken from official ONS sources for the years 1981 to 2018.  
maleMortality = pd.read_csv('../data/ONS_mortalities_male_parsed.csv')
femaleMortality = pd.read_csv('../data/ONS_mortalities_female_parsed.csv')

# Import the parsed mortalities of males and females for the same age groups
# predicted for the future using an exponential regression based on the ONS
# 1981-2018 data.
maleMortalityPredicted = pd.read_csv('../data/mortalities_male_predicted_parsed.csv')
femaleMortalityPredicted = pd.read_csv('../data/mortalities_female_predicted_parsed.csv')

# Import birthrates per year taken from UN (predicted up to 2100)
birthRate = pd.read_csv('../data/UN_UK_birth_rates_1950_to_2100_parsed.csv')

# Import net migration rates taken from UN (predicted up to 2100)
netMigrationRate = pd.read_csv('../data/UN_UK_net_migration_1950_to_2100_parsed.csv')

# Import the age structure of the UK from 1991 as the initial condition of the 
# model and calculate populations as percentage of total population. This data
# is limited as >90 ages are grouped together. To get around this I assume the
# individuals in the >90 are equally distributed in ages 90-100, and 100 is 
# redefined as 100+.

population1991 = pd.read_csv('../data/ONS_population_1991_parsed.csv')
femaleDivide = population1991['Female'][90]/11
maleDivide = population1991['Male'][90]/11
population1991 = population1991.drop(90)
population1991extra = pd.DataFrame([[90,maleDivide,femaleDivide],
            [91,maleDivide,femaleDivide],[92,maleDivide,femaleDivide],
            [93,maleDivide,femaleDivide],[94,maleDivide,femaleDivide],
            [95,maleDivide,femaleDivide],[96,maleDivide,femaleDivide],
            [97,maleDivide,femaleDivide],[98,maleDivide,femaleDivide],
            [99,maleDivide,femaleDivide],[100,maleDivide,femaleDivide]], 
            columns=('Age','Male','Female'))
population1991 = population1991.append(population1991extra, ignore_index=True)

totalPop = []
totalPop.append((np.sum(population1991['Male']) + np.sum(population1991['Female'])))

population1991['Male_percent'] = (population1991['Male']*100/totalPop)
population1991['Female_percent'] = (population1991['Female']*100/totalPop)        


# Create population dataframes for male and female to contain population 
# structure for each year.
male_population = pd.DataFrame(population1991['Age'], columns=['Age'])
male_population['1991'] = population1991['Male']

female_population = pd.DataFrame(population1991['Age'], columns=['Age'])
female_population['1991'] = population1991['Female']

# Set starting year and set current year to starting year. 
starting_year = 1991
end_year = 2100

current_year = starting_year

#%% Test plot initial population pyramid

if PLOT == True:
    plt.figure(1)
    ypos = np.arange(len(population1991['Age']))
    xpos_male = -population1991['Male_percent']
    xpos_female = population1991['Female_percent']
    plt.barh(ypos,xpos_male)
    plt.barh(ypos,xpos_female)
    plt.grid(True,which='both')
    plt.yticks(np.arange(0,105,5))
    plt.xlabel('Percent of total population')
    plt.ylabel('Age (years)')
    plt.legend(['Male','Female'])
    plt.axis([-1.5, 1.5, 0, 100])
    plt.title('Year = %s; Total population = %sM'%(current_year,round(totalPop[0]/1e6,2)))

#%% Tidying up

# Delete what's not needed.
del population1991extra
del population1991
del maleDivide
del femaleDivide


#%% Main loop

# For each year simulated, create a new list encompassing the new population
# for the new year. 

for i in range(end_year-starting_year):
    current_year += 1 # Increase the current year and print out
    print(' --- The current year is %s'%current_year)
    
    # Set new male and new female populations to empty lists
    new_male_population = []
    new_female_population = []
    
    # New births are calculated based on the imported birth rates multiplied
    # by the total population of the previous year. N.B. I assume births are 
    # evenly split 50/50 male and female.
    new_male_population.append(0.5*totalPop[-1]*birthRate[str(current_year)][0])
    new_female_population.append(0.5*totalPop[-1]*birthRate[str(current_year)][0])
    
    # For each age between 1 and 99, calculate the new population based on the 
    # old population minus the newly deceased. 
    for j in range(len(male_population['1991'])-2):
        if current_year < 2020:
            new_male_population.append(
                    male_population[str(current_year-1)][j]*
                    (1-maleMortality[str(current_year-1)][j]))  
            new_female_population.append(
                    female_population[str(current_year-1)][j]*
                    (1-femaleMortality[str(current_year-1)][j]))
        else:
            new_male_population.append(
                    male_population[str(current_year-1)][j]*
                    (1-maleMortalityPredicted[str(current_year-1)][j]))  
            new_female_population.append(
                    female_population[str(current_year-1)][j]*
                    (1-femaleMortalityPredicted[str(current_year-1)][j]))
               
    # The 100+ age for the current year is the previous population 
    # multiplied by the mortality plus the previous 99 population multiplied
    # by the relevant mortality.
    if current_year < 2020:
        new_male_population.append((male_population[str(current_year-1)][100]*
                    (1-maleMortality[str(current_year-1)][100]))+ 
                    (male_population[str(current_year-1)][99]*
                    (1-maleMortality[str(current_year-1)][99])))
        
        new_female_population.append((female_population[str(current_year-1)][100]*
                    (1-femaleMortality[str(current_year-1)][100]))+ 
                    (female_population[str(current_year-1)][99]*
                    (1-femaleMortality[str(current_year-1)][99])))
    else:
        new_male_population.append((male_population[str(current_year-1)][100]*
                    (1-maleMortalityPredicted[str(current_year-1)][100]))+ 
                    (male_population[str(current_year-1)][99]*
                    (1-maleMortalityPredicted[str(current_year-1)][99])))
        
        new_female_population.append((female_population[str(current_year-1)][100]*
                    (1-femaleMortalityPredicted[str(current_year-1)][100]))+ 
                    (female_population[str(current_year-1)][99]*
                    (1-femaleMortalityPredicted[str(current_year-1)][99])))        
    
    # Add in the effects of migration (immigration/emmigration) using net
    # migration rate. Total population increase is determined based on the 
    # relevant net migration rate multiplied by the previous year's total 
    # population. This new population is then evenly split across ages 0 to 70
    # and across both sexes.
    # N.B. Here I assume that the demographic of immigrants/emmigrants are the 
    # same and can be modelled as evenly-split from 0-70. However, it's likely 
    # that the age/sex demographic of incoming migrants is focussed around
    # working-age males, although I couldn't find good data for this. 
    maleMigrantPop = 0.5*totalPop[-1]*netMigrationRate[str(current_year)][0]
    maleMigrantDivide = maleMigrantPop/71
    femaleMigrantDivide = maleMigrantDivide
    
    for j in range(71):
       new_male_population[j] += maleMigrantDivide
       new_female_population[j] += femaleMigrantDivide
  
    # Update the total population
    totalPop.append((np.sum(new_male_population) + np.sum(new_female_population)))
    
    # Add the new populations to the df in new cols for the current year.
    male_population[str(current_year)] = new_male_population
    female_population[str(current_year)] = new_female_population
    
    # delete what isn't needed
    del new_male_population, new_female_population
    del maleMigrantDivide, femaleMigrantDivide, maleMigrantPop

#%% Test plot final population pyramid

if PLOT == True:
    plt.figure(2)
    ypos = np.arange(len(male_population['Age']))
    xpos_male = -1*(male_population[str(current_year)]*100/
            (np.sum(male_population[str(current_year)]) + 
             np.sum(female_population[str(current_year)])))
    xpos_female = (female_population[str(current_year)]*100/
            (np.sum(male_population[str(current_year)]) + 
             np.sum(female_population[str(current_year)])))
    plt.barh(ypos,xpos_male)
    plt.barh(ypos,xpos_female)
    plt.grid(True,which='both')
    plt.yticks(np.arange(0,105,5))
    plt.xlabel('Percent of total population')
    plt.ylabel('Age (years)')
    plt.legend(['Male','Female'])
    plt.axis([-1.5, 1.5, 0, 100])
    plt.title('Year = %s; Total population = %sM'%(current_year,round(totalPop[-1]/1e6,2)))
    
#    plt.figure(3)
#    plt.plot(np.arange(starting_year, end_year+1),totalPop)
#    plt.grid(True)
#    plt.xlabel('Year')
#    plt.ylabel('Total Population')

#%% Plot an animation of the age structure changing over time

if ANIMATE == True:

    fig3 = plt.figure(4)
    ax = plt.axes(xlim=(-1., 1.), ylim=(0, 100))
    ypos = np.arange(len(male_population['Age']))
    plt.yticks(np.arange(0,105,5))
    plt.xlabel('Percent of total population')
    plt.ylabel('Age (years)')  
    plt.grid(True,which='both')
    bar = ax.barh([], [])
        
    def animateGraph(i):
        ax.clear()
        plt.grid(True,which='both')
        plt.yticks(np.arange(0,105,5))
        plt.xlabel('Percent of total population')
        plt.ylabel('Age (years)')
        plt.axis([-1., 1., 0, 100])
        xpos_male = -1*(male_population[str(starting_year+i)]*100/
            (np.sum(male_population[str(starting_year+i)]) + 
             np.sum(female_population[str(starting_year+i)])))
        xpos_female = (female_population[str(starting_year+i)]*100/
            (np.sum(male_population[str(starting_year+i)]) + 
             np.sum(female_population[str(starting_year+i)])))
        plt.title('Year = %s; Total population = %sM'%(starting_year+i,round(totalPop[i]/1e6,2)))
        plt.barh(ypos,xpos_male)
        plt.barh(ypos,xpos_female)
        plt.legend(['Male','Female'])
    
    anim = animation.FuncAnimation(fig3, animateGraph, 
                                   frames=len(range(end_year-starting_year)), 
                                   interval=1000, blit=False)

