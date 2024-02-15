
# Initialize Variables
 Use_Text <- 0
 Use_Fourier_time <- 0
 closest_distance_type <- 0
 our_k <- 30
 dim_reduction_type <- 2     # dim_reduction_type <- 21
 if_PR <- FALSE
 if_SMOTE <- FALSE
 if_test <- TRUE
 handle_9999 <- TRUE
 impute <- TRUE
 popelev <- TRUE
 landuse <- TRUE  ## Include this also - all TRUE gives seperate naming system. Fix that.Z
 radardat <- FALSE
 


# ################# Import Functions from new_all_fn #################
tryCatch(source("new_all_fn.R"),
             error = function(e) message("Oops!  ", as.character(e)))


# Library Import and File Reading

library(mxnet)
library(caret);library(caretEnsemble)
library(pROC);library(plotROC)



# ################# Read the files ####################
(names_of_files <- dir("/work/wgallus/etirone2/hwt_2023",
                       pattern = "table_with_elevation_and_pop_*", full.names = TRUE, ignore.case = TRUE))  ##2019
all_dat <- c()
for(i in names_of_files[1]){
  i_th_file <- read.csv(i)
  all_dat <- rbind(all_dat, i_th_file)
}
(n_new <- NROW(all_dat))


################# Text Processing ####################

joined_text_new <- as.character(all_dat$Remarks)
joined_text_new <- lapply(strsplit(joined_text_new ,split='(', fixed=T), function(x){x[1]})
joined_text_new <- unlist(joined_text_new)

library("tm"); library("SnowballC"); library("wordcloud"); library("RColorBrewer");library("Matrix")

# Matrix Initialization and Column Binding:
  B <- matrix(NA, n_new, our_k)

colnames(B) <- paste0("text_", 1:our_k)
all_dat <-(cbind(all_dat,B))
names(all_dat)

########### Predict ##########

# Column Renaming and Data Processing:
all_dat$magnitude_type <- ifelse(all_dat$Speed.MPH.=='UNK', 'EG', 'MG')
dat_names <- names(all_dat)
dat_names[dat_names == "Time"] <- "beginUTC"
dat_names[dat_names == "LAT"] <- "location_1_lat"
dat_names[dat_names == "LON"] <- "location_1_lon"
dat_names[dat_names == "Speed.MPH."] <- "magnitude"
names(all_dat) <- dat_names



# Handling factor-like conversion in Python
if(is.factor(all_dat$magnitude)){     #UNK values
  all_dat$magnitude <- as.numeric(levels(all_dat$magnitude))[all_dat$magnitude]
}

final_mat_2_new <- all_dat

# Event ID Extraction:
event_id <- final_mat_2_new$event_id





######## *Further preprocessing* ##########
if(!is.null(final_mat_2_new$land_use)){
        final_mat_2_new$land_use <- ifelse(is.na(final_mat_2_new$land_use), 12, final_mat_2_new$land_use)
        final_mat_2_new$land_use <- factor(final_mat_2_new$land_use)
}

## Add the distance
## Warning - take care that it is included when dim is reduced  - Subrata  -CHECK
measured_cases <- final_mat_2_new[final_mat_2_new$magnitude_type == "MG",]
estimated_cases <- final_mat_2_new[final_mat_2_new$magnitude_type == "EG",]

if(closest_distance_type == 1){
  final_mat_2_new$magnitude_closest <- NA
  final_mat_2_new$s_t_dist <- 0

  mes_closest <- distance_1_measured(measured_cases$beginUTC, measured_cases$location_1_lat,
                                      measured_cases$location_1_lon, measured_cases$magnitude, "%Y-%m-%d %H:%M")

  est_closest <- distance_1_estimated(measured_cases$beginUTC, measured_cases$location_1_lat,
                                                measured_cases$location_1_lon, measured_cases$magnitude,
                                                estimated_cases$beginUTC, estimated_cases$location_1_lat,
                                                estimated_cases$location_1_lon, "%Y-%m-%d %H:%M")

  final_mat_2_new$magnitude_closest[final_mat_2_new$magnitude_type == "MG"] <-  mes_closest[,1]
  final_mat_2_new$s_t_dist[final_mat_2_new$magnitude_type == "MG"] <-  mes_closest[,2]

  final_mat_2_new$magnitude_closest[final_mat_2_new$magnitude_type == "EG"] <-  est_closest[,1]
  final_mat_2_new$s_t_dist[final_mat_2_new$magnitude_type == "EG"] <-  est_closest[,2]

} else if (closest_distance_type == 2){

  final_mat_2_new$s_t_ind <- 0
  mes_closest <- distance_2_measured(measured_cases$beginUTC, measured_cases$location_1_lat,
                                      measured_cases$location_1_lon, measured_cases$magnitude, "%Y-%m-%d %H:%M")

  est_closest <- distance_2_estimated(measured_cases$beginUTC, measured_cases$location_1_lat,
                                                measured_cases$location_1_lon, measured_cases$magnitude,
                                                estimated_cases$beginUTC, estimated_cases$location_1_lat,
                                                estimated_cases$location_1_lon, "%Y-%m-%d %H:%M")

  final_mat_2_new$s_t_ind[final_mat_2_new$magnitude_type == "MG"] <- mes_closest
  final_mat_2_new$s_t_ind[final_mat_2_new$magnitude_type == "EG"] <- est_closest
}

