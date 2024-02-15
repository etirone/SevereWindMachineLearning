
# Initialize Variables
use_text = 0
use_fourier_time = 0
closest_distance_type = 0
our_k = 30
dim_reduction_type = 2  # dim_reduction_type = 21
if_pr = False
if_smote = False
if_test = True
handle_9999 = True
impute = True
popelev = True
landuse = True ## Include this also - all TRUE gives seperate naming system. Fix that.Z
radardat = False

# Input File directories 
# assumes a single file for now.
InputDir_pop = "/Users/andrewseverin/isugif/2023_Gallus_SevereWind/Notebook_Severin/temp"

# ################# Import Functions from new_all_fn #################

# Assuming new_all_fn.py contains equivalent Python functions
import new_all_fn as fn

# Library Import and File Reading

import pandas as pd
import os


# ################# Read the files ####################
# directory = "/work/wgallus/etirone2/hwt_2023"
# this script expects a single file not sure why it is globbing here.
files = [os.path.join(InputDir_pop, f) for f in os.listdir(InputDir_pop) 
         if f.startswith("table_with_elevation_and_pop_")]
all_dat = pd.concat([pd.read_csv(file) for file in files], ignore_index=True)
n_new = len(all_dat)





#2################ Text Processing ####################

#import pandas as pd
import numpy as np

joined_text_new = all_dat['Remarks'].astype(str)
joined_text_new = [text.split('(')[0] for text in joined_text_new]


# Matrix Initialization and Column Binding:
B = pd.DataFrame(np.nan, index=range(n_new), columns=[f"text_{i}" for i in range(1, our_k+1)])
all_dat = pd.concat([all_dat, B], axis=1)



########### Predict ##########

# Column Renaming and Data Processing:
all_dat.rename(columns={'Time': 'beginUTC', 
                        'LAT': 'location_1_lat', 
                        'LON': 'location_1_lon', 
                        'Speed(MPH)': 'magnitude'}, inplace=True)
# in the original R code the rename used "Speed.MPH." instead of "Speed(MPH)". This new code assumes that all data will infact be exact rather than using the any character .

all_dat['magnitude_type'] = np.where(all_dat['magnitude'] == 'UNK', 'EG', 'MG')



# Handling factor-like conversion in Python
if all_dat['magnitude'].dtype == 'category':
    all_dat['magnitude'] = all_dat['magnitude'].cat.codes


final_mat_2_new = all_dat
#delete  still has text columns Dec 5, 2023
# Event ID Extraction:
event_id = final_mat_2_new['event_id']





# #3################ Further Processing ####################
if 'land_use' in final_mat_2_new.columns:
    final_mat_2_new['land_use'] = final_mat_2_new['land_use'].fillna(12).astype('category')


# Subsetting dataframes 
## Warning - take care that it is included when dim is reduced  - Subrata  -CHECK
measured_cases = final_mat_2_new[final_mat_2_new['magnitude_type'] == 'MG']
estimated_cases = final_mat_2_new[final_mat_2_new['magnitude_type'] == 'EG']




#delete  still has text columns Dec 5, 2023


## 4 Adding distance calculations 


if closest_distance_type == 1:
    final_mat_2_new['magnitude_closest'] = np.nan
    final_mat_2_new['s_t_dist'] = 0
    mes_closest = fn.distance_1_measured(measured_cases['beginUTC'], measured_cases['location_1_lat'], measured_cases['location_1_lon'], measured_cases['magnitude'], "%Y-%m-%d %H:%M")
    est_closest = fn.distance_1_estimated(estimated_cases['beginUTC'], estimated_cases['location_1_lat'], estimated_cases['location_1_lon'], estimated_cases['magnitude'], "%Y-%m-%d %H:%M")
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'MG', 'magnitude_closest'] = mes_closest[:, 0]
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'MG', 's_t_dist'] = mes_closest[:, 1]
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'EG', 'magnitude_closest'] = est_closest[:, 0]
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'EG', 's_t_dist'] = est_closest[:, 1]
elif closest_distance_type == 2:
    final_mat_2_new['s_t_ind'] = 0
    mes_closest = fn.distance_2_measured(measured_cases['beginUTC'], measured_cases['location_1_lat'], measured_cases['location_1_lon'], measured_cases['magnitude'], "%Y-%m-%d %H:%M")
    est_closest = fn.distance_2_estimated(estimated_cases['beginUTC'], estimated_cases['location_1_lat'], estimated_cases['location_1_lon'], estimated_cases['magnitude'], "%Y-%m-%d %H:%M")
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'MG', 's_t_ind'] = mes_closest
    final_mat_2_new.loc[final_mat_2_new['magnitude_type'] == 'EG', 's_t_ind'] = est_closest



