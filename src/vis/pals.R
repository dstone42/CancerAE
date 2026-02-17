library(data.table)
library(scales)
library(RJSONIO)
library(viridis)  # Add viridis library

# Read in the data
data_path <- "data/processed/cleaned/merged_formatted.csv"
data <- fread(data_path, sep = "$")

# Make palette for AE_Category

# Get unique values from AE_Category column
unique_categories <- unique(data$AE_Category)
# Remove NA values from unique categories
unique_categories <- unique_categories[!is.na(unique_categories)]
# Remove empty strings from unique categories
unique_categories <- unique_categories[unique_categories != ""]

# Generate a color palette with enough unique colors using turbo
palette <- turbo(length(unique_categories))

# Create a named vector for the palette
named_palette <- setNames(palette, unique_categories)

# Write the palette to a JSON file with names and colors as key-value pairs (colors as strings)
palette_output_path <- "data/processed/palettes/ae_categories.json"

jsonPal <- toJSON(named_palette)
write(jsonPal, palette_output_path)

# Visualize the palette
# barplot(rep(1, length(named_palette)), col = named_palette, names.arg = names(named_palette), las = 2, main = "AE Categories Palette", cex.names = 0.7)

# Make palette for drug_category

# Get unique values from drug_category column
unique_drug_categories <- unique(data$drug_category)
# Remove NA values from unique drug categories
unique_drug_categories <- unique_drug_categories[!is.na(unique_drug_categories)]
# Remove empty strings from unique drug categories
unique_drug_categories <- unique_drug_categories[unique_drug_categories != ""]

# Generate a color palette with enough unique colors using viridis
palette_drug <- viridis(length(unique_drug_categories), option = "D")

# Create a named vector for the drug category palette
named_palette_drug <- setNames(palette_drug, unique_drug_categories)

# Write the drug category palette to a JSON file with names and colors as key-value pairs (colors as strings)
palette_output_path_drug <- "data/processed/palettes/drug_categories.json"

jsonPal_drug <- toJSON(named_palette_drug)
write(jsonPal_drug, palette_output_path_drug)