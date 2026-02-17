
# Set the container ID
CONTAINER_ID=$(docker ps -q --filter ancestor=cancer_ae_dash:latest)

docker cp shiny-app/. $CONTAINER_ID:/srv/shiny-server

# Remove symlinks in the container before copying real files
docker exec $CONTAINER_ID rm /srv/shiny-server/data/data.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/AE_Category_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/cancer_type_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/AE_Category_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/cancer_type_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/cancer_type_stats.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_stats.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/ae_categories.json
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/drug_categories.json
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/outcomes.json

docker cp data/processed/cleaned/merged_formatted.csv $CONTAINER_ID:/srv/shiny-server/data/data.csv
docker cp data/processed/statistics/AE_Category_Expanded_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/AE_Category_freq_table.csv
docker cp data/processed/statistics/cancer_type_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/cancer_type_freq_table.csv
docker cp data/processed/statistics/drug_category_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_freq_table.csv
docker cp data/processed/statistics/overlap/AE_Category_Expanded_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/AE_Category_overlap_coefficient.csv
docker cp data/processed/statistics/overlap/cancer_type_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/cancer_type_overlap_coefficient.csv
docker cp data/processed/statistics/overlap/drug_category_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_overlap_coefficient.csv
docker cp data/processed/statistics/cancer_type_stats.csv $CONTAINER_ID:/srv/shiny-server/data/cancer_type_stats.csv
docker cp data/processed/statistics/drug_category_stats.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_stats.csv
docker cp data/processed/palettes/ae_categories.json $CONTAINER_ID:/srv/shiny-server/www/palettes/ae_categories.json
docker cp data/processed/palettes/drug_categories.json $CONTAINER_ID:/srv/shiny-server/www/palettes/drug_categories.json
docker cp data/raw/palettes/outcomes.json $CONTAINER_ID:/srv/shiny-server/www/palettes/outcomes.json
