# ============================================================
# Logging Configuration
# ============================================================
DEBUG_LOG_ENABLED = False

def log(message):
    if DEBUG_LOG_ENABLED:
        print(f"[ConditioningTimestepSwitch] {message}")

# ============================================================


class ConditioningTimestepSwitch:
    BOUNDARY_EPSILON = 1e-3
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_1": ("CONDITIONING", {"tooltip": "Conditioning active BEFORE the threshold (Start)"}),
                "threshold": ("FLOAT", {"default": 0.1, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "The switching point (0.0 to 1.0)"})
            },
            "optional": {
                "conditioning_2": ("CONDITIONING", {"tooltip": "Conditioning active AFTER the threshold (End). If not provided, nothing happens after the threshold."}),
            }
        }

    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "switch_conditioning"
    CATEGORY = "advanced/conditioning"

    def switch_conditioning(self, conditioning_1, threshold, conditioning_2=None):
        log("=" * 60)
        log("SWITCH_CONDITIONING CALLED")
        
        threshold = round(threshold, 6)
        log(f"Threshold: {threshold}")
        log(f"Epsilon: {self.BOUNDARY_EPSILON}")
        
        log(f"conditioning_1 count: {len(conditioning_1)}")
        log(f"conditioning_2 provided: {conditioning_2 is not None}")
        if conditioning_2 is not None:
            log(f"conditioning_2 count: {len(conditioning_2)}")
        log("=" * 60)
        
        c_out = []

        # Handle edge cases explicitly
        if threshold <= 0:
            # threshold = 0: conditioning_1 should NEVER be active
            # conditioning_2 should be active for the entire range
            cond1_end = 0.0      # [0.0, 0.0) = empty range
            cond2_start = 0.0    # [0.0, 1.0) = full range
            log("EDGE CASE: threshold <= 0")
            log("  conditioning_1 will be SILENCED (empty range)")
            log("  conditioning_2 will cover [0.0, 1.0)")
        elif threshold >= 1:
            # threshold = 1: conditioning_1 should be active for the entire range
            # conditioning_2 should NEVER be active
            cond1_end = 1.0      # [0.0, 1.0) = full range
            cond2_start = 1.0    # [1.0, 1.0) = empty range
            log("EDGE CASE: threshold >= 1")
            log("  conditioning_1 will cover [0.0, 1.0)")
            log("  conditioning_2 will be SILENCED (empty range)")
        else:
            # Normal case: add epsilon to include threshold point in conditioning_1
            cond1_end = threshold + self.BOUNDARY_EPSILON
            cond2_start = threshold + self.BOUNDARY_EPSILON
            log(f"NORMAL CASE: threshold = {threshold}")
            log(f"  conditioning_1: [0.0, {cond1_end})")
            log(f"  conditioning_2: [{cond2_start}, 1.0)")

        def get_time_intersection(params, limit_start, limit_end):
            old_start = params.get("start_percent", 0.0)
            old_end = params.get("end_percent", 1.0)
            
            log(f"  get_time_intersection:")
            log(f"    Input: [{old_start}, {old_end}]")
            log(f"    Limits: [{limit_start}, {limit_end}]")

            new_start = max(old_start, limit_start)
            new_end = min(old_end, limit_end)
            
            log(f"    Result: [{new_start}, {new_end}]")

            if new_start >= new_end:
                log(f"    INVALID -> Silencing")
                return 1.0, 0.0
            
            return new_start, new_end

        # Process Conditioning 1
        log("-" * 40)
        log(f"PROCESSING CONDITIONING_1 (Range: 0.0 -> {cond1_end})")
        log("-" * 40)
        
        for i, t in enumerate(conditioning_1):
            log(f"Processing conditioning_1[{i}]:")
            n = [t[0], t[1].copy()]
            s_val, e_val = get_time_intersection(n[1], 0.0, cond1_end)
            n[1]["start_percent"] = s_val
            n[1]["end_percent"] = e_val
            log(f"  FINAL: [{s_val}, {e_val}]")
            c_out.append(n)

        # Process Conditioning 2
        if conditioning_2 is not None:
            log("-" * 40)
            log(f"PROCESSING CONDITIONING_2 (Range: {cond2_start} -> 1.0)")
            log("-" * 40)
            
            for i, t in enumerate(conditioning_2):
                log(f"Processing conditioning_2[{i}]:")
                n = [t[0], t[1].copy()]
                s_val, e_val = get_time_intersection(n[1], cond2_start, 1.0)
                n[1]["start_percent"] = s_val
                n[1]["end_percent"] = e_val
                log(f"  FINAL: [{s_val}, {e_val}]")
                c_out.append(n)

        # Summary
        log("=" * 60)
        log("FINAL OUTPUT SUMMARY")
        log(f"Total conditionings: {len(c_out)}")
        for i, c in enumerate(c_out):
            start = c[1].get("start_percent", "N/A")
            end = c[1].get("end_percent", "N/A")
            silenced = "(SILENCED)" if start == 1.0 and end == 0.0 else ""
            log(f"  c_out[{i}]: [{start}, {end}] {silenced}")
        log("=" * 60)

        return (c_out, )


NODE_CLASS_MAPPINGS = {
    "ConditioningTimestepSwitch": ConditioningTimestepSwitch
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ConditioningTimestepSwitch": "Conditioning Timestep Switch"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
