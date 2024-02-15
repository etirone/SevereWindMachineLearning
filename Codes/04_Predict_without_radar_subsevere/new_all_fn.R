###### *Preamble #######
# module load gcc/7.3.0-xegsmw4  r-digest  opencv  gsl  r



## To be fixed:

## Somehow '3KRH' becomes 'X3KRH'
## See dim_reduction_2
## Add 999 to 9999 also
## Add Aug 3rd's meeting in the dim reduction also









## Try to install packages if not installed
list.of.packages <- c("MASS","lattice","nlme","Matrix","class","codetools","rpart","survival","ROCR",
                      "tidyverse","ggplot2", "dplyr", "tidyr",
                      "topicmodels", "tm", "SnowballC", "wordcloud", "tidytext", "stringr",
                      "RColorBrewer", "maps", "caret", "caretEnsemble")
#new.packages <- list.of.packages[!(list.of.packages %in% installed.packages()[,"Package"])]
#if(length(new.packages)>0){
#  install.packages(new.packages,repos='https://cloud.r-project.org/')
#}
prev_dir <- getwd()






# ################  clean_text_vec   ################
###### Text cleaning #####
library("tm")
library("SnowballC")
library("wordcloud")
library("RColorBrewer")
library("Matrix")



clean_text_vec <- function(joined_text, if_remove_num = F){

  ## Define indices and make corpus:
  n <- length(joined_text)
  index_null <- which(joined_text=="")
  index_non_null <- (1:n)[-index_null]
  if(length(index_null)==0){
    index_non_null <- (1:n)
  }
  if(length(index_non_null)!=n){cat("There are missing docs in text!")}
  # if(length(index_non_null)!=n){cat("There are missing docs in text, those are removed")}
  # docs <- Corpus(VectorSource( joined_text[index_non_null] ))
  docs <- Corpus(VectorSource( joined_text ))




  ## Text transformation:
  toSpace <- content_transformer(function (x , pattern ) gsub(pattern, " ", x))
  docs <- tm_map(docs, toSpace, "/"); docs <- tm_map(docs, toSpace, "@"); docs <- tm_map(docs, toSpace, "\\|")


  ####### Cleaning the text ##########
  # Convert the text to lower case
  docs <- tm_map(docs, content_transformer(tolower))
  # Remove numbers
  if(if_remove_num){
    docs <- tm_map(docs, removeNumbers)
  }
  # Remove english common stopwords
  docs <- tm_map(docs, removeWords, stopwords("english"))
  # Remove your own stop word
  # specify your stopwords as a character vector
  # docs <- tm_map(docs, removeWords, c("blabla1", "blabla2"))
  # Remove punctuations
  docs <- tm_map(docs, removePunctuation)
  # Eliminate extra white spaces
  docs <- tm_map(docs, stripWhitespace)
  # Text stemming
  docs <- tm_map(docs, stemDocument)

  return(docs)
}




# ################  refined_dtm   ################

refined_dtm <- function(joined_text, if_remove_num = F){

  ## Define indices and make corpus:
  # n <- length(joined_text)
  # index_null <- which(joined_text=="")
  # index_non_null <- (1:n)[-index_null]
  # if(length(index_null)==0){
  #   index_non_null <- (1:n)
  # }
  # if(length(index_non_null)!=n){cat("There are missing docs in text, those are removed")}

  new_docs <- clean_text_vec(joined_text, if_remove_num)
  dtm <- DocumentTermMatrix(new_docs)

  # ## remove null docs
  # m_rowSums <- rowSums(sparseMatrix(i = dtm$i, j = dtm$j, x = dtm$v, dimnames = dtm$dimnames))
  # n <- nrow(dtm)
  # if(any(m_rowSums==0)){
  #   ind_non_null <- which(m_rowSums!=0)
  #   dtm <- dtm[ind_non_null,]
  #   return(list(dtm = dtm, ind_non_null = ind_non_null, n = n))
  # } else {
  #   ind_non_null <- 1:n
  #   return(list(dtm = dtm, ind_non_null = ind_non_null, n = n))
  # }



  ## Don't remove null docs, but have a index of non-null docs
  m_rowSums <- rowSums(sparseMatrix(i = dtm$i, j = dtm$j, x = dtm$v, dimnames = dtm$dimnames))
  n <- nrow(dtm)
  if(all(m_rowSums==0)){
    warning("No non-null document! Take as a serious warning!")
  }
  ind_non_null <- which(m_rowSums!=0)
  return(list(dtm = dtm, non_null = ind_non_null, n = n))
}

# dtm <- DocumentTermMatrix(docs)
# text_ctm <- CTM(dtm, k = 30)
# refined_dtm(joined_text)$dtm






####### *Finding nearest Distance ########

# Haversine formula is used to calculate distances:
# https://en.wikipedia.org/wiki/Haversine_formula
# https://www.movable-type.co.uk/scripts/latlong.html
# Haversin distance: Earth radius*0.0017 = 6371*0.0017 km (* 2) ~ 11 km (*2)

# abc <- "11/23/2019 16:24"
# (bcd <- strptime(as.character(abc), "%m/%d/%Y %H:%M"))
# difftime(c(bcd, bcd), Sys.time(), units="secs")


### second_min ### 

second_min <- function(arr){
  tmp1 <- min(arr[-which.min(arr)])
  return(which(arr==tmp1))
}

### distance_1_measured ###

## Takes time, lat and lon
# notice the format ("%m/%d/%Y %H:%M"), change if necessary

distance_1_measured <- function(time_vec, lat_vec, lon_vec, magnitude, date_format = "%m/%d/%Y %H:%M"){
  time_vec <- strptime(as.character(time_vec), date_format)
  lat_vec <- lat_vec*pi/180
  lon_vec <- lon_vec*pi/180

  n <- length(time_vec)
  magnitude_closest <- array(dim=n)
  s_t_dist <- array(dim=n)
  BIG_DIST <- 20000                 ## 0-1434 in ../final_mat_2_close_1st.csv
  BIG_CLOSEST <- 50                 ## Boundary point

  if(n==1){
    magnitude_closest <- BIG_CLOSEST
    s_t_dist <- BIG_DIST
  } else if(n>1) {
    for(indexm in 1:n){
      time_diff <- difftime(time_vec, time_vec[indexm], units="mins")/20   # 20 min as 1 time unit

      lat_diff <- (lat_vec - lat_vec[indexm])
      lon_diff <- (lon_vec - lon_vec[indexm])
      tmp_diff <- sin(lat_diff)^2 + cos(lat_vec)*cos(lat_vec[indexm])*sin(lon_diff)^2
      final_dist <- sqrt(as.numeric(time_diff)^2 +
                           (2*atan2(sqrt(tmp_diff), sqrt(1-tmp_diff))/0.0017)^2 )
      # Haversin distance: Earth radius*0.0017 = 6371*0.0017 km (* 2) ~ 11 km (*2)
      # 0.0017 degrees(?) as unit

      tmp_order <- second_min(final_dist)
      if(length(tmp_order)>1){
        if(any(indexm == tmp_order)){
          print(paste("Report from same time and place! index:", indexm))
          tmp_order <- tmp_order[-which(tmp_order==indexm)]
        }
        tmp_order <- tmp_order[1]
      }

      magnitude_closest[indexm] <- magnitude[tmp_order]
      s_t_dist[indexm] <- final_dist[tmp_order]
    }
  }
  # list(magnitude_closest=magnitude_closest, s_t_dist=s_t_dist)
  cbind(magnitude_closest=magnitude_closest, s_t_dist=s_t_dist)
}



