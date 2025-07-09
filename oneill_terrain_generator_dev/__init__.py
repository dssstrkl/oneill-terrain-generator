# ===================== O'NEILL TERRAIN GENERATOR - MAIN REGISTRATION =====================
"""
O'Neill Terrain Generator - Professional Blender Add-on
Main registration and metadata file for ZIP package distribution.
"""

bl_info = {
    "name": "O'Neill Terrain Generator",
    "author": "dssstrkl",
    "version": (2, 3, 0),  # Incremented for modular release
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > O'Neill Tab",
    "description": "Professional terrain generation for O'Neill cylinder interiors with real-time painting and advanced monitoring",
    "category": "Mesh",
    "doc_url": "https://github.com/your-repo/oneill-terrain-generator",
    "tracker_url": "https://github.com/your-repo/oneill-terrain-generator/issues",
}

import bpy

# ========================= MODULE IMPORTS =========================

# Import main terrain system
from . import main_terrain_system

# Import optional modules with graceful fallback
try:
    from .modules import realtime_canvas_monitor
    REALTIME_MONITORING_AVAILABLE = True
    print("✅ Enhanced real-time monitoring loaded")
except ImportError as e:
    REALTIME_MONITORING_AVAILABLE = False
    print(f"⚠️ Real-time monitoring not available: {e}")

try:
    from .modules import terrain_painting
    ADVANCED_PAINTING_AVAILABLE = True
    print("✅ Advanced terrain painting loaded")
except ImportError:
    ADVANCED_PAINTING_AVAILABLE = False
    print("⚠️ Advanced painting module not available")

try:
    from .modules import biome_geometry_generator
    BIOME_GENERATION_AVAILABLE = True
    print("✅ Biome geometry generation loaded")
except ImportError:
    BIOME_GENERATION_AVAILABLE = False
    print("⚠️ Biome generation module not available")

# ========================= ADDON INFORMATION =========================

class ONeillAddonInfo(bpy.types.PropertyGroup):
    """PropertyGroup for addon information"""
    name: bpy.props.StringProperty(default="O'Neill Terrain Generator")
    version: bpy.props.StringProperty(default="2.3.0")
    author: bpy.props.StringProperty(default="dssstrkl")
    description: bpy.props.StringProperty(default="Professional terrain generation")
    realtime_monitoring: bpy.props.BoolProperty(default=False)
    advanced_painting: bpy.props.BoolProperty(default=False)
    biome_generation: bpy.props.BoolProperty(default=False)

def get_addon_info():
    """Get formatted addon information for UI display (legacy support)"""
    return {
        'name': bl_info['name'],
        'version': f"{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}",
        'author': bl_info['author'],
        'description': bl_info['description'],
        'modules': {
            'realtime_monitoring': REALTIME_MONITORING_AVAILABLE,
            'advanced_painting': ADVANCED_PAINTING_AVAILABLE,
            'biome_generation': BIOME_GENERATION_AVAILABLE,
        }
    }

# ========================= REGISTRATION FUNCTIONS =========================

def cleanup_existing_registrations():
    """Clean up any existing registrations to prevent conflicts"""
    
    # Remove scene properties first
    if hasattr(bpy.types.Scene, 'oneill_addon_info'):
        del bpy.types.Scene.oneill_addon_info
    
    # List of potentially conflicting classes
    conflict_classes = [
        'ONEILL_OT_StartEnhancedMonitoring',
        'EnhancedRealtimeStatistics',
        'ONeillAddonInfo'
    ]
    
    for class_name in conflict_classes:
        if hasattr(bpy.types, class_name):
            try:
                cls = getattr(bpy.types, class_name)
                bpy.utils.unregister_class(cls)
                print(f"🧹 Cleaned up existing class: {class_name}")
            except Exception as e:
                print(f"⚠️ Could not clean up {class_name}: {e}")

