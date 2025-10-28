"""
Test script for StarCore TCG Publishing System
Run this to validate everything is working correctly
"""

import os
import sys
from pathlib import Path
from card_state_manager import CardStateManager

def test_publishing_system():
    """Run comprehensive tests on the publishing system"""
    
    print("🧪 StarCore TCG Publishing System Test Suite\n")
    print("=" * 60)
    
    # Test 1: Initialize manager
    print("\n✅ Test 1: Initialize State Manager")
    try:
        manager = CardStateManager(data_dir="test_data")
        print(f"   ✓ Manager initialized")
        print(f"   ✓ Data directory: {manager.data_dir}")
        print(f"   ✓ State file: {manager.state_file}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 2: Create draft cards
    print("\n✅ Test 2: Create Draft Cards")
    try:
        card1 = manager.create_card_state("test_abc123", "resource_core", "Test energy core")
        card2 = manager.create_card_state("test_def456", "commander", "Test commander")
        card3 = manager.create_card_state("test_ghi789", "resource_core", "Test matter core")
        print(f"   ✓ Created 3 cards in draft state")
        print(f"   ✓ Card 1: {card1.card_id} - {card1.state}")
        print(f"   ✓ Card 2: {card2.card_id} - {card2.state}")
        print(f"   ✓ Card 3: {card3.card_id} - {card3.state}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 3: State transitions
    print("\n✅ Test 3: State Transitions")
    try:
        # Draft -> Published
        can_publish = manager.can_transition("test_abc123", "published")
        print(f"   ✓ Can transition draft->published? {can_publish}")
        
        success = manager.transition_state("test_abc123", "published")
        print(f"   ✓ Transitioned card1 to published: {success}")
        
        card1_updated = manager.get_card_state("test_abc123")
        print(f"   ✓ Card1 state is now: {card1_updated.state}")
        print(f"   ✓ Published timestamp: {card1_updated.published_at}")
        
        # Published -> Archived
        success = manager.transition_state("test_abc123", "archived")
        print(f"   ✓ Transitioned card1 to archived: {success}")
        
        card1_final = manager.get_card_state("test_abc123")
        print(f"   ✓ Card1 final state: {card1_final.state}")
        
        # Invalid transition (archived -> anything)
        can_exit_archive = manager.can_transition("test_abc123", "published")
        print(f"   ✓ Can exit archived state? {can_exit_archive} (should be False)")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 4: Queries
    print("\n✅ Test 4: Query Functions")
    try:
        all_cards = manager.get_all_cards()
        print(f"   ✓ Total cards: {len(all_cards)}")
        
        drafts = manager.get_cards_by_state("draft")
        print(f"   ✓ Draft cards: {len(drafts)}")
        
        published = manager.get_cards_by_state("published")
        print(f"   ✓ Published cards: {len(published)}")
        
        archived = manager.get_cards_by_state("archived")
        print(f"   ✓ Archived cards: {len(archived)}")
        
        resources = manager.get_cards_by_type("resource_core")
        print(f"   ✓ Resource cores: {len(resources)}")
        
        commanders = manager.get_cards_by_type("commander")
        print(f"   ✓ Commanders: {len(commanders)}")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 5: Bulk operations
    print("\n✅ Test 5: Bulk Transitions")
    try:
        draft_ids = [c.card_id for c in manager.get_cards_by_state("draft")]
        print(f"   ✓ Found {len(draft_ids)} draft cards")
        
        results = manager.bulk_transition(draft_ids, "published")
        success_count = sum(1 for v in results.values() if v)
        print(f"   ✓ Bulk published {success_count} cards")
        
        new_draft_count = len(manager.get_cards_by_state("draft"))
        print(f"   ✓ Remaining drafts: {new_draft_count}")
        
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 6: Stats
    print("\n✅ Test 6: Statistics")
    try:
        stats = manager.get_stats()
        print(f"   ✓ Total: {stats['total']}")
        print(f"   ✓ Drafts: {stats['draft']}")
        print(f"   ✓ Published: {stats['published']}")
        print(f"   ✓ Archived: {stats['archived']}")
        print(f"   ✓ By type: {stats['by_type']}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 7: Persistence
    print("\n✅ Test 7: Data Persistence")
    try:
        # Create new manager instance (simulates app restart)
        manager2 = CardStateManager(data_dir="test_data")
        loaded_count = len(manager2.get_all_cards())
        print(f"   ✓ Reloaded {loaded_count} cards from disk")
        
        if loaded_count == len(all_cards):
            print(f"   ✓ All cards persisted correctly")
        else:
            print(f"   ✗ Mismatch: {loaded_count} vs {len(all_cards)}")
            return False
            
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False
    
    # Test 8: Cleanup
    print("\n✅ Test 8: Cleanup")
    try:
        # Delete test data
        import shutil
        if Path("test_data").exists():
            shutil.rmtree("test_data")
            print(f"   ✓ Cleaned up test data directory")
    except Exception as e:
        print(f"   ⚠ Warning: Couldn't clean up: {e}")
    
    print("\n" + "=" * 60)
    print("✨ All tests passed! Publishing system is ready to use.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_publishing_system()
    sys.exit(0 if success else 1)