### distance_1_estimated ###


distance_1_estimated <- function(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m,
                                 time_vec_e, lat_vec_e, lon_vec_e, date_format = "%m/%d/%Y %H:%M"){
  time_vec_m <- strptime(as.character(time_vec_m), date_format)
  time_vec_e <- strptime(as.character(time_vec_e), date_format)
  lat_vec_m <- lat_vec_m*pi/180
  lon_vec_m <- lon_vec_m*pi/180
  lat_vec_e <- lat_vec_e*pi/180
  lon_vec_e <- lon_vec_e*pi/180

  n_m <- length(time_vec_m)
  n_e <- length(time_vec_e)
  magnitude_closest <- array(dim = n_e)
  s_t_dist <- array(dim = n_e)
  BIG_DIST <- 20000
  BIG_CLOSEST <- 50


  if(n_m == 0){
    ## No measured case:
    magnitude_closest <- rep(BIG_CLOSEST, n_e)
    s_t_dist <- rep(BIG_DIST, n_e)
  } else if(n_m > 0){
    for(indexe in 1:n_e){
      time_diff <- difftime(time_vec_m, time_vec_e[indexe], units="mins")/20   # 20 min as 1 time unit

      lat_diff <- (lat_vec_m - lat_vec_e[indexe])
      lon_diff <- (lon_vec_m - lon_vec_e[indexe])
      tmp_diff <- sin(lat_diff)^2 + cos(lat_vec_m)*cos(lat_vec_e[indexe])*sin(lon_diff)^2
      final_dist <- sqrt(as.numeric(time_diff)^2 +
                           (2*atan2(sqrt(tmp_diff), sqrt(1-tmp_diff))/0.0017)^2 )
      # 0.0017 degrees(~11 km)(?) as 1 unit


      tmp_order <- which(final_dist == min(final_dist))
      tmp_order <- tmp_order[1]

      magnitude_closest[indexe] <- magnitude_m[tmp_order]
      s_t_dist[indexe] <- final_dist[tmp_order]
    }
  }
  # list(magnitude_closest=magnitude_closest, s_t_dist=s_t_dist)
  cbind(magnitude_closest=magnitude_closest, s_t_dist=s_t_dist)
}





distance_2_measured <- function(time_vec, lat_vec, lon_vec, magnitude, date_format = "%m/%d/%Y %H:%M"){
  time_vec <- strptime(as.character(time_vec), date_format)
  lat_vec <- lat_vec*pi/180
  lon_vec <- lon_vec*pi/180

  n <- length(time_vec)
  s_t_ind <- array(dim=n)

  if(n==1){
    s_t_ind <- 0
  } else if(n>1) {
    for(indexm in 1:n){
      count_1 <- 0
      count_2 <- 0

      ## Calculating the differences:
      time_diff <- difftime(time_vec[-indexm], time_vec[indexm], units="mins")

      lat_diff <- (lat_vec[-indexm] - lat_vec[indexm])
      lon_diff <- (lon_vec[-indexm] - lon_vec[indexm])
      tmp_diff <- sin(lat_diff)^2 + cos(lat_vec[-indexm])*cos(lat_vec[indexm])*sin(lon_diff)^2
      sp_diff  <- 2*atan2(sqrt(tmp_diff), sqrt(1-tmp_diff))


      ## Counting number of events of type 1 and 2 inside the window:
      # count_1 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude<=50), count_1+1, count_1)
      # count_2 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude>50), count_2+1, count_2)
      ## BUG: sp and time_diff is of length n-1. magnitude is of length n
      count_1 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude[-indexm]<=50), count_1+1, count_1)
      count_2 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude[-indexm]>50), count_2+1, count_2)


      if(count_2>0){
        s_t_ind[indexm] <- 2
      } else if(count_1>0){
        s_t_ind[indexm] <- 1
      } else {
        s_t_ind[indexm] <- 0
      }
    }
  }
  factor(s_t_ind, levels = 0:2)
}


distance_2_estimated <- function(time_vec_m, lat_vec_m, lon_vec_m, magnitude_m,
                                 time_vec_e, lat_vec_e, lon_vec_e, date_format = "%m/%d/%Y %H:%M"){
  time_vec_m <- strptime(as.character(time_vec_m), date_format)
  time_vec_e <- strptime(as.character(time_vec_e), date_format)
  lat_vec_m <- lat_vec_m*pi/180
  lon_vec_m <- lon_vec_m*pi/180
  lat_vec_e <- lat_vec_e*pi/180
  lon_vec_e <- lon_vec_e*pi/180

  n_m <- length(time_vec_m)
  n_e <- length(time_vec_e)
  s_t_ind <- array(dim = n_e)


  for(indexe in 1:n_e){
    count_1 <- 0
    count_2 <- 0

    ## Calculating the differences:
    time_diff <- difftime(time_vec_m, time_vec_e[indexe], units="mins")

    lat_diff <- (lat_vec_m - lat_vec_e[indexe])
    lon_diff <- (lon_vec_m - lon_vec_e[indexe])
    tmp_diff <- sin(lat_diff)^2 + cos(lat_vec_m)*cos(lat_vec_e[indexe])*sin(lon_diff)^2
    sp_diff  <- 2*atan2(sqrt(tmp_diff), sqrt(1-tmp_diff))


    ## Counting number of events of type 1 and 2 inside the window:
    count_1 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude_m<=50), count_1+1, count_1)
    count_2 <- ifelse(any(sp_diff<0.0017 & time_diff<20 & magnitude_m>50), count_2+1, count_2)


    # check these are indexe, not indexm
    if(count_2>0){
      s_t_ind[indexe] <- 2
    } else if(count_1>0){
      s_t_ind[indexe] <- 1
    } else {
      s_t_ind[indexe] <- 0
    }
  }
  factor(s_t_ind, levels = 0:2)
}



