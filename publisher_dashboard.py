"""
StarCore TCG - Publisher Dashboard
Unified publishing workflow for all card types
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from card_state_manager import CardStateManager, CardState

# Page config
st.set_page_config(page_title="Publisher Dashboard", page_icon="📋", layout="wide")

# Initialize state manager
@st.cache_resource
def get_state_manager():
    return CardStateManager(data_dir="data")

manager = get_state_manager()

# Header
st.title("📋 Publisher Dashboard")
st.markdown("Manage card publishing workflow across all card types")

# Stats Overview
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

stats = manager.get_stats()
with col1:
    st.metric("📦 Total Cards", stats["total"])
with col2:
    st.metric("📝 Drafts", stats["draft"])
with col3:
    st.metric("✅ Published", stats["published"])
with col4:
    st.metric("🗄️ Archived", stats["archived"])

# Filters
st.markdown("---")
st.subheader("🔍 Filters")

filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    state_filter = st.multiselect(
        "State",
        ["draft", "published", "archived"],
        default=["draft", "published"]
    )

with filter_col2:
    # Get unique card types
    all_cards = manager.get_all_cards()
    card_types = list(set([card.card_type for card in all_cards])) if all_cards else []
    type_filter = st.multiselect(
        "Card Type",
        card_types,
        default=card_types
    )

with filter_col3:
    search_id = st.text_input("Search Card ID", placeholder="Enter hash ID...")

# Get filtered cards
filtered_cards = manager.get_all_cards()

# Apply filters
if state_filter:
    filtered_cards = [c for c in filtered_cards if c.state in state_filter]
if type_filter:
    filtered_cards = [c for c in filtered_cards if c.card_type in type_filter]
if search_id:
    filtered_cards = [c for c in filtered_cards if search_id.lower() in c.card_id.lower()]

# Sort by created date (newest first)
filtered_cards.sort(key=lambda x: x.created_at, reverse=True)

# Display cards
st.markdown("---")
st.subheader(f"📚 Cards ({len(filtered_cards)})")

if not filtered_cards:
    st.info("No cards match your filters. Generate some cards first!")
else:
    # Create DataFrame for display
    card_data = []
    for card in filtered_cards:
        # State emoji
        state_emoji = {
            "draft": "📝",
            "published": "✅",
            "archived": "🗄️"
        }
        
        # Card type emoji
        type_emoji = {
            "resource_core": "⚡",
            "commander": "👑",
            "unit": "🎖️"
        }
        
        card_data.append({
            "State": f"{state_emoji.get(card.state, '')} {card.state.title()}",
            "Type": f"{type_emoji.get(card.card_type, '📦')} {card.card_type.replace('_', ' ').title()}",
            "Card ID": card.card_id,
            "Created": datetime.fromisoformat(card.created_at).strftime("%Y-%m-%d %H:%M"),
            "Published": datetime.fromisoformat(card.published_at).strftime("%Y-%m-%d %H:%M") if card.published_at else "-",
            "Version": card.version,
            "Notes": card.notes[:50] + "..." if len(card.notes) > 50 else card.notes
        })
    
    # Display table
    df = pd.DataFrame(card_data)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=400
    )
    
    # Bulk actions
    st.markdown("---")
    st.subheader("⚡ Bulk Actions")
    
    bulk_col1, bulk_col2, bulk_col3 = st.columns(3)
    
    with bulk_col1:
        st.markdown("**Promote All Drafts**")
        draft_cards = [c for c in filtered_cards if c.state == "draft"]
        if st.button(f"📤 Publish {len(draft_cards)} Drafts", disabled=len(draft_cards) == 0):
            results = manager.bulk_transition([c.card_id for c in draft_cards], "published")
            success_count = sum(1 for v in results.values() if v)
            st.success(f"✅ Published {success_count} cards!")
            st.rerun()
    
    with bulk_col2:
        st.markdown("**Archive Published**")
        published_cards = [c for c in filtered_cards if c.state == "published"]
        if st.button(f"🗄️ Archive {len(published_cards)} Published", disabled=len(published_cards) == 0):
            results = manager.bulk_transition([c.card_id for c in published_cards], "archived")
            success_count = sum(1 for v in results.values() if v)
            st.success(f"✅ Archived {success_count} cards!")
            st.rerun()
    
    with bulk_col3:
        st.markdown("**Export Data**")
        if st.button("💾 Download CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download",
                data=csv,
                file_name=f"card_states_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Individual Card Management
st.markdown("---")
st.subheader("🎴 Manage Individual Card")

manage_col1, manage_col2 = st.columns([2, 1])

with manage_col1:
    selected_card_id = st.selectbox(
        "Select Card",
        options=[c.card_id for c in filtered_cards],
        format_func=lambda x: f"{x} - {next((c.state.title() for c in filtered_cards if c.card_id == x), '')}"
    ) if filtered_cards else None

if selected_card_id:
    selected_card = manager.get_card_state(selected_card_id)
    
    with manage_col2:
        st.markdown("**Current State**")
        state_emoji = {"draft": "📝", "published": "✅", "archived": "🗄️"}
        st.markdown(f"### {state_emoji.get(selected_card.state, '')} {selected_card.state.title()}")
    
    # Show card details
    detail_col1, detail_col2 = st.columns(2)
    
    with detail_col1:
        st.markdown("**Card Information**")
        st.text(f"ID: {selected_card.card_id}")
        st.text(f"Type: {selected_card.card_type.replace('_', ' ').title()}")
        st.text(f"Version: {selected_card.version}")
        st.text(f"Created: {datetime.fromisoformat(selected_card.created_at).strftime('%Y-%m-%d %H:%M:%S')}")
    
    with detail_col2:
        st.markdown("**Timeline**")
        if selected_card.published_at:
            st.text(f"✅ Published: {datetime.fromisoformat(selected_card.published_at).strftime('%Y-%m-%d %H:%M:%S')}")
        if selected_card.archived_at:
            st.text(f"🗄️ Archived: {datetime.fromisoformat(selected_card.archived_at).strftime('%Y-%m-%d %H:%M:%S')}")
    
    if selected_card.notes:
        st.markdown("**Notes**")
        st.text_area("", value=selected_card.notes, height=100, disabled=True)
    
    # State transition buttons
    st.markdown("**Available Actions**")
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if manager.can_transition(selected_card_id, "published"):
            if st.button("📤 Promote to Published", use_container_width=True):
                if manager.transition_state(selected_card_id, "published"):
                    st.success("✅ Card published!")
                    st.rerun()
                else:
                    st.error("❌ Failed to publish card")
    
    with action_col2:
        if manager.can_transition(selected_card_id, "archived"):
            if st.button("🗄️ Archive Card", use_container_width=True):
                if manager.transition_state(selected_card_id, "archived"):
                    st.success("✅ Card archived!")
                    st.rerun()
                else:
                    st.error("❌ Failed to archive card")
    
    with action_col3:
        if st.button("🗑️ Delete State", use_container_width=True, type="secondary"):
            if st.session_state.get(f"confirm_delete_{selected_card_id}"):
                manager.delete_card_state(selected_card_id)
                st.success("✅ Card state deleted!")
                st.rerun()
            else:
                st.session_state[f"confirm_delete_{selected_card_id}"] = True
                st.warning("⚠️ Click again to confirm deletion")

# Workflow Reference
with st.expander("ℹ️ Publishing Workflow Reference"):
    st.markdown("""
    ### State Transitions
    
    ```
    📝 DRAFT ──────────> ✅ PUBLISHED ──────────> 🗄️ ARCHIVED
         │                                              ↑
         └──────────────────────────────────────────────┘
    ```
    
    **Valid Transitions:**
    - **Draft → Published**: Card is ready for gameplay
    - **Draft → Archived**: Card is shelved without publishing
    - **Published → Archived**: Card is retired from active play
    - **Archived**: Terminal state (no further transitions)
    
    **Best Practices:**
    1. Generate cards in **Draft** state for testing
    2. Promote to **Published** when balanced and ready
    3. Move to **Archived** for retired or replaced cards
    4. Use bulk actions for set releases
    """)

# Debug info (collapsible)
with st.expander("🔧 Debug Info"):
    st.json(stats)
    st.text(f"State file: {manager.state_file}")
    st.text(f"Total states loaded: {len(manager.states)}")
