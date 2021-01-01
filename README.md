# Age_Structure_Predictor
This project considers the prediction of the age structure/population pyramid of the United Kingdom based on birth rates, mortalities, and net migration values. The age structure of the UK for 1991 is used as the initial condition, based on ONS data. 
Birth rate and net migration data are taken from UN data, predicted up to 2100. Mortality rates per age group are predicted up to 2100 using exponential regression of the 1981-2018 ONS data within the mortalityPredictor.py script. The ageStructurePredictor.py script predicts and saves the male and female populations between 1991 and 2100, based on a timestep of 1 year, and outputs an animated population pyramid. 

HOW TO:
1. Download and unzip the files.
2. Run mortalityPredictor.py, which will produce mortalities_female_predicted_parsed.csv and mortalities_male_predicted_parsed.csv files within the data folder.
3. Run ageStructurePredictor.py.
4. Review the outputs.

Considerations:
1. The age structure for 1991, used as the intial condition, groups together those 90 and over. I assume these are evenly split from 90-100, and define age band 100 as >=100. 
2. Mortalities are taken from ONS life tables for 1981-2018 for ages 0-100, therefore those in the >=100 age group are considered to have a mortality equal to that of age 100. 
3. New births are calculated each year based on the total population of the previous year rather than the current year, and are assumed to be equally split between male and female.
4. Migration is calculated based on net migration rates multiplied byt the total population of the previour year rather than the current year.
5. The demographics of net migration are not known and are instead assumed to be equally split between male and female and between ages 0-70, inclusive. If I can find stratified data encompassing age/sex of immigration/emmigration I will update the model. 