###### *Pre processing ####

# if month added = TRUE, make month_comp more than 4?

transform_time <- function(time_vec, do_fourier = 0,
                           month_comp = 4, hour_comp = 8, month_added = TRUE, date_format = "%m/%d/%Y %H:%M"){
  time_vec  <- strptime(as.character(time_vec), date_format)
  year_vec  <- as.numeric(format(time_vec, "%Y"))
  month_vec <- as.numeric(format(time_vec, "%m"))
  day_vec   <- as.numeric(format(time_vec, "%d"))
  hour_vec  <- as.numeric(format(time_vec, "%H"))
  min_vec   <- as.numeric(format(time_vec, "%M"))


  if(do_fourier){

    hour_vec  <- hour_vec + min_vec/60
    if(month_added){
      month_vec <- month_vec - 1 + day_vec/31
      ## rough addition - use it or remove it?,
      ## -1 to start from 0 as in %H
    }

    # Center or not? - not needed I guess - anyhow, it's periodic
    # month_vec <- month_vec - 6.5
    # hour_vec  <- hour_vec - 12    # or 11.5? - It would be definitely 12 if hr and min were combined


    month_extended <- cbind(month_1 = cos(2*pi*month_vec/12), month_2 = sin(2*pi*month_vec/12)) # change if min is added
    hour_extended  <- cbind(hour_1  = cos(2*pi*hour_vec/24),  hour_2  = sin(2*pi*hour_vec/24))

    for(i in 2:((month_comp/2))){
      month_extended <- cbind(month_extended, cos(2*pi*i*month_vec/12), sin(2*pi*i*month_vec/12))
      colnames(month_extended)[c(2*i-1, 2*i)] <- paste0("month_", c(2*i-1, 2*i))
    }

    for(i in 2:((hour_comp/2))){
      hour_extended <- cbind(hour_extended, cos(2*pi*i*hour_vec/24), sin(2*pi*i*hour_vec/24))
      colnames(hour_extended)[c(2*i-1, 2*i)] <- paste0("hour_", c(2*i-1, 2*i))
    }

    if(month_added){
      return(cbind(year_vec, month_extended, hour_extended))
    } else {
      return(cbind(year_vec, month_extended, day_vec, hour_extended))
    }
  } else {
    return(cbind(Year = year_vec,
                 day = day_vec,
                 month = month_vec,
                 hour = hour_vec,
                 minute = min_vec))
  }
}











# magnitude_type?
# change names to "lat", "lon"
######### event_id?????????????????????????????????
# basic_var_names <- c("event_id", "magnitude", "location_1_lat", "location_1_lon")
basic_var_names <- c("magnitude", "location_1_lat", "location_1_lon")
env_var_names <- c("LR75", "LR85", "LPS4", "UWND", "VWND", "SBCP", "SBCN",
                   "MUCP", "MUCN", "UPMW", "VPMW", "SRH3", "U6SV", "V6SV",
                   "DNCP", "M1CP", "M1CN", "QTRN", "XTRN", "SLCH", "RHLC",
                   "WNDG", "EDCP", "U8SV", "V8SV", "S6MG", "X3KRH", "UEIL",
                   "VEIL", "RH80", "RH70")
# paste(rep(env_var_names, each=25), 1:25, sep="_")  ## this would give proper format with 1 to 25
# our_k
# text_var_names <- paste0("text_", 1:our_k)


"%w/o%" <- function(x, y) {
  x[!x %in% y]   #--  x without y
}

### check_names_fn Function ###

check_names_fn <- function(var_names, if_text = c(TRUE, FALSE), our_k = 30, spatial_window = c(0,1,2),
                        if_fourier_time = T, month_comp = 4, hour_comp = 8, month_added = TRUE,
                        verbose = TRUE){

  text_var_names <- paste0("text_", 1:our_k)

  if(if_text){
    check_names <- c(basic_var_names, paste(rep(env_var_names, each=25), 1:25, sep="_"), text_var_names)
  } else {
    check_names <- c(basic_var_names, paste(rep(env_var_names, each=25), 1:25, sep="_"))
  }

  if(spatial_window == 1){
    check_names <- c(check_names, "magnitude_closest", "s_t_dist")
  } else if (spatial_window == 2){
    check_names <- c(check_names, "s_t_ind")
  }

  sample_time <- c("05/16/2019 21:55", "02/20/2018 22:55")
  if(!if_fourier_time){
    time_name <- colnames(transform_time(sample_time))
    # time_name <- c("Year", "day", "month", "hour", "minute")
  } else {
    time_name <- colnames(transform_time(sample_time, 1,
                                         month_comp, hour_comp , month_added))
  }
  check_names <- c(time_name, check_names)

  if(if_text){
    # var_names_2 <- stringr::str_replace_all(var_names, "X", "text_")  # risky  XTERN would be problematic
    check_names_2 <- stringr::str_replace_all(check_names, "text_", "X")
  }



  #### Now check:
  if(all(check_names == var_names)){  ## Exact same
    if(verbose){
      print("Columns are okay!")
    }
    return(var_names)
  } else if ( all(sort(check_names) == sort(var_names))){   ## Diff order
    if(verbose){
      print("Columns are same - but not ordered!")
    }
    return(var_names)  ##?
  } else if(all(check_names_2 == var_names)){
    if(verbose){
      print("Columns are okay - but X1 instead of text_1 etc!")
    }
    var_names_2 -> var_names
    for(i in 1:our_k){
      var_names_2[which(var_names==paste0("X", i))] <- paste0("text_", i)
    }
  } else if(all(sort(check_names_2) == sort(var_names))){
    if(verbose){
      print("Columns are okay - but X1 instead of text_1 etc!")
    }
    var_names_2 -> var_names
    for(i in 1:our_k){
      var_names_2[which(var_names==paste0("X", i))] <- paste0("text_", i)
    }
  } else if( setequal(check_names, var_names) | setequal(check_names_2, var_names)){  ## Same names, duplicates?
    warning("Problem, set of names are equal - but they are not same!")
    return(var_names)
  } else {  ## Really different names
    warning("Problem, names are different!\n")
    print("Names are different:")
    unique(check_names %w/o% var_names)
    print("and")
    unique(var_names %w/o% check_names)
    # print(setdiff(check_names, var_names))
    return(var_names)
  }
}


