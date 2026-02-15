from src.http_eksempel_4.rest_api import Rest_api

api = Rest_api(database_file_name = "./src/db_flat_file.json")
app = api.app

# Kør i terminal/console med: 
# uvicorn src.http_eksempel_4.main:app --reload
#
# Kør i browser:
# http://127.0.0.1:8000/ 
#
# Documentation: 
# http://127.0.0.1:8000/docs