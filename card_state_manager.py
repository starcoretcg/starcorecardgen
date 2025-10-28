"""
StarCore TCG - Card State Manager
Handles publishing workflow: draft -> published -> archived
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict

@dataclass
class CardState:
    """Represents the publishing state of any card"""
    card_id: str  # Hash ID
    card_type: str  # resource_core, commander, unit, etc.
    state: str  # draft, published, archived
    created_at: str
    published_at: Optional[str] = None
    archived_at: Optional[str] = None
    version: int = 1
    notes: str = ""

class CardStateManager:
    """Manages card publishing states across all card types"""
    
    VALID_STATES = ["draft", "published", "archived"]
    VALID_TRANSITIONS = {
        "draft": ["published", "archived"],
        "published": ["archived"],
        "archived": []  # Terminal state
    }
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the state manager"""
        self.data_dir = Path(data_dir)
        self.state_file = self.data_dir / "card_states.json"
        self._ensure_data_dir()
        self.states = self._load_states()
    
    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.state_file.exists():
            self.state_file.write_text(json.dumps({}, indent=2))
    
    def _load_states(self) -> Dict[str, CardState]:
        """Load all card states from JSON"""
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                return {
                    card_id: CardState(**state_data)
                    for card_id, state_data in data.items()
                }
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_states(self):
        """Save all card states to JSON"""
        data = {
            card_id: asdict(state)
            for card_id, state in self.states.items()
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_card_state(self, card_id: str, card_type: str, notes: str = "") -> CardState:
        """Create a new card in draft state"""
        if card_id in self.states:
            return self.states[card_id]  # Already exists
        
        state = CardState(
            card_id=card_id,
            card_type=card_type,
            state="draft",
            created_at=datetime.now().isoformat(),
            notes=notes
        )
        
        self.states[card_id] = state
        self._save_states()
        return state
    
    def get_card_state(self, card_id: str) -> Optional[CardState]:
        """Get the state of a specific card"""
        return self.states.get(card_id)
    
    def transition_state(self, card_id: str, new_state: str) -> bool:
        """
        Transition a card to a new state
        Returns True if successful, False if invalid transition
        """
        if card_id not in self.states:
            return False
        
        card_state = self.states[card_id]
        current_state = card_state.state
        
        # Validate transition
        if new_state not in self.VALID_STATES:
            return False
        
        if new_state not in self.VALID_TRANSITIONS[current_state]:
            return False
        
        # Update state
        card_state.state = new_state
        
        # Update timestamps
        if new_state == "published":
            card_state.published_at = datetime.now().isoformat()
        elif new_state == "archived":
            card_state.archived_at = datetime.now().isoformat()
        
        self._save_states()
        return True
    
    def get_cards_by_state(self, state: str) -> List[CardState]:
        """Get all cards in a specific state"""
        return [
            card_state for card_state in self.states.values()
            if card_state.state == state
        ]
    
    def get_cards_by_type(self, card_type: str) -> List[CardState]:
        """Get all cards of a specific type"""
        return [
            card_state for card_state in self.states.values()
            if card_state.card_type == card_type
        ]
    
    def get_all_cards(self) -> List[CardState]:
        """Get all card states"""
        return list(self.states.values())
    
    def delete_card_state(self, card_id: str) -> bool:
        """Delete a card state (use carefully!)"""
        if card_id in self.states:
            del self.states[card_id]
            self._save_states()
            return True
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about card states"""
        stats = {
            "total": len(self.states),
            "draft": 0,
            "published": 0,
            "archived": 0
        }
        
        # Count by type
        type_counts = {}
        
        for card_state in self.states.values():
            stats[card_state.state] += 1
            
            if card_state.card_type not in type_counts:
                type_counts[card_state.card_type] = 0
            type_counts[card_state.card_type] += 1
        
        stats["by_type"] = type_counts
        return stats
    
    def bulk_transition(self, card_ids: List[str], new_state: str) -> Dict[str, bool]:
        """
        Transition multiple cards at once
        Returns dict of {card_id: success_bool}
        """
        results = {}
        for card_id in card_ids:
            results[card_id] = self.transition_state(card_id, new_state)
        return results
    
    def can_transition(self, card_id: str, new_state: str) -> bool:
        """Check if a transition is valid without performing it"""
        if card_id not in self.states:
            return False
        
        current_state = self.states[card_id].state
        return new_state in self.VALID_TRANSITIONS.get(current_state, [])


# Helper functions for common operations
def promote_to_published(manager: CardStateManager, card_id: str) -> bool:
    """Promote a draft card to published"""
    return manager.transition_state(card_id, "published")

def archive_card(manager: CardStateManager, card_id: str) -> bool:
    """Archive a card"""
    return manager.transition_state(card_id, "archived")

def get_publishable_cards(manager: CardStateManager) -> List[CardState]:
    """Get all cards that can be published (drafts)"""
    return manager.get_cards_by_state("draft")

def get_active_cards(manager: CardStateManager) -> List[CardState]:
    """Get all published cards"""
    return manager.get_cards_by_state("published")


if __name__ == "__main__":
    # Test the system
    print("🧪 Testing Card State Manager\n")
    
    manager = CardStateManager(data_dir="test_data")
    
    # Create some test cards
    print("Creating test cards...")
    card1 = manager.create_card_state("abc123def456", "resource_core", "Test energy core")
    card2 = manager.create_card_state("xyz789uvw012", "commander", "Test commander")
    card3 = manager.create_card_state("lmn345opq678", "resource_core", "Test matter core")
    
    print(f"✅ Created {len(manager.states)} cards\n")
    
    # Test transitions
    print("Testing state transitions...")
    print(f"Card 1 can publish? {manager.can_transition('abc123def456', 'published')}")
    manager.transition_state("abc123def456", "published")
    print(f"✅ Card 1 promoted to published\n")
    
    # Get stats
    print("📊 Current Stats:")
    stats = manager.get_stats()
    print(f"Total cards: {stats['total']}")
    print(f"Drafts: {stats['draft']}")
    print(f"Published: {stats['published']}")
    print(f"Archived: {stats['archived']}")
    print(f"By Type: {stats['by_type']}")
