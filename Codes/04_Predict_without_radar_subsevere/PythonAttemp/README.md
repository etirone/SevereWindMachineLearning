# 04_Predict_without_radar_subsevere

These are the files I generated during my failed attempt to convert the R script to python.

While I suspect it is possible, there is a lot of the model that would be difficult to transfer over without better knowledge of the model and how it was generated.

This file contains my notes as I tried to convert the R code to python code.  


Dec 6, 2023

Working on loading rds models today.  I want to convert the rds models to something that can be read in by python 

Here are the models I will be working with 

* Nova

```
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_main_model_1.rds
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_model_stack_glm.rds
#/work/wgallus/subrata_tmp/codes_4/test/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_model_stack_rf.rds

```

**They are pretty large files in the 50-100Mb range so I will have to provide them somewhere else. **

## Download these rds files

## install a python library to read in rds files

```
pip install pyreadr
```

## Read in the rds files

```
R
model_1 <- readRDS('/Users/andrewseverin/GIFNew/isugif/2023_Gallus_SevereWind/Notebook_Severin/04_Predict_without_radar_subsevere/04_Predict_without_radar_subsevere/temp/new_fit_subsevere_notext_closest_0_dimred_2__down_2017_50_test__9999_imputed_popelev_landuse_noradar_main_model_1.rds')



```

## Get information about the model 

Basic information
```
> class(model)
[1] "caretList"


summary((model))
          Length Class Mode
gbm       24     train list
svmRadial 24     train list
mxnetAdam 24     train list

> attributes(model)
$names
[1] "gbm"       "svmRadial" "mxnetAdam"

$class
[1] "caretList"

> attributes(model$gbm)
$names
 [1] "method"       "modelInfo"    "modelType"    "results"      "pred"
 [6] "bestTune"     "call"         "dots"         "metric"       "control"
[11] "finalModel"   "preProcess"   "trainingData" "resample"     "resampledCM"
[16] "perfNames"    "maximize"     "yLimits"      "times"        "levels"
[21] "terms"        "coefnames"    "contrasts"    "xlevels"

$class
[1] "train"         "train.formula"

```


More details 

```
attributes(model$gbm$finalModel)
$names
 [1] "initF"             "fit"               "train.error"
 [4] "valid.error"       "oobag.improve"     "trees"
 [7] "c.splits"          "bag.fraction"      "distribution"
[10] "interaction.depth" "n.minobsinnode"    "num.classes"
[13] "n.trees"           "nTrain"            "train.fraction"
[16] "response.name"     "shrinkage"         "var.levels"
[19] "var.monotone"      "var.names"         "var.type"
[22] "verbose"           "data"              "xNames"
[25] "problemType"       "tuneValue"         "obsLevels"
[28] "param"

$class
[1] "gbm"

attributes(model$gbm$bestTune
+ )
$names
[1] "n.trees"           "interaction.depth" "shrinkage"
[4] "n.minobsinnode"

$row.names
[1] 15

$class
[1] "data.frame"

attributes(model$gbm$preProcess
+ )
$names
 [1] "dim"               "bc"                "yj"
 [4] "et"                "invHyperbolicSine" "mean"
 [7] "std"               "ranges"            "rotation"
[10] "method"            "thresh"            "pcaComp"
[13] "numComp"           "ica"               "wildcards"
[16] "k"                 "knnSummary"        "bagImp"
[19] "median"            "data"              "rangeBounds"
[22] "call"

$class
[1] "preProcess"
```

## Convert the model to a dataframe


Let's work on converting these to dataframes and exporting them.

Exporting an entire `caretList` object, which contains multiple models and their metadata, directly to a format easily readable in Python is quite complex due to the fundamental differences in data structures between R and Python. However, you can attempt to export the essential components of each model within the `caretList` to CSV files, which can then be read into Python. This approach requires breaking down the `caretList` into simpler, exportable parts.

Let's go through the key components of each model within your `caretList` and export them:

0. **Make a folder to hold the csv files for the model**

```
system('mkdir model_1')
setwd('/Users/andrewseverin/GIFNew/isugif/2023_Gallus_SevereWind/Notebook_Severin/temp/model_1/')
```
1. **Export Model Hyperparameters (bestTune)**:
   - For each model (e.g., `gbm`, `svmRadial`, `mxnetAdam`), export the `bestTune` data frame, which contains the best-found hyperparameters.

     ```R
     write.csv(model$gbm$bestTune, "gbm_bestTune.csv", row.names = FALSE)
     write.csv(model$svmRadial$bestTune, "svmRadial_bestTune.csv", row.names = FALSE)
     write.csv(model$mxnetAdam$bestTune, "mxnetAdam_bestTune.csv", row.names = FALSE)
     ```

