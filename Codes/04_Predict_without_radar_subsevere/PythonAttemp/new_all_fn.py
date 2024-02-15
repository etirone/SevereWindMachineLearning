###### *Preamble #######

## potential open issues:

## 1) Somehow '3KRH' becomes 'X3KRH'  XXXThis was fixed Dec 5, 2023 Andrew Severin
##    See dim_reduction_2
## Add 999 to 9999 also
## Add Aug 3rd's meeting in the dim reduction also

## Dec 5, 2023 Andrew Severin
## 1) The other dim_reduction functions need to be fixed to include environmental variables or we need to change the input to 
##    put the environmental variables as a parameter for dim_reduction_2_ind to match the other functions 


# ################  clean_text_vec   ################
# not used in Predict_without_radar_subsevere.py

# 1 Creates a corpus from the input text.
# 2 Replaces certain characters (/, @, |) with spaces.
# 3 Converts text to lowercase.
# 4 Optionally removes numbers.
# 5 Removes common English stopwords.
# 6 Removes punctuations.
# 7 Strips extra whitespace.
# 8 Applies stemming to reduce words to their root form.

# * The text is processed document by document.
# * Regular expressions are used for pattern replacements and optional number removal.
# * The nltk library is used for tokenization, stopword removal, and stemming.
# * The function assumes joined_text is a list of strings (text documents).
# * Each text processing step corresponds to the operations performed by the R function.

#import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

# Ensure stopwords are downloaded
nltk.download('stopwords')
nltk.download('punkt')

def clean_text_vec(joined_text, if_remove_num=False):
    """
    Cleans and preprocesses a collection of text documents.

    Args:
    - joined_text (list of str): A list of text documents.
    - if_remove_num (bool): Flag to remove numbers from the text.

    Returns:
    - list of str: A list of processed text documents.
    """

    # Function to replace specific patterns with space
    def replace_pattern(text, pattern):
        return re.sub(pattern, " ", text)

    # Processing each document in the corpus
    processed_docs = []
    for doc in joined_text:
        if doc:  # Check if the document is not empty
            # Replacing specific characters with spaces
            doc = replace_pattern(doc, "[/@|]")
            
            # Convert to lower case
            doc = doc.lower()

            # Remove numbers if flagged
            if if_remove_num:
                doc = re.sub(r'\d+', '', doc)

            # Tokenization and cleaning
            words = word_tokenize(doc)
            words = [word for word in words if word.isalpha()]  # Remove punctuations
            words = [word for word in words if word not in stopwords.words('english')]  # Remove stopwords

            # Stemming
            stemmer = SnowballStemmer("english")
            words = [stemmer.stem(word) for word in words]

            # Rejoining words
            doc = ' '.join(words)
            processed_docs.append(doc)

    return processed_docs
############################################################################################################





# ################  refined_dtm   ################

# 1 It first calls the clean_text_vec function to preprocess the text.
# 2 It then creates a Document-Term Matrix (DTM) from the processed text.
# 3 Calculates the sum of terms in each document.
# 4 Identifies non-null documents (documents that contain at least one term).
# 5 Returns the DTM along with indices of non-null documents and the total number of documents.


from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

def refined_dtm(joined_text, if_remove_num=False):
    """
    Creates a refined document-term matrix from a list of text documents.

    Args:
    - joined_text (list of str): A list of text documents.
    - if_remove_num (bool): Flag to remove numbers from the text.

    Returns:
    - dict: A dictionary containing the document-term matrix ('dtm'), indices of non-null documents ('non_null'), and the total number of documents ('n').
    """

    # Clean the text documents
    new_docs = clean_text_vec(joined_text, if_remove_num)

    # Create a Document-Term Matrix
    vectorizer = CountVectorizer()
    dtm = vectorizer.fit_transform(new_docs)

    # Calculate row sums (sum of terms in each document)
    m_rowSums = np.sum(dtm.toarray(), axis=1)
    
    # Identify non-null documents
    ind_non_null = np.where(m_rowSums != 0)[0]

    # Check for no non-null documents
    if np.all(m_rowSums == 0):
        print("No non-null document! Take as a serious warning!")

    # Return the results
    return {"dtm": dtm, "non_null": ind_non_null, "n": len(new_docs)}
############################################################################################################






# ################  Finding nearest Distance   ################

# Haversine formula is used to calculate distances:
# https://en.wikipedia.org/wiki/Haversine_formula
# https://www.movable-type.co.uk/scripts/latlong.html
# Haversin distance: Earth radius*0.0017 = 6371*0.0017 km (* 2) ~ 11 km (*2)

# ### second_min ### 

# this function is no longer needed. 
# import numpy as np

# def second_min(arr):
#     """
#     Finds the index of the second smallest value in an array.

#     Args:
#     - arr (numpy.array): The array to search.

#     Returns:
#     - int: The index of the second smallest value in the array.
#     """
#     # Ensure the array is a numpy array
#     arr = np.array(arr)

#     # Find the index of the smallest value
#     first_min_index = np.argmin(arr)

#     # Temporarily set the smallest value to a very high number
#     temp_value = arr[first_min_index]
#     arr[first_min_index] = np.inf

#     # Find the index of the new smallest value, which is the second smallest in the original array
#     second_min_index = np.argmin(arr)

#     # Restore the original smallest value
#     arr[first_min_index] = temp_value

#     return second_min_index

# # Example usage:
# # second_min_index = second_min(your_array)
############################################################################################################


### distance_1_measured

## Takes time, lat and lon
# notice the format ("%m/%d/%Y %H:%M"), change if necessary

# Inputs: The function takes vectors for time (time_vec), latitude (lat_vec), and longitude (lon_vec), along with a magnitude vector and a date format (date_format).
# Preprocessing:
# Converts time to POSIXlt format.
# Converts latitude and longitude to radians (assuming they are initially in degrees).
# Calculations:
# For each point, it calculates the time difference with every other point in minutes, adjusting by a factor of 20 minutes as a unit.
# It calculates spatial differences using a form of the Haversine formula to compute distances.
# Combines time and spatial distances into a final distance measure.
# Finds the second smallest distance (excluding the distance to itself) and records the corresponding magnitude.
# Outputs: Returns a matrix with the closest magnitude and the spatial-temporal distance for each point in the input vectors.


import numpy as np
import pandas as pd

