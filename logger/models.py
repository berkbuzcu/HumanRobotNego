from peewee import * 
import json
import ast
import pathlib

DB_FOLDER_PATH = pathlib.Path(__file__).parent / "log_file"
DB_PATH = DB_FOLDER_PATH / "logs.sqlite3"

db =  SqliteDatabase(DB_PATH)

class JSONField(TextField):
    def db_value(self, value):
        #serialize JSON to string
        return value if value is None else json.dumps(value)

    def python_value(self, value):
        #deserialize
        return value if value is None else json.loads(value)

class ListField(TextField):
    def db_value(self, value):
        #serialize list to string
        #list -> str
        return str(value)

    def python_value(self, value):
        #deserialize
        #str -> list
        #warning: nuclear if online
        return ast.literal_eval(value)

class BaseModel( Model):
    class Meta:
        database = db

class SessionInformation(BaseModel):
    participant_uuid = UUIDField()
    session_location = CharField()
    agent_type = CharField()
    interaction_type = CharField()
    domain = CharField()

class SessionOfferHistory(BaseModel):
    session_id = ForeignKeyField(SessionInformation, backref='offer_history')
    bidder = CharField()
    agent_utility = FloatField()
    human_utility = FloatField()
    offer = JSONField()
    scaled_time = FloatField()
    move = CharField(null=True)
    agent_mood = CharField(null=True)
    max_valance = FloatField()
    min_valance	= FloatField()
    valance = FloatField()
    max_arousal	= FloatField()
    min_arousal = FloatField()
    arousal	= FloatField()
    sentences = ListField()

class SessionSummary(BaseModel):
    session_id = ForeignKeyField(SessionInformation, backref='summary')
    is_agreement = BooleanField()
    final_scaled_time = FloatField()
    final_agent_score = FloatField()
    final_user_score = FloatField()
    total_offers = IntegerField()
    human_awareness = FloatField()
    sensitivity_analysis = JSONField()
    robot_moods = JSONField()
    # Sensitivity:
    # Silent
    # Nice	
    # Fortunate	
    # Unfortunate	
    # Concession	
    # Selfish	

    # Robot Moods
    #Frustrated	
    #Annoyed	
    #Dissatisfied	
    #Neutral	
    #Convinced	
    #Content	
    #Worried

class SolverAgentLogs(BaseModel):
    session_id = ForeignKeyField(SessionInformation, backref='solver')
    logger = CharField()
    offer = JSONField()
    agent_utility = FloatField()
    scaled_time = FloatField()
    behavior_based = FloatField()
    behavior_based_final = FloatField()
    pe = FloatField()
    pa = FloatField()
    time_based = FloatField()
    final_utility = FloatField()
    predictions = JSONField()
    normalized_predictions = JSONField()
    sensitivity_class = CharField()

class HybridAgentLogs(BaseModel):
    session_id = ForeignKeyField(SessionInformation, backref='hybrid')
    logger = CharField()
    offer = JSONField()
    agent_utility = FloatField()
    scaled_time = FloatField()   
    behavior_based = FloatField()
    time_based = FloatField()

def create_tables():
    with db:
        db.create_tables([SolverAgentLogs, HybridAgentLogs, SessionInformation, SessionOfferHistory, SessionSummary])