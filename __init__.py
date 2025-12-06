class ConditioningTimestepSwitch:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "conditioning_1": ("CONDITIONING", {"tooltip": "Conditioning active BEFORE the threshold (Start)"}),
                "threshold": ("FLOAT", {"default": 0.5, "min": 0.0, "max": 1.0, "step": 0.01, "tooltip": "The switching point (0.0 to 1.0)"})
            },
            "optional": {
                "conditioning_2": ("CONDITIONING", {"tooltip": "Conditioning active AFTER the threshold (End). If not provided, nothing happens after the threshold."}),
            }
        }
    
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "switch_conditioning"
    CATEGORY = "advanced/conditioning"

    def switch_conditioning(self, conditioning_1, threshold, conditioning_2=None):
        c_out = []

        # Helper function to calculate time intersection
        def get_time_intersection(params, limit_start, limit_end):
            # Get existing times (default to full range 0.0-1.0 if missing)
            old_start = params.get("start_percent", 0.0)
            old_end = params.get("end_percent", 1.0)

            # Calculate intersection
            # Start is the MAX of the two starts
            new_start = max(old_start, limit_start)
            # End is the MIN of the two ends
            new_end = min(old_end, limit_end)

            # If the range is invalid (Start >= End), the conditioning should be silenced.
            # We use the standard fix: set start to 1.0
            if new_start >= new_end:
                return 1.0, 0.0
            
            return new_start, new_end

        # ----------------------------------------------------------------
        # 1. Process Conditioning 1
        # Allowed Range: 0.0 -> Threshold
        # ----------------------------------------------------------------
        for t in conditioning_1:
            n = [t[0], t[1].copy()]
            
            # Calculate the intersection between the prompt's own timing and our threshold
            s_val, e_val = get_time_intersection(n[1], 0.0, threshold)
            
            n[1]["start_percent"] = s_val
            n[1]["end_percent"] = e_val
            
            c_out.append(n)

        # ----------------------------------------------------------------
        # 2. Process Conditioning 2 (Optional)
        # Allowed Range: Threshold -> 1.0
        # ----------------------------------------------------------------
        if conditioning_2 is not None:
            for t in conditioning_2:
                n = [t[0], t[1].copy()]
                
                # Calculate the intersection between the prompt's own timing and our threshold
                s_val, e_val = get_time_intersection(n[1], threshold, 1.0)
                
                n[1]["start_percent"] = s_val
                n[1]["end_percent"] = e_val
                
                c_out.append(n)

        return (c_out, )

# Mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "ConditioningTimestepSwitch": ConditioningTimestepSwitch
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ConditioningTimestepSwitch": "Conditioning Timestep Switch"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']