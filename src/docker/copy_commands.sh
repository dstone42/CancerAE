
# Set the container ID
CONTAINER_ID=$(docker ps -q --filter ancestor=cancer_ae_dash:latest)

docker cp shiny-app/. $CONTAINER_ID:/srv/shiny-server

# Remove symlinks in the container before copying real files
docker exec $CONTAINER_ID rm /srv/shiny-server/data/data.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/ae_type_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/tumor_type_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_freq_table.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/ae_type_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/tumor_type_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_overlap_coefficient.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/tumor_type_stats.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/data/drug_category_stats.csv
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/ae_type.json
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/drug_categories.json
docker exec $CONTAINER_ID rm /srv/shiny-server/www/palettes/outcomes.json

docker cp data/processed/data.csv $CONTAINER_ID:/srv/shiny-server/data/data.csv
docker cp data/processed/statistics/ae_type_Expanded_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/ae_type_freq_table.csv
docker cp data/processed/statistics/tumor_type_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/tumor_type_freq_table.csv
docker cp data/processed/statistics/drug_category_freq_table.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_freq_table.csv
docker cp data/processed/statistics/overlap/ae_type_Expanded_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/ae_type_overlap_coefficient.csv
docker cp data/processed/statistics/overlap/tumor_type_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/tumor_type_overlap_coefficient.csv
docker cp data/processed/statistics/overlap/drug_category_overlap_coefficient.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_overlap_coefficient.csv
docker cp data/processed/statistics/tumor_type_stats.csv $CONTAINER_ID:/srv/shiny-server/data/tumor_type_stats.csv
docker cp data/processed/statistics/drug_category_stats.csv $CONTAINER_ID:/srv/shiny-server/data/drug_category_stats.csv
docker cp data/processed/palettes/ae_type.json $CONTAINER_ID:/srv/shiny-server/www/palettes/ae_type.json
docker cp data/processed/palettes/drug_categories.json $CONTAINER_ID:/srv/shiny-server/www/palettes/drug_categories.json
docker cp data/raw/palettes/outcomes.json $CONTAINER_ID:/srv/shiny-server/www/palettes/outcomes.json