# final_mat_2_new.shape (1391, 821)
#delete  still has text columns Dec 5, 2023







################# Time ####################
time_transformed = fn.transform_time(final_mat_2_new['beginUTC'], use_fourier_time, date_format="%Y-%m-%d %H:%M")
# Assuming time_transformed is a NumPy array returned by transform_time function
# Convert the NumPy array to a pandas DataFrame
time_transformed_df = pd.DataFrame(time_transformed, index=final_mat_2_new.index)

# Now concatenate the DataFrame version of time_transformed with final_mat_2_new
final_mat_2_new = pd.concat([time_transformed_df, final_mat_2_new], axis=1)

#final_mat_2_new = pd.concat([time_transformed, final_mat_2_new], axis=1)

# Removing rows with Too Many NAs:
# too_many_nas = final_mat_2_new.columns[final_mat_2_new.isna().mean() > 0.50]
# if len(too_many_nas) > 0:
#     final_mat_2_new.drop(columns=too_many_nas, inplace=True)
# Calculate the proportion of NA values in each row
na_proportion = final_mat_2_new.isna().mean(axis=1)

# Identify rows where the proportion of NA values is greater than 50%
too_many_nas = na_proportion > 0.50

# Remove rows with more than 50% NA values
final_mat_2_new = final_mat_2_new.loc[~too_many_nas]




# Handling -9999's and Imputing Variables:

if impute:
    final_mat_2_new = fn.impute_UVEIL_RH7080(final_mat_2_new)

# final_mat_2_new.shape (1391, 796)




## The other dim_reduction functions need to be fixed to include environmental variables or we need to change the input to 
# put the environmental variables as a parameter for dim_reduction_2_ind to match the other functions 

#import importlib
#importlib.reload(fn) 
#
#import new_all_fn as fn
# Handling -9999's and Dimensionality Reduction:
if handle_9999:
    if dim_reduction_type == 0:
        final_mat_2_new = fn.add_indicator(final_mat_2_new)
        print(final_mat_2_new.shape)
    elif dim_reduction_type in [1, 11]:
        final_mat_2_new = fn.dim_reduction_1_ind(final_mat_2_new)
        print(final_mat_2_new.shape)
    elif dim_reduction_type in [2, 21]:
        final_mat_2_new = fn.dim_reduction_2_ind(final_mat_2_new)
        print(final_mat_2_new.shape)
    # Convert _ind columns to categorical
    all_env_ind_new = [col for col in final_mat_2_new.columns if '_ind' in col]
    for col in all_env_ind_new:
        final_mat_2_new[col] = final_mat_2_new[col].astype('category')
else:
    if dim_reduction_type == 1:
        final_mat_2_new = fn.dim_reduction_1(final_mat_2_new, remove_9999=True, remove_999=True)
        print(final_mat_2_new.shape)
    elif dim_reduction_type == 2:
        final_mat_2_new = fn.dim_reduction_2(final_mat_2_new, remove_9999=True, remove_999=True)
        print(final_mat_2_new.shape)
    elif dim_reduction_type == 11:
        final_mat_2_new = fn.dim_reduction_11(final_mat_2_new, remove_9999=True, remove_999=True)
        print(final_mat_2_new.shape)
    elif dim_reduction_type == 21:
        final_mat_2_new = fn.dim_reduction_21(final_mat_2_new, remove_9999=True, remove_999=True)
        print(final_mat_2_new.shape)