def distance_1_measured(time_vec, lat_vec, lon_vec, magnitude, date_format="%m/%d/%Y %H:%M"):
    # Convert times to pandas datetime objects
    time_vec = pd.to_datetime(time_vec, format=date_format)

    # Convert lat and lon to radians
    lat_vec = np.radians(lat_vec)
    lon_vec = np.radians(lon_vec)

    n = len(time_vec)
    magnitude_closest = np.zeros(n)
    s_t_dist = np.zeros(n)
    BIG_DIST = 20000
    BIG_CLOSEST = 50

    if n == 1:
        magnitude_closest[0] = BIG_CLOSEST
        s_t_dist[0] = BIG_DIST
    elif n > 1:
        for indexm in range(n):
            time_diff = (time_vec - time_vec[indexm]).total_seconds() / 60 / 20  # 20 min as 1 time unit

            lat_diff = lat_vec - lat_vec[indexm]
            lon_diff = lon_vec - lon_vec[indexm]
  # keeping the original Haversine formula that doesn't divide by 2 from the original R code
  #          tmp_diff = np.sin(lat_diff / 2) ** 2 + np.cos(lat_vec) * np.cos(lat_vec[indexm]) * np.sin(lon_diff / 2) ** 2  # Haversine formula
            tmp_diff = np.sin(lat_diff) ** 2 + np.cos(lat_vec) * np.cos(lat_vec[indexm]) * np.sin(lon_diff) ** 2   # modified Haversine formula used in ML training 

            final_dist = np.sqrt(time_diff ** 2 + (2 * np.arctan2(np.sqrt(tmp_diff), np.sqrt(1 - tmp_diff)) / 0.0017) ** 2)

            # Find the second smallest distance
            tmp_order = np.argsort(final_dist)[1]  # Second smallest, [0] would be the smallest
            magnitude_closest[indexm] = magnitude[tmp_order]
            s_t_dist[indexm] = final_dist[tmp_order]

    return np.column_stack((magnitude_closest, s_t_dist))

# Example usage
# distance_1_measured(time_vector, latitude_vector, longitude_vector, magnitude_vector)
############################################################################################################


### distance_1_estimated ###

import numpy as np
import pandas as pd

def distance_1_estimated(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m, 
                         time_vec_e, lat_vec_e, lon_vec_e, date_format="%m/%d/%Y %H:%M"):
    # Convert times to pandas datetime objects
    time_vec_m = pd.to_datetime(time_vec_m, format=date_format)
    time_vec_e = pd.to_datetime(time_vec_e, format=date_format)

    # Convert lat and lon to radians
    lat_vec_m = np.radians(lat_vec_m)
    lon_vec_m = np.radians(lon_vec_m)
    lat_vec_e = np.radians(lat_vec_e)
    lon_vec_e = np.radians(lon_vec_e)

    n_m = len(time_vec_m)
    n_e = len(time_vec_e)
    magnitude_closest = np.zeros(n_e)
    s_t_dist = np.zeros(n_e)
    BIG_DIST = 20000
    BIG_CLOSEST = 50

    if n_m == 0:
        magnitude_closest.fill(BIG_CLOSEST)
        s_t_dist.fill(BIG_DIST)
    else:
        for indexe in range(n_e):
            time_diff = (time_vec_m - time_vec_e[indexe]).total_seconds() / 60 / 20   # 20 min as 1 time unit
            lat_diff = lat_vec_m - lat_vec_e[indexe]
            lon_diff = lon_vec_m - lon_vec_e[indexe]

            # tmp_diff = np.sin(lat_diff / 2) ** 2 + np.cos(lat_vec_m) * np.cos(lat_vec_e[indexe]) * np.sin(lon_diff / 2) ** 2
            tmp_diff = np.sin(lat_diff) ** 2 + np.cos(lat_vec_m) * np.cos(lat_vec_e[indexe]) * np.sin(lon_diff) ** 2
            final_dist = np.sqrt(time_diff ** 2 + (2 * np.arctan2(np.sqrt(tmp_diff), np.sqrt(1 - tmp_diff)) / 0.0017) ** 2)

            tmp_order = np.argmin(final_dist)
            magnitude_closest[indexe] = magnitude_m[tmp_order]
            s_t_dist[indexe] = final_dist[tmp_order]

    return np.column_stack((magnitude_closest, s_t_dist))

# Example usage:
# distance_1_estimated(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m, time_vec_e, lat_vec_e, lon_vec_e)
############################################################################################################



### distance_2_measured ### 


# * The function categorizes each event as 0, 1, or 2 based on its proximity to other events within a certain spatial (less than 0.0017 radians) and temporal (less than 20 minutes) window.
# * Category 1 is assigned if there's at least one event within the window with a magnitude of 50 or less, and category 2 for magnitudes greater than 50. If neither condition is met, category 0 is assigned.
# * Pandas and NumPy are used for date-time handling and vectorized operations, respectively.


import numpy as np
import pandas as pd

def distance_2_measured(time_vec, lat_vec, lon_vec, magnitude, date_format="%m/%d/%Y %H:%M"):
    # Convert times to pandas datetime objects
    time_vec = pd.to_datetime(time_vec, format=date_format)

    # Convert lat and lon to radians
    lat_vec = np.radians(lat_vec)
    lon_vec = np.radians(lon_vec)

    n = len(time_vec)
    s_t_ind = np.zeros(n)

    if n == 1:
        s_t_ind[0] = 0
    elif n > 1:
        for indexm in range(n):
            count_1, count_2 = 0, 0

            # Calculating differences
            time_diff = (time_vec - time_vec[indexm]).total_seconds() / 60
            lat_diff = lat_vec - lat_vec[indexm]
            lon_diff = lon_vec - lon_vec[indexm]
#            tmp_diff = np.sin(lat_diff / 2) ** 2 + np.cos(lat_vec) * np.cos(lat_vec[indexm]) * np.sin(lon_diff / 2) ** 2
            tmp_diff = np.sin(lat_diff) ** 2 + np.cos(lat_vec) * np.cos(lat_vec[indexm]) * np.sin(lon_diff) ** 2   
            sp_diff = 2 * np.arctan2(np.sqrt(tmp_diff), np.sqrt(1 - tmp_diff))

            # Excluding the current index from magnitude
            magnitude_excluded = np.delete(magnitude, indexm)

            # Counting events
            condition_1 = (sp_diff < 0.0017) & (time_diff < 20) & (magnitude_excluded <= 50)
            condition_2 = (sp_diff < 0.0017) & (time_diff < 20) & (magnitude_excluded > 50)
            count_1 = np.any(condition_1)
            count_2 = np.any(condition_2)

            # Assigning categories
            if count_2:
                s_t_ind[indexm] = 2
            elif count_1:
                s_t_ind[indexm] = 1
            else:
                s_t_ind[indexm] = 0

    return pd.Categorical(s_t_ind, categories=[0, 1, 2])

# Example usage:
# distance_2_measured(time_vector, latitude_vector, longitude_vector, magnitude_vector)
############################################################################################################


### distance_2_estimated ###

# * This function mirrors the R function's logic but uses NumPy and Pandas for efficient calculations.
# * Each estimated event is categorized based on its proximity to the measured events within a specified spatial (less than 0.0017 radians) and temporal (less than 20 minutes) window.
# * Categories are assigned based on whether there are any nearby events within these thresholds and whether their magnitudes are below or above 50.

import numpy as np
import pandas as pd