2. **Export Training Data Summary (trainingData)**:
   - While you may not be able to export the entire training dataset, you can export summaries or metadata about it, such as column names or data types.

     ```R
     write.csv(data.frame(names = names(model$gbm$trainingData), 
                          class = sapply(model$gbm$trainingData, class)),
               "gbm_trainingDataSummary.csv", row.names = FALSE)
     ```

3. **Export Preprocessing Steps (preProcess)**:
   - This is a bit tricky, as the `preProcess` object contains complex elements. You might need to manually document the steps or try to summarize them into a simpler format for export.

    General stats
    ```R
    if ("center" %in% model$gbm$preProcess$method) {
        write.csv(model$gbm$preProcess$mean, "gbm_scalingMeans.csv", row.names = FALSE)
    }
    if ("scale" %in% model$gbm$preProcess$method) {
        write.csv(model$gbm$preProcess$std, "gbm_scalingStds.csv", row.names = FALSE)
    }

    ```
    Range information 

    ```
    if ("range" %in% model$gbm$preProcess$method) {
        write.csv(model$gbm$preProcess$ranges, "gbm_dataRanges.csv", row.names = FALSE)
    }
    ```

    PCA information 

    ```
    if ("pca" %in% model$gbm$preProcess$method) {
        write.csv(model$gbm$preProcess$rotation, "gbm_pcaRotation.csv", row.names = FALSE)
    }
    ```

    General information 

    ```
    write.csv(as.data.frame(model$gbm$preProcess$method$center), "gbm_preProcessMethods_center.csv", row.names = FALSE)
    write.csv(as.data.frame(model$gbm$preProcess$method$scale), "gbm_preProcessMethods_scale.csv", row.names = FALSE)
    write.csv(as.data.frame(model$gbm$preProcess$method$ignore), "gbm_preProcessMethods_ignore.csv", row.names = FALSE)
    ```

4. **Export Model Performance Metrics (results, resample, etc.)**:
   - For each model, export any available performance metrics. This could include resampling results, validation errors, etc.

     ```R
     write.csv(model$gbm$results, "gbm_results.csv", row.names = FALSE)
     write.csv(model$gbm$resample, "gbm_resample.csv", row.names = FALSE)
     ```

5. **Export Final Model Structure**:
   - The structure of the final model (`finalModel`) is often the most complex part to export. You can try to summarize its key attributes or configurations into a CSV, but recreating this exactly in Python will be challenging.

     ```R
     gbm_finalModel_summary <- summary(model$gbm$finalModel)
     write.csv(data.frame(summary = gbm_finalModel_summary), "gbm_finalModelSummary.csv", row.names = FALSE)
     ```

Once these components are exported, you can read them in Python and use them as references to recreate equivalent models and preprocessing steps. However, remember that some manual interpretation and adjustments will likely be necessary due to the differences between R and Python modeling libraries.


## General function for exporting all attributes in the models 




```
exportModelAttributes <- function(modelObject, outputDir, filePrefix) {
    # Ensure the output directory ends with a slash
    if (substr(outputDir, nchar(outputDir), nchar(outputDir)) != "/") {
        outputDir <- paste0(outputDir, "/")
    }
  
    # Loop through each model in the caretList
    for (modelName in names(modelObject)) {
        # Access the model
        currentModel <- modelObject[[modelName]]

        # List all attributes of the current model
        attributesList <- attributes(currentModel)$names

        # Loop through each attribute
        for(attrName in attributesList) {
            # Use tryCatch to handle errors
            tryCatch({
                attrValue <- currentModel[[attrName]]
                
                # Check if the attribute can be converted to a data frame
                if(is.data.frame(attrValue) || is.matrix(attrValue) || is.vector(attrValue)) {
                    # Convert matrix or vector to data frame
                    if (is.matrix(attrValue) || is.vector(attrValue)) {
                        attrValue <- as.data.frame(attrValue)
                    }

                    # Construct file path
                    filePath <- paste0(outputDir, filePrefix, "_", modelName, "_", attrName, ".csv")

                    # Write to CSV
                    write.csv(attrValue, file = filePath, row.names = FALSE)
                }
            }, error = function(e) {
                # Print message for attributes that need special handling
                message(paste("Attribute", attrName, "of model", modelName, "could not be exported and needs special handling."))
            })
        }
    }
}

# Example usage of the function:
# exportModelAttributes(model_1, "path/to/output/directory", "model_1")

```