##########################################################################################################
### WHY DOES THAT MODEL HAVE A LAND_USE DATA --------------___CHECK IMMEDIATELY.
##########################################################################################################

# Adjusting avg_pop Column:

#import numpy as np

final_mat_2_new['avg_pop'] = np.where(final_mat_2_new['avg_pop'].isna(), 1.01, final_mat_2_new['avg_pop'])



# Index of Rows Containing Text and Not Containing Text:

# Dec 5, 2023 his is if there is text and not sure what it does in the R script. Tthe code doesn't seem to populate those columns in the final matrix
# adding the next line to append the text_X columns 

no_text_index = final_mat_2_new[final_mat_2_new['text_1'].isna()].index
text_index = final_mat_2_new[final_mat_2_new['text_1'].notna()].index

# Setting Variables:

cut_off = 50
train_start = 2007
train_end = 2017
test_start = train_end + 1
test_end = 2018
sourcefile = "new_fit_subsevere"

# Generating final output file names

outFile = fn.save_fn_names(base_name=sourcefile, Use_Text=use_text, 
                           closest_distance_type=closest_distance_type,
                           train_end=train_end, dim_reduction_type=dim_reduction_type,
                           cut_off=cut_off, train_start=train_start,
                           our_k=our_k, Use_Fourier_time=use_fourier_time,
                           if_PR=if_pr, if_SMOTE=if_smote,
                           if_test=if_test, handle_9999=handle_9999, impute=impute,
                           popelev=popelev, landuse=landuse, radardat=radardat)
print(outFile)


# Loading Models


###??????Dec 4, 2023####
# NOVA:/work/wgallus/subrata_tmp/codes_4/
# models <- readRDS(paste0(outFile_path, "_main_model_1.rds"))
# stack.glm <- readRDS(paste0(outFile_path, "_model_stack_glm.rds"))
# stack.rf <- readRDS(paste0(outFile_path, "_model_stack_rf.rds"))
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_main_model_1.rds
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_model_stack_glm.rds
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_model_stack_rf.rds


# Comparing Column Names:

#
## Assuming `models` is a dictionary or object with attribute `gbm` which has attribute `trainingData`
set_difference = set(models.gbm.trainingData.columns) - set(final_mat_2_new.columns)
print(set_difference)


############ ****NO TEXT***** ################
# This was an if loop in R that 


# Dec 4, 2023
# working through why dim_reduction_2_ind is not working. or why I am getting Problem in indexing!!! error
# I may just leave this for now and come back to it later
# todo 
# * figure out how to convert the rds model files to cvs for python read in and proceed with the code. 

# Dec 5, 2023
# Questions for Lizzie  
# Does dim_reduction_2_ind in R produce a matrix with nan values in it? say 'DNCP_max'
#       I believe the answer should be no and these values set to 0 
# 2) Is the code in R setting the max to zero if the number of nan's in a row is > 20 or is ignoring the column all together?
#       Would that even make sense, I mean the columns I have all have less than 19 nan's in them.
#       temp1['DNCP_max'].isna().sum()  = 19
#       The issue arises during the check at the end of this function.  So do we expect more than 255 columns? We have all the rows just fewer columns
# 3) Will the presence of nan's in the final matrix be a problem in the next step during prediction and models?

# Dec 5, 2023
# found a mistake in the removing of rows with > 20 NAs it was doing columns instead. I need to rerun the script from the
# beginning again tomorrow and see if I can get the dim_reduction_2_ind to work properly and have a matrix with the text_X columns intact
# also start on convert the rds files to something python can read in.

# Dec 6, 2023
# script is only run on a single file and may change all the questions above
# I believe it is a row sum not a column sum check.