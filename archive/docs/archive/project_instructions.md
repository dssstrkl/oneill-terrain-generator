# O'Neill Terrain Generator - Project Instructions

**Project**: O'Neill Terrain Generator - Revolutionary Sharp Boundary System  
**Created**: July 20, 2025  
**Status**: Mandatory instructions for all development sessions

---

## 🚨 CRITICAL PROJECT DIRECTIVES

### **1. CANVAS-FIRST WORKFLOW (MANDATORY)**

**ALWAYS follow this mandatory sequence for terrain generation:**

#### **Canvas Verification First**
- ✅ Check `ONeill_Terrain_Canvas` exists and has painted data
- ✅ Verify canvas dimensions and painted coverage percentage  
- ✅ Never proceed without confirming actual painted areas
- ❌ Never assume terrain should be applied without canvas verification

#### **Use Add-On Workflow Only**
- ✅ Always use built-in operators: `oneill.start_terrain_painting`, `oneill.detect_paint_apply_previews`, `oneill.apply_phase4_complete`
- ✅ Follow UI panel sequence: Steps 1→2→3→4→4.5→5
- ❌ Never manually create displacement modifiers outside the workflow
- ❌ Never bypass the established operator system

#### **Canvas-to-Vertex Sampling Mandatory**
- ✅ All terrain must come from vertex-level canvas sampling
- ✅ Each vertex samples its exact canvas pixel position
- ✅ Unpainted (black) areas must remain flat
- ✅ Painted colors determine biome assignment per vertex
- ❌ Never apply uniform biomes to entire objects

#### **Forbidden Approaches**
- ❌ **Never apply biomes to entire objects uniformly**
- ❌ **Never ignore the painted canvas**
- ❌ **Never manually assign terrain without canvas analysis**
- ❌ **Never use generic preview application**
- ❌ **Never create terrain where canvas is unpainted**

#### **Verification Requirement**
- ✅ Always validate terrain matches painted canvas patterns
- ✅ Check that unpainted areas remain flat
- ✅ Confirm sharp boundaries follow painted edges
- ✅ Verify multi-biome objects where canvas shows multiple colors

**🎯 Key Principle**: *"Paint first, then let the system read the canvas"*

---

## 📁 PROJECT STRUCTURE

### **File Paths (Always Use These)**
- **Documentation**: `/Users/dssstrkl/Documents/Projects/oneill terrain generator/docs`
- **Main Script**: `/Users/dssstrkl/Documents/Projects/oneill terrain generator/oneill_terrain_generator_dev/main_terrain_system.py`
- **Modules**: `/Users/dssstrkl/Documents/Projects/oneill terrain generator/oneill_terrain_generator_dev/modules`

### **Critical Files**
- **Canvas**: `ONeill_Terrain_Canvas` (2816x2048) - Always verify first
- **Flat Objects**: Objects with `oneill_flat` property - Target for terrain
- **Sharp Boundary Modules**: `modules/phase4/` - Core precision system
- **Status Documentation**: `docs/current_status_updated.md` - Current project state

---

## 🎯 SESSION BEHAVIOR DIRECTIVES

### **Code and Blender Connection Policy**
**MANDATORY**: Explain reasoning and goals before writing any code or connecting to Blender unless explicitly asked to write code or connect to Blender in the prompt.

**Process Required**:
1. **Read prompt carefully** - Determine if code/Blender connection is explicitly requested
2. **If NOT explicitly requested**: Explain reasoning and approach first
3. **If explicitly requested**: Proceed directly with implementation
4. **Always use canvas-first workflow** when dealing with terrain

### **Session Management**
**MANDATORY**: Stop working when remaining conversation capacity drops below 15% and:
1. **Update documentation** with current progress and achievements
2. **Write continuation prompt** for the next session with clear next steps
3. **Document any issues or blockers** encountered
4. **Preserve working state** and provide clear handoff instructions

### **Development Approach**
- **Use existing working code** - Never rebuild from scratch
- **Follow established patterns** - Build on proven implementations
- **Test incrementally** - Validate each step before proceeding
- **Document achievements** - Update status files with progress

---

## 🏆 PROJECT CONTEXT

### **Current Achievement Level**
The O'Neill Terrain Generator has achieved **revolutionary sharp boundary precision**:
- ✅ **Pixel-perfect terrain boundaries** following painted canvas
- ✅ **Multi-biome vertex groups** for complex terrain patterns
- ✅ **Canvas-to-3D correspondence** at vertex level
- ✅ **Professional quality** suitable for game development

### **Revolutionary Capabilities**
- **🏝️ Paint islands → Exact 3D islands** where painted
- **🗺️ Paint coastlines → Precise 3D coastlines** following boundaries
- **🏔️ Paint mountains → Sharp peaks** exactly where painted
- **🌊 Paint rivers → Exact 3D valleys** cutting through terrain
- **🎨 Complete artistic freedom** - Paint any pattern, see exact 3D result

### **Core Technical Systems**
- **Canvas Analysis**: 2816x2048 pixel-level precision sampling
- **Vertex-Level Precision**: 90,000+ vertices individually processed
- **Sharp Boundary Displacement**: Vertex-group-constrained modifiers
- **Multi-Biome Support**: Complex terrain patterns on single objects

---

## ⚠️ CRITICAL REMINDERS

### **Never Do This:**
- ❌ Apply terrain without checking canvas first
- ❌ Create uniform biome assignments across objects
- ❌ Bypass the established workflow operators
- ❌ Ignore unpainted (black) canvas areas
- ❌ Write code without explaining reasoning first (unless explicitly requested)

### **Always Do This:**
- ✅ Start with canvas verification and analysis
- ✅ Use vertex-level sampling for all terrain generation
- ✅ Follow the established add-on workflow sequence
- ✅ Preserve flat areas where canvas is unpainted
- ✅ Explain reasoning before coding (unless explicitly requested to code)

### **Session Success Criteria:**
- ✅ Terrain matches painted canvas patterns exactly
- ✅ Unpainted areas remain flat
- ✅ Sharp boundaries follow painted edges precisely
- ✅ Documentation updated with progress
- ✅ Clear continuation prompt provided when needed

---

## 🎯 WORKFLOW VALIDATION CHECKLIST

Before any terrain application, verify:
- [ ] Canvas exists and has painted data
- [ ] Canvas dimensions confirmed (2816x2048)
- [ ] Painted coverage percentage calculated
- [ ] Flat objects identified and ready
- [ ] Using established operators (not manual methods)

After terrain application, verify:
- [ ] Terrain only appears where canvas is painted
- [ ] Unpainted areas remain flat
- [ ] Sharp boundaries follow painted edges
- [ ] Multi-biome objects where canvas shows multiple colors
- [ ] Professional quality displacement visible

---

## 🚀 SUCCESS PRINCIPLE

**"The canvas is the source of truth"** - All terrain generation must originate from and correspond exactly to what is painted on the canvas. The revolutionary sharp boundary system provides pixel-perfect artistic control, and this must never be compromised by shortcuts or manual overrides.

---

**These instructions are MANDATORY for all O'Neill Terrain Generator development sessions.**

**Violation of the canvas-first workflow directive compromises the core revolutionary achievement of the project.**

**🎯 Always remember: Paint first, then let the system read the canvas.**