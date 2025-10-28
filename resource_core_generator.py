"""
StarCore TCG - Resource Core Generation System
Version: 1.0
Date: October 28, 2025

10-Tier, 100-Point Quality System with Weighted Stat Rolls
"""

import random
import hashlib
from datetime import datetime
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class ResourceCore:
    """Generated Resource Core with all stats"""
    size: str  # Small, Medium, Large, Massive
    tier: int  # 1-10
    quality: int  # 1-100
    cost: int
    rpt: int  # Resources Per Turn
    hp: int
    links: int
    resource_type: str  # Energy, Matter, Signal, Life, Omni
    rarity: str  # Common, Uncommon, Rare, Epic, Legendary
    card_id: str = field(default="")  # Unique hash ID
    
    def __post_init__(self):
        """Generate unique hash ID if not provided"""
        if not self.card_id:
            core_data = f"{self.size}{self.tier}{self.quality}{self.cost}{self.rpt}{self.hp}{self.links}{self.resource_type}{datetime.now().isoformat()}"
            self.card_id = hashlib.sha256(core_data.encode()).hexdigest()[:12]


# Core size stat ranges
CORE_RANGES = {
    "Small": {
        "cost": (0, 0),  # Always 0
        "rpt": (2, 2),   # Always 2
        "hp": (2, 4),
        "links": (1, 1)  # Always 1
    },
    "Medium": {
        "cost": (1, 3),
        "rpt": (2, 4),
        "hp": (3, 5),
        "links": (1, 2)
    },
    "Large": {
        "cost": (2, 5),
        "rpt": (3, 6),
        "hp": (4, 8),
        "links": (1, 3)
    },
    "Massive": {
        "cost": (4, 8),
        "rpt": (5, 10),
        "hp": (7, 12),
        "links": (2, 4)
    }
}


def roll_tier() -> int:
    """
    Roll a tier from 1-10 where higher tiers are exponentially rarer.
    Tier 10 is 10x harder to roll than Tier 1.
    
    Uses inverse probability weighting:
    - Tier 1: weight = 10
    - Tier 2: weight = 9
    - ...
    - Tier 10: weight = 1
    """
    weights = [11 - i for i in range(1, 11)]  # [10, 9, 8, ..., 1]
    tier = random.choices(range(1, 11), weights=weights, k=1)[0]
    return tier


def roll_quality() -> int:
    """
    Roll a quality score from 1-100 where higher values are exponentially rarer.
    100 is 100x harder to roll than 1.
    
    Uses inverse probability weighting.
    """
    weights = [101 - i for i in range(1, 101)]  # [100, 99, 98, ..., 1]
    quality = random.choices(range(1, 101), weights=weights, k=1)[0]
    return quality


def calculate_weight(tier: int, quality: int) -> float:
    """
    Calculate the combined weight from tier and quality.
    
    Weight formula: (tier/10) * (quality/100)
    - Min: 0.01 (Tier 1, Quality 1)
    - Max: 1.0 (Tier 10, Quality 100)
    
    This weight influences stat rolls within their ranges.
    """
    return (tier / 10.0) * (quality / 100.0)


def weighted_roll(min_val: int, max_val: int, weight: float) -> int:
    """
    Roll a value between min_val and max_val, weighted by the quality/tier weight.
    
    Higher weight = bias toward max_val
    Lower weight = bias toward min_val
    
    Uses weighted random selection across the range.
    """
    if min_val == max_val:
        return min_val
    
    range_size = max_val - min_val + 1
    values = list(range(min_val, max_val + 1))
    
    # Create weights that favor higher values based on weight parameter
    # weight=0.01 → heavily favor min
    # weight=1.0 → heavily favor max
    weights = [1 + (i * weight * 10) for i in range(range_size)]
    
    return random.choices(values, weights=weights, k=1)[0]


