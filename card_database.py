import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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
    state = Column(String(20), default="draft")  # NEW: draft, published, archived
    notes = Column(String(500), default="")  # NEW: optional notes
    published_at = Column(DateTime, nullable=True)  # NEW: timestamp
    archived_at = Column(DateTime, nullable=True)  # NEW: timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db_engine():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return None
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    return create_engine(database_url)

def init_database():
    engine = get_db_engine()
    if engine:
        Base.metadata.create_all(engine)
    return True

def save_card(core, card_type="Resource Core", state="draft", notes=""):
    """Save a card with initial state (default: draft)"""
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
            score=score,
            state=state,
            notes=notes
        )
        session.add(card)
        session.commit()
        session.close()
        return True
    except:
        return False

def load_recent_cards(limit=100, card_type="Resource Core"):
    engine = get_db_engine()
    if not engine:
        return []
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        cards = session.query(GeneratedCard).filter_by(card_type=card_type).order_by(GeneratedCard.created_at.desc()).limit(limit).all()
        session.close()
        return cards
    except:
        return []

def clear_all_cards(card_type="Resource Core"):
    engine = get_db_engine()
    if not engine:
        return False
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        session.query(GeneratedCard).filter_by(card_type=card_type).delete()
        session.commit()
        session.close()
        return True
    except:
        return False

# ========== NEW STATE MANAGEMENT FUNCTIONS ==========

def update_card_state(card_id, new_state):
    """Update card state: draft -> published -> archived"""
    engine = get_db_engine()
    if not engine:
        return False
    
    valid_transitions = {
        "draft": ["published", "archived"],
        "published": ["archived"],
        "archived": []
    }
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        card = session.query(GeneratedCard).filter_by(card_id=card_id).first()
        
        if not card:
            session.close()
            return False
        
        # Validate transition
        if new_state not in valid_transitions.get(card.state, []):
            session.close()
            return False
        
        # Update state
        card.state = new_state
        
        # Update timestamps
        if new_state == "published":
            card.published_at = datetime.utcnow()
        elif new_state == "archived":
            card.archived_at = datetime.utcnow()
        
        session.commit()
        session.close()
        return True
    except:
        return False

def get_cards_by_state(state, card_type=None):
    """Get all cards in a specific state"""
    engine = get_db_engine()
    if not engine:
        return []
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        query = session.query(GeneratedCard).filter_by(state=state)
        if card_type:
            query = query.filter_by(card_type=card_type)
        cards = query.order_by(GeneratedCard.created_at.desc()).all()
        session.close()
        return cards
    except:
        return []

def get_state_stats():
    """Get statistics about card states"""
    engine = get_db_engine()
    if not engine:
        return {"total": 0, "draft": 0, "published": 0, "archived": 0, "by_type": {}}
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        total = session.query(GeneratedCard).count()
        draft = session.query(GeneratedCard).filter_by(state="draft").count()
        published = session.query(GeneratedCard).filter_by(state="published").count()
        archived = session.query(GeneratedCard).filter_by(state="archived").count()
        
        # Count by type
        cards = session.query(GeneratedCard).all()
        by_type = {}
        for card in cards:
            by_type[card.card_type] = by_type.get(card.card_type, 0) + 1
        
        session.close()
        
        return {
            "total": total,
            "draft": draft,
            "published": published,
            "archived": archived,
            "by_type": by_type
        }
    except:
        return {"total": 0, "draft": 0, "published": 0, "archived": 0, "by_type": {}}

def bulk_update_states(card_ids, new_state):
    """Update multiple cards to a new state"""
    engine = get_db_engine()
    if not engine:
        return False
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        valid_transitions = {
            "draft": ["published", "archived"],
            "published": ["archived"],
            "archived": []
        }
        
        for card_id in card_ids:
            card = session.query(GeneratedCard).filter_by(card_id=card_id).first()
            if card and new_state in valid_transitions.get(card.state, []):
                card.state = new_state
                if new_state == "published":
                    card.published_at = datetime.utcnow()
                elif new_state == "archived":
                    card.archived_at = datetime.utcnow()
        
        session.commit()
        session.close()
        return True
    except:
        return False

def can_transition(card_id, new_state):
    """Check if a state transition is valid"""
    engine = get_db_engine()
    if not engine:
        return False
    
    valid_transitions = {
        "draft": ["published", "archived"],
        "published": ["archived"],
        "archived": []
    }
    
    try:
        Session = sessionmaker(bind=engine)
        session = Session()
        card = session.query(GeneratedCard).filter_by(card_id=card_id).first()
        session.close()
        
        if not card:
            return False
        
        return new_state in valid_transitions.get(card.state, [])
    except:
        return False