def distance_2_estimated(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m, 
                         time_vec_e, lat_vec_e, lon_vec_e, date_format="%m/%d/%Y %H:%M"):
    # Convert times to pandas datetime objects
    time_vec_m = pd.to_datetime(time_vec_m, format=date_format)
    time_vec_e = pd.to_datetime(time_vec_e, format=date_format)

    # Convert lat and lon to radians
    lat_vec_m = np.radians(lat_vec_m)
    lon_vec_m = np.radians(lon_vec_m)
    lat_vec_e = np.radians(lat_vec_e)
    lon_vec_e = np.radians(lon_vec_e)

    n_e = len(time_vec_e)
    s_t_ind = np.zeros(n_e)

    for indexe in range(n_e):

        # Calculating differences
        time_diff = (time_vec_m - time_vec_e[indexe]).total_seconds() / 60
        lat_diff = lat_vec_m - lat_vec_e[indexe]
        lon_diff = lon_vec_m - lon_vec_e[indexe]
#        tmp_diff = np.sin(lat_diff / 2) ** 2 + np.cos(lat_vec_m) * np.cos(lat_vec_e[indexe]) * np.sin(lon_diff / 2) ** 2
        tmp_diff = np.sin(lat_diff) ** 2 + np.cos(lat_vec_m) * np.cos(lat_vec_e[indexe]) * np.sin(lon_diff) ** 2
        sp_diff = 2 * np.arctan2(np.sqrt(tmp_diff), np.sqrt(1 - tmp_diff))

        # Counting events
        condition_1 = (sp_diff < 0.0017) & (time_diff < 20) & (magnitude_m <= 50)
        condition_2 = (sp_diff < 0.0017) & (time_diff < 20) & (magnitude_m > 50)
        count_1 = np.any(condition_1)
        count_2 = np.any(condition_2)

        # Assigning categories
        if count_2:
            s_t_ind[indexe] = 2
        elif count_1:
            s_t_ind[indexe] = 1
        else:
            s_t_ind[indexe] = 0

    return pd.Categorical(s_t_ind, categories=[0, 1, 2])

# Example usage:
# distance_2_estimated(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m, time_vec_e, lat_vec_e, lon_vec_e)
############################################################################################################



### Pre processing ###

# * The function uses Pandas to handle date and time parsing and manipulation.
# * It performs Fourier transformation on the month and hour components if do_fourier is set.
# * The Fourier components for months and hours are extended based on the month_comp and hour_comp parameters.
# * It returns a NumPy array with the desired time components, either in raw form or after applying Fourier transformations.

# The transform_time function in R processes a vector of time stamps and converts them into various components (year, month, day, hour, minute), and optionally performs a Fourier transformation on the month and hour components. 


import pandas as pd
import numpy as np

#def transform_time(time_vec, do_fourier=0, month_comp=4, hour_comp=8, month_added=True, date_format="%m/%d/%Y %H:%M"):
#    # Convert time strings to datetime objects
#    time_vec = pd.to_datetime(time_vec, format=date_format)
#    print(time_vec)
#    # Extracting time components
#    year_vec = time_vec.year
#    month_vec = time_vec.month
#    day_vec = time_vec.day
#    hour_vec = time_vec.hour
#    min_vec = time_vec.minute

