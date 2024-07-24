FROM mongo

COPY users.json /users.json
CMD mongoimport --host mongodb --db incitev --collection users --authenticationDatabase admin --username root --password testing_db --type json --file /users.json --jsonArray