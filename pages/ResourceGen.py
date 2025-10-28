"""
StarCore Resource Core Generator - Streamlit Page
Two-column layout with featured card, data table, and statistics
WITH DATABASE PERSISTENCE
"""

import streamlit as st
import pandas as pd
from resource_core_generator import generate_resource_core, calculate_weight
from card_database import init_database, save_card, load_recent_cards, get_card_stats, clear_all_cards

st.title("⚡ Resource Core Generator")

# Initialize database on first load
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Load cards from database
if 'cards_loaded' not in st.session_state:
    db_cards = load_recent_cards(limit=100)
    st.session_state.generated_cards = db_cards
    st.session_state.cards_loaded = True

# Two-column layout - STRICT SEPARATION
left_col, right_col = st.columns([1, 2], gap="large")

# ============ LEFT COLUMN: GENERATOR ============
with left_col:
    st.subheader("Generator")
    
    # Selectors
    core_size = st.selectbox(
        "Core Size",
        ["Random", "Small", "Medium", "Large", "Massive"]
    )
    
    resource_type = st.selectbox(
        "Resource Type",
        ["Energy", "Matter", "Signal", "Life", "Omni"]
    )
    
    # Generate button
    if st.button("🎲 Generate Resource Core", type="primary", use_container_width=True):
        # Generate the core
        core = generate_resource_core(resource_type)
        
        # If specific size requested, keep trying (max 100 attempts)
        if core_size != "Random":
            attempts = 0
            while core.size != core_size and attempts < 100:
                core = generate_resource_core(resource_type)
                attempts += 1
        
        # Save to database
        if save_card(core, card_type="Resource Core"):
            st.session_state.generated_cards.insert(0, core)
            st.success("✅ Card saved!")
        else:
            # Fallback to session only if DB fails
            st.session_state.generated_cards.insert(0, core)
            st.warning("⚠️ Session only (DB unavailable)")
    
    # Most recent card display (stays in left column)
    if st.session_state.generated_cards:
        st.markdown("---")
        st.subheader("🎴 Most Recent")
        
        core = st.session_state.generated_cards[0]
        score = (core.quality * 0.7) + (core.tier * 3)
        
        # Card display - NO EMOJIS, USE RARITY TEXT
        st.markdown(f"### {core.size} {core.resource_type} Core")
        st.code(f"ID: {core.card_id}", language=None)
        st.caption(f"**{core.rarity}** | T{core.tier} Q{core.quality} | Score: {score:.1f}")
        
        # Stats in a grid
        st.markdown("**Stats:**")
        stat_cols = st.columns(4)
        with stat_cols[0]:
            st.metric("Cost", core.cost)
        with stat_cols[1]:
            st.metric("RPT", core.rpt)
        with stat_cols[2]:
            st.metric("HP", core.hp)
        with stat_cols[3]:
            st.metric("Links", core.links)

# ============ RIGHT COLUMN: DATA TABLE ============
with right_col:
    st.subheader(f"📊 Generation History ({len(st.session_state.generated_cards)} cards)")
    
    if st.session_state.generated_cards:
        # Build dataframe - NO EMOJIS
        data = []
        for core in st.session_state.generated_cards:
            score = (core.quality * 0.7) + (core.tier * 3)
            
            data.append({
                "Rarity": core.rarity,  # NO EMOJI
                "Size": core.size,
                "Type": core.resource_type,
                "ID": core.card_id[:8],
                "T": core.tier,
                "Q": core.quality,
                "Cost": core.cost,
                "RPT": core.rpt,
                "HP": core.hp,
                "Links": core.links,
                "Score": round(score, 1)
            })
        
        df = pd.DataFrame(data)
        
        # Display dataframe with full height
        st.dataframe(
            df,
            use_container_width=True,
            height=600,  # Full height table
            hide_index=True
        )
    else:
        st.info("👆 Generate your first card to see the data table!")

# ============ STATISTICS SECTION (FULL WIDTH BELOW COLUMNS) ============
st.markdown("---")

if st.session_state.generated_cards:
    st.header("📈 Generation Statistics")
    
    # Summary metrics
    total_cards = len(st.session_state.generated_cards)
    avg_quality = sum(c.quality for c in st.session_state.generated_cards) / total_cards
    avg_tier = sum(c.tier for c in st.session_state.generated_cards) / total_cards
    epic_plus = len([c for c in st.session_state.generated_cards if c.rarity in ["Epic", "Legendary"]])
    epic_rate = (epic_plus / total_cards) * 100
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Total Cards", total_cards)
    with metric_col2:
        st.metric("Avg Quality", f"{avg_quality:.1f}")
    with metric_col3:
        st.metric("Avg Tier", f"{avg_tier:.1f}")
    with metric_col4:
        st.metric("Epic+ Rate", f"{epic_rate:.1f}%")
    
    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        # Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="starcore_resources.csv",
            mime="text/csv",
            use_container_width=True
        )
    with btn_col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if clear_all_cards(card_type="Resource Core"):
                st.session_state.generated_cards = []
                st.success("✅ Database cleared!")
                st.rerun()
            else:
                st.error("❌ Failed to clear database")
    with btn_col3:
        st.button("🎲 Batch Generate (Coming Soon)", disabled=True, use_container_width=True)
    
    st.markdown("---")
    
    # Distribution charts
    chart_col1, chart_col2, chart_col3 = st.columns(3)
    
    with chart_col1:
        st.subheader("Rarity Distribution")
        rarity_counts = {}
        for core in st.session_state.generated_cards:
            rarity_counts[core.rarity] = rarity_counts.get(core.rarity, 0) + 1
        
        rarity_df = pd.DataFrame({
            "Rarity": list(rarity_counts.keys()),
            "Count": list(rarity_counts.values())
        })
        st.bar_chart(rarity_df.set_index("Rarity"))
    
    with chart_col2:
        st.subheader("Size Distribution")
        size_counts = {}
        for core in st.session_state.generated_cards:
            size_counts[core.size] = size_counts.get(core.size, 0) + 1
        
        size_df = pd.DataFrame({
            "Size": list(size_counts.keys()),
            "Count": list(size_counts.values())
        })
        st.bar_chart(size_df.set_index("Size"))
    
    with chart_col3:
        st.subheader("Type Distribution")
        type_counts = {}
        for core in st.session_state.generated_cards:
            type_counts[core.resource_type] = type_counts.get(core.resource_type, 0) + 1
        
        type_df = pd.DataFrame({
            "Type": list(type_counts.keys()),
            "Count": list(type_counts.values())
        })
        st.bar_chart(type_df.set_index("Type"))
    
    # Quality histogram
    st.subheader("Quality Distribution")
    quality_brackets = {
        "Q1-20": 0,
        "Q21-40": 0,
        "Q41-60": 0,
        "Q61-80": 0,
        "Q81-100": 0
    }
    
    for core in st.session_state.generated_cards:
        if core.quality <= 20:
            quality_brackets["Q1-20"] += 1
        elif core.quality <= 40:
            quality_brackets["Q21-40"] += 1
        elif core.quality <= 60:
            quality_brackets["Q41-60"] += 1
        elif core.quality <= 80:
            quality_brackets["Q61-80"] += 1
        else:
            quality_brackets["Q81-100"] += 1
    
    quality_df = pd.DataFrame({
        "Quality Range": list(quality_brackets.keys()),
        "Count": list(quality_brackets.values())
    })
    st.bar_chart(quality_df.set_index("Quality Range"))