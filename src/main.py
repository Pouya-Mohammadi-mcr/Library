from comp62521 import app
from comp62521.database import database, mock_database
import sys
import os

if len(sys.argv) == 1:
    dataset = "Mock"
    db = mock_database.MockDatabase()
else:
    data_file = sys.argv[1]
    path, dataset = os.path.split(data_file)
    print(f"Database: path={path} name={dataset}")
    db = database.Database()
    if not db.read(data_file):
        sys.exit(1)

app.config['DATASET'] = dataset
app.config['DATABASE'] = db

if "DEBUG" in os.environ:
    app.config['DEBUG'] = True

if "TESTING" in os.environ:
    app.config['TESTING'] = True

app.run(host='0.0.0.0', port=9292 ,debug=True) # debug=True forces auto reload
