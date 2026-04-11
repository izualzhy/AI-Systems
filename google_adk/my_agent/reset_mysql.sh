#!/bin/bash

HOST=localhost
PORT=3306
USER=root
PASSWORD=1234
DB=adk_sessions

echo "Cleaning all tables in $DB ..."

TABLES=$(mysql -h$HOST -P$PORT -u$USER -p$PASSWORD -N -e "SELECT table_name FROM information_schema.tables WHERE table_schema='$DB';")

for TABLE in $TABLES; do
    echo "Truncating $TABLE"
    mysql -h$HOST -P$PORT -u$USER -p$PASSWORD -e "DROP TABLE $DB.$TABLE;"
done

echo "Done."