# save_fn_names <- function(Use_Text = 1, closest_distance_type = 0,
#                           train_end = 2017, dim_reduction_type = 2,
#                           cut_off = 50, train_start = 2007,
#                           our_k = 30, Use_Fourier_time = 0){
#
#   save_names <- "Result"
#   save_names <- paste(save_names, "text", Use_Text, sep="_")
#   save_names <- paste(save_names, "close", closest_distance_type, sep="_")
#   save_names <- paste(save_names, "year", train_end, sep="_")
#   save_names <- paste(save_names, "dimred", dim_reduction_type, sep="_")
#   save_names <- paste(save_names, "sep", cut_off, sep="_")
#
#   return(save_names)
# }
# See args file







# Dimension Reduction:



## Does dim reduction type 1
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      all NA's(/25) is considered as NA for min/max
## Now not used I guess

dim_reduction_1 <- function(whole_mat, na.rm = TRUE,
                            remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  inner_var <- env_var_names %w/o% outer_var



  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  inner_var_names <- paste(rep(inner_var, each=3), c("min", "avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names, inner_var_names)

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat),
                                         ncol(whole_mat)
                                         - 25*31 + 25*length(outer_var) + 3*length(inner_var))))
  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    new_mat[, which(outer_var_names[j] == short_names)] <-
      whole_mat[, which(outer_var_names[j] == long_names)]
  }

  # Reduced Variables
  for(j in 1:length(inner_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(inner_var[j], each=9), inner_pts, sep="_")
    # grep(paste0("^", inner_var[j],"_"), long_names, value=TRUE)
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    tmp_vec <- array(dim = c(nrow(whole_mat)))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, NA, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(inner_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    ## what about NA values and -9999 values?


    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", inner_var[j],"_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { min(x, na.rm = na.rm) } })
    ## colwsie min is taken

    ## Max:
    new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { max(x, na.rm = na.rm) } })
  }

  return(new_mat)
}































## Does dim reduction type 11
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      more than 20 NA's(/25) is considered as NA for min/max

dim_reduction_11 <- function(whole_mat, na.rm = TRUE,
                            remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  inner_var <- env_var_names %w/o% outer_var



  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  inner_var_names <- paste(rep(inner_var, each=3), c("min", "avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names, inner_var_names)

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat),
                                         ncol(whole_mat)
                                         - 25*31 + 25*length(outer_var) + 3*length(inner_var))))
  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    new_mat[, which(outer_var_names[j] == short_names)] <-
      whole_mat[, which(outer_var_names[j] == long_names)]
  }

  # Reduced Variables
  for(j in 1:length(inner_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(inner_var[j], each=9), inner_pts, sep="_")
    # grep(paste0("^", inner_var[j],"_"), long_names, value=TRUE)
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    tmp_vec <- array(dim = c(nrow(whole_mat)))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, NA, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(inner_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    ## what about NA values and -9999 values?


    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", inner_var[j],"_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    # new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] <-
    #   apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { min(x, na.rm = na.rm) } })
    new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(sum(is.na(x)) >= 20){ NA } else { min(x, na.rm = na.rm) } })
    

    ## Max:
    # new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] <-
    #  apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { max(x, na.rm = na.rm) } })
    new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(sum(is.na(x)) >= 20){ NA } else { max(x, na.rm = na.rm) } })
  }

  return(new_mat)
}



## Does dim reduction type 2
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      all NA's(/25) is considered as NA for min/max
## Now not used I guess

dim_reduction_2 <- function(whole_mat, na.rm = TRUE,
                            remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  # min_var <- c("RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  min_var <- c("RHLC", "X3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  ## Somehow '3KRH' becomes 'X3KRH'
  max_var <- env_var_names %w/o% union(outer_var, min_var)



  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  min_var_names <- paste(rep(min_var, each=2), c("min", "avg"), sep = "_")
  max_var_names <- paste(rep(max_var, each=2), c("avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names, union(min_var_names, max_var_names))

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat),
                                         ncol(whole_mat)
                                         - 25*31 + 25*length(outer_var)
                                         + 2*length(min_var) + 2*length(max_var))))
  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    new_mat[, which(outer_var_names[j] == short_names)] <-
      whole_mat[, which(outer_var_names[j] == long_names)]
  }

  # Reduced Min type Variables
  for(j in 1:length(min_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(min_var[j], each = 9), inner_pts, sep="_")
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    new_mat[, which(paste(min_var[j], "avg", sep="_") == short_names)] <-
      rowMeans(tmp_mat, na.rm = na.rm)


    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", min_var[j], "_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { min(x, na.rm = na.rm) } })
    ## colwsie min is taken

  }


  # Reduced Max type Variables
  for(j in 1:length(max_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(max_var[j], each=9), inner_pts, sep="_")
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    new_mat[, which(paste(max_var[j], "avg", sep="_") == short_names)] <-
      rowMeans(tmp_mat, na.rm = na.rm)
    ## what about NA values and -9999 values?


    ## max:
    tmp_mat <- whole_mat[, grepl(paste0("^", max_var[j], "_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { max(x, na.rm = na.rm) } })
    ## colwsie max is taken
  }

  return(new_mat)
}




## Does dim reduction type 21
## First, -9999's are treated as NA
## Then,
##      more than 7 NA's(/9) is considered as NA for avg
##      more than 20 NA's(/25) is considered as NA for min/max



dim_reduction_21 <- function(whole_mat, na.rm = TRUE,
                            remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  # min_var <- c("RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  min_var <- c("RHLC", "X3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  ## Somehow '3KRH' becomes 'X3KRH'
  max_var <- env_var_names %w/o% union(outer_var, min_var)



  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  min_var_names <- paste(rep(min_var, each=2), c("min", "avg"), sep = "_")
  max_var_names <- paste(rep(max_var, each=2), c("avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names, union(min_var_names, max_var_names))

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat),
                                         ncol(whole_mat)
                                         - 25*31 + 25*length(outer_var)
                                         + 2*length(min_var) + 2*length(max_var))))
  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    new_mat[, which(outer_var_names[j] == short_names)] <-
      whole_mat[, which(outer_var_names[j] == long_names)]
  }

  # Reduced Min type Variables
  for(j in 1:length(min_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(min_var[j], each = 9), inner_pts, sep="_")
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    # new_mat[, which(paste(min_var[j], "avg", sep="_") == short_names)] <-
    #   rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, NA, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(min_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    ## Problem: there can be too many -9999 so that the mean becomes NaN (not NA)
    ## Check - Subrata



    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", min_var[j], "_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    # new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] <-
    #   apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { min(x, na.rm = na.rm) } })
    new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(sum(is.na(x)) >= 20){ NA } else { min(x, na.rm = na.rm) } })
    ## colwsie min is taken

  }


  # Reduced Max type Variables
  for(j in 1:length(max_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(max_var[j], each=9), inner_pts, sep="_")
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, NA, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(max_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    # new_mat[, which(paste(max_var[j], "avg", sep="_") == short_names)] <-
    #   rowMeans(tmp_mat, na.rm = na.rm)
    ## what about NA values and -9999 values?


    ## max:
    tmp_mat <- whole_mat[, grepl(paste0("^", max_var[j], "_"), long_names)]
    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }
    # new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] <-
    #   apply(tmp_mat, 1, function(x){ if(all(is.na(x))){ NA } else { max(x, na.rm = na.rm) } })
    new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if(sum(is.na(x)) >= 20){ NA } else { max(x, na.rm = na.rm) } })
    ## colwsie max is taken
  }

  return(new_mat)
}





