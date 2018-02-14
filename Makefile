default: all

all: clean models

clean:
	rm models.py

models:
	flask-sqlacodegen --outfile=models.py --flask mysql+pymysql://fydp@fydp-db-server:are_you_beast_9@fydp-db-server.mysql.database.azure.com/fydp