def determine_size_from_tier(tier: int) -> str:
    """
    Determine core size based on tier.
    
    Tier 1-3: Small
    Tier 4-6: Medium
    Tier 7-8: Large
    Tier 9-10: Massive
    """
    if tier <= 3:
        return "Small"
    elif tier <= 6:
        return "Medium"
    elif tier <= 8:
        return "Large"
    else:
        return "Massive"


def determine_rarity(tier: int, quality: int) -> str:
    """
    Determine rarity based on quality score and tier.
    
    Rarity is an OUTPUT, not an INPUT.
    Since Legendary/Unique/Artifact have deck limits (1 each),
    they must be extremely rare.
    
    Score = (quality * 0.7) + (tier * 3)
    
    Legendary: Only T9-10 with Q95+ (ultra-rare, ~0.1-0.5%)
    Epic: God-rolls across all tiers (~2-5%)
    Rare: Strong rolls (~10-15%)
    Uncommon: Decent rolls (~25-35%)
    Common: Everything else (~40-50%)
    """
    score = (quality * 0.7) + (tier * 3)
    
    if score >= 98:
        return "Legendary"  # 🟡 Only the absolute best
    elif score >= 90:
        return "Epic"  # 🟣 God-rolls
    elif score >= 75:
        return "Rare"  # 🔵 Strong rolls
    elif score >= 55:
        return "Uncommon"  # 🔵 Decent rolls
    else:
        return "Common"  # ⚪ Everything else


def generate_resource_core(resource_type: str = "Energy") -> ResourceCore:
    """
    Generate a complete Resource Core using the tier/quality weighted system.
    
    Process:
    1. Roll tier (1-10, exponentially harder)
    2. Roll quality (1-100, exponentially harder)
    3. Calculate weight from tier + quality
    4. Determine size from tier
    5. Roll all stats using weighted rolls within size ranges
    6. Determine rarity from tier + quality (OUTPUT)
    """
    # Step 1: Roll tier and quality
    tier = roll_tier()
    quality = roll_quality()
    
    # Step 2: Calculate combined weight
    weight = calculate_weight(tier, quality)
    
    # Step 3: Determine size from tier
    size = determine_size_from_tier(tier)
    ranges = CORE_RANGES[size]
    
    # Step 4: Roll stats using weight
    cost = weighted_roll(ranges["cost"][0], ranges["cost"][1], weight)
    rpt = weighted_roll(ranges["rpt"][0], ranges["rpt"][1], weight)
    hp = weighted_roll(ranges["hp"][0], ranges["hp"][1], weight)
    links = weighted_roll(ranges["links"][0], ranges["links"][1], weight)
    
    # Step 5: Determine rarity (OUTPUT based on tier + quality)
    rarity = determine_rarity(tier, quality)
    
    return ResourceCore(
        size=size,
        tier=tier,
        quality=quality,
        cost=cost,
        rpt=rpt,
        hp=hp,
        links=links,
        resource_type=resource_type,
        rarity=rarity
    )


def print_card(core: ResourceCore) -> None:
    """Pretty print a generated card"""
    rarity_colors = {
        "Common": "⚪",
        "Uncommon": "🔵",
        "Rare": "🔵",
        "Epic": "🟣",
        "Legendary": "🟡"
    }
    
    rarity_symbol = rarity_colors.get(core.rarity, "")
    
    print(f"\n{'='*50}")
    print(f"{core.size} {core.resource_type} Core")
    print(f"Card ID: {core.card_id}")
    print(f"Tier {core.tier} | Quality {core.quality} | {rarity_symbol} {core.rarity.upper()}")
    print(f"Weight: {calculate_weight(core.tier, core.quality):.3f} | Score: {(core.quality * 0.7) + (core.tier * 3):.1f}")
    print(f"{'='*50}")
    print(f"Cost: {core.cost}")
    print(f"RPT: {core.rpt}")
    print(f"HP: {core.hp}")
    print(f"Links: {core.links}")
    print(f"{'='*50}")


def generate_batch(count: int = 10, resource_type: str = "Energy") -> list[ResourceCore]:
    """Generate a batch of Resource Cores"""
    return [generate_resource_core(resource_type) for _ in range(count)]