##### *Imputation (NA and -9999) ########

## Imputes RH70, RH80 (by RHLC), UEIL and VEIL (by U8SV and V8SV)
## Recovers huge number of data points

impute_UVEIL_RH7080 <- function(dat1){

  for(i in 1:25){
    ind_1 <- paste("RH70", i, sep="_")
    ind_2 <- paste("RHLC", i, sep="_")
    dat1[[ind_1]] <- ifelse(is.na(dat1[[ind_1]]), dat1[[ind_2]], dat1[[ind_1]])

    ind_1 <- paste("RH80", i, sep="_")
    ind_2 <- paste("RHLC", i, sep="_")
    dat1[[ind_1]] <- ifelse(is.na(dat1[[ind_1]]), dat1[[ind_2]], dat1[[ind_1]])

    ind_1 <- paste("UEIL", i, sep="_")
    ind_2 <- paste("U8SV", i, sep="_")
    dat1[[ind_1]] <- ifelse(is.na(dat1[[ind_1]]), dat1[[ind_2]], dat1[[ind_1]])

    ind_1 <- paste("VEIL", i, sep="_")
    ind_2 <- paste("V8SV", i, sep="_")
    dat1[[ind_1]] <- ifelse(is.na(dat1[[ind_1]]), dat1[[ind_2]], dat1[[ind_1]])
  }

  return(dat1)
}





# dat <- tail(final_mat_2, 200)
# dim(dat)

## Add indicators for the 9999 cases
## and puts a 0 instead of -9999 cases
##      must be called when handle_9999 is TRUE and no dim reduction is done
##      compress_ind must be called after this

add_indicator <- function(dat1, case_9999 = T, case_999 = T, case_99 = T){
  all_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  for(i in all_env_names){
    tmp <- dat1[[i]]
    # if(any(tmp == -9999) || any(tmp == -999.9) || any(tmp == -99.99)){
      ind_name <- paste0(i, "_ind")
      dat1[[ind_name]] <- ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99,
                                1, 0)

      dat1[[i]] <- ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99,
                         0, tmp)
    # }
    ## Create ind variable for all, then compress in the next variable
  }
  return(dat1)
}

# dat <- tail(final_mat_2, 200)
# dim(dat)
# dat <- add_indicator(dat)
# dim(dat)



## dat1 is the output from add_indicator/dim_reduction_1_ind(see next)
## i.e., (with indicators)
## Removes repetition of indicator columns and/or linearly independent columns

compress_ind <- function(dat1, remove_identical_col = T, remove_lin_dep = T){
  all_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  # all_env_ind <- paste(all_env_names, "ind", sep="_")
  all_env_ind <- grep("_ind", names(dat1), value = T)
  tmp_dat <- subset(dat1, select = all_env_ind)
  dim(tmp_dat); names(tmp_dat)


  ## Removing non-9999 cols:
  ## colSums(tmp_dat) = 1 if there exists some -9999 etc case
  non_null_names <- names(which(colSums(tmp_dat, na.rm = TRUE) > 0))
  tmp_dat <- subset(tmp_dat, select = non_null_names)
  dim(tmp_dat); names(tmp_dat)


  ## Identical columns:
  black_listed <- c()  ## not very big vector
  for(i in seq_along(non_null_names)){
    for(j in seq_along(non_null_names)){
      if(i > j){
        if( identical(tmp_dat[[non_null_names[i]]], tmp_dat[[non_null_names[j]]]) ){
          black_listed <- c(black_listed, non_null_names[j])
          # print(paste(non_null_names[i], non_null_names[j], "are identical!"))
        }
      }
    }
  }
  black_listed
  white_listed <- non_null_names %w/o% black_listed
  # tmp_dat_2 <- subset(tmp_dat, select = white_listed)
  tmp_dat <- subset(tmp_dat, select = white_listed)
  dim(tmp_dat); names(tmp_dat)
  # rm(tmp_dat)



  ## Linear dependency:
  # tmp_dat_3_1 <- tmp_dat_2[, duplicated(cor(tmp_dat_2))]
  q <- qr(tmp_dat)
  tmp_dat <- tmp_dat[, q$pivot[seq_len(q$rank)]]
  dim(tmp_dat); names(tmp_dat)
  # https://stackoverflow.com/questions/14943422/r-independent-columns-in-matrix
  # https://stackoverflow.com/questions/19100600/extract-maximal-set-of-independent-columns-from-a-matrix



  ## Remove ind, then cbind:
  dat_names <- names(dat1)
  tmp_names_1 <- dat_names %w/o% all_env_ind
  # tmp_names_1
  # tmp_names_1 <- union(tmp_names_1, names(tmp_dat_3))
  dat1 <- subset(dat1, select = tmp_names_1)
  dat1 <- cbind(dat1, tmp_dat)
  names(dat1)



  ## Make them factor:
  all_env_ind_new <- grep("_ind", names(dat1), value = T)
  for(i in all_env_ind_new){
    dat1[[i]] <- as.factor(dat1[[i]])
  }


  return(dat1)
}


# dat <- tail(final_mat_2, 200)
# dim(dat)
# dat <- add_indicator(dat)
# dim(dat)
# dat <- compress_ind(dat)
# dim(dat)





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

