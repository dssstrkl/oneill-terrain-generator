"""
O'Neill Terrain Generator - Phase 4: Vertex-Level Precision Module
Exports all Phase 4 components for main system integration
"""

# Import Phase 4 core systems
from .vertex_level_precision import (
    VertexLevelPrecisionSystem,
    SeamlessTransitionSystem, 
    Phase4Integration
)

# Import Phase 4 operators
from .vertex_precision_operators import (
    ONEILL_OT_ApplyPhase4Complete,
    ONEILL_OT_ValidatePhase4,
    ONEILL_OT_DebugPhase4Coordinates,
    ONEILL_OT_ClearPhase4Terrain
)

# Import seamless transitions (existing module)
try:
    from .seamless_transitions import *
except ImportError:
    print("⚠️ Seamless transitions module not available")

# Export all Phase 4 components
__all__ = [
    # Core systems
    'VertexLevelPrecisionSystem',
    'SeamlessTransitionSystem',
    'Phase4Integration',
    
    # Operators
    'ONEILL_OT_ApplyPhase4Complete',
    'ONEILL_OT_ValidatePhase4', 
    'ONEILL_OT_DebugPhase4Coordinates',
    'ONEILL_OT_ClearPhase4Terrain'
]

# Phase 4 registration helper
def get_phase4_classes():
    """Return all Phase 4 classes that need to be registered"""
    return [
        ONEILL_OT_ApplyPhase4Complete,
        ONEILL_OT_ValidatePhase4,
        ONEILL_OT_DebugPhase4Coordinates,
        ONEILL_OT_ClearPhase4Terrain
    ]

def register_phase4():
    """Register all Phase 4 components"""
    import bpy
    
    for cls in get_phase4_classes():
        try:
            bpy.utils.register_class(cls)
            print(f"✅ Registered {cls.__name__}")
        except Exception as e:
            print(f"❌ Failed to register {cls.__name__}: {e}")

def unregister_phase4():
    """Unregister all Phase 4 components"""
    import bpy
    
    for cls in reversed(get_phase4_classes()):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print(f"⚠️ Failed to unregister {cls.__name__}: {e}")

print("🚀 Phase 4 Vertex-Level Precision Module Loaded")
