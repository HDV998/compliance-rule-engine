from sqlalchemy import Column, Integer, String, Text
from database import Base

class RuleModel(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    rule_json = Column(Text)