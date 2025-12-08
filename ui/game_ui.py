import imgui
from OpenGL.GLU import gluProject
import numpy as np
from game_objects.components.ai_component import CatAIComponent

def render_ui(window_width, window_height, scene_manager=None, world_setting=None, renderer=None, selected_object=None):
    # Fixed Layout: Right side, 250px width, full height
    panel_width = 250
    imgui.set_next_window_position(window_width - panel_width, 0)
    imgui.set_next_window_size(panel_width, window_height)
    
    # "Main" window
    flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_COLLAPSE
    
    imgui.begin("Main", flags=flags)
    
    if imgui.collapsing_header("Performance", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
        imgui.text(f"FPS: {imgui.get_io().framerate:.1f}")
        if scene_manager:
            imgui.text(f"AABB Checks: {scene_manager.aabb_checks} / {scene_manager.potential_checks}")

    reset_requested = False
    if scene_manager:
        label = "Resume" if scene_manager.is_paused else "Pause"
        if imgui.button(label, width=imgui.get_content_region_available_width()):
            scene_manager.is_paused = not scene_manager.is_paused
            
        if imgui.button("Reset World", width=imgui.get_content_region_available_width()):
            reset_requested = True
            
        # Cat stats
        cat_count = 0
        cats_satiety_sum = 0
        first_cat = None
        
        hamster_adults = 0
        hamster_babies = 0
        
        # Single loop for stats
        for obj in scene_manager.objects:
            if "Cat" in obj.name:
                cat_count += 1
                if not first_cat:
                    first_cat = obj
                
                # Get satiety for avg (expensive? no)
                from game_objects.components.ai_component import CatAIComponent
                c_ai = obj.get_component(CatAIComponent)
                if c_ai:
                    cats_satiety_sum += c_ai.satiety
            
            if "Hamster" in obj.name:
                from game_objects.components.ai_component import HamsterAIComponent
                comp = obj.get_component(HamsterAIComponent)
                if comp:
                    if comp.is_adult:
                        hamster_adults += 1
                    else:
                        hamster_babies += 1
        
        if cat_count > 0:
            avg_satiety = cats_satiety_sum / cat_count
            imgui.text(f"Avg Cat Satiety: {avg_satiety:.1f}")
        
        imgui.separator()
        imgui.text("Population")
        imgui.text(f"Cats: {cat_count}")
        imgui.text(f"Adult Hamsters: {hamster_adults}")
        imgui.text(f"Baby Hamsters: {hamster_babies}")
        imgui.separator()
            
    if world_setting:
        if imgui.collapsing_header("World Settings", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            # Field Size
            fs = world_setting.field_size
            imgui.text(f"Field: {fs[0]}x{fs[1]}")
            
            # Time Scale
            changed_ts, val_ts = imgui.input_float("Time Scale", world_setting.time_scale)
            if changed_ts:
                # Clamp to reasonable values to prevent physics explosion
                if val_ts < 0.0: val_ts = 0.0 
                if val_ts > 10.0: val_ts = 10.0
                world_setting.time_scale = val_ts
            
            # Move Speed
            # changed, val = imgui.slider_float("Move Speed", world_setting.move_speed, 0.1, 10.0)
            # if changed:
            #     world_setting.move_speed = val

            # Cat Settings
            imgui.text("Cat Settings")
            changed_c, val_c = imgui.slider_float("Speed##Cat", world_setting.cat_setting.move_speed, 0.1, 10.0)
            if changed_c:
                world_setting.cat_setting.move_speed = val_c
            changed_cmd, val_cmd = imgui.slider_float("Move Time##Cat", world_setting.cat_setting.move_duration, 0.1, 10.0)
            if changed_cmd:
                world_setting.cat_setting.move_duration = val_cmd
            changed_crd, val_crd = imgui.slider_float("Rest Time##Cat", world_setting.cat_setting.rest_duration, 0.1, 10.0)
            if changed_crd:
                world_setting.cat_setting.rest_duration = val_crd
            changed_chr, val_chr = imgui.slider_float("Hunger Rate##Cat", world_setting.cat_setting.hunger_rate, 0.1, 20.0)
            if changed_chr:
                world_setting.cat_setting.hunger_rate = val_chr
            
            changed_cc, val_cc = imgui.input_int("Count##Cat", world_setting.cat_count)
            if changed_cc:
                if val_cc < 0: val_cc = 0
                if val_cc > 50: val_cc = 50
                world_setting.cat_count = val_cc

            imgui.separator()

            # Hamster Settings
            imgui.text("Hamster Settings")
            changed_h, val_h = imgui.slider_float("Speed##Hamster", world_setting.hamster_setting.move_speed, 0.1, 10.0)
            if changed_h:
                world_setting.hamster_setting.move_speed = val_h
            changed_hmd, val_hmd = imgui.slider_float("Move Time##Hamster", world_setting.hamster_setting.move_duration, 0.1, 10.0)
            if changed_hmd:
                world_setting.hamster_setting.move_duration = val_hmd
            changed_hrd, val_hrd = imgui.slider_float("Rest Time##Hamster", world_setting.hamster_setting.rest_duration, 0.1, 10.0)
            if changed_hrd:
                world_setting.hamster_setting.rest_duration = val_hrd
            
            changed_hdr, val_hdr = imgui.slider_float("Detect Radius##Hamster", world_setting.hamster_setting.detection_radius, 0.5, 5.0)
            if changed_hdr:
                world_setting.hamster_setting.detection_radius = val_hdr

            changed_hmr, val_hmr = imgui.slider_float("Mating Range##Hamster", world_setting.hamster_setting.mating_search_range, 1.0, 10.0)
            if changed_hmr:
                world_setting.hamster_setting.mating_search_range = val_hmr
            
            changed_hc, val_hc = imgui.input_int("Count##Hamster", world_setting.hamster_count)
            if changed_hc:
                # Clamp value
                if val_hc < 1: val_hc = 1
                if val_hc > 100: val_hc = 100
                world_setting.hamster_count = val_hc
                
        if renderer:
            _, renderer.show_aabb = imgui.checkbox("Show AABB (Red)", renderer.show_aabb)
            _, renderer.show_sphere = imgui.checkbox("Show Sphere (Green)", renderer.show_sphere)
        
    imgui.end()

    # Inspector Window (Top Left)
    if selected_object:
        imgui.set_next_window_position(10, 10, imgui.ONCE)
        imgui.set_next_window_size(200, 300, imgui.ONCE)
        imgui.begin("Inspector", flags=imgui.WINDOW_NO_COLLAPSE)
        
        imgui.text(f"Name: {selected_object.name}")
        imgui.separator()
        
        # Icon
        if hasattr(selected_object, 'material') and selected_object.material and selected_object.material.texture_id:
            # Display image (texture_id, width, height)
            # Use fixed size for icon
            imgui.image(selected_object.material.texture_id, 64, 64, uv0=(0, 1), uv1=(1, 0))
            imgui.separator()
            
        # Stats
        # Try to find AI Component
        from game_objects.components.ai_component import BaseAIComponent, CatAIComponent, HamsterAIComponent
        
        # We need to access components. Object doesn't expose list easily but has get_component
        # Let's try casting
        ai = selected_object.get_component(BaseAIComponent)
        if ai:
            imgui.text("AI Stats:")
            imgui.text(f"State: {'Moving' if ai.is_moving else 'Resting'}")
            imgui.text(f"Move Speed: {ai.move_speed:.1f}")
            imgui.text(f"Move Duration: {ai.move_duration:.1f}")
            imgui.text(f"Rest Duration: {ai.rest_duration:.1f}")
            
            if isinstance(ai, CatAIComponent):
                imgui.text(f"Satiety: {ai.satiety:.1f}")
                imgui.text(f"Hunger Rate: {ai.hunger_rate:.1f}")
                
            if isinstance(ai, HamsterAIComponent):
                imgui.text(f"Gender: {'Male' if ai.gender == 0 else 'Female'}")
                imgui.text(f"Age: {'Adult' if ai.is_adult else 'Baby'}")
                if not ai.is_adult:
                    imgui.text(f"Growth: {ai.growth_timer:.1f}/10.0")
                imgui.text(f"Repro Cooldown: {ai.repro_timer:.1f}")
                imgui.text(f"Detect Radius: {ai.detection_radius:.1f}")
                imgui.text(f"Mating Range: {ai.repro_range:.1f}")

        imgui.end()

    # Log History Window (Bottom)
    log_height = 150
    imgui.set_next_window_position(0, window_height - log_height)
    imgui.set_next_window_size(window_width - panel_width, log_height)
    
    imgui.begin("Log History", flags=flags)
    if scene_manager and scene_manager.logs:
        # Show last 10 logs visible or scroll
        for log in scene_manager.logs[-50:]: # Simple display
             imgui.text(log)
    imgui.end()
    
    return reset_requested

def render_status_bars(scene_manager, view_matrix, proj_matrix, viewport):
    if not scene_manager:
        return
        
    draw_list = imgui.get_background_draw_list()
    
    # Pre-transpose matrices for glu (as done in main/world selection logic)
    # View/Proj from world are already "Row-Linked"? main.py passes `current_view_matrix` which is Transposed?
    # In world.py select_object, we did: `view_d = view_matrix.transpose()`
    # We should do the same here if main passes the same matrix.
    # We will assume passed matrices are the global ones from main.
    
    try:
        view_d = np.ascontiguousarray(view_matrix.transpose(), dtype=np.float64)
        proj_d = np.ascontiguousarray(proj_matrix.transpose(), dtype=np.float64)
    except:
        return

    for obj in scene_manager.objects:
        if "Cat" in obj.name:
            # Check Satiety
            ai = obj.get_component(CatAIComponent)
            if ai:
                satiety = ai.satiety
                ratio = satiety / 100.0
                
                # Position above head (Cat is at Y=2.0 usually? No, moved to random)
                # Cat Scale 0.5. Top is roughly +0.25 Y?
                # Actually Cat is a Quad on Z plane?
                # "cat.transform.position.SetY(2.0)" in Reset WAS old code. New code randomizes.
                # It's on XY plane. Z=-0.1 for Floor. Objects at 0?
                # World.py: `cat.transform.scale.Set(0.5)`. Quad is unit size centered.
                # So visual top is Y + 0.25 (approx).
                # Let's add offset Y + 0.4
                
                wx = obj.transform.position.X()
                wy = obj.transform.position.Y() + 0.4
                wz = obj.transform.position.Z()
                
                # Project
                coords = gluProject(wx, wy, wz, view_d, proj_d, viewport)
                if coords:
                    sx, sy, sz = coords
                    # Invert Y for ImGui
                    sy = viewport[3] - sy
                    
                    # Draw Bar
                    w = 40
                    h = 6
                    x = sx - w/2
                    y = sy
                    
                    # Background (Black, 2px larger)
                    padding = 2
                    draw_list.add_rect_filled(x - padding, y - padding, x + w + padding, y + h + padding, imgui.get_color_u32_rgba(0, 0, 0, 1))
                    
                    # Determine Color
                    if ratio > 0.75:
                        col = imgui.get_color_u32_rgba(0, 1, 0, 1) # Green
                    elif ratio > 0.30:
                        col = imgui.get_color_u32_rgba(1, 1, 0, 1) # Yellow
                    else:
                        col = imgui.get_color_u32_rgba(1, 0, 0, 1) # Red

                    # Foreground
                    fw = w * ratio
                    draw_list.add_rect_filled(x, y, x + fw, y + h, col)
