# SevereWindMachineLearning
Machine learning approach to predict the probability that a severe wind report was caused by severe intensity wind (greater than or equal to 50 knots)

* Working codes to quality control the data, train the machine learning models, and make predictions are in progress and will be published upon completion

# Data
1. Testing
   * Contain wind reports from 2018-2021 that were used to feed into the machine learning models
   * Data are separated by type (measured and estimated) and by year
  
2. Training
   * Contain measured wind reports from 2007-2017 that were used to train the machine learning models
   * Data have been quality controled to remove reports with speeds < 30 kt with changes between start and end times > 20 minutes