# Time
final_mat_2_new <- cbind(transform_time(final_mat_2_new$beginUTC, Use_Fourier_time, date_format = "%Y-%m-%d %H:%M"), final_mat_2_new)

#### NA's:
## Remove rows with too many NA's
too_many_nas <- which(rowMeans(is.na(final_mat_2_new))>0.50)   ## same as 0.2
if(length(too_many_nas)>0){ final_mat_2_new <- final_mat_2_new[-too_many_nas, ] }
# Creates missingness - be aware

## Handle -9999's and impute some of the variables:
if(impute){
  final_mat_2_new <- impute_UVEIL_RH7080(final_mat_2_new)
}


##  final_mat_2_new <- na.omit(final_mat_2_new)  ### Should this be done?????? - at least not now I guess
## Remove Na's. Otherwise it is possibly hard to remove linearly dependent columns
if(handle_9999){

  if(dim_reduction_type == 0){
    #dim(final_mat_2_new)
    final_mat_2_new <- add_indicator(final_mat_2_new)
    ## WARNING: Don't repeat this, once you run final_mat_2_new, all -9999's are gone
    print(dim(final_mat_2_new))

  } else if(dim_reduction_type == 1 || dim_reduction_type == 11){
    final_mat_2_new <- dim_reduction_1_ind(final_mat_2_new)
    print(dim(final_mat_2_new))

  } else if(dim_reduction_type == 2 || dim_reduction_type == 21){
    final_mat_2_new <- dim_reduction_2_ind(final_mat_2_new)
    print(dim(final_mat_2_new))
  }
  # final_mat_2_new <- compress_ind(final_mat_2_new)   ## Switch off this for now. It won't hurt for the test data.'
  all_env_ind_new <- grep("_ind", names(final_mat_2_new), value = T)
  for(i in all_env_ind_new){
    final_mat_2_new[[i]] <- as.factor(final_mat_2_new[[i]])
  }

  print(dim(final_mat_2_new))

} else {
  if(dim_reduction_type == 1){
    final_mat_2_new <- dim_reduction_1(final_mat_2_new, na.rm = TRUE,
                                   remove_9999 = T, remove_999 = T)
    print(dim(final_mat_2_new))
  } else if(dim_reduction_type == 2){
    final_mat_2_new <- dim_reduction_2(final_mat_2_new, na.rm = TRUE,
                                   remove_9999 = T, remove_999 = T)
    print(dim(final_mat_2_new))
  } else if(dim_reduction_type == 11){
    final_mat_2_new <- dim_reduction_11(final_mat_2_new, na.rm = TRUE,
                                    remove_9999 = T, remove_999 = T)
    print(dim(final_mat_2_new))
  } else if(dim_reduction_type == 21){
    final_mat_2_new <- dim_reduction_21(final_mat_2_new, na.rm = TRUE,
                                    remove_9999 = T, remove_999 = T)
    print(dim(final_mat_2_new))
  }

}

##########################################################################################################
### WHY DOES THAT MODEL HAVE A LAND_USE DATA --------------___CHECK IMMEDIATELY.
##########################################################################################################

# Adjusting avg_pop Column:
final_mat_2_new$avg_pop <-  ifelse(is.na(final_mat_2_new$avg_pop), 1.01, final_mat_2_new$avg_pop) ## If it is on the water


### Index of containing text and not containing text:
no_text_index <- which(is.na(final_mat_2_new$text_1))
text_index <- which(!is.na(final_mat_2_new$text_1))

# Index of Rows Containing Text and Not Containing Text:
# no_text_index <- 1:n_new
no_text_index <- 1:nrow(final_mat_2_new)
text_index <- numeric(0)

# Setting Variables:
cut_off <- 50
train_start <- 2007
train_end   <- 2017
test_start <- train_end + 1
test_end <- 2018


# Generating final output file names
# sourcefile <- "new_fit"
sourcefile <- "new_fit_subsevere"
outFile <- save_fn_names(base_name = sourcefile, Use_Text = Use_Text,
                         closest_distance_type = closest_distance_type,
                         train_end = train_end, dim_reduction_type = dim_reduction_type,
                         cut_off = cut_off, train_start = train_start,
                         our_k = our_k, Use_Fourier_time = Use_Fourier_time,
                         if_PR = if_PR, if_SMOTE = if_SMOTE,
                         if_test = if_test,
                         handle_9999 = handle_9999, impute = impute,
                         popelev = popelev, landuse = landuse, radardat = radardat)
