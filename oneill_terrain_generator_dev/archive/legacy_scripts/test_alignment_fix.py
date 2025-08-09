"""
Test script for O'Neill terrain generator alignment fix
Run this in Blender to validate the alignment bug fix
"""

import bpy
import bmesh
import mathutils

def create_test_cylinders():
    """Create test cylinders with problematic transforms"""
    
    # Clear existing mesh objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)
    
    # Create 3 test cylinders
    test_cylinders = []
    
    for i in range(3):
        # Create cylinder
        bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(i*6-6, 0, 0))
        cylinder = bpy.context.active_object
        cylinder.name = f"TestCylinder_{i+1:03d}"
        
        # Apply problematic transforms (as described in the bug report)
        cylinder.rotation_euler[1] = 1.5708  # 90 degrees Y rotation
        cylinder.scale = (3.0, 3.0, 1.0)     # 3x scale in X and Y
        
        # Apply transforms to mesh
        bpy.context.view_layer.objects.active = cylinder
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        
        test_cylinders.append(cylinder)
        print(f"✅ Created {cylinder.name} at location {cylinder.location}")
    
    # Select all test cylinders
    bpy.ops.object.select_all(action='DESELECT')
    for cylinder in test_cylinders:
        cylinder.select_set(True)
    
    print(f"\n=== CREATED {len(test_cylinders)} TEST CYLINDERS ===")
    return test_cylinders

def measure_gaps(objects):
    """Measure gaps between objects using true bounds"""
    gaps = []
    
    def get_true_bounds(obj):
        """Calculate true world bounds"""
        mesh = obj.data
        world_coords = [obj.matrix_world @ v.co for v in mesh.vertices]
        x_coords = [co.x for co in world_coords]
        return min(x_coords), max(x_coords)
    
    # Sort objects by X position
    sorted_objects = sorted(objects, key=lambda obj: obj.location.x)
    
    print("\n=== MEASURING OBJECT BOUNDS ===")
    for i, obj in enumerate(sorted_objects):
        min_x, max_x = get_true_bounds(obj)
        width = max_x - min_x
        print(f"{obj.name}: center={obj.location.x:.3f}, bounds={min_x:.3f} to {max_x:.3f}, width={width:.3f}")
        
        if i > 0:
            prev_min, prev_max = get_true_bounds(sorted_objects[i-1])
            gap = min_x - prev_max
            gaps.append(gap)
            print(f"  Gap from previous: {gap:.6f}")
    
    return gaps

def test_alignment_fix():
    """Complete test of the alignment fix"""
    
    print("="*60)
    print("TESTING O'NEILL TERRAIN GENERATOR ALIGNMENT FIX")
    print("="*60)
    
    # Step 1: Create test objects
    test_cylinders = create_test_cylinders()
    
    # Step 2: Measure initial gaps
    print("\n=== BEFORE ALIGNMENT ===")
    initial_gaps = measure_gaps(test_cylinders)
    
    # Step 3: Try to run the alignment operator
    try:
        # First ensure the oneill addon is loaded
        try:
            # Try to access oneill properties
            props = bpy.context.scene.oneill_props
            print("✅ O'Neill addon detected")
        except AttributeError:
            print("⚠️ O'Neill addon not loaded - loading from file...")
            
            # Load the main script
            script_path = "/Users/dssstrkl/Documents/Projects/oneill terrain generator/oneill_terrain_generator_dev/main_terrain_system.py"
            exec(open(script_path).read())
            print("✅ O'Neill script loaded")
        
        # Set alignment axis to X
        bpy.context.scene.oneill_props.alignment_axis = 'X'
        
        # Run the alignment operator
        print("\n=== RUNNING ALIGNMENT OPERATOR ===")
        result = bpy.ops.oneill.align_cylinders()
        
        if result == {'FINISHED'}:
            print("✅ Alignment operator completed successfully")
            
            # Step 4: Measure gaps after alignment
            print("\n=== AFTER ALIGNMENT ===")
            final_gaps = measure_gaps(test_cylinders)
            
            # Step 5: Analyze results
            print("\n=== RESULTS ANALYSIS ===")
            print(f"Initial gaps: {[f'{gap:.6f}' for gap in initial_gaps]}")
            print(f"Final gaps: {[f'{gap:.6f}' for gap in final_gaps]}")
            
            # Check if gaps are close to zero (contiguous)
            max_gap = max(abs(gap) for gap in final_gaps)
            if max_gap < 0.001:  # Less than 1mm gap
                print("✅ SUCCESS: Objects are contiguous (gaps < 0.001)")
                print("✅ ALIGNMENT FIX WORKING CORRECTLY")
            else:
                print(f"❌ FAILURE: Objects still have gaps (max gap: {max_gap:.6f})")
                print("❌ ALIGNMENT FIX NEEDS MORE WORK")
                
        else:
            print(f"❌ Alignment operator failed: {result}")
            
    except Exception as e:
        print(f"❌ Error testing alignment: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    # Run the test
    test_alignment_fix()
