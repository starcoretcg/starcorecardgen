"""
StarCore TCG - Publisher Dashboard
Unified publishing workflow using database backend
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from card_database import (
    init_database, get_cards_by_state, get_state_stats,
    update_card_state, bulk_update_states, can_transition
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from card_database import GeneratedCard, get_db_engine

st.set_page_config(page_title="Publisher Dashboard", page_icon="📋", layout="wide")

# Initialize database
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Header
st.title("📋 Publisher Dashboard")
st.markdown("Manage card publishing workflow across all card types")

# Stats Overview
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)

stats = get_state_stats()
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
    # Get unique card types from stats
    card_types = list(stats["by_type"].keys()) if stats["by_type"] else []
    type_filter = st.multiselect(
        "Card Type",
        card_types,
        default=card_types
    )

with filter_col3:
    search_id = st.text_input("Search Card ID", placeholder="Enter hash ID...")

# Get filtered cards from database
try:
    engine = get_db_engine()
    if engine:
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Build query
        query = session.query(GeneratedCard)
        
        if state_filter:
            query = query.filter(GeneratedCard.state.in_(state_filter))
        
        if type_filter:
            query = query.filter(GeneratedCard.card_type.in_(type_filter))
        
        if search_id:
            query = query.filter(GeneratedCard.card_id.contains(search_id))
        
        filtered_cards = query.order_by(GeneratedCard.created_at.desc()).all()
        session.close()
    else:
        filtered_cards = []
except:
    filtered_cards = []

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
            "Resource Core": "⚡",
            "Commander": "👑",
            "Unit": "🎖️"
        }
        
        card_data.append({
            "State": f"{state_emoji.get(card.state, '')} {card.state.title()}",
            "Type": f"{type_emoji.get(card.card_type, '📦')} {card.card_type}",
            "Card ID": card.card_id,
            "Size": card.size,
            "Resource": card.resource_type,
            "Rarity": card.rarity,
            "Tier": card.tier,
            "Quality": card.quality,
            "Score": round(card.score, 1),
            "Created": card.created_at.strftime("%Y-%m-%d %H:%M") if card.created_at else "-",
            "Published": card.published_at.strftime("%Y-%m-%d %H:%M") if card.published_at else "-",
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
            if bulk_update_states([c.card_id for c in draft_cards], "published"):
                st.success(f"✅ Published {len(draft_cards)} cards!")
                st.rerun()
    
    with bulk_col2:
        st.markdown("**Archive Published**")
        published_cards = [c for c in filtered_cards if c.state == "published"]
        if st.button(f"🗄️ Archive {len(published_cards)} Published", disabled=len(published_cards) == 0):
            if bulk_update_states([c.card_id for c in published_cards], "archived"):
                st.success(f"✅ Archived {len(published_cards)} cards!")
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
    selected_card = next((c for c in filtered_cards if c.card_id == selected_card_id), None)
    
    if selected_card:
        with manage_col2:
            st.markdown("**Current State**")
            state_emoji = {"draft": "📝", "published": "✅", "archived": "🗄️"}
            st.markdown(f"### {state_emoji.get(selected_card.state, '')} {selected_card.state.title()}")
        
        # Show card details
        detail_col1, detail_col2, detail_col3 = st.columns(3)
        
        with detail_col1:
            st.markdown("**Card Information**")
            st.text(f"ID: {selected_card.card_id}")
            st.text(f"Type: {selected_card.card_type}")
            st.text(f"Size: {selected_card.size}")
            st.text(f"Resource: {selected_card.resource_type}")
        
        with detail_col2:
            st.markdown("**Stats**")
            st.text(f"Rarity: {selected_card.rarity}")
            st.text(f"Tier: {selected_card.tier}")
            st.text(f"Quality: {selected_card.quality}")
            st.text(f"Score: {selected_card.score:.1f}")
        
        with detail_col3:
            st.markdown("**Timeline**")
            st.text(f"Created: {selected_card.created_at.strftime('%Y-%m-%d %H:%M')}" if selected_card.created_at else "Created: -")
            if selected_card.published_at:
                st.text(f"✅ Published: {selected_card.published_at.strftime('%Y-%m-%d %H:%M')}")
            if selected_card.archived_at:
                st.text(f"🗄️ Archived: {selected_card.archived_at.strftime('%Y-%m-%d %H:%M')}")
        
        # State transition buttons
        st.markdown("**Available Actions**")
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if can_transition(selected_card_id, "published"):
                if st.button("📤 Promote to Published", use_container_width=True):
                    if update_card_state(selected_card_id, "published"):
                        st.success("✅ Card published!")
                        st.rerun()
        
        with action_col2:
            if can_transition(selected_card_id, "archived"):
                if st.button("🗄️ Archive Card", use_container_width=True):
                    if update_card_state(selected_card_id, "archived"):
                        st.success("✅ Card archived!")
                        st.rerun()

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
    st.text(f"Total states: {stats['total']}")