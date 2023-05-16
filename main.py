from rnn import model, generate_combinations
from server import DatabaseConnector, uri, fill_db, app


connectionDB = DatabaseConnector(uri)

app.run()