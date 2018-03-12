default: all

all: clean models

clean:
	rm models.py

models:
	flask-sqlacodegen --outfile=models.py --flask mysql+pymysql://fydp@hiza:are_you_beast_9@hiza.mysql.database.azure.com/hiza
