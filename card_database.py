"""
StarCore Card Database Helper
PostgreSQL storage for generated cards using SQLAlchemy
"""

import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import streamlit as st

Base = declarative_base()

class GeneratedCard(Base):
    __tablename__ = 'generated_cards'
    
    card_id = Column(String(12), primary_key=True)
    card_type = Column(String(50))  # "Resource Core", "Commander", etc.
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
    """Get database engine from environment or secrets"""
    try:
        # Try Railway environment variable first
        database_url = os.getenv("DATABASE_URL")
        
        # Try Streamlit secrets if env var not found
        if not database_url:
            database_url = st.secrets.get("DATABASE_URL")
        
        if not database_url:
            st.warning("No DATABASE_URL found. Using in-memory session storage.")
            return None
        
        # Fix postgres:// to postgresql:// (Railway uses old format)
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
        st.error(f"Error saving card: {e}")
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
        st.error(f"Error loading cards: {e}")
        return []

def get_card_stats(card_type="Resource Core"):
    """Get statistics for generated cards"""
    engine = get_db_engine()
    if not engine:
        return None
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        from sqlalchemy import func
        
        stats = session.query(
            func.count(GeneratedCard.card_id).label('total'),
            func.avg(GeneratedCard.quality).label('avg_quality'),
            func.avg(GeneratedCard.tier).label('avg_tier'),
            func.avg(GeneratedCard.score).label('avg_score')
        ).filter_by(card_type=card_type).first()
        
        session.close()
        return stats
    
    except Exception as e:
        st.error(f"Error getting stats: {e}")
        return None

def clear_all_cards(card_type="Resource Core"):
    """Clear all cards of a specific type"""
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
        st.error(f"Error clearing cards: {e}")
        return False