print(outFile)
# outFile_path <- file.path("/work/wgallus/subrata_tmp/codes_2/result", outFile)
outFile_path <- file.path("/work/wgallus/subrata_tmp/codes_4/test", outFile)

models <- readRDS(paste0(outFile_path, "_main_model_1.rds"))
stack.glm <- readRDS(paste0(outFile_path, "_model_stack_glm.rds"))
stack.rf <- readRDS(paste0(outFile_path, "_model_stack_rf.rds"))

# Comparing Column Names:

setdiff( names(models$gbm$trainingData), names(final_mat_2_new))

############ ****NO TEXT***** ################

if(length(no_text_index)>0){
  our_k <- 30
  na_row_index <- which(rowSums(is.na(final_mat_2_new[no_text_index,]))>our_k)
  if(length(na_row_index)>0){Testset <- na.omit(final_mat_2_new)}
  # Testset <- na.omit(final_mat_2_new[no_text_index,-(784:813)])

  ## Should have more adjustments!!
  nm <- colnames(final_mat_2_new)
  start_without_text <- which(!(nm %in% grep("^text_", nm, value=TRUE)))
  text_ind <- which((nm %in% grep("^text_", nm, value=TRUE)))
  # Testset <- final_mat_2_new[, start_without_text]
  Testset <- final_mat_2_new
  tmp <- Testset[,text_ind]
  for(i in 1:nrow(tmp)){
    for(j in 1:ncol(tmp)){
      if(is.na(tmp[i,j])){
        tmp[i,j] = 0.1
      }
    }
  }
  Testset[,text_ind] <- tmp

  ## RHLC NA
  for(i in 1:nrow(Testset)){
    for(j in 1:ncol(Testset)){
      if(is.na(Testset[i,j])){
        Testset[i,j] = -999
      }
    }
  }


  if(is.factor(Testset$magnitude)){     #UNK values
    Testset$magnitude <- as.numeric(levels(Testset$magnitude))[Testset$magnitude]
  }


  ########### Predictions #############
  ## Predicting the probabilities of being in class A
  Predicted_probs <- predict(models, Testset)
  Predicted_stack_glm_prob <- predict(stack.glm, Testset, type='prob')
  Predicted_stack_rf_prob <- predict(stack.rf, Testset,type='prob')



  ### *manually done ensemble #########
  # Taking average of predictions
  pred_avg <- rowMeans(Predicted_probs)

  Testset$pred_majority <- as.factor(ifelse(predict(models$gbm, Testset)=='A' & predict(models$svmRadial, Testset)=='A','A',
                                            ifelse(predict(models$gbm, Testset)=='A' & predict(models$mxnetAdam, Testset)=='A','A',
                                                   ifelse(predict(models$svmRadial, Testset)=='A' & predict(models$mxnetAdam, Testset)=='A','A','B')
                                            )
  )
  )
  # (pred_final_majority <- table(Testset$pred_majority, Testset$class1))

  Predicted_probs <- data.frame(Predicted_probs,
                                Predicted_stack_glm_prob, Predicted_stack_rf_prob, pred_avg)
  names(Predicted_probs)[length(names(Predicted_probs))+c(-2,-1, 0)] <- c("stack_glm","stack_rf", "avg_ens")



  Predicted_probs <-
  cbind(
    cbind(final_mat_2_new$event_id,
          final_mat_2_new$location_1_lat,final_mat_2_new$location_1_lon,
          final_mat_2_new$Year,final_mat_2_new$day, final_mat_2_new$month,
          final_mat_2_new$hour, final_mat_2_new$minute)[no_text_index,]
    ,Predicted_probs
  )
}


Predicted_probs_whole <- Predicted_probs
colnames(Predicted_probs_whole)[1:8] <- c('event_id', 'lon', 'lat',
                                          'year', 'day','month','hr','min')
indicator_text <- rep(0, nrow(Predicted_probs_whole))
indicator_text[text_index] <- 1

if(is.factor(final_mat_2_new$magnitude)){
  final_mat_2_new$magnitude <- as.numeric(levels(final_mat_2_new$magnitude))[final_mat_2_new$magnitude]
}

Predicted_probs_whole <- cbind(Predicted_probs_whole, indicator_text, final_mat_2_new$magnitude)
colnames(Predicted_probs_whole)[ncol(Predicted_probs_whole)] <- "magnitude"

Predicted_probs_whole <- as.data.frame(Predicted_probs_whole)
Predicted_probs_whole <- Predicted_probs_whole[order(Predicted_probs_whole$event_id),]
Predicted_probs_whole

## Lizzie, change of paths
write.csv(Predicted_probs_whole, "/work/wgallus/etirone2/hwt_2023/final_probs_subsevere_2023.csv")