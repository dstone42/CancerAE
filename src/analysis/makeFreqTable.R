library(data.table)

makeFreqTable <- function(df, subset_column) {
  unique_vals <- unique(unlist(strsplit(df[[subset_column]], ",")))
  freq_table <- matrix(0, nrow = length(unique_vals), ncol = length(unique_vals),
                       dimnames = list(unique_vals, unique_vals))
  item_counts <- setNames(rep(0, length(unique_vals)), unique_vals)
  for (row in df[[subset_column]]) {
    split <- unlist(strsplit(row, ","))
    # Count each item occurrence
    for (item in split) {
      item_counts[item] <- item_counts[item] + 1
    }
    if (length(split) > 1) {
      for (i in seq_len(length(split) - 1)) {
        for (j in (i+1):length(split)) {
          freq_table[split[i], split[j]] <- freq_table[split[i], split[j]] + 1
          freq_table[split[j], split[i]] <- freq_table[split[j], split[i]] + 1
        }
      }
    }
  }
  return(list(freq_table = freq_table, item_counts = item_counts))
}

data <- fread("data/processed/cleaned/merged_formatted.csv", sep = "$")

# AE Category Expanded Frequency Table
AE_Category_Expanded_result <- makeFreqTable(data, "AE_Category_Expanded")
write.csv(AE_Category_Expanded_result$freq_table, "data/processed/statistics/AE_Category_Expanded_freq_table.csv", row.names = TRUE)
write.csv(data.frame(item = names(AE_Category_Expanded_result$item_counts), 
                     count = AE_Category_Expanded_result$item_counts), 
          "data/processed/statistics/counts/AE_Category_Expanded_item_counts.csv", row.names = FALSE)

# Cancer Type Frequency Table
cancer_type_result <- makeFreqTable(data, "cancerType")
write.csv(cancer_type_result$freq_table, "data/processed/statistics/cancer_type_freq_table.csv", row.names = TRUE)
write.csv(data.frame(item = names(cancer_type_result$item_counts), 
                     count = cancer_type_result$item_counts), 
          "data/processed/statistics/counts/cancer_type_item_counts.csv", row.names = FALSE)

# Drug Category Frequency Table
drug_category_result <- makeFreqTable(data, "drug_category_expanded")
write.csv(drug_category_result$freq_table, "data/processed/statistics/drug_category_freq_table.csv", row.names = TRUE)
write.csv(data.frame(item = names(drug_category_result$item_counts), 
                     count = drug_category_result$item_counts), 
          "data/processed/statistics/counts/drug_category_item_counts.csv", row.names = FALSE)