## Export the model attributes 
```
install.packages('kernlab')

```

```
exportModelAttributes(model,"Full", "model_1")
exportModelAttributes(model$gbm$modelInfo,"Full", "model_1_gbm_modelInfo")
exportModelAttributes(model$gbm$control,"Full", "model_1_gbm_control")
exportModelAttributes(model$gbm$times,"Full", "model_1_gbm_times")
exportModelAttributes(model$svmRadial$modelInfo,"Full", "model_1_svmRadial_modelInfo")
exportModelAttributes(model$svmRadial$control,"Full", "model_1_svmRadial_control")
exportModelAttributes(model$svmRadial$finalModel,"Full", "model_1_svmRadial_finalModel")
exportModelAttributes(model$svmRadial$times,"Full", "model_1_svmRadial_times")
exportModelAttributes(model$mxnetAdam$modelInfo,"Full", "model_1_mxnetAdam_modelInfo")
exportModelAttributes(model$mxnetAdam$control,"Full", "model_1_mxnetAdam_control")
exportModelAttributes(model$mxnetAdam$times,"Full", "model_1_mxnetAdam_times")

```

This generated a ton of files!! But it should be relatively easy now to grab the information we need to recreate this object in Python, or at least I hope. 

```
> dir('Full')
  [1] "model_1_gbm_bestTune.csv"
  [2] "model_1_gbm_coefnames.csv"
  [3] "model_1_gbm_contrasts.csv"
  [4] "model_1_gbm_control_adaptive_alpha.csv"
  [5] "model_1_gbm_control_adaptive_complete.csv"
  [6] "model_1_gbm_control_adaptive_method.csv"
  [7] "model_1_gbm_control_adaptive_min.csv"
  [8] "model_1_gbm_control_index_Fold1.Rep1.csv"
  [9] "model_1_gbm_control_index_Fold1.Rep2.csv"
 [10] "model_1_gbm_control_index_Fold1.Rep3.csv"
 [11] "model_1_gbm_control_index_Fold1.Rep4.csv"
 [12] "model_1_gbm_control_index_Fold1.Rep5.csv"
 [13] "model_1_gbm_control_index_Fold2.Rep1.csv"
 [14] "model_1_gbm_control_index_Fold2.Rep2.csv"
 [15] "model_1_gbm_control_index_Fold2.Rep3.csv"
 [16] "model_1_gbm_control_index_Fold2.Rep4.csv"
 [17] "model_1_gbm_control_index_Fold2.Rep5.csv"
 [18] "model_1_gbm_control_index_Fold3.Rep1.csv"
 [19] "model_1_gbm_control_index_Fold3.Rep2.csv"
 [20] "model_1_gbm_control_index_Fold3.Rep3.csv"
 [21] "model_1_gbm_control_index_Fold3.Rep4.csv"
 [22] "model_1_gbm_control_index_Fold3.Rep5.csv"
 [23] "model_1_gbm_control_index_Fold4.Rep1.csv"
 [24] "model_1_gbm_control_index_Fold4.Rep2.csv"
 [25] "model_1_gbm_control_index_Fold4.Rep3.csv"
 [26] "model_1_gbm_control_index_Fold4.Rep4.csv"
 [27] "model_1_gbm_control_index_Fold4.Rep5.csv"
 [28] "model_1_gbm_control_index_Fold5.Rep1.csv"
 [29] "model_1_gbm_control_index_Fold5.Rep2.csv"
 [30] "model_1_gbm_control_index_Fold5.Rep3.csv"
 [31] "model_1_gbm_control_index_Fold5.Rep4.csv"
 [32] "model_1_gbm_control_index_Fold5.Rep5.csv"
 [33] "model_1_gbm_control_index_Fold6.Rep1.csv"
 [34] "model_1_gbm_control_index_Fold6.Rep2.csv"
 [35] "model_1_gbm_control_index_Fold6.Rep3.csv"
 [36] "model_1_gbm_control_index_Fold6.Rep4.csv"
 [37] "model_1_gbm_control_index_Fold6.Rep5.csv"
 [38] "model_1_gbm_control_indexOut_Resample01.csv"
 [39] "model_1_gbm_control_indexOut_Resample02.csv"
 [40] "model_1_gbm_control_indexOut_Resample03.csv"
 [41] "model_1_gbm_control_indexOut_Resample04.csv"
 [42] "model_1_gbm_control_indexOut_Resample05.csv"
 [43] "model_1_gbm_control_indexOut_Resample06.csv"
 [44] "model_1_gbm_control_indexOut_Resample07.csv"
 [45] "model_1_gbm_control_indexOut_Resample08.csv"
 [46] "model_1_gbm_control_indexOut_Resample09.csv"
 [47] "model_1_gbm_control_indexOut_Resample10.csv"
 [48] "model_1_gbm_control_indexOut_Resample11.csv"
 [49] "model_1_gbm_control_indexOut_Resample12.csv"
 [50] "model_1_gbm_control_indexOut_Resample13.csv"
 [51] "model_1_gbm_control_indexOut_Resample14.csv"
 [52] "model_1_gbm_control_indexOut_Resample15.csv"
 [53] "model_1_gbm_control_indexOut_Resample16.csv"
 [54] "model_1_gbm_control_indexOut_Resample17.csv"
 [55] "model_1_gbm_control_indexOut_Resample18.csv"
 [56] "model_1_gbm_control_indexOut_Resample19.csv"
 [57] "model_1_gbm_control_indexOut_Resample20.csv"
 [58] "model_1_gbm_control_indexOut_Resample21.csv"
 [59] "model_1_gbm_control_indexOut_Resample22.csv"
 [60] "model_1_gbm_control_indexOut_Resample23.csv"
 [61] "model_1_gbm_control_indexOut_Resample24.csv"
 [62] "model_1_gbm_control_indexOut_Resample25.csv"
 [63] "model_1_gbm_control_indexOut_Resample26.csv"
 [64] "model_1_gbm_control_indexOut_Resample27.csv"
 [65] "model_1_gbm_control_indexOut_Resample28.csv"
 [66] "model_1_gbm_control_indexOut_Resample29.csv"
 [67] "model_1_gbm_control_indexOut_Resample30.csv"
 [68] "model_1_gbm_control_preProcOptions_cutoff.csv"
 [69] "model_1_gbm_control_preProcOptions_freqCut.csv"
 [70] "model_1_gbm_control_preProcOptions_ICAcomp.csv"
 [71] "model_1_gbm_control_preProcOptions_k.csv"
 [72] "model_1_gbm_control_preProcOptions_thresh.csv"
 [73] "model_1_gbm_control_preProcOptions_uniqueCut.csv"
 [74] "model_1_gbm_control_sampling_first.csv"
 [75] "model_1_gbm_control_sampling_name.csv"
 [76] "model_1_gbm_dots.csv"
 [77] "model_1_gbm_maximize.csv"
 [78] "model_1_gbm_method.csv"
 [79] "model_1_gbm_metric.csv"
 [80] "model_1_gbm_modelInfo_parameters_class.csv"
 [81] "model_1_gbm_modelInfo_parameters_label.csv"
 [82] "model_1_gbm_modelInfo_parameters_parameter.csv"
 [83] "model_1_gbm_modelType.csv"
 [84] "model_1_gbm_perfNames.csv"
 [85] "model_1_gbm_pred.csv"
 [86] "model_1_gbm_resample.csv"
 [87] "model_1_gbm_resampledCM.csv"
 [88] "model_1_gbm_results.csv"
 [89] "model_1_gbm_times_everything_elapsed.csv"
 [90] "model_1_gbm_times_everything_sys.child.csv"
 [91] "model_1_gbm_times_everything_sys.self.csv"
 [92] "model_1_gbm_times_everything_user.child.csv"
 [93] "model_1_gbm_times_everything_user.self.csv"
 [94] "model_1_gbm_times_final_elapsed.csv"
 [95] "model_1_gbm_times_final_sys.child.csv"
 [96] "model_1_gbm_times_final_sys.self.csv"
 [97] "model_1_gbm_times_final_user.child.csv"
 [98] "model_1_gbm_times_final_user.self.csv"
 [99] "model_1_gbm_trainingData.csv"
[100] "model_1_gbm_xlevels.csv"
[101] "model_1_mxnetAdam_bestTune.csv"
[102] "model_1_mxnetAdam_coefnames.csv"
[103] "model_1_mxnetAdam_contrasts.csv"
[104] "model_1_mxnetAdam_control_adaptive_alpha.csv"
[105] "model_1_mxnetAdam_control_adaptive_complete.csv"
[106] "model_1_mxnetAdam_control_adaptive_method.csv"
[107] "model_1_mxnetAdam_control_adaptive_min.csv"
[108] "model_1_mxnetAdam_control_index_Fold1.Rep1.csv"
[109] "model_1_mxnetAdam_control_index_Fold1.Rep2.csv"
[110] "model_1_mxnetAdam_control_index_Fold1.Rep3.csv"
[111] "model_1_mxnetAdam_control_index_Fold1.Rep4.csv"
[112] "model_1_mxnetAdam_control_index_Fold1.Rep5.csv"
[113] "model_1_mxnetAdam_control_index_Fold2.Rep1.csv"
[114] "model_1_mxnetAdam_control_index_Fold2.Rep2.csv"
[115] "model_1_mxnetAdam_control_index_Fold2.Rep3.csv"
[116] "model_1_mxnetAdam_control_index_Fold2.Rep4.csv"
[117] "model_1_mxnetAdam_control_index_Fold2.Rep5.csv"
[118] "model_1_mxnetAdam_control_index_Fold3.Rep1.csv"
[119] "model_1_mxnetAdam_control_index_Fold3.Rep2.csv"
[120] "model_1_mxnetAdam_control_index_Fold3.Rep3.csv"
[121] "model_1_mxnetAdam_control_index_Fold3.Rep4.csv"
[122] "model_1_mxnetAdam_control_index_Fold3.Rep5.csv"
[123] "model_1_mxnetAdam_control_index_Fold4.Rep1.csv"
[124] "model_1_mxnetAdam_control_index_Fold4.Rep2.csv"
[125] "model_1_mxnetAdam_control_index_Fold4.Rep3.csv"
[126] "model_1_mxnetAdam_control_index_Fold4.Rep4.csv"
[127] "model_1_mxnetAdam_control_index_Fold4.Rep5.csv"
[128] "model_1_mxnetAdam_control_index_Fold5.Rep1.csv"
[129] "model_1_mxnetAdam_control_index_Fold5.Rep2.csv"
[130] "model_1_mxnetAdam_control_index_Fold5.Rep3.csv"
[131] "model_1_mxnetAdam_control_index_Fold5.Rep4.csv"
[132] "model_1_mxnetAdam_control_index_Fold5.Rep5.csv"
[133] "model_1_mxnetAdam_control_index_Fold6.Rep1.csv"
[134] "model_1_mxnetAdam_control_index_Fold6.Rep2.csv"
[135] "model_1_mxnetAdam_control_index_Fold6.Rep3.csv"
[136] "model_1_mxnetAdam_control_index_Fold6.Rep4.csv"
[137] "model_1_mxnetAdam_control_index_Fold6.Rep5.csv"
[138] "model_1_mxnetAdam_control_indexOut_Resample01.csv"
[139] "model_1_mxnetAdam_control_indexOut_Resample02.csv"
[140] "model_1_mxnetAdam_control_indexOut_Resample03.csv"
[141] "model_1_mxnetAdam_control_indexOut_Resample04.csv"
[142] "model_1_mxnetAdam_control_indexOut_Resample05.csv"
[143] "model_1_mxnetAdam_control_indexOut_Resample06.csv"
[144] "model_1_mxnetAdam_control_indexOut_Resample07.csv"
[145] "model_1_mxnetAdam_control_indexOut_Resample08.csv"
[146] "model_1_mxnetAdam_control_indexOut_Resample09.csv"
[147] "model_1_mxnetAdam_control_indexOut_Resample10.csv"
[148] "model_1_mxnetAdam_control_indexOut_Resample11.csv"
[149] "model_1_mxnetAdam_control_indexOut_Resample12.csv"
[150] "model_1_mxnetAdam_control_indexOut_Resample13.csv"
[151] "model_1_mxnetAdam_control_indexOut_Resample14.csv"
[152] "model_1_mxnetAdam_control_indexOut_Resample15.csv"
[153] "model_1_mxnetAdam_control_indexOut_Resample16.csv"
[154] "model_1_mxnetAdam_control_indexOut_Resample17.csv"
[155] "model_1_mxnetAdam_control_indexOut_Resample18.csv"
[156] "model_1_mxnetAdam_control_indexOut_Resample19.csv"
[157] "model_1_mxnetAdam_control_indexOut_Resample20.csv"
[158] "model_1_mxnetAdam_control_indexOut_Resample21.csv"
[159] "model_1_mxnetAdam_control_indexOut_Resample22.csv"
[160] "model_1_mxnetAdam_control_indexOut_Resample23.csv"
[161] "model_1_mxnetAdam_control_indexOut_Resample24.csv"
[162] "model_1_mxnetAdam_control_indexOut_Resample25.csv"
[163] "model_1_mxnetAdam_control_indexOut_Resample26.csv"
[164] "model_1_mxnetAdam_control_indexOut_Resample27.csv"
[165] "model_1_mxnetAdam_control_indexOut_Resample28.csv"
[166] "model_1_mxnetAdam_control_indexOut_Resample29.csv"
[167] "model_1_mxnetAdam_control_indexOut_Resample30.csv"
[168] "model_1_mxnetAdam_control_preProcOptions_cutoff.csv"
[169] "model_1_mxnetAdam_control_preProcOptions_freqCut.csv"
[170] "model_1_mxnetAdam_control_preProcOptions_ICAcomp.csv"
[171] "model_1_mxnetAdam_control_preProcOptions_k.csv"
[172] "model_1_mxnetAdam_control_preProcOptions_thresh.csv"
[173] "model_1_mxnetAdam_control_preProcOptions_uniqueCut.csv"
[174] "model_1_mxnetAdam_control_sampling_first.csv"
[175] "model_1_mxnetAdam_control_sampling_name.csv"
[176] "model_1_mxnetAdam_dots.csv"
[177] "model_1_mxnetAdam_maximize.csv"
[178] "model_1_mxnetAdam_method.csv"
[179] "model_1_mxnetAdam_metric.csv"
[180] "model_1_mxnetAdam_modelInfo_parameters_class.csv"
[181] "model_1_mxnetAdam_modelInfo_parameters_label.csv"
[182] "model_1_mxnetAdam_modelInfo_parameters_parameter.csv"
[183] "model_1_mxnetAdam_modelType.csv"
[184] "model_1_mxnetAdam_perfNames.csv"
[185] "model_1_mxnetAdam_pred.csv"
[186] "model_1_mxnetAdam_resample.csv"
[187] "model_1_mxnetAdam_resampledCM.csv"
[188] "model_1_mxnetAdam_results.csv"
[189] "model_1_mxnetAdam_times_everything_elapsed.csv"
[190] "model_1_mxnetAdam_times_everything_sys.child.csv"
[191] "model_1_mxnetAdam_times_everything_sys.self.csv"
[192] "model_1_mxnetAdam_times_everything_user.child.csv"
[193] "model_1_mxnetAdam_times_everything_user.self.csv"
[194] "model_1_mxnetAdam_times_final_elapsed.csv"
[195] "model_1_mxnetAdam_times_final_sys.child.csv"
[196] "model_1_mxnetAdam_times_final_sys.self.csv"
[197] "model_1_mxnetAdam_times_final_user.child.csv"
[198] "model_1_mxnetAdam_times_final_user.self.csv"
[199] "model_1_mxnetAdam_trainingData.csv"
[200] "model_1_mxnetAdam_xlevels.csv"
[201] "model_1_svmRadial_bestTune.csv"
[202] "model_1_svmRadial_coefnames.csv"
[203] "model_1_svmRadial_contrasts.csv"
[204] "model_1_svmRadial_control_adaptive_alpha.csv"
[205] "model_1_svmRadial_control_adaptive_complete.csv"
[206] "model_1_svmRadial_control_adaptive_method.csv"
[207] "model_1_svmRadial_control_adaptive_min.csv"
[208] "model_1_svmRadial_control_index_Fold1.Rep1.csv"
[209] "model_1_svmRadial_control_index_Fold1.Rep2.csv"
[210] "model_1_svmRadial_control_index_Fold1.Rep3.csv"
[211] "model_1_svmRadial_control_index_Fold1.Rep4.csv"
[212] "model_1_svmRadial_control_index_Fold1.Rep5.csv"
[213] "model_1_svmRadial_control_index_Fold2.Rep1.csv"
[214] "model_1_svmRadial_control_index_Fold2.Rep2.csv"
[215] "model_1_svmRadial_control_index_Fold2.Rep3.csv"
[216] "model_1_svmRadial_control_index_Fold2.Rep4.csv"
[217] "model_1_svmRadial_control_index_Fold2.Rep5.csv"
[218] "model_1_svmRadial_control_index_Fold3.Rep1.csv"
[219] "model_1_svmRadial_control_index_Fold3.Rep2.csv"
[220] "model_1_svmRadial_control_index_Fold3.Rep3.csv"
[221] "model_1_svmRadial_control_index_Fold3.Rep4.csv"
[222] "model_1_svmRadial_control_index_Fold3.Rep5.csv"
[223] "model_1_svmRadial_control_index_Fold4.Rep1.csv"
[224] "model_1_svmRadial_control_index_Fold4.Rep2.csv"
[225] "model_1_svmRadial_control_index_Fold4.Rep3.csv"
[226] "model_1_svmRadial_control_index_Fold4.Rep4.csv"
[227] "model_1_svmRadial_control_index_Fold4.Rep5.csv"
[228] "model_1_svmRadial_control_index_Fold5.Rep1.csv"
[229] "model_1_svmRadial_control_index_Fold5.Rep2.csv"
[230] "model_1_svmRadial_control_index_Fold5.Rep3.csv"
[231] "model_1_svmRadial_control_index_Fold5.Rep4.csv"
[232] "model_1_svmRadial_control_index_Fold5.Rep5.csv"
[233] "model_1_svmRadial_control_index_Fold6.Rep1.csv"
[234] "model_1_svmRadial_control_index_Fold6.Rep2.csv"
[235] "model_1_svmRadial_control_index_Fold6.Rep3.csv"
[236] "model_1_svmRadial_control_index_Fold6.Rep4.csv"
[237] "model_1_svmRadial_control_index_Fold6.Rep5.csv"
[238] "model_1_svmRadial_control_indexOut_Resample01.csv"
[239] "model_1_svmRadial_control_indexOut_Resample02.csv"
[240] "model_1_svmRadial_control_indexOut_Resample03.csv"
[241] "model_1_svmRadial_control_indexOut_Resample04.csv"
[242] "model_1_svmRadial_control_indexOut_Resample05.csv"
[243] "model_1_svmRadial_control_indexOut_Resample06.csv"
[244] "model_1_svmRadial_control_indexOut_Resample07.csv"
[245] "model_1_svmRadial_control_indexOut_Resample08.csv"
[246] "model_1_svmRadial_control_indexOut_Resample09.csv"
[247] "model_1_svmRadial_control_indexOut_Resample10.csv"
[248] "model_1_svmRadial_control_indexOut_Resample11.csv"
[249] "model_1_svmRadial_control_indexOut_Resample12.csv"
[250] "model_1_svmRadial_control_indexOut_Resample13.csv"
[251] "model_1_svmRadial_control_indexOut_Resample14.csv"
[252] "model_1_svmRadial_control_indexOut_Resample15.csv"
[253] "model_1_svmRadial_control_indexOut_Resample16.csv"
[254] "model_1_svmRadial_control_indexOut_Resample17.csv"
[255] "model_1_svmRadial_control_indexOut_Resample18.csv"
[256] "model_1_svmRadial_control_indexOut_Resample19.csv"
[257] "model_1_svmRadial_control_indexOut_Resample20.csv"
[258] "model_1_svmRadial_control_indexOut_Resample21.csv"
[259] "model_1_svmRadial_control_indexOut_Resample22.csv"
[260] "model_1_svmRadial_control_indexOut_Resample23.csv"
[261] "model_1_svmRadial_control_indexOut_Resample24.csv"
[262] "model_1_svmRadial_control_indexOut_Resample25.csv"
[263] "model_1_svmRadial_control_indexOut_Resample26.csv"
[264] "model_1_svmRadial_control_indexOut_Resample27.csv"
[265] "model_1_svmRadial_control_indexOut_Resample28.csv"
[266] "model_1_svmRadial_control_indexOut_Resample29.csv"
[267] "model_1_svmRadial_control_indexOut_Resample30.csv"
[268] "model_1_svmRadial_control_preProcOptions_cutoff.csv"
[269] "model_1_svmRadial_control_preProcOptions_freqCut.csv"
[270] "model_1_svmRadial_control_preProcOptions_ICAcomp.csv"
[271] "model_1_svmRadial_control_preProcOptions_k.csv"
[272] "model_1_svmRadial_control_preProcOptions_thresh.csv"
[273] "model_1_svmRadial_control_preProcOptions_uniqueCut.csv"
[274] "model_1_svmRadial_control_sampling_first.csv"
[275] "model_1_svmRadial_control_sampling_name.csv"
[276] "model_1_svmRadial_dots.csv"
[277] "model_1_svmRadial_maximize.csv"
[278] "model_1_svmRadial_method.csv"
[279] "model_1_svmRadial_metric.csv"
[280] "model_1_svmRadial_modelInfo_parameters_class.csv"
[281] "model_1_svmRadial_modelInfo_parameters_label.csv"
[282] "model_1_svmRadial_modelInfo_parameters_parameter.csv"
[283] "model_1_svmRadial_modelType.csv"
[284] "model_1_svmRadial_perfNames.csv"
[285] "model_1_svmRadial_pred.csv"
[286] "model_1_svmRadial_resample.csv"
[287] "model_1_svmRadial_resampledCM.csv"
[288] "model_1_svmRadial_results.csv"
[289] "model_1_svmRadial_times_everything_elapsed.csv"
[290] "model_1_svmRadial_times_everything_sys.child.csv"
[291] "model_1_svmRadial_times_everything_sys.self.csv"
[292] "model_1_svmRadial_times_everything_user.child.csv"
[293] "model_1_svmRadial_times_everything_user.self.csv"
[294] "model_1_svmRadial_times_final_elapsed.csv"
[295] "model_1_svmRadial_times_final_sys.child.csv"
[296] "model_1_svmRadial_times_final_sys.self.csv"
[297] "model_1_svmRadial_times_final_user.child.csv"
[298] "model_1_svmRadial_times_final_user.self.csv"
[299] "model_1_svmRadial_trainingData.csv"
[300] "model_1_svmRadial_xlevels.csv"
```

