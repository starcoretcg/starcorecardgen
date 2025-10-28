cd /workspaces/starcorecardgen

# Download the card_database.py file I created earlier
# OR create it now:

cat > card_database.py << 'EOF'
"""
StarCore Card Database Helper
PostgreSQL storage for generated cards using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

Base = declarative_base()

class GeneratedCard(Base):
    __tablename__ = 'generated_cards'
    
    card_id = Column(String(12), primary_key=True)
    card_type = Column(String(50))
    size = Column(String(20))
    resource_type = Column(String(20))
    tier = Column(Integer)
    quality = Column(Integer)
    rarity = Column(String(20))
    cost = Column(Integer)
    rpt = Column(Integer)
    hp = Column(Integer)
    links = Column(Integer)
    score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db_engine():
    """Get database engine from environment"""
    try:
        database_url = os.getenv("DATABASE_URL")
        
        if not database_url:
            return None
        
        # Fix postgres:// to postgresql://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        engine = create_engine(database_url)
        return engine
    
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def init_database():
    """Initialize database tables"""
    engine = get_db_engine()
    if engine:
        Base.metadata.create_all(engine)
        return True
    return False

def save_card(core, card_type="Resource Core"):
    """Save a generated card to database"""
    engine = get_db_engine()
    if not engine:
        return False
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        score = (core.quality * 0.7) + (core.tier * 3)
        
        card = GeneratedCard(
            card_id=core.card_id,
            card_type=card_type,
            size=core.size,
            resource_type=core.resource_type,
            tier=core.tier,
            quality=core.quality,
            rarity=core.rarity,
            cost=core.cost,
            rpt=core.rpt,
            hp=core.hp,
            links=core.links,
            score=score
        )
        
        session.add(card)
        session.commit()
        session.close()
        return True
    
    except Exception as e:
        return False

def load_recent_cards(limit=100, card_type="Resource Core"):
    """Load recent cards from database"""
    engine = get_db_engine()
    if not engine:
        return []
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        cards = session.query(GeneratedCard)\
            .filter_by(card_type=card_type)\
            .order_by(GeneratedCard.created_at.desc())\
            .limit(limit)\
            .all()
        
        session.close()
        return cards
    
    except Exception as e:
        return []

def clear_all_cards(card_type="Resource Core"):
    """Clear all cards"""
    engine = get_db_engine()
    if not engine:
        return False
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        session.query(GeneratedCard)\
            .filter_by(card_type=card_type)\
            .delete()
        
        session.commit()
        session.close()
        return True
    
    except Exception as e:
        return False
EOF

# Add database dependencies to requirements.txt
cat >> requirements.txt << 'EOF'
psycopg2-binary
sqlalchemy
EOF