dim_reduction_1_ind <- function(whole_mat, na.rm = TRUE,
                            remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  inner_var <- env_var_names %w/o% outer_var


  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  inner_var_names <- paste(rep(inner_var, each=3), c("min", "avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names, inner_var_names)

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat), ncol(whole_mat) -
                                          25*31 + 25*length(outer_var) + 3*length(inner_var))))
  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    tmp <- whole_mat[, which(outer_var_names[j] == long_names)]
    new_mat[, which(outer_var_names[j] == short_names)] <- tmp

    ind_name <- paste0(outer_var_names[j], "_ind")
    new_mat[[ind_name]] <-
      ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99, 1, 0)

    new_mat[, which(outer_var_names[j] == short_names)] <-
      ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99, 0, tmp)
  }


  # Reduced Variables:
  for(j in 1:length(inner_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(inner_var[j], each=9), inner_pts, sep="_")
    # grep(paste0("^", inner_var[j],"_"), long_names, value=TRUE)
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    tmp_vec <- array(dim = c(nrow(whole_mat)))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    tmp_mat_ind <- (tmp_mat == -9999 | tmp_mat == -999.9 | tmp_mat == -99.99)


    ## Wait: what if some of the NA's are non-zero - take care of that later
    ## TODO: NA part is still to be handled


    ## Mean: without the NA's, or -9999's - just the inner part
    ## With one indicator of being more than 20 -9999's or not
    ## 2 columns


    tmp_mat[tmp_mat== -9999 | tmp_mat== -999.9 | tmp_mat== -99.99] <- NA
    ## This would not work if na is not removed first

    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, 0, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(inner_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    new_mat[[paste(inner_var[j], "avg_ind", sep="_")]] <- (rowSums(tmp_mat_ind)>7)+0




    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", inner_var[j],"_"), long_names)]

    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }

    ## Change:
    ## if(all(is.na(x))){ NA }  would be replaced by if(all(is.na(x))){ 0 }

    #new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] <-
    #  apply(tmp_mat, 1, function(x){ if( all(is.na(x)) ){ 0 } else { min(x, na.rm = na.rm) } })

    new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 0 } else { min(x, na.rm = na.rm) } })

    ## colwsie min is taken
    #new_mat[[paste(inner_var[j], "min_ind", sep="_")]] <-
    #  is.na(new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)]) + 0
    ## ^BUG I guess
    new_mat[[paste(inner_var[j], "min_ind", sep="_")]] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 1 } else { 0 } })



    ## Max:
    #new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] <-
    #  apply(tmp_mat, 1, function(x){ if( all(is.na(x)) ){ 0 } else { max(x, na.rm = na.rm) } })

    new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 0 } else { max(x, na.rm = na.rm) } })


    #new_mat[[paste(inner_var[j], "max_ind", sep="_")]] <-
    #  is.na(new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)]) + 0
    new_mat[[paste(inner_var[j], "max_ind", sep="_")]] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 1 } else { 0 } })



    ## Check:
    if(any(new_mat[, which(paste(inner_var[j], "avg", sep="_") == short_names)] *
           new_mat[[paste(inner_var[j], "avg_ind", sep="_")]] != 0) |
       any(new_mat[, which(paste(inner_var[j], "min", sep="_") == short_names)] *
           new_mat[[paste(inner_var[j], "min_ind", sep="_")]] != 0) |
       any(new_mat[, which(paste(inner_var[j], "max", sep="_") == short_names)] *
           new_mat[[paste(inner_var[j], "max_ind", sep="_")]] != 0)){

      warning("Problem in indexing!!!")
    }

  }

  return(new_mat)
}

############################################################################################################