## Dec 6, 2023

* Start here 

Great, you've successfully exported a comprehensive set of data from your R models into CSV files. To recreate these models in Python, you'll need to follow a multi-step process:

### Step 1: Identify Key Components to Recreate Models

Based on the extracted data, determine the key components you need to recreate each model in Python. Typically, these components include:

1. **Model Parameters and Hyperparameters**: These are the settings used to train the model. For each model (`gbm`, `svmRadial`, `mxnetAdam`), look for files related to parameters and best tuning settings. For instance, `model_1_gbm_bestTune.csv` may contain hyperparameters for the GBM model.

2. **Preprocessing Steps**: Check the preprocessing steps applied to the training data. Look for files like `model_1_gbm_preProcessSummary.csv`. This file should give you an idea of any scaling, normalization, or other transformations.

3. **Training Data**: You need the data used to train the models. Look for files like `model_1_gbm_trainingData.csv`.

### Step 2: Read the Exported Data into Python

Use Python to read the CSV files. This can be done using the `pandas` library. For example:

```python
import pandas as pd

# Example of reading a CSV file
gbm_best_tune = pd.read_csv("path/to/model_1_gbm_bestTune.csv")
```

### Step 3: Recreate Models in Python

Based on the extracted information, recreate each model in Python using equivalent libraries. For example:

- **GBM**: Use libraries like `XGBoost` or `LightGBM`.
- **svmRadial**: Use `scikit-learn`'s SVM with a radial basis function kernel.
- **mxnetAdam**: Use `MXNet` or another deep learning library if `mxnetAdam` refers to a neural network model.

You'll need to manually set the parameters for each model based on the exported CSV files.

### Step 4: Preprocess the Data

Apply the same preprocessing steps to your data in Python as were done in R. This might involve scaling, normalization, or other transformations.

### Step 5: Train the Models

Using the preprocessed data and the set parameters, train the models in Python.

### Step 6: Export or Use the Models

Once the models are recreated and trained, you can either use them for predictions or export them for future use.

### Notes and Considerations

- The recreation might not be 100% identical due to differences in how R and Python libraries implement certain algorithms.
- If there are custom functions or very specific methods used in the R models that don't have direct Python equivalents, you might need to look for workarounds or similar approaches in Python.
- Recreating the models is based on the assumption that you have a good understanding of both the R and Python ecosystems, particularly the machine learning libraries in both languages. If not, there might be a significant learning curve involved.

