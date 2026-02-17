
calculateOverlapCoefficient <- function(freq_table, item_counts) {
  items <- rownames(freq_table)
  overlap_matrix <- matrix(0, nrow = length(items), ncol = length(items),
                           dimnames = list(items, items))
  for (i in items) {
    for (j in items) {
      if (i != j) {
        min_count <- min(item_counts[i], item_counts[j])
        if (min_count > 0) {
          overlap_matrix[i, j] <- freq_table[i, j] / min_count
        } else {
          overlap_matrix[i, j] <- 0
        }
      }
    }
  }
  return(overlap_matrix)
}

# AE_Category
AE_Category_Expanded_freq_table <- as.matrix(read.csv("data/processed/statistics/AE_Category_Expanded_freq_table.csv", row.names = 1, check.names = FALSE))
AE_Category_Expanded_item_counts <- read.csv("data/processed/statistics/counts/AE_Category_Expanded_item_counts.csv")
AE_Category_Expanded_item_counts <- setNames(AE_Category_Expanded_item_counts$count, AE_Category_Expanded_item_counts$item)
AE_Category_Expanded_overlap <- calculateOverlapCoefficient(AE_Category_Expanded_freq_table, AE_Category_Expanded_item_counts)
write.csv(AE_Category_Expanded_overlap, "data/processed/statistics/overlap/AE_Category_Expanded_overlap_coefficient.csv", row.names = TRUE)

# Cancer Type
cancer_type_freq_table <- as.matrix(read.csv("data/processed/statistics/cancer_type_freq_table.csv", row.names = 1, check.names = FALSE))
cancer_type_item_counts <- read.csv("data/processed/statistics/counts/cancer_type_item_counts.csv")
cancer_type_item_counts <- setNames(cancer_type_item_counts$count, cancer_type_item_counts$item)
cancer_type_overlap <- calculateOverlapCoefficient(cancer_type_freq_table, cancer_type_item_counts)
write.csv(cancer_type_overlap, "data/processed/statistics/overlap/cancer_type_overlap_coefficient.csv", row.names = TRUE)

# Drug Category
drug_category_freq_table <- as.matrix(read.csv("data/processed/statistics/drug_category_freq_table.csv", row.names = 1, check.names = FALSE))
drug_category_item_counts <- read.csv("data/processed/statistics/counts/drug_category_item_counts.csv")
drug_category_item_counts <- setNames(drug_category_item_counts$count, drug_category_item_counts$item)
drug_category_overlap <- calculateOverlapCoefficient(drug_category_freq_table, drug_category_item_counts)
write.csv(drug_category_overlap, "data/processed/statistics/overlap/drug_category_overlap_coefficient.csv", row.names = TRUE)