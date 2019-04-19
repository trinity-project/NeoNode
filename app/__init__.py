

from flask import Flask
from flask_jsonrpc import JSONRPC
from flask_sqlalchemy import SQLAlchemy
import pymysql
from flask_cors import CORS
from config import setting
from project_log import setup_logger

pymysql.install_as_MySQLdb()

app = Flask(__name__,template_folder="../")
cors = CORS(app, support_credentials=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' %(setting.MYSQLDATABASE["user"],
                                                                setting.MYSQLDATABASE["passwd"],
                                                                setting.MYSQLDATABASE["host"],
                                                                setting.MYSQLDATABASE["db_neo_table"])
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=True
app.config["DEBUG"] = True
db = SQLAlchemy(app)
jsonrpc = JSONRPC(app, "/")
logger = setup_logger()


from .controller import *

