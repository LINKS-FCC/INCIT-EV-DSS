FROM mongo

COPY defaults.json /defaults.json
CMD mongoimport --host mongodb --db incitev --collection defaults --authenticationDatabase admin --username root --password testing_db --type json --file /defaults.json --jsonArray