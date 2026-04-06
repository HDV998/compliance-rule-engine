from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Any, Union, List, Literal
from pydantic import model_validator
from database import SessionLocal
from database import engine
from models import Base
from testing import evaluate_rules
import json
from models import RuleModel

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"api is working"}


class Transaction(BaseModel):
    amount: int
    country: str
    
class rule(BaseModel):
    kind: Literal["rule"]
    field: str
    operator: str
    value: Any
        
class rulegroup(BaseModel):
    kind: Literal["group"]
    type: Literal["AND", "OR", "NOT"]
    rules:List[Union[rule, "rulegroup"]]
    
    @model_validator(mode="after")
    def check_not_rules(self):
        print("validator running")
        if self.type == "NOT":
            if len(self.rules) > 1:
                raise ValueError("for applying NOT, there must be only one rule")
        return self
    
rulegroup.model_rebuild()

class RuleCreateRequest(BaseModel):
    name: str
    rules: rulegroup


class RequestModel(BaseModel):
    transaction : Transaction
    rules: rulegroup
    

@app.post("/evaluate")
def evaluate(data:RequestModel):
    transaction = data.transaction.model_dump()
    rules = data.rules.model_dump()

    try:
        result = evaluate_rules(transaction, rules)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"result": result}


@app.post("/rules")
def create_rule(data: RuleCreateRequest):
    db = SessionLocal()
    try:
        rule_json = json.dumps(data.rules.model_dump())
        db_rule = RuleModel(
            name=data.name,
            rule_json=rule_json
        )
        
        db.add(db_rule)
        db.commit()
        db.refresh(db_rule)
        
        return {
            "id": db_rule.id,
            "name": db_rule.name
        }
        
    finally:
        db.close()
        
@app.post("/evaluate/{rule_id}")
def evaluate_saved_rule(rule_id: int, transaction: dict):
    db = SessionLocal()
    try:
        rule = db.query(RuleModel).filter(RuleModel.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rules = json.loads(rule.rule_json)
        try:
            result = evaluate_rules(transaction, rules)
        
        except ValueError as e:
            raise HTTPException(status_code=404, detail = str(e)); 
        
        return {
            "rule_id": rule_id,
            "result": result
        }
    finally:
        db.close()
        
        
@app.put("/rules/{rule_id}")
def update_rules(rule_id:int, data:RuleCreateRequest):
    db = SessionLocal()
    
    rule = db.query(RuleModel).filter(RuleModel.id == rule_id).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail = "the rule does not exsist")
    
    rule.name = data.name
    rule.rule_json = json.dumps(data.rules.model_dump())
    
    db.commit()
    db.refresh(rule)
    
    return {
        "msg":"updated successfully"
    }

    
    
    
    
    
    
    
    
    
    