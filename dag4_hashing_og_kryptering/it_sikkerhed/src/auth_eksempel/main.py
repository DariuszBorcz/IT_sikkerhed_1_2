import uvicorn
from src.auth_eksempel.auth_rest_api import Auth_rest_api

api = Auth_rest_api()
app = api.app


# Kør i terminal/console med: 
# uvicorn src.auth_eksempel.main:app --reload
#
# Kør i browser:
# http://127.0.0.1:8000/ 
#
# Documentation: 
# http://127.0.0.1:8000/docs