dim_reduction_2_ind <- function(whole_mat, na.rm = TRUE,
                                remove_9999 = T, remove_999 = T, remove_99 = T){

  inner_pts <- c(7, 8, 9, 12, 13, 14, 17, 18, 19)
  outer_var <- c("UWND", "VWND", "SBCP")
  # min_var <- c("RHLC", "3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  min_var <- c("RHLC", "X3KRH", "RH80", "RH70", "SBCN", "M1CN", "MUCN")
  ## Somehow '3KRH' becomes 'X3KRH'
  max_var <- env_var_names %w/o% union(outer_var, min_var)


  long_names <- colnames(whole_mat)
  long_env_names <- paste(rep(env_var_names, each=25), 1:25, sep="_")
  other_var_names <- long_names %w/o% long_env_names

  min_var_names <- paste(rep(min_var, each=2), c("min", "avg"), sep = "_")
  max_var_names <- paste(rep(max_var, each=2), c("avg", "max"), sep = "_")
  outer_var_names <- paste(rep(outer_var, each=25), 1:25, sep = "_")
  short_env_names <- union(outer_var_names,
                           union(min_var_names, max_var_names))

  short_names <- union(other_var_names, short_env_names)
  new_mat <- as.data.frame(array(dim = c(nrow(whole_mat), ncol(whole_mat) -
                                           25*31 + 25*length(outer_var)
                                         + 2*length(min_var) + 2*length(max_var))))
  ## Change dim properly and check

  colnames(new_mat) <- short_names


  # Other non-environmental variables
  for(j in 1:length(other_var_names)){
    new_mat[, which(other_var_names[j] == short_names)] <-
      whole_mat[, which(other_var_names[j] == long_names)]
  }

  # All 25 variables
  for(j in 1:length(outer_var_names)){
    tmp <- whole_mat[, which(outer_var_names[j] == long_names)]
    new_mat[, which(outer_var_names[j] == short_names)] <- tmp

    ind_name <- paste0(outer_var_names[j], "_ind")
    new_mat[[ind_name]] <-
      ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99, 1, 0)

    new_mat[, which(outer_var_names[j] == short_names)] <-
      ifelse(tmp == -9999 | tmp == -999.9 | tmp == -99.99, 0, tmp)
  }

    # Reduced min type Variables:
  for(j in 1:length(min_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(min_var[j], each=9), inner_pts, sep="_")
    # grep(paste0("^", min_var[j],"_"), long_names, value=TRUE)
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    tmp_vec <- array(dim = c(nrow(whole_mat)))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    tmp_mat_ind <- (tmp_mat == -9999 | tmp_mat == -999.9 | tmp_mat == -99.99)


    ## Wait: what if some of the NA's are non-zero - take care of that later
    ## TODO: NA part is still to be handled


    ## Mean: without the NA's, or -9999's - just the inner part
    ## With one indicator of being more than 20 -9999's or not
    ## 2 columns


    tmp_mat[tmp_mat== -9999 | tmp_mat== -999.9 | tmp_mat== -99.99] <- NA
    ## This would not work if na is not removed first

    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, 0, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(min_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    new_mat[[paste(min_var[j], "avg_ind", sep="_")]] <- (rowSums(tmp_mat_ind)>7)+0




    ## Min:
    tmp_mat <- whole_mat[, grepl(paste0("^", min_var[j],"_"), long_names)]

    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }

    ## Change:
    ## if(all(is.na(x))){ NA }  would be replaced by if(all(is.na(x))){ 0 }

    #new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] <-
    #  apply(tmp_mat, 1, function(x){ if( all(is.na(x)) ){ 0 } else { min(x, na.rm = na.rm) } })

    new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 0 } else { min(x, na.rm = na.rm) } })

    ## colwsie min is taken
    #new_mat[[paste(min_var[j], "min_ind", sep="_")]] <-
    #  is.na(new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)]) + 0
    ## ^BUG I guess
    new_mat[[paste(min_var[j], "min_ind", sep="_")]] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 1 } else { 0 } })


    ## Check:
    if(any(new_mat[, which(paste(min_var[j], "avg", sep="_") == short_names)] *
           new_mat[[paste(min_var[j], "avg_ind", sep="_")]] != 0) |
       any(new_mat[, which(paste(min_var[j], "min", sep="_") == short_names)] *
           new_mat[[paste(min_var[j], "min_ind", sep="_")]] != 0) ){

      warning("Problem in indexing!!!")
    }
  }




  # Reduced max type Variables:
  for(j in 1:length(max_var)){

    ## avg of inside elements:
    tmp_names <- paste(rep(max_var[j], each=9), inner_pts, sep="_")
    # grep(paste0("^", max_var[j],"_"), long_names, value=TRUE)
    tmp_mat <- array(dim = c(nrow(whole_mat), 9))
    tmp_vec <- array(dim = c(nrow(whole_mat)))
    for(j1 in 1:9){
      tmp_mat[,j1] <-
        whole_mat[, which(tmp_names[j1] == long_names)]
    }
    tmp_mat_ind <- (tmp_mat == -9999 | tmp_mat == -999.9 | tmp_mat == -99.99)


    ## Wait: what if some of the NA's are non-zero - take care of that later
    ## TODO: NA part is still to be handled


    ## Mean: without the NA's, or -9999's - just the inner part
    ## With one indicator of being more than 20 -9999's or not
    ## 2 columns


    tmp_mat[tmp_mat== -9999 | tmp_mat== -999.9 | tmp_mat== -99.99] <- NA
    ## This would not work if na is not removed first

    tmp_vec <- rowMeans(tmp_mat, na.rm = na.rm)
    tmp_vec[is.nan(tmp_vec)] <- NA
    tmp_vec <- ifelse(rowSums(is.na(tmp_mat))>7, 0, tmp_vec)  ## added >7 NA per 9
    new_mat[, which(paste(max_var[j], "avg", sep="_") == short_names)] <- tmp_vec
    new_mat[[paste(max_var[j], "avg_ind", sep="_")]] <- (rowSums(tmp_mat_ind)>7)+0




    ## max:
    tmp_mat <- whole_mat[, grepl(paste0("^", max_var[j],"_"), long_names)]

    if(remove_9999){
      tmp_mat[tmp_mat== -9999] <- NA
    }
    if(remove_999){
      tmp_mat[tmp_mat== -999.9] <- NA
    }
    if(remove_99){
      tmp_mat[tmp_mat== -99.99] <- NA
    }

    ## Change:
    ## if(all(is.na(x))){ NA }  would be replaced by if(all(is.na(x))){ 0 }

    #new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] <-
    #  apply(tmp_mat, 1, function(x){ if( all(is.na(x)) ){ 0 } else { max(x, na.rm = na.rm) } })

    new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 0 } else { max(x, na.rm = na.rm) } })

    ## colwsie max is taken
    #new_mat[[paste(max_var[j], "max_ind", sep="_")]] <-
    #  is.na(new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)]) + 0
    ## ^BUG I guess
    new_mat[[paste(max_var[j], "max_ind", sep="_")]] <-
      apply(tmp_mat, 1, function(x){ if( sum(is.na(x)) >= 20 ){ 1 } else { 0 } })


    ## Check:
    if(any(new_mat[, which(paste(max_var[j], "avg", sep="_") == short_names)] *
           new_mat[[paste(max_var[j], "avg_ind", sep="_")]] != 0) |
       any(new_mat[, which(paste(max_var[j], "max", sep="_") == short_names)] *
           new_mat[[paste(max_var[j], "max_ind", sep="_")]] != 0)){

      warning("Problem in indexing!!!")
    }
  }



  return(new_mat)
}

############################################################################################################


### Set up some Variables ### 

pos <- matrix(1:25, 5, 5)
n_tmp <- nrow(pos)
mat.pad <- rbind(NA, cbind(NA, pos, NA), NA)
ind <- 2:(n_tmp+1)
neigh = rbind(N  = as.vector(mat.pad[ind - 1, ind    ]),
                  E  = as.vector(mat.pad[ind    , ind + 1]),
                  S  = as.vector(mat.pad[ind + 1, ind    ]),
                  W  = as.vector(mat.pad[ind    , ind - 1]))
# https://stackoverflow.com/a/29105929/16426739


neighbour_avg_9999 <- function(whole_mat){
  paste(env_var_names, 1:25, sep="_")
  var_names <- colnames(whole_mat)
  for(i in 1:nrow(whole_mat)){

    ## Checking if there are any bad cases
    if(sum(whole_mat[i, ] == -9999 || whole_mat[i, ] == -999.9 || whole_mat[i, ] == -99.99)>0){
      tmp <- whole_mat[i,]

      for(j in 1:31){
        for(k in 1:25){
          name1 <- paste0(env_var_names[j], "_", k)
          name1_ind <- which(var_names==name1)
          ## getting an index which may contain -9999 etc

          if(tmp[name1_ind] == -9999 || tmp[name1_ind] == -999.9 || tmp[name1_ind] == -99.99){

            ## if there exists such cases, find the nbd indices
            nbd_ind <- c(neigh[,k])
            name_nbds <- paste0(env_var_names[j], nbd_ind, sep="_")

            for(l in 1:length(name_nbds)){
              final_nbd_ind <- which(var_names==name_nbds[l])
              tmp_nbd_val <- tmp[final_nbd_ind]
              tmp_nbd_val_NA <- ifelse(tmp_nbd_val == -9999 | tmp_nbd_val == -999.9 | tmp_nbd_val == -99.99, NA, tmp_nbd_val)
              tmp_mean <- mean(tmp_nbd_val_NA, na.rm=T)
              tmp[name1_ind] <- ifelse(is.na(tmp_mean), tmp[name1_ind], tmp_mean)
            }
          }
        }
      }
      whole_mat[i,] <- tmp
    }
  }
  whole_mat
}