def analyze_batch(cores: list[ResourceCore]) -> None:
    """Analyze statistics from a batch of generated cores"""
    print(f"\n{'='*50}")
    print(f"BATCH ANALYSIS ({len(cores)} cards)")
    print(f"{'='*50}")
    
    # Tier distribution
    tier_counts = {}
    for core in cores:
        tier_counts[core.tier] = tier_counts.get(core.tier, 0) + 1
    
    print("\nTier Distribution:")
    for tier in sorted(tier_counts.keys()):
        count = tier_counts[tier]
        pct = (count / len(cores)) * 100
        print(f"  Tier {tier:2d}: {count:3d} cards ({pct:5.1f}%)")
    
    # Size distribution
    size_counts = {}
    for core in cores:
        size_counts[core.size] = size_counts.get(core.size, 0) + 1
    
    print("\nSize Distribution:")
    for size in ["Small", "Medium", "Large", "Massive"]:
        count = size_counts.get(size, 0)
        pct = (count / len(cores)) * 100
        print(f"  {size:7s}: {count:3d} cards ({pct:5.1f}%)")
    
    # Quality brackets
    quality_brackets = {
        "1-20": 0,
        "21-40": 0,
        "41-60": 0,
        "61-80": 0,
        "81-100": 0
    }
    
    for core in cores:
        if core.quality <= 20:
            quality_brackets["1-20"] += 1
        elif core.quality <= 40:
            quality_brackets["21-40"] += 1
        elif core.quality <= 60:
            quality_brackets["41-60"] += 1
        elif core.quality <= 80:
            quality_brackets["61-80"] += 1
        else:
            quality_brackets["81-100"] += 1
    
    print("\nQuality Distribution:")
    for bracket, count in quality_brackets.items():
        pct = (count / len(cores)) * 100
        print(f"  Q{bracket:7s}: {count:3d} cards ({pct:5.1f}%)")
    
    # God rolls (Tier 9-10, Quality 90+)
    god_rolls = [c for c in cores if c.tier >= 9 and c.quality >= 90]
    print(f"\nGod Rolls (T9-10, Q90+): {len(god_rolls)} ({len(god_rolls)/len(cores)*100:.2f}%)")
    
    # Average stats by size
    print("\nAverage Stats by Size:")
    for size in ["Small", "Medium", "Large", "Massive"]:
        size_cores = [c for c in cores if c.size == size]
        if not size_cores:
            continue
        
        avg_cost = sum(c.cost for c in size_cores) / len(size_cores)
        avg_rpt = sum(c.rpt for c in size_cores) / len(size_cores)
        avg_hp = sum(c.hp for c in size_cores) / len(size_cores)
        avg_links = sum(c.links for c in size_cores) / len(size_cores)
        
        print(f"  {size:7s}: Cost {avg_cost:.1f} | RPT {avg_rpt:.1f} | HP {avg_hp:.1f} | Links {avg_links:.1f}")


# Example usage
if __name__ == "__main__":
    print("StarCore Resource Core Generator")
    print("=" * 50)
    
    # Generate a few example cards
    print("\n>>> EXAMPLE CARDS <<<")
    for i in range(5):
        core = generate_resource_core("Energy")
        print_card(core)
    
    # Generate and analyze a large batch
    print("\n\n>>> GENERATING 1000 CARDS FOR ANALYSIS <<<")
    batch = generate_batch(1000, "Energy")
    analyze_batch(batch)
    
    # Show some extreme examples
    print("\n\n>>> EXTREME EXAMPLES <<<")
    
    # Find best and worst in batch
    best = max(batch, key=lambda c: calculate_weight(c.tier, c.quality))
    worst = min(batch, key=lambda c: calculate_weight(c.tier, c.quality))
    
    print("\nBEST ROLL:")
    print_card(best)
    
    print("\nWORST ROLL:")
    print_card(worst)