def register():
    """Register all addon components with modular architecture"""
    # Clean up any existing registrations first
    cleanup_existing_registrations()
    
    print(f"🚀 Registering {bl_info['name']} v{bl_info['version'][0]}.{bl_info['version'][1]}.{bl_info['version'][2]}")    
    # Register main terrain system
    try:
        main_terrain_system.register()
        print("✅ Main terrain system registered")
    except Exception as e:
        print(f"❌ Failed to register main terrain system: {e}")
        raise
    
    # Register optional modules
    if REALTIME_MONITORING_AVAILABLE:
        try:
            realtime_canvas_monitor.register()
            print("✅ Real-time monitoring registered")
        except Exception as e:
            print(f"⚠️ Real-time monitoring registration failed: {e}")
    
    if ADVANCED_PAINTING_AVAILABLE:
        try:
            terrain_painting.register()
            print("✅ Advanced painting registered")
        except Exception as e:
            print(f"⚠️ Advanced painting registration failed: {e}")
    
    if BIOME_GENERATION_AVAILABLE:
        try:
            biome_geometry_generator.register()
            print("✅ Biome generation registered")
        except Exception as e:
            print(f"⚠️ Biome generation registration failed: {e}")
    
    # Register PropertyGroup first
    bpy.utils.register_class(ONeillAddonInfo)
    
    # Add global addon info to scene
    bpy.types.Scene.oneill_addon_info = bpy.props.PointerProperty(type=ONeillAddonInfo)
    
    # Set the addon info values
    addon_data = get_addon_info()
    # Note: Values will be set when scene is accessed
    
    print(f"🎉 {bl_info['name']} registration complete!")

def unregister():
    """Unregister all addon components"""
    print(f"🔄 Unregistering {bl_info['name']}")
    
    # Remove global addon info FIRST
    if hasattr(bpy.types.Scene, 'oneill_addon_info'):
        del bpy.types.Scene.oneill_addon_info
    
    # Unregister optional modules (reverse order) with better error handling
    if BIOME_GENERATION_AVAILABLE:
        try:
            biome_geometry_generator.unregister()
            print("✅ Biome generation unregistered")
        except Exception as e:
            print(f"⚠️ Biome generation unregister failed: {e}")
    
    if ADVANCED_PAINTING_AVAILABLE:
        try:
            terrain_painting.unregister()
            print("✅ Advanced painting unregistered")
        except Exception as e:
            print(f"⚠️ Advanced painting unregister failed: {e}")
    
    if REALTIME_MONITORING_AVAILABLE:
        try:
            realtime_canvas_monitor.unregister()
            print("✅ Real-time monitoring unregistered")
        except Exception as e:
            print(f"⚠️ Real-time monitoring unregister failed: {e}")
    
    # Unregister main terrain system
    try:
        main_terrain_system.unregister()
        print("✅ Main terrain system unregistered")
    except Exception as e:
        print(f"⚠️ Main system unregister warning: {e}")
    
    # Unregister PropertyGroup LAST
    try:
        bpy.utils.unregister_class(ONeillAddonInfo)
        print("✅ Addon info PropertyGroup unregistered")
    except Exception as e:
        print(f"⚠️ PropertyGroup unregister failed: {e}")
    
    print(f"👋 {bl_info['name']} unregistered successfully")

# ========================= DEVELOPMENT HELPERS =========================

def reload_addon():
    """Helper function for development - reload all modules"""
    import importlib
    
    print("🔄 Reloading O'Neill Terrain Generator modules...")
    
    # Reload main system
    importlib.reload(main_terrain_system)
    
    # Reload optional modules
    if REALTIME_MONITORING_AVAILABLE:
        importlib.reload(realtime_canvas_monitor)
    if ADVANCED_PAINTING_AVAILABLE:
        importlib.reload(terrain_painting)
    if BIOME_GENERATION_AVAILABLE:
        importlib.reload(biome_geometry_generator)
    
    print("✅ Module reload complete")

if __name__ == "__main__":
    register()

# ========================= MODULE METADATA =========================

"""
O'NEILL TERRAIN GENERATOR - MODULAR ARCHITECTURE
=================================================

PACKAGE STRUCTURE:
├── __init__.py                    # This file - main registration
├── main_terrain_system.py         # Core terrain functionality
├── modules/
│   ├── realtime_canvas_monitor.py # Enhanced monitoring system
│   ├── terrain_painting.py        # Advanced painting tools
│   └── biome_geometry_generator.py # Biome generation system
├── assets/
│   └── geometry_nodes/            # Terrain generation assets
└── docs/
    └── README.md                  # User documentation

FEATURES:
✅ Modular architecture with graceful fallbacks
✅ Professional ZIP package distribution
✅ Development-friendly with reload helpers
✅ Comprehensive error handling and logging
✅ Version tracking and addon information
✅ Compatible with Blender Market standards

DEVELOPMENT WORKFLOW:
1. Develop modules independently
2. Test with reload_addon() function
3. Package as ZIP for distribution
4. Maintain modular structure for updates

This architecture ensures the addon can grow with additional modules
while maintaining compatibility and professional standards.
"""