##### * * specific way: #####





###### *Model Fitting #####
#source("Install_mxnet.R")
#library(mxnet)



##### *Post processing #####




###### *Different meaures #####
Brier_decomposition <- function(predicted, class, Thres=0.5){
  n <- length(predicted);
  m <- 2
  ind_1 <- which(predicted<Thres); ind_2 <- which(predicted>Thres)
  n_1 <- length(ind_1); n_2 <- length(ind_2)

  f1<- predicted[ind_1]; f2 <- predicted[ind_2];   o1<- class[ind_1]; o2 <- class[ind_2]
  f1_bar <- mean(f1); f2_bar <- mean(f2); o1_bar <- mean(o1); o2_bar <- mean(o2); o_bar <- mean(class)

  REL <- (n_1*((f1_bar-o1_bar)^2)+n_2*((f2_bar-o2_bar)^2))/n
  RES <- -(n_1*((o1_bar-o_bar)^2)+n_2*((o2_bar-o_bar)^2))/n
  UNC <- o_bar*(1-o_bar)
  WBV <- ((var(f1)*(n_1-1))+(var(f2)*(n_2-1)))/n
  WBC <- -2*((cov(o1, f1)*(n_1-1)) + (cov(o2, f2)*(n_2-1)))/n

  round(c(REL, RES, UNC, WBV, WBC), 4)
}



## See other types of measures also such as:
## prbe, rch, f, mi, phi, mxe, cal, sar


## Calculates Area under the ROC curve or Precision-Recall curve
## and plots the curve if 'if_plot' is set TRUE.
## Input:
#       Prediction Probs (of label 1),
#       actual class labels(label=1)
# Direct output is the measures


Under_the_curve <- function(prob, category, if_plot=T, type=c('auc', 'aucpr')){
  m   <- ncol(prob)
  val <- array(dim = m)
  if(!any(type==c('auc', 'aucpr'))){
    print("Currently supports auc, aucpr only!")
  }
  category <- (category == 'A')
  if(type == 'auc') {
    for(i in 1:m){
      pred_obj <- ROCR::prediction(prob[,i], category+0)
      val[i]   <- ROCR::performance(pred_obj, 'auc')@y.values[[1]]
      if(if_plot){
        perf_obj <- ROCR::performance(pred_obj, measure = "tpr", x.measure = "fpr")
        ROCR::plot(perf_obj, ylim = c(0,1), col=i, add = (i!=1)+0 )
      }
    }
  } else if(type == 'aucpr'){
    for(i in 1:m){
      pred_obj <- ROCR::prediction(prob[,i], category+0)
      val[i]   <- ROCR::performance(pred_obj, 'aucpr')@y.values[[1]]
      if(if_plot){
        perf_obj <- ROCR::performance(pred_obj, measure = "prec", x.measure = "rec")
        ROCR::plot(perf_obj, ylim = c(0,1), col=i, add = (i!=1)+0 )
      }
    }
  }
  return(val)
}


plot_PR = function(predicted, class, our_col = 1, if_add=T, if_colorise=F){
  pred_obj <- ROCR::prediction(predicted, class+0)
  perf_obj <- ROCR::performance(pred_obj, measure = "prec", x.measure = "rec")
  ROCR::plot(perf_obj, ylim = c(0,1), col=our_col, colorize=if_colorise, add=if_add)
}


PR_val_maj <- function(thres){
  predicted_majorities <- factor(ifelse(Predicted_probs[,1]>thres & Predicted_probs[,2]>thres,'A',
                                        ifelse(Predicted_probs[,1]>thres & Predicted_probs[,3]>thres,'A',
                                               ifelse(Predicted_probs[,2]>thres & Predicted_probs[,3]>thres,'A','B')
                                        )
  ), levels=c('A','B')
  )

  c(
    precision(table(Testset$class1, predicted_majorities)),
    recall(table(Testset$class1, predicted_majorities))
  )
}



## Write this here also

save_fn_names <- function(base_name = NULL,
                          Use_Text = 1, closest_distance_type = 0,
                          train_end = 2017, dim_reduction_type = 2,
                          cut_off = 50, train_start = 2007,
                          our_k = 30, Use_Fourier_time = 0,
                          if_PR = FALSE, if_SMOTE = FALSE,
                          if_test = 0, handle_9999 = TRUE, impute = TRUE,
                          popelev = TRUE, landuse = TRUE, radardat = TRUE){
  if(is.null(base_name)){
    save_names <- "Result"
  } else {
    save_names <- base_name
  }

  save_names <- paste(save_names, ifelse(Use_Text, "text", "notext"), sep="_")
  save_names <- paste(save_names, "closest", closest_distance_type, sep="_")
  save_names <- paste(save_names, "dimred", dim_reduction_type, sep="_")

  save_names <- paste0(save_names, "_")

  if(if_PR & if_SMOTE){
    stop("PR and SMOTE - both is on - change that!")
  } else if (if_PR){
    save_names <- paste(save_names, "PR", sep="_")
  } else if (!if_PR & if_SMOTE){
    save_names <- paste(save_names, "smote", sep="_")
  } else if (!if_PR & !if_SMOTE){
    save_names <- paste(save_names, "down", sep="_")
  }
  save_names <- paste(save_names, train_end, sep="_")
  # save_names <- paste(save_names, "cutoff_mag", cut_off, sep="_")
  save_names <- paste(save_names, cut_off, sep="_")
  if(if_test) {
    save_names <- paste(save_names, "test", sep="_")
  }
  if(Use_Fourier_time){
    save_names <- paste(save_names, "fourier", sep="_")
  }

  save_names <- paste0(save_names, "_")

  if(handle_9999){
    save_names <- paste(save_names, "9999", sep="_")
  } else {
    save_names <- paste(save_names, "no9999", sep="_")
  }
  if(impute){
    save_names <- paste(save_names, "imputed", sep="_")
  } else {
    save_names <- paste(save_names, "noimputed", sep="_")
  }
  if(popelev){
    save_names <- paste(save_names, "popelev", sep="_")
  } else {
    save_names <- paste(save_names, "nopopelev", sep="_")
  }
  if(landuse){
    save_names <- paste(save_names, "landuse", sep="_")
  } else {
    save_names <- paste(save_names, "nolanduse", sep="_")
  }
  if(radardat){
    save_names <- paste(save_names, "radar", sep="_")
  } else {
    save_names <- paste(save_names, "noradar", sep="_")
  }
  return(save_names)
}

