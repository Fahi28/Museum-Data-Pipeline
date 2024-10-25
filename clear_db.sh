export $(grep -E 'DB_IP|DB_USERNAME|DB_PASSWORD|DB_NAME' .env | xargs)

PGPASSWORD=$DB_PASSWORD psql -h $DB_IP -U $DB_USERNAME -d $DB_NAME -f schema.sql

if [ $? -eq 0 ]; then
    echo "Database successfully cleared"
else
    echo "Failed to clean database"
fi