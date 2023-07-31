# SevereWindMachineLearning
Machine learning approach to predict the probability that a severe wind report was caused by severe intensity wind (greater than or equal to 50 knots)

* Working codes to quality control the data, train the machine learning models, and make predictions are in progress and will be published upon completion

# Data
Wind reports have speeds that were either measured (MG) or estimated (EG). The machine learning models were only trained on MG, but predictions can be made on estimated, however, due to the nature of the reports, skill metrics cannot be calculated on estimated as their speeds are not considered "ground-truth." 
1. WindReports
   * Contain wind reports from 2007-2018 that were used to train and test the machine learning models
   * Data from 2007-2017 have been quality controled to remove reports with speeds < 30 kt with changes between start and end times > 20 minutes
2. EnvironmentalFeatures
   * Contain wind reports from 20017-2018 with environmental features used in training/testing
   * SPC mesoanalysis data are labeled as NAME_point with "NAME" corresponding to the variable name and "point" referencing the number on the grid (see diagram below)
   * Elevation and population are columns at the end of each row (labeled)
  
  