def transform_time(time_vec, do_fourier=0, month_comp=4, hour_comp=8, month_added=True, date_format="%m/%d/%Y %H:%M"):
    # Convert time strings to datetime objects if they are not already
    if not pd.api.types.is_datetime64_any_dtype(time_vec):
        time_vec = pd.to_datetime(time_vec, format=date_format)

    # Extracting time components using .dt accessor
    year_vec = time_vec.dt.year
    month_vec = time_vec.dt.month
    day_vec = time_vec.dt.day
    hour_vec = time_vec.dt.hour
    min_vec = time_vec.dt.minute



    if do_fourier:
        hour_vec += min_vec / 60
        if month_added:
            month_vec -= 1 + day_vec / 31

        # Fourier Transform for Month and Hour
        month_extended = np.column_stack([np.cos(2 * np.pi * month_vec / 12),
                                          np.sin(2 * np.pi * month_vec / 12)])  # change if min is added
        hour_extended = np.column_stack([np.cos(2 * np.pi * hour_vec / 24),
                                         np.sin(2 * np.pi * hour_vec / 24)])

        for i in range(2, month_comp // 2 + 1):
            month_extended = np.column_stack([month_extended, 
                                              np.cos(2 * np.pi * i * month_vec / 12),
                                              np.sin(2 * np.pi * i * month_vec / 12)])

        for i in range(2, hour_comp // 2 + 1):
            hour_extended = np.column_stack([hour_extended, 
                                             np.cos(2 * np.pi * i * hour_vec / 24),
                                             np.sin(2 * np.pi * i * hour_vec / 24)])

        if month_added:
            return np.column_stack([year_vec, month_extended, hour_extended])
        else:
            return np.column_stack([year_vec, month_extended, day_vec, hour_extended])
    else:
        return np.column_stack([year_vec, day_vec, month_vec, hour_vec, min_vec])

# Example usage
# transform_time(time_vector)
############################################################################################################



# magnitude_type
# changes names to "lat", "lon" 

### event_id? ### 

# def transform_time_sample():  # Placeholder for the transform_time function
#     # Implement transform_time function here as per previous conversion
#     pass

#  Variable Names Definitions
basic_var_names = ["magnitude", "location_1_lat", "location_1_lon"]
#env_var_names = ["LR75", "LR85", "LPS4", "UWND", "VWND", "SBCP", "SBCN",
#                 "MUCP", "MUCN", "UPMW", "VPMW", "SRH3", "U6SV", "V6SV",
#                 "DNCP", "M1CP", "M1CN", "QTRN", "XTRN", "SLCH", "RHLC",
#                 "WNDG", "EDCP", "U8SV", "V8SV", "S6MG", "X3KRH", "UEIL",
#                 "VEIL", "RH80", "RH70"]
# removed X from X3KRH
env_var_names = ["LR75", "LR85", "LPS4", "UWND", "VWND", "SBCP", "SBCN",
                 "MUCP", "MUCN", "UPMW", "VPMW", "SRH3", "U6SV", "V6SV",
                 "DNCP", "M1CP", "M1CN", "QTRN", "XTRN", "SLCH", "RHLC",
                 "WNDG", "EDCP", "U8SV", "V8SV", "S6MG", "3KRH", "UEIL",
                 "VEIL", "RH80", "RH70"]

#  without Function (Equivalent to %w/o%)
def without(x, y):
    return [item for item in x if item not in y]

### check_names_fn Function ###

import pandas as pd

def check_names_fn(var_names, if_text, our_k, spatial_window, 
                   if_fourier_time, month_comp, hour_comp, month_added, 
                   basic_var_names, env_var_names, verbose=True):
    
    text_var_names = [f"text_{i}" for i in range(1, our_k + 1)]

    if if_text:
        check_names = basic_var_names + [f"{env_var}_{i}" for env_var in env_var_names for i in range(1, 26)] + text_var_names
    else:
        check_names = basic_var_names + [f"{env_var}_{i}" for env_var in env_var_names for i in range(1, 26)]

    if spatial_window == 1:
        check_names += ["magnitude_closest", "s_t_dist"]
    elif spatial_window == 2:
        check_names += ["s_t_ind"]

    # Assuming transform_time is a function that transforms time and returns column names
    sample_time = ["05/16/2019 21:55", "02/20/2018 22:55"]
    time_name = transform_time(sample_time, if_fourier_time, month_comp, hour_comp, month_added).columns.tolist() if if_fourier_time else ['Year', 'day', 'month', 'hour', 'minute']
    check_names = time_name + check_names

    if if_text:
        check_names_2 = [name.replace("text_", "X") for name in check_names]
    else:
        check_names_2 = check_names

    # Add additional logic as per the original function's requirements

    return check_names, check_names_2

# Example usage
# var_names = [...] # Define your list of variable names
# basic_var_names = [...] # Define basic variable names
# env_var_names = [...] # Define environmental variable names
# check_names, check_names_2 = check_names_fn(var_names, if_text, our_k, spatial_window, if_fourier_time, month_comp, hour_comp, month_added, basic_var_names, env_var_names)



#def check_names_fn(var_names, if_text=True, our_k=30, spatial_window=0,
#                   if_fourier_time=True, month_comp=4, hour_comp=8, month_added=True,
#                   verbose=True):
#    # Generate text_var_names and check_names
#    text_var_names = [f"text_{i}" for i in range(1, our_k + 1)]
#    env_var_rep_names = [f"{var}_{i}" for var in env_var_names for i in range(1, 26)]
#
#    if if_text:
#        check_names = basic_var_names + env_var_rep_names + text_var_names
#    else:
#        check_names = basic_var_names + env_var_rep_names
#
#    if spatial_window == 1:
#        check_names += ["magnitude_closest", "s_t_dist"]
#    elif spatial_window == 2:
#        check_names += ["s_t_ind"]
#
#    sample_time <- c("05/16/2019 21:55", "02/20/2018 22:55")
#    if not (if_fourier_time){
#        time_name <- colnames(transform_time(sample_time))
#        # time_name <- c("Year", "day", "month", "hour", "minute")
#    } else {
#        time_name <- colnames(transform_time(sample_time, 1,
#                                            month_comp, hour_comp , month_added))
#    }
#        
#    check_names = time_name + check_names
#    if(if_text){
#        check_names_2 = [name.replace("text_", "X") for name in check_names] if if_text else check_names
#    }
#
#    # Perform the check
#    return check_var_names(var_names, check_names, check_names_2, our_k, verbose)

# Example usage
# updated_var_names = check_names_fn(var_names)
############################################################################################################


### Dimension Reduction ### 

import pandas as pd
import numpy as np

def dim_reduction_1(whole_mat, env_var_names):
    # Replace -9999, -999, and -99 with NaN
    whole_mat = whole_mat.replace([-9999, -999, -99], np.nan)

    # Define outer and inner variables
    outer_var = ["UWND", "VWND", "SBCP"]
    inner_var = [var for var in env_var_names if var not in outer_var]

    # Prepare for new DataFrame
    new_columns = []
    new_data = []

    # Process other non-environmental variables
    # Assuming these are the columns in whole_mat that are not in env_var_names
    other_vars = [col for col in whole_mat.columns if col.split('_')[0] not in env_var_names]
    new_columns.extend(other_vars)
    new_data.append(whole_mat[other_vars])

    # Process outer variables (retaining all 25)
    outer_vars = [f"{var}_{i}" for var in outer_var for i in range(1, 26)]
    new_columns.extend(outer_vars)
    new_data.append(whole_mat[outer_vars])

    # Process inner variables with dimension reduction
    for var in inner_var:
        for metric in ['min', 'avg', 'max']:
            col_name = f"{var}_{metric}"
            new_columns.append(col_name)

            if metric == 'avg':
                # Compute average, ignoring NA values
                avg_col = whole_mat[[f"{var}_{i}" for i in range(1, 10)]].mean(axis=1, skipna=True)
                new_data.append(avg_col)
            elif metric == 'min':
                # Compute min, ignoring NA values
                min_col = whole_mat[[f"{var}_{i}" for i in range(1, 26)]].min(axis=1, skipna=True)
                new_data.append(min_col)
            elif metric == 'max':
                # Compute max, ignoring NA values
                max_col = whole_mat[[f"{var}_{i}" for i in range(1, 26)]].max(axis=1, skipna=True)
                new_data.append(max_col)

    # Construct the new DataFrame
    new_mat = pd.DataFrame(np.column_stack(new_data), columns=new_columns)

    return new_mat

# Example usage
# env_var_names = [...]  # Define your environmental variable names
# new_mat = dim_reduction_1(whole_mat, env_var_names)
############################################################################################################


### Dimension Reduction 11 ### 


# Does dim reduction type 11
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      more than 20 NA's(/25) is considered as NA for min/max

#This script replicates the functionality of the dim_reduction_11 R function. It creates a new DataFrame with reduced dimensions 
# for the specified variables, handling missing values and applying the specific logic for averaging, minimum, and maximum calculations. 

def dim_reduction_11(whole_mat, env_var_names):
    # Replace -9999, -999, and -99 with NaN
    whole_mat = whole_mat.replace([-9999, -999, -99], np.nan)

    # Define outer and inner variables

    inner_pts = [7, 8, 9, 12, 13, 14, 17, 18, 19]
    outer_var = ["UWND", "VWND", "SBCP"]
    inner_var = [var for var in env_var_names if var not in outer_var]

    new_mat = pd.DataFrame()

    # Other non-environmental variables
    other_vars = [col for col in whole_mat.columns if col.split('_')[0] not in env_var_names]
    new_mat[other_vars] = whole_mat[other_vars]

    # All 25 variables for outer_var
    for var in outer_var:
        outer_var_names = [f"{var}_{i}" for i in range(1, 26)]
        new_mat[outer_var_names] = whole_mat[outer_var_names]

    # Reduced Variables for inner_var
    for var in inner_var:
        # Average
        avg_cols = [f"{var}_{i}" for i in inner_pts]
        new_mat[f"{var}_avg"] = whole_mat[avg_cols].mean(axis=1, skipna=True)

        # Min and Max with NA handling
        min_max_cols = [f"{var}_{i}" for i in range(1, 26)]
        tmp_mat = whole_mat[min_max_cols]

        # Min
        new_mat[f"{var}_min"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.min(skipna=True), axis=1)

        # Max
        new_mat[f"{var}_max"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.max(skipna=True), axis=1)

    return new_mat

# Example usage
# env_var_names = [...]  # Define your environmental variable names
# new_mat = dim_reduction_11(whole_mat, env_var_names)
############################################################################################################


### Does dim reduction type 2 ### 

## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      all NA's(/25) is considered as NA for min/max
## Now not used I guess

# * The dim_reduction_2 function in R is similar to dim_reduction_1 but has a distinct approach for handling different sets of environmental variables. It separates variables into three categories: outer_var, min_var, and max_var, and performs dimension reduction differently for each:
# * 
# * outer_var: Retains all 25 instances of these variables.
# * min_var: Calculates the minimum and average for these variables based on a subset of data points (inner_pts).
# * max_var: Calculates the maximum and average for these variables, also based on inner_pts.

def dim_reduction_2(whole_mat, env_var_names):
    # Replace -9999, -999, and -99 with NaN
    whole_mat = whole_mat.replace([-9999, -999, -99], np.nan)

    # Define variable categories
    outer_var = ["UWND", "VWND", "SBCP"]
    min_var = ["RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN"]  # I think R was adding the X in X3KRH.
    #min_var = ["RHLC", "X3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN"]
    max_var = [var for var in env_var_names if var not in outer_var + min_var]

    # Inner points for averaging
    inner_pts = [7, 8, 9, 12, 13, 14, 17, 18, 19]

    new_mat = pd.DataFrame()

    # Other non-environmental variables
    other_vars = [col for col in whole_mat.columns if col.split('_')[0] not in env_var_names]
    new_mat[other_vars] = whole_mat[other_vars]

    # All 25 variables for outer_var
    for var in outer_var:
        outer_var_names = [f"{var}_{i}" for i in range(1, 26)]
        new_mat[outer_var_names] = whole_mat[outer_var_names]

    # Reduced Min type Variables
    for var in min_var:
        # Average
        avg_cols = [f"{var}_{i}" for i in inner_pts]
        new_mat[f"{var}_avg"] = whole_mat[avg_cols].mean(axis=1, skipna=True)

        # Min
        min_cols = [f"{var}_{i}" for i in range(1, 26)]
        tmp_mat = whole_mat[min_cols]
        new_mat[f"{var}_min"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.min(skipna=True), axis=1)

    # Reduced Max type Variables
    for var in max_var:
        # Average
        avg_cols = [f"{var}_{i}" for i in inner_pts]
        new_mat[f"{var}_avg"] = whole_mat[avg_cols].mean(axis=1, skipna=True)

        # Max
        max_cols = [f"{var}_{i}" for i in range(1, 26)]
        tmp_mat = whole_mat[max_cols]
        new_mat[f"{var}_max"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.max(skipna=True), axis=1)

    return new_mat

# Example usage
# new_mat = dim_reduction_2(whole_mat, env_var_names)
############################################################################################################








#### Does dim reduction type 21 ####
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      more than 20 NA's(/25) is considered as NA for min/max

# * The dim_reduction_21 function in R is a variant of the dimension reduction functions we've seen earlier. It differs in the following ways:
# * 
# * Variable Categories: Like dim_reduction_2, it divides variables into outer_var, min_var, and max_var, but with slightly different treatment of min_var and max_var.
# * Handling of NA Values: The function uses a similar approach to handle missing values (represented by -9999, -999, and -99) but introduces specific conditions for calculating averages, minimums, and maximums:
# * For averages, more than 7 NAs out of 9 values result in an NA for the average.
# * For minimums and maximums, more than 20 NAs out of 25 values result in an NA.


def dim_reduction_21(whole_mat, env_var_names):
    # Replace specific values with NaN
    whole_mat = whole_mat.replace([-9999, -999, -99], np.nan)

    outer_var = ["UWND", "VWND", "SBCP"]
#    min_var = ["RHLC", "X3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN"]
    min_var = ["RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN"]
    max_var = [var for var in env_var_names if var not in outer_var + min_var]

    inner_pts = [7, 8, 9, 12, 13, 14, 17, 18, 19]

    new_mat = pd.DataFrame()

    # Process other non-environmental variables
    other_vars = [col for col in whole_mat.columns if col.split('_')[0] not in env_var_names]
    new_mat[other_vars] = whole_mat[other_vars]

    # Process outer variables
    for var in outer_var:
        outer_var_names = [f"{var}_{i}" for i in range(1, 26)]
        new_mat[outer_var_names] = whole_mat[outer_var_names]

    # Process min and max variables
    for var in min_var + max_var:
        # Average
        avg_cols = [f"{var}_{i}" for i in inner_pts]
        tmp_mat = whole_mat[avg_cols]
        tmp_mat = tmp_mat.apply(lambda x: x if x.count() > 7 else [np.nan] * len(x), axis=1)
        new_mat[f"{var}_avg"] = tmp_mat.mean(axis=1)

        # Min or Max
        min_max_cols = [f"{var}_{i}" for i in range(1, 26)]
        tmp_mat = whole_mat[min_max_cols]
        if var in min_var:
            new_mat[f"{var}_min"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.min(), axis=1)
        else:
            new_mat[f"{var}_max"] = tmp_mat.apply(lambda x: np.nan if x.isna().sum() >= 20 else x.max(), axis=1)

    return new_mat

# Example usage
# new_mat = dim_reduction_21(whole_mat, env_var_names)


# The R function impute_UVEIL_RH7080 iterates over a range of column names and performs conditional imputation: 
# if a value in a specified column is NA, it replaces it with the value from a corresponding column. Here's the Python equivalent using pandas:
############################################################################################################




##### *Imputation (NA and -9999) ########
## Imputes RH70, RH80 (by RHLC), UEIL and VEIL (by U8SV and V8SV)
## Recovers huge number of data points

def impute_UVEIL_RH7080(dat1):
    for i in range(1, 26):
        ind_1 = f"RH70_{i}"
        ind_2 = f"RHLC_{i}"
        dat1[ind_1] = dat1[ind_1].fillna(dat1[ind_2])

        ind_1 = f"RH80_{i}"
        dat1[ind_1] = dat1[ind_1].fillna(dat1[ind_2])

        ind_1 = f"UEIL_{i}"
        ind_2 = f"U8SV_{i}"
        dat1[ind_1] = dat1[ind_1].fillna(dat1[ind_2])

        ind_1 = f"VEIL_{i}"
        ind_2 = f"V8SV_{i}"
        dat1[ind_1] = dat1[ind_1].fillna(dat1[ind_2])

    return dat1

# Example usage
# dat1 = impute_UVEIL_RH7080(dat1)
############################################################################################################


#### Add indicator #### 
# The R function add_indicator adds indicator variables to a dataset for specific cases where values are -9999, -999.9, or -99.99. 
# It also replaces these specific values with 0. Here's how to translate this function into Python:

# This Python function assumes dat1 is a pandas DataFrame and env_var_names is a list of environmental variable names. 
# The function iterates over the specified columns, creates an indicator column for each, and replaces the specified values with 0.

def add_indicator(dat1, env_var_names, case_9999=True, case_999=True, case_99=True):
    all_env_names = [f"{var}_{i}" for var in env_var_names for i in range(1, 26)]
    for col in all_env_names:
        ind_name = f"{col}_ind"
        # Create indicator variable
        dat1[ind_name] = ((dat1[col] == -9999) | (dat1[col] == -999.9) | (dat1[col] == -99.99)).astype(int)

        # Replace specific values with 0
        dat1[col] = dat1[col].replace([-9999, -999.9, -99.99], 0)

    return dat1

# Example usage
# dat1 = add_indicator(dat1, env_var_names)

############################################################################################################


#### Compress_ind ####


## dat1 is the output from add_indicator/dim_reduction_1_ind(see next)
## i.e., (with indicators)
## Removes repetition of indicator columns and/or linearly independent columns

# The R function compress_ind is designed to process a dataset by focusing on indicator columns 
# that denote specific cases (like -9999 values). Here's how you can convert it to Python:

def compress_ind(dat1, env_var_names, remove_identical_col=True, remove_lin_dep=True):
    # Create list of all environmental indicator column names
    all_env_ind = [col for col in dat1.columns if "_ind" in col]
    tmp_dat = dat1[all_env_ind]

    # Removing columns without any indicators
    non_null_names = [col for col in tmp_dat.columns if tmp_dat[col].sum() > 0]
    tmp_dat = tmp_dat[non_null_names]

    # Identical columns removal
    if remove_identical_col:
        white_listed = []
        for i in non_null_names:
            if all(not tmp_dat[i].equals(tmp_dat[j]) for j in white_listed):
                white_listed.append(i)
        tmp_dat = tmp_dat[white_listed]

    # For linear dependence removal, additional logic would be required

    return tmp_dat

# Example usage
# compressed_dat = compress_ind(dat1, env_var_names)
# This script replicates the operations performed by the original R function, using pandas and SciPy for data manipulation and QR decomposition 
# (for linear dependency check). The function assumes that dat1 is a pandas DataFrame.



import pandas as pd
import numpy as np

def compress_ind(dat1, env_var_names, remove_identical_col=True, remove_lin_dep=True):
    all_env_ind = [col for col in dat1.columns if "_ind" in col]
    tmp_dat = dat1[all_env_ind]

    # Removing non-9999 columns
    non_null_names = tmp_dat.columns[tmp_dat.sum(axis=0, skipna=True) > 0]
    tmp_dat = tmp_dat[non_null_names]

    # Identical columns removal
    if remove_identical_col:
        tmp_dat = tmp_dat.loc[:, ~tmp_dat.columns.duplicated()]

    # Linear dependency check
    if remove_lin_dep:
        q, _ = np.linalg.qr(tmp_dat.fillna(0))  # Replace NA values with 0 for QR decomposition
        tmp_dat = tmp_dat.iloc[:, np.abs(q).sum(axis=0).argsort()]  # Order columns by importance

    # Combine with original data, excluding old indicator columns
    dat1 = dat1.drop(columns=all_env_ind)
    dat1 = pd.concat([dat1, tmp_dat], axis=1)

    # Convert new indicator columns to factors (categorical in pandas)
    for col in tmp_dat.columns:
        dat1[col] = dat1[col].astype('category')

    return dat1

#import pandas as pd
#from scipy.linalg import qr

#def compress_ind(dat1, env_var_names, remove_identical_col=True, remove_lin_dep=True):
#    all_env_ind = [col for col in dat1.columns if "_ind" in col]
#    tmp_dat = dat1[all_env_ind]
#
#    # Removing non-9999 columns
#    non_null_names = tmp_dat.columns[tmp_dat.sum(na.rm=True) > 0]
#    tmp_dat = tmp_dat[non_null_names]
#
#    # Identical columns removal
#    if remove_identical_col:
#        tmp_dat = tmp_dat.loc[:,~tmp_dat.columns.duplicated()]
#
#    # Linear dependency check
#    if remove_lin_dep:
#        q, _ = qr(tmp_dat, pivoting=True)
#        tmp_dat = tmp_dat.iloc[:, q[:tmp_dat.shape[1]]]
#
#    # Combine with original data, excluding old indicator columns
#    dat1 = dat1.drop(columns=all_env_ind)
#    dat1 = pd.concat([dat1, tmp_dat], axis=1)
#
#    # Convert new indicator columns to factors (categorical in pandas)
#    for col in tmp_dat.columns:
#        dat1[col] = dat1[col].astype('category')
#
#    return dat1

# Example usage
# compressed_dat = compress_ind(dat1, env_var_names)
############################################################################################################






#### Dim Reduction 1 IND ####

## Does dim reduction type 11 with added indices
## First, before coming to this function, original NA's are removed
##      (CHECK this is better or we should use count both NA and -9999 cases and consider 7/20 cases etc.)
##
## Then,
##      first, -9999 are treated as NA and indicators are added
##
##      more than 7 NA's(/9) is considered as 0 for avg (with corresponding ind)
##      more than 20 NA's(/25) is considered as 0 for min/max (with corresponding ind)
##
## compress_ind must be called after this function
##

# The dim_reduction_1_ind function in R performs dimension reduction while adding indicators for certain cases (-9999, -999.9, -99.99) 
# and replacing these cases with zeros. Here's the Python translation:

import numpy as np
import pandas as pd
#import warnings

def dim_reduction_1_ind(whole_mat, env_var_names):
    inner_pts = [7, 8, 9, 12, 13, 14, 17, 18, 19]
    outer_var = ["UWND", "VWND", "SBCP"]
    inner_var = [var for var in env_var_names if var not in outer_var]

    # Process outer_var variables
    for var in outer_var:
        for i in range(1, 26):
            col_name = f"{var}_{i}"
            ind_name = f"{var}_{i}_ind"
            whole_mat[ind_name] = whole_mat[col_name].isin([-9999, -999.9, -99.99]).astype(int)
            whole_mat[col_name] = whole_mat[col_name].replace([-9999, -999.9, -99.99], 0)

    # Process inner_var variables
    for var in inner_var:
        for i in range(1, 26):
            col_name = f"{var}_{i}"
            ind_name = f"{var}_{i}_ind"
            whole_mat[ind_name] = whole_mat[col_name].isin([-9999, -999.9, -99.99]).astype(int)
            whole_mat[col_name] = whole_mat[col_name].replace([-9999, -999.9, -99.99], 0)

        # Compute averages with indicators
        avg_cols = [f"{var}_{i}" for i in inner_pts]
        avg_ind_cols = [f"{var}_{i}_ind" for i in inner_pts]
        whole_mat[f"{var}_avg"] = whole_mat[avg_cols].replace({0: np.nan}).mean(axis=1)
        whole_mat[f"{var}_avg_ind"] = (whole_mat[avg_ind_cols].sum(axis=1) > 7).astype(int)

        # Compute min and max with indicators
        for metric in ['min', 'max']:
            cols = [f"{var}_{i}" for i in range(1, 26)]
            ind_cols = [f"{var}_{i}_ind" for i in range(1, 26)]
            if metric == 'min':
                whole_mat[f"{var}_min"] = whole_mat[cols].replace({0: np.nan}).min(axis=1)
            else:
                whole_mat[f"{var}_max"] = whole_mat[cols].replace({0: np.nan}).max(axis=1)
            whole_mat[f"{var}_{metric}_ind"] = (whole_mat[ind_cols].sum(axis=1) >= 20).astype(int)

    # Checking for indexing problems
    for var in inner_var:
        for metric in ['avg', 'min', 'max']:
            val_col = f"{var}_{metric}"
            ind_col = f"{var}_{metric}_ind"
            if any(whole_mat[val_col] * whole_mat[ind_col] != 0):
                warnings.warn(f"Problem in indexing for {var} {metric}!")

    return whole_mat

# Example usage
# new_mat = dim_reduction_1_ind(whole_mat, env_var_names)




############################################################################################################

### Dim Reduction 2 IND ###
# final_mat_2_new.shape
# (1391, 821)

import pandas as pd
import numpy as np

def dim_reduction_2_ind(whole_mat, na_rm=True, remove_9999=True, remove_999=True, remove_99=True):
    inner_pts = [7, 8, 9, 12, 13, 14, 17, 18, 19]
    outer_var = ["UWND", "VWND", "SBCP"]
    min_var = ["RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN"]
    max_var = list(set(env_var_names) - set(outer_var + min_var))

    long_names = whole_mat.columns
    long_env_names = [f"{var}_{i}" for var in env_var_names for i in range(1, 26)]
    other_var_names = list(set(long_names) - set(long_env_names))

    min_var_names = [f"{var}_{suffix}" for var in min_var for suffix in ["min", "avg"]]
    max_var_names = [f"{var}_{suffix}" for var in max_var for suffix in ["avg", "max"]]
    outer_var_names = [f"{var}_{i}" for var in outer_var for i in range(1, 26)]
    short_env_names = list(set(outer_var_names + min_var_names + max_var_names))
    short_names = list(set(other_var_names + short_env_names))

    new_mat = pd.DataFrame(index=whole_mat.index, columns=short_names)
    print("whole_mat:", whole_mat.shape)
    print("new_mat:", new_mat.shape)

    # Other non-environmental variables
    for var in other_var_names:
        new_mat[var] = whole_mat[var]

    # All 25 variables

    for var in outer_var_names:
        tmp = whole_mat[var]
        new_mat[var] = tmp
        ind_name = f"{var}_ind"
        new_mat[ind_name] = np.where((tmp == -9999) | (tmp == -999.9) | (tmp == -99.99), 1, 0) # replace -9999, -999.9, -99.99 with 1 else 0
        new_mat[var] = np.where((tmp == -9999) | (tmp == -999.9) | (tmp == -99.99), 0, tmp)  # replace -9999, -999.9, -99.99 with 0
    print("whole_mat:", whole_mat.shape)
    print("new_mat:", new_mat.shape)

    # Reduced min and max type variables
    print(min_var)
    print(max_var)
    print(inner_pts)
    for var_list in [min_var, max_var]:
        ## avg of inside elements:
        for var in var_list:
            # print(var)
            tmp_names = [f"{var}_{i}" for i in inner_pts]
 #           print(f"Variable: {var}, tmp_names: {tmp_names}")
            tmp_mat = whole_mat[tmp_names]

            # tmp_mat_ind = (tmp_mat == -9999) | (tmp_mat == -999.9) | (tmp_mat == -99.99)
            tmp_mat = tmp_mat.replace([-9999, -999.9, -99.99], np.nan) # replace -9999, -999.9, -99.99 with NaN

            tmp_vec = tmp_mat.mean(axis=1, skipna=na_rm)
            tmp_vec = np.where(tmp_mat.isna().sum(axis=1) > 7, 0, tmp_vec) ## added >7 NA per 9
            
            suffix = "min" if var_list == min_var else "max"
            new_mat[f"{var}_{suffix}"] = tmp_mat.apply(lambda x: 0 if x.isna().sum() >= 20 else x.min(skipna=na_rm) if suffix == "min" else x.max(skipna=na_rm), axis=1) # provides min or max values for a row unless # of na >20
            new_mat[f"{var}_{suffix}_ind"] = tmp_mat.apply(lambda x: 1 if x.isna().sum() >= 20 else 0, axis=1) # identifies the rows with >20 na's

            # Check for indexing issues
            #for var in var_list:
            #    suffix = "min" if var_list == min_var else "max"
            #    problem_rows = new_mat[(new_mat[f"{var}_{suffix}"] * new_mat[f"{var}_{suffix}_ind"] != 0)]
            #    if not problem_rows.empty:
            #        print(f"Problem in {var}_{suffix}:")
            #        print(problem_rows[[f"{var}_{suffix}", f"{var}_{suffix}_ind"]].head())  # Show first few problematic rows

## need to figure out if the next 3 lines really are required Dec 5, 2023 as a check change the nans?
          #  if any((new_mat[f"{var}_{suffix}"] * new_mat[f"{var}_{suffix}_ind"] != 0).values):
          #      print("Problem in indexing!!!")
          #     # print(new_mat[f"{var}_{suffix}"],new_mat[f"{var}_{suffix}_ind"], var, suffix)

            #problem_rows = new_mat[(new_mat[f"{var}_{suffix}"] * new_mat[f"{var}_{suffix}_ind"] != 0)]
            #print(problem_rows[[f"{var}_{suffix}", f"{var}_{suffix}_ind"]].head())  # Show first few problematic rows

    return new_mat

############################################################################################################


### Set up some Variables ### 
# these variables were outside of the function, as far as I can tell they are only used for this function so I put them within the function below. 

#   import numpy as np
#   
#   # Create a 5x5 matrix with values from 1 to 25
#   pos = np.arange(1, 26).reshape(5, 5)
#   
#   # Get the number of rows in pos
#   n_tmp = pos.shape[0]
#   
#   # Create a padded matrix with NaNs
#   mat_pad = np.pad(pos, pad_width=1, mode='constant', constant_values=np.nan)
#   
#   # Define indices for the original matrix within the padded matrix
#   ind = np.arange(1, n_tmp + 1)
#   
#   # Extract neighbors
#   N = mat_pad[ind - 1, ind].flatten()
#   E = mat_pad[ind, ind + 1].flatten()
#   S = mat_pad[ind + 1, ind].flatten()
#   W = mat_pad[ind, ind - 1].flatten()
#   
#   # Combine into a single array
#   neigh = np.vstack([N, E, S, W])
#   
#   # If you need it in a dictionary format
#   neigh_dict = {"N": N, "E": E, "S": S, "W": W}

import numpy as np
import pandas as pd

def neighbour_avg_9999(whole_mat, env_var_names):
    # Create a 5x5 matrix with values from 1 to 25
    pos = np.arange(1, 26).reshape(5, 5)

    # Create a padded matrix with NaNs
    mat_pad = np.pad(pos, pad_width=1, mode='constant', constant_values=np.nan)

    # Define indices for the original matrix within the padded matrix
    ind = np.arange(1, pos.shape[0] + 1)

    # Extract neighbors
    N = mat_pad[ind - 1, ind].flatten()
    E = mat_pad[ind, ind + 1].flatten()
    S = mat_pad[ind + 1, ind].flatten()
    W = mat_pad[ind, ind - 1].flatten()
    neigh = np.vstack([N, E, S, W])

    # Process the whole matrix
    var_names = [f"{var}_{i}" for var in env_var_names for i in range(1, 26)]
    for i in range(whole_mat.shape[0]):
        if np.any(np.isin(whole_mat.iloc[i, :], [-9999, -999.9, -99.99])):
            tmp = whole_mat.iloc[i, :].copy()

            for j in range(len(env_var_names)):
                for k in range(25):
                    name1 = f"{env_var_names[j]}_{k + 1}"
                    name1_ind = var_names.index(name1)

                    if tmp[name1_ind] in [-9999, -999.9, -99.99]:
                        nbd_ind = neigh[:, k].astype(int) - 1
                        name_nbds = [f"{env_var_names[j]}_{idx + 1}" for idx in nbd_ind if idx != -1]
                        tmp_nbd_val = tmp[[var_names.index(name) for name in name_nbds if name in var_names]]
                        tmp_nbd_val_NA = tmp_nbd_val.replace([-9999, -999.9, -99.99], np.nan)
                        tmp_mean = tmp_nbd_val_NA.mean(skipna=True)

                        if not np.isnan(tmp_mean):
                            tmp[name1_ind] = tmp_mean

            whole_mat.iloc[i, :] = tmp

    return whole_mat

# Usage example:
# env_var_names = ['your', 'list', 'of', 'variable', 'names']
# whole_mat = pd.DataFrame(...)  # your DataFrame
# result = neighbour_avg_9999(whole_mat, env_var_names)

############################################################################################################


# These are comments that didn't have any functions from the R script but wanted to keep them in case they are useful later
##### * * specific way: #####





###### *Model Fitting #####
#source("Install_mxnet.R")
#library(mxnet)



##### *Post processing #####

############################################################################################################

### Brier Decomposition Function: ###

import numpy as np

def brier_decomposition(predicted, classes, Thres=0.5):
    n = len(predicted)
    ind_1 = np.where(predicted < Thres)[0]
    ind_2 = np.where(predicted >= Thres)[0]
    n_1, n_2 = len(ind_1), len(ind_2)

    f1, f2 = predicted[ind_1], predicted[ind_2]
    o1, o2 = classes[ind_1], classes[ind_2]
    f1_bar, f2_bar = f1.mean(), f2.mean()
    o1_bar, o2_bar = o1.mean(), o2.mean()
    o_bar = classes.mean()

    REL = (n_1 * ((f1_bar - o1_bar) ** 2) + n_2 * ((f2_bar - o2_bar) ** 2)) / n
    RES = -(n_1 * ((o1_bar - o_bar) ** 2) + n_2 * ((o2_bar - o_bar) ** 2)) / n
    UNC = o_bar * (1 - o_bar)
    WBV = ((np.var(f1) * (n_1 - 1)) + (np.var(f2) * (n_2 - 1))) / n
    WBC = -2 * ((np.cov(o1, f1, ddof=1)[0, 1] * (n_1 - 1)) + (np.cov(o2, f2, ddof=1)[0, 1] * (n_2 - 1))) / n

    return np.round([REL, RES, UNC, WBV, WBC], 4)


############################################################################################################

### Area Under the Curve (AUC) and Precision-Recall (AUCPR) Function: ### 

from sklearn.metrics import roc_auc_score, average_precision_score, roc_curve, precision_recall_curve
import matplotlib.pyplot as plt

def under_the_curve(prob, category, if_plot=True, type='auc'):
    m = prob.shape[1]
    val = np.zeros(m)

    if type not in ['auc', 'aucpr']:
        print("Currently supports auc, aucpr only!")
        return val

    category = category == 'A'

    for i in range(m):
        if type == 'auc':
            val[i] = roc_auc_score(category, prob[:, i])
            if if_plot:
                fpr, tpr, _ = roc_curve(category, prob[:, i])
                plt.plot(fpr, tpr, label=f"ROC curve (area = {val[i]:.2f})", color='C'+str(i))
        else:  # aucpr
            val[i] = average_precision_score(category, prob[:, i])
            if if_plot:
                precision, recall, _ = precision_recall_curve(category, prob[:, i])
                plt.plot(recall, precision, label=f"PR curve (area = {val[i]:.2f})", color='C'+str(i))

    if if_plot:
        plt.ylim([0, 1])
        plt.legend()
        plt.show()

    return val


############################################################################################################

### Plot Precision-Recall Function: ### 

def plot_pr(predicted, classes, our_col=1, if_add=True, if_colorise=False):
    precision, recall, _ = precision_recall_curve(classes, predicted)
    plt.plot(recall, precision, color=('C' + str(our_col)) if not if_colorise else None, label='Precision-Recall curve')
    plt.ylim([0, 1])
    if if_add:
        plt.show()


############################################################################################################

### PR_val_maj Function: ### 

import pandas as pd
from sklearn.metrics import precision_score, recall_score

def PR_val_maj(thres, Predicted_probs, Testset):
    conditions = [
        (Predicted_probs[:, 0] > thres) & (Predicted_probs[:, 1] > thres),
        (Predicted_probs[:, 0] > thres) & (Predicted_probs[:, 2] > thres),
        (Predicted_probs[:, 1] > thres) & (Predicted_probs[:, 2] > thres)
    ]
    choices = ['A', 'A', 'A']
    predicted_majorities = pd.Series(np.select(conditions, choices, default='B'))

    precision_val = precision_score(Testset['class1'], predicted_majorities, average='binary', pos_label='A')
    recall_val = recall_score(Testset['class1'], predicted_majorities, average='binary', pos_label='A')

    return precision_val, recall_val

############################################################################################################

### save fn names Function: ###

def save_fn_names(base_name=None, Use_Text=1, closest_distance_type=0,
                  train_end=2017, dim_reduction_type=2,
                  cut_off=50, train_start=2007,
                  our_k=30, Use_Fourier_time=0,
                  if_PR=False, if_SMOTE=False,
                  if_test=0, handle_9999=True, impute=True,
                  popelev=True, landuse=True, radardat=True):
    
    if base_name is None:
        save_names = "Result"
    else:
        save_names = base_name

    save_names += "_" + ("text" if Use_Text else "notext")
    save_names += "_closest_" + str(closest_distance_type)
    save_names += "_dimred_" + str(dim_reduction_type) + "_"

    if if_PR and if_SMOTE:
        raise ValueError("PR and SMOTE - both is on - change that!")
    elif if_PR:
        save_names += "PR_"
    elif not if_PR and if_SMOTE:
        save_names += "smote_"
    else:
        save_names += "_down_"

    save_names += str(train_end) + "_" + str(cut_off) + "_"

    if if_test:
        save_names += "test_"

    if Use_Fourier_time:
        save_names += "fourier_"

    save_names += "_"

    save_names += "9999_" if handle_9999 else "no9999_"
    save_names += "imputed_" if impute else "noimputed_"
    save_names += "popelev_" if popelev else "nopopelev_"
    save_names += "landuse_" if landuse else "nolanduse_"
    save_names += "radar" if radardat else "noradar"

    return save_names

############################################################################################################
############################################################################################################

