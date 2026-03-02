
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

# ae_type
ae_type_Expanded_freq_table <- as.matrix(read.csv("data/processed/statistics/ae_type_Expanded_freq_table.csv", row.names = 1, check.names = FALSE))
ae_type_Expanded_item_counts <- read.csv("data/processed/statistics/counts/ae_type_Expanded_item_counts.csv")
ae_type_Expanded_item_counts <- setNames(ae_type_Expanded_item_counts$count, ae_type_Expanded_item_counts$item)
ae_type_Expanded_overlap <- calculateOverlapCoefficient(ae_type_Expanded_freq_table, ae_type_Expanded_item_counts)
write.csv(ae_type_Expanded_overlap, "data/processed/statistics/overlap/ae_type_Expanded_overlap_coefficient.csv", row.names = TRUE)

# Tumor Type
tumor_type_freq_table <- as.matrix(read.csv("data/processed/statistics/tumor_type_freq_table.csv", row.names = 1, check.names = FALSE))
tumor_type_item_counts <- read.csv("data/processed/statistics/counts/tumor_type_item_counts.csv")
tumor_type_item_counts <- setNames(tumor_type_item_counts$count, tumor_type_item_counts$item)
tumor_type_overlap <- calculateOverlapCoefficient(tumor_type_freq_table, tumor_type_item_counts)
write.csv(tumor_type_overlap, "data/processed/statistics/overlap/tumor_type_overlap_coefficient.csv", row.names = TRUE)

# Drug Category
drug_category_freq_table <- as.matrix(read.csv("data/processed/statistics/drug_category_freq_table.csv", row.names = 1, check.names = FALSE))
drug_category_item_counts <- read.csv("data/processed/statistics/counts/drug_category_item_counts.csv")
drug_category_item_counts <- setNames(drug_category_item_counts$count, drug_category_item_counts$item)
drug_category_overlap <- calculateOverlapCoefficient(drug_category_freq_table, drug_category_item_counts)
write.csv(drug_category_overlap, "data/processed/statistics/overlap/drug_category_overlap_coefficient.csv", row.names = TRUE)
