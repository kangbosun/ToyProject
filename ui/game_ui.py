import imgui

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
            
        # Cat Satiety Status
        cat = None
        for obj in scene_manager.objects:
            if "Cat" in obj.name:
                cat = obj
                break
        
        if cat and hasattr(cat, "get_component"):
            from game_objects.components.ai_component import CatAIComponent
            cat_ai = cat.get_component(CatAIComponent)
            if cat_ai:
                imgui.text(f"Cat Satiety: {cat_ai.satiety:.1f}")
            
    if world_setting:
        if imgui.collapsing_header("World Settings", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            # Field Size
            fs = world_setting.field_size
            imgui.text(f"Field: {fs[0]}x{fs[1]}")
            
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
                imgui.text(f"Detect Radius: {ai.detection_radius:.1f}")

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
