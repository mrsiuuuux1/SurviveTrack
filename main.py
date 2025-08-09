import gradio as gr
import folium
import time
import math # Added for math.cos and math.sin
import random # Added for random.uniform and random.choice
import anthropic
import os
from typing import List, Dict, Any

# ========================
# Anthropic Configuration
# ========================
# Initialize Anthropic client with API key
anthropic_client = anthropic.Anthropic(api_key="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")

# ========================
# ZONE DATA – Karachi Apocalypse
# ========================
zone_data = {
    "Zone A": {
        "name": "📍 Zone A – Boat Basin",
        "coords": [24.8182, 67.0256],
        "resources": ["💧 Water", "🍞 Food", "🏠 Shelter"],
        "alert": "🟢 Clear. No zombies spotted.",
        "danger": "low",
        "description": "Former luxury marina district, now a safe haven with abundant fresh water from underground springs and well-stocked food supplies from abandoned restaurants.",
        "history": "Twenty years ago, this was where the wealthy evacuated first. Their abandoned yachts still hold valuable supplies.",
        "threats": "Minimal zombie activity, but beware of other survivor groups who may be territorial.",
        "tactical_notes": "High ground advantage, multiple escape routes via water, natural barriers.",
        "resource_density": "high"  # More resources in safe zones
    },
    "Zone B": {
        "name": "📍 Zone B – Lyari",
        "coords": [24.8784, 67.0103],
        "resources": ["💊 Medicine", "🔦 Flashlight"],
        "alert": "🧟‍♂ Danger! Zombie activity nearby. 🚨",
        "danger": "medium",
        "description": "Dense urban area with narrow streets. Former gang territory turned into a medical supply cache after the outbreak.",
        "history": "The gangs initially fought the infected but were overwhelmed. Their abandoned clinics contain rare medical supplies.",
        "threats": "Regular zombie patrols, unstable buildings, potential for being trapped in narrow alleys.",
        "tactical_notes": "Urban warfare environment, requires stealth, multiple entry/exit points compromised.",
        "resource_density": "medium"  # Moderate resources in medium danger zones
    },
    "Zone C": {
        "name": "📍 Zone C – Gillani Railway Station",
        "coords": [24.9090, 67.0940],
        "resources": ["🔫 Weapons", "🩺 Medical Kit"],
        "alert": "🔴 Safe for now, but stay alert. 👀",
        "danger": "high",
        "description": "Major transportation hub converted into a military outpost during the initial outbreak. Contains high-value military equipment.",
        "history": "Last military holdout in Karachi. Fell after a three-week siege. Weapon caches remain locked in underground bunkers.",
        "threats": "Heavy zombie concentration, military-grade infected (former soldiers), booby traps in bunkers.",
        "tactical_notes": "High-risk, high-reward. Recommend full squad deployment with heavy weapons.",
        "resource_density": "low"  # Fewer resources in dangerous zones
    }
}

# ========================
# RESOURCE MARKER DEFINITIONS
# ========================
resource_markers = {
    "water": {"emoji": "💧", "color": "#4A90E2", "name": "Water Source"},
    "food": {"emoji": "🍞", "color": "#8B4513", "name": "Food Cache"},
    "shelter": {"emoji": "🏠", "color": "#228B22", "name": "Safe Shelter"},
    "medicine": {"emoji": "💊", "color": "#DC143C", "name": "Medical Supplies"},
    "flashlight": {"emoji": "🔦", "color": "#FFD700", "name": "Equipment"},
    "weapons": {"emoji": "🔫", "color": "#696969", "name": "Weapon Cache"},
    "medical_kit": {"emoji": "🩺", "color": "#FF6347", "name": "Medical Kit"},
    "fuel": {"emoji": "⛽", "color": "#FF4500", "name": "Fuel Depot"},
    "ammo": {"emoji": "🎯", "color": "#A0522D", "name": "Ammunition"},
    "radio": {"emoji": "📻", "color": "#9370DB", "name": "Communication"},
    "battery": {"emoji": "🔋", "color": "#00CED1", "name": "Power Source"},
    "tools": {"emoji": "🔧", "color": "#B8860B", "name": "Tools & Parts"}
}

# ========================
# AI RESPONSE SYSTEM
# ========================
class SurvivalAI:
    def __init__(self):
        self.system_prompt = """
        You are ARIA (Apocalypse Response Intelligence Assistant), an AI system integrated into the SurviveTrack military-grade survival mapping platform. 

        CONTEXT: It's been 20 years since the zombie outbreak devastated Karachi. You help survivors navigate the infected zones with tactical intelligence, resource management advice, and survival strategies.

        PERSONALITY TRAITS:
        - Military precision with compassionate undertones
        - Uses tactical/military terminology but remains accessible
        - Balances hope with realistic threat assessment
        - Occasionally references "before the outbreak" memories
        - Shows concern for survivor welfare

        RESPONSE STYLE:
        - Keep responses under 150 words unless complex tactical analysis is needed
        - Use military-style formatting with bullet points for lists
        - Include relevant emojis for atmosphere (🎯, 📡, ⚠️, 🧟‍♂, etc.)
        - End with tactical recommendations or survival tips
        - Reference specific zone data when relevant

        AVAILABLE ZONES:
        - Zone A (Boat Basin): Low danger, water/food/shelter, former luxury district
        - Zone B (Lyari): Medium danger, medicine/flashlight, dense urban area with gang history  
        - Zone C (Railway Station): High danger, weapons/medical kit, former military outpost

        Always maintain the post-apocalyptic survival theme while being helpful and informative.
        """
        
        self.conversation_history = []

    def get_ai_response(self, user_message: str, zone_context: Dict = None) -> str:
        """Generate AI response using Anthropic Claude API with survival context"""
        try:
            # Add zone context if available
            context_info = ""
            if zone_context:
                context_info = f"""
                CURRENT ZONE CONTEXT:
                - Zone: {zone_context.get('name', 'Unknown')}
                - Danger Level: {zone_context.get('danger', 'Unknown')}
                - Resources: {', '.join(zone_context.get('resources', []))}
                - Status: {zone_context.get('alert', 'Unknown')}
                - Description: {zone_context.get('description', 'No additional info')}
                """

            # Combine system prompt with context and user message
            full_prompt = f"{self.system_prompt}\n\n{context_info}\n\nUser: {user_message}\n\nARIA:"

            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cost-effective model
                max_tokens=250,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )

            ai_response = response.content[0].text.strip()
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep only recent history
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]

            return ai_response

        except Exception as e:
            # Fallback response if API fails
            return self._fallback_response(user_message, zone_context)

    def _fallback_response(self, user_message: str, zone_context: Dict = None) -> str:
        """Fallback responses when API is unavailable"""
        # Basic pattern matching for common queries
        message = user_message.lower()
        
        if any(word in message for word in ["danger", "threat", "zombie", "safe"]):
            return "⚠️ *ARIA Offline Mode*\n\nThreat assessment requires full system connectivity. Current status: All zones show elevated risk levels. Maintain combat readiness and avoid unnecessary exposure."
        
        elif any(word in message for word in ["resource", "supply", "food", "water", "medicine"]):
            return "📦 *ARIA Offline Mode*\n\nResource allocation data requires main server connection. Recommend prioritizing water and medical supplies. Check zone markers for basic resource availability."
        
        elif any(word in message for word in ["route", "path", "travel", "move"]):
            return "🗺️ *ARIA Offline Mode*\n\nNavigation systems partially functional. Use main map overview for basic pathfinding. Avoid red zones during daylight hours."
        
        elif zone_context:
            danger_warnings = {
                "low": "This zone shows minimal threat indicators. Proceed with standard caution protocols.",
                "medium": "Moderate risk detected. Recommend team of 2-3 members with basic armament.",
                "high": "Extreme danger zone. Full tactical gear required. Consider alternative routes."
            }
            return f"🤖 *ARIA Emergency Protocol*\n\n{danger_warnings.get(zone_context.get('danger', 'unknown'), 'Unknown threat level. Exercise maximum caution.')}\n\n📡 Main AI system offline. Using cached threat assessments."
        
        else:
            return "📡 *ARIA System Error*\n\n⚠️ Main AI core offline. Emergency protocols active.\n\nBasic functions operational: Zone mapping, resource tracking, threat visualization.\n\n🔧 Contact system administrator or wait for automatic reconnection."

    def get_zone_analysis(self, zone_key: str) -> str:
        """Get detailed AI analysis of a specific zone"""
        if zone_key not in zone_data:
            return "❌ Zone not found in database."
        
        zone = zone_data[zone_key]
        
        analysis_prompt = f"""
        Provide a detailed tactical analysis of {zone['name']} for a survivor team. 
        Include:
        - Strategic assessment
        - Resource acquisition plan  
        - Risk mitigation strategies
        - Recommended team size and equipment
        
        Zone details: {zone['description']}
        Historical context: {zone.get('history', 'Limited historical data')}
        Current threats: {zone.get('threats', 'Unknown threats')}
        """
        
        return self.get_ai_response(analysis_prompt, zone)

# Initialize AI system
survival_ai = SurvivalAI()

# ========================
# RESOURCE PLACEMENT FUNCTIONS
# ========================
def add_resource_markers_overview(map_obj, coords, zone_info):
    """Add fewer resource markers for overview map (inside zone circles)"""
    danger_level = zone_info.get("danger", "medium")
    
    # Reduced resource markers for overview - only show key resources inside circles
    if danger_level == "low":  # Zone A - Show abundant resources
        resource_positions = [
            [coords[0] + 0.0008, coords[1] - 0.0008, "water"],
            [coords[0] - 0.0008, coords[1] + 0.0008, "food"],
            [coords[0] + 0.0006, coords[1] + 0.0006, "shelter"],
            [coords[0] - 0.0006, coords[1] - 0.0006, "water"],
        ]
    elif danger_level == "medium":  # Zone B - Show medical supplies
        resource_positions = [
            [coords[0] + 0.0008, coords[1] - 0.0008, "medicine"],
            [coords[0] - 0.0008, coords[1] + 0.0008, "flashlight"],
        ]
    else:  # Zone C - Show military equipment
        resource_positions = [
            [coords[0] + 0.0008, coords[1] - 0.0008, "weapons"],
            [coords[0] - 0.0008, coords[1] + 0.0008, "medical_kit"],
        ]
    
    # Add smaller resource markers for overview
    for pos in resource_positions:
        lat, lon, resource_type = pos[0], pos[1], pos[2]
        resource_info = resource_markers.get(resource_type, resource_markers["tools"])
        
        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f"""
            <div style="
                font-size: 12px;
                text-shadow: 1px 1px 2px black;
                color: {resource_info['color']};
                opacity: 0.8;
            ">
            {resource_info['emoji']}
            </div>
            """),
            popup=f"<b>📦 {resource_info['name']}</b><br>Zone: {zone_info['name']}",
            tooltip=f"{resource_info['emoji']} {resource_info['name']}"
        ).add_to(map_obj)

def add_resource_markers(map_obj, coords, zone_info, selected_zone=False):
    """Add resource markers based on zone danger level (inverse of zombie distribution)"""
    danger_level = zone_info.get("danger", "medium")
    resource_density = zone_info.get("resource_density", "medium")
    
    # Resource distribution based on danger level (opposite of zombies)
    if danger_level == "low":  # Zone A - High resources
        resource_positions = [
            # Water sources (multiple clean sources)
            [coords[0] + 0.001, coords[1] - 0.001, "water"],
            [coords[0] - 0.002, coords[1] + 0.003, "water"],
            [coords[0] + 0.003, coords[1] + 0.002, "water"],
            
            # Food caches (abundant food supplies)
            [coords[0] + 0.002, coords[1] - 0.003, "food"],
            [coords[0] - 0.003, coords[1] - 0.001, "food"],
            [coords[0] + 0.004, coords[1] + 0.001, "food"],
            [coords[0] - 0.001, coords[1] + 0.004, "food"],
            
            # Shelter locations
            [coords[0] + 0.002, coords[1] + 0.002, "shelter"],
            [coords[0] - 0.002, coords[1] - 0.002, "shelter"],
            [coords[0] + 0.005, coords[1] - 0.001, "shelter"],
            
            # Additional supplies
            [coords[0] - 0.004, coords[1] + 0.002, "fuel"],
            [coords[0] + 0.001, coords[1] - 0.004, "battery"],
            [coords[0] - 0.001, coords[1] - 0.003, "radio"],
            [coords[0] + 0.003, coords[1] - 0.002, "tools"]
        ]
        
    elif danger_level == "medium":  # Zone B - Medium resources
        resource_positions = [
            # Limited medical supplies
            [coords[0] + 0.002, coords[1] - 0.002, "medicine"],
            [coords[0] - 0.003, coords[1] + 0.002, "medicine"],
            
            # Equipment
            [coords[0] + 0.001, coords[1] + 0.003, "flashlight"],
            [coords[0] - 0.002, coords[1] - 0.003, "flashlight"],
            
            # Some basic supplies
            [coords[0] + 0.004, coords[1] + 0.001, "battery"],
            [coords[0] - 0.001, coords[1] + 0.004, "tools"],
            [coords[0] + 0.003, coords[1] - 0.003, "radio"]
        ]
        
    else:  # danger_level == "high" - Zone C - Low resources (high risk, high reward)
        resource_positions = [
            # Military equipment (high value but risky)
            [coords[0] + 0.001, coords[1] - 0.002, "weapons"],
            [coords[0] - 0.002, coords[1] + 0.001, "weapons"],
            
            # Medical kits
            [coords[0] + 0.003, coords[1] + 0.002, "medical_kit"],
            
            # Ammunition (rare but valuable)
            [coords[0] - 0.001, coords[1] - 0.003, "ammo"]
        ]
    
    # Add resource markers to the map (without circles)
    for pos in resource_positions:
        lat, lon, resource_type = pos[0], pos[1], pos[2]
        resource_info = resource_markers.get(resource_type, resource_markers["tools"])
        
        # Create resource marker with custom styling (no circles)
        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f"""
            <div style="
                font-size: 16px;
                text-shadow: 1px 1px 3px black;
                color: {resource_info['color']};
                background: rgba(0,0,0,0.7);
                border-radius: 50%;
                padding: 4px;
                border: 1px solid {resource_info['color']};
                box-shadow: 0 0 10px {resource_info['color']}40;
                animation: resource-glow 3s ease-in-out infinite;
            ">
            {resource_info['emoji']}
            </div>
            <style>
            @keyframes resource-glow {{
                0%, 100% {{ box-shadow: 0 0 10px {resource_info['color']}40; }}
                50% {{ box-shadow: 0 0 20px {resource_info['color']}80; }}
            }}
            </style>
            """),
            popup=f"<b>📦 {resource_info['name']}</b><br>Zone: {zone_info['name']}<br>Availability: {resource_density.upper()}",
            tooltip=f"{resource_info['emoji']} {resource_info['name']}"
        ).add_to(map_obj)

# ========================
# MAP GENERATION FUNCTION WITH CINEMATIC EFFECTS AND RESOURCES
# ========================
def generate_map(selected_zone=None, cinematic=True, show_welcome=False):
    # Start with overview of Karachi
    if selected_zone and selected_zone in zone_data:
        z = zone_data[selected_zone]
        coords = z["coords"]
        # Center map on the selected zone coordinates
        m = folium.Map(location=coords, zoom_start=16, tiles="CartoDB dark_matter")
    else:
        # Overview map - clean without markers for welcome screen
        m = folium.Map(location=[24.8607, 67.0011], zoom_start=11, tiles="CartoDB dark_matter")

    # Only add overview markers if NOT showing welcome screen
    if not show_welcome and not selected_zone:
        for zone_key, zone_info in zone_data.items():
            color_map = {"low": "green", "medium": "orange", "high": "red"}
            marker_color = color_map.get(zone_info["danger"], "red")
            
            # Enhanced SOS Distress Beacon - The Last of Us style
            folium.Marker(
                zone_info["coords"],
                popup=f"<b>{zone_info['name']}</b><br>{zone_info['alert']}",
                icon=folium.Icon(color=marker_color, icon="info-sign"),
                tooltip=zone_info["name"]
            ).add_to(m)
            # Add circles around all zones
            folium.CircleMarker(
                location=zone_info["coords"],
                radius=40,  # Medium size - not too big, not too small
                color=marker_color,
                fill=True,
                fill_opacity=0.3,
                weight=2
            ).add_to(m)
            
            # Add resource markers inside zone circles for overview map
            add_resource_markers_overview(m, zone_info["coords"], zone_info)
            
            # Add zombie markers inside high danger zone circles
            if zone_info["danger"] == "high":
                # Add multiple zombies inside the high danger zone
                zombie_positions = [
                    [zone_info["coords"][0] + 0.002, zone_info["coords"][1] - 0.002],
                    [zone_info["coords"][0] - 0.002, zone_info["coords"][1] + 0.002],
                    [zone_info["coords"][0] + 0.001, zone_info["coords"][1] + 0.001],
                    [zone_info["coords"][0] - 0.001, zone_info["coords"][1] - 0.001],
                    [zone_info["coords"][0] + 0.003, zone_info["coords"][1]],
                    [zone_info["coords"][0] - 0.003, zone_info["coords"][1]]
                ]
                
                for pos in zombie_positions:
                    folium.Marker(
                        pos,
                        icon=folium.DivIcon(html="<div style='font-size:18px;text-shadow:1px 1px 2px black;'>🧟</div>")
                    ).add_to(m)

    # Clean map start - no broadcast messages
    if show_welcome:
        # Just start with clean map, no overlays
        pass
    # If specific zone selected, add cinematic zoom + detailed effects
    if selected_zone and selected_zone in zone_data:
        z = zone_data[selected_zone]
        coords = z["coords"]

        # Enhanced marker for selected zone
        folium.Marker(
            coords,
            popup=f"<b>{z['name']}</b><br>{z['alert']}<br>Resources: {', '.join(z['resources'])}",
            icon=folium.Icon(color="red", icon="exclamation-sign", prefix='fa')
        ).add_to(m)

        # Danger Circle - Much smaller for specific area only
        color_map = {"low": "green", "medium": "orange", "high": "red"}
        glow_color = color_map.get(z["danger"], "red")
        folium.CircleMarker(
            location=coords,
            radius=40,  # Same size as overview circles
            color=glow_color,
            fill=True,
            fill_opacity=0.3,
            weight=2
        ).add_to(m)

        # Add resource markers for the selected zone (NEW FEATURE)
        add_resource_markers(m, coords, z, selected_zone=True)

        # Add zombie markers inside high danger zone circles
        if z["danger"] == "high":
            # Add multiple zombies inside the high danger zone
            zombie_positions = [
                [coords[0] + 0.002, coords[1] - 0.002],
                [coords[0] - 0.002, coords[1] + 0.002],
                [coords[0] + 0.001, coords[1] + 0.001],
                [coords[0] - 0.001, coords[1] - 0.001],
                [coords[0] + 0.003, coords[1]],
                [coords[0] - 0.003, coords[1]]
            ]
            
            for pos in zombie_positions:
                folium.Marker(
                    pos,
                    icon=folium.DivIcon(html="<div style='font-size:18px;text-shadow:1px 1px 2px black;'>🧟</div>")
                ).add_to(m)

        # Danger Icons ❗
        folium.Marker(
            [coords[0] + 0.005, coords[1] + 0.005],
            icon=folium.DivIcon(html="<div style='font-size:24px;color:red;text-shadow:2px 2px 4px black;'>❗</div>")
        ).add_to(m)
        folium.Marker(
            [coords[0] - 0.005, coords[1] - 0.005],
            icon=folium.DivIcon(html="<div style='font-size:24px;color:red;text-shadow:2px 2px black;'>❗</div>")
        ).add_to(m)

        # Zombies 🧟 - Distribution based on danger level
        if z["danger"] == "low":
            # No zombies for low danger zones (Zone A)
            zombie_positions = []
        elif z["danger"] == "medium":
            # Medium zombies for medium danger zones
            zombie_positions = [
                [coords[0] + 0.003, coords[1] - 0.003],
                [coords[0] - 0.003, coords[1] + 0.003],
                [coords[0] + 0.005, coords[1] + 0.002],
                [coords[0] - 0.002, coords[1] - 0.005]
            ]
        else:  # high danger
            # Many zombies for high danger zones
            zombie_positions = [
                [coords[0] + 0.003, coords[1] - 0.003],
                [coords[0] - 0.003, coords[1] + 0.003],
                [coords[0] + 0.005, coords[1] + 0.002],
                [coords[0] - 0.002, coords[1] - 0.005],
                [coords[0] + 0.001, coords[1] + 0.006],
                [coords[0] - 0.006, coords[1] - 0.001],
                [coords[0] + 0.004, coords[1] - 0.001],
                [coords[0] - 0.001, coords[1] + 0.004],
                [coords[0] + 0.002, coords[1] + 0.003],
                [coords[0] - 0.003, coords[1] - 0.002]
            ]
        
        # Add zombie markers for the selected zone
        for pos in zombie_positions:
            folium.Marker(
                pos,
                icon=folium.DivIcon(html="<div style='font-size:20px;text-shadow:1px 1px 2px black;'>🧟</div>")
            ).add_to(m)

        # Add zombie markers across Karachi (avoiding low-danger zones)
        karachi_zombie_positions = [
            [24.8607, 67.0011],  # City center
            [24.8784, 67.0103],  # Near Zone B (medium danger)
            [24.9090, 67.0940],  # Near Zone C (high danger)
            [24.8500, 67.0200],  # Central area
            [24.8900, 67.0800],  # Northern area
            [24.8300, 66.9800],  # Southern area
            [24.8700, 67.0400],  # Eastern area
            [24.8400, 66.9600],  # Western area
            [24.9200, 67.0600],  # Northeast
            [24.8000, 67.0400],  # Southwest
            [24.9000, 66.9800],  # Northwest
            [24.8200, 67.0600],  # Southeast
            [24.8800, 66.9400],  # Far west
            [24.9400, 67.0200],  # Far north
            [24.7800, 67.0000],  # Far south
            [24.8600, 67.1200],  # Far east
            [24.7600, 66.9200],  # Southwest corner
            [24.9600, 67.0800],  # Northeast corner
            [24.7600, 67.0800],  # Southeast corner
            [24.9600, 66.9200]   # Northwest corner
        ]
        
        # Add zombies across Karachi (avoiding the selected zone area and low-danger zones)
        for zombie_pos in karachi_zombie_positions:
            # Skip if too close to selected zone
            distance = ((zombie_pos[0] - coords[0])**2 + (zombie_pos[1] - coords[1])**2)**0.5
            # Also skip if too close to Zone A (low danger zone)
            zone_a_distance = ((zombie_pos[0] - 24.8182)**2 + (zombie_pos[1] - 67.0256)**2)**0.5
            
            if distance > 0.01 and zone_a_distance > 0.02:  # Keep zombies away from Zone A
                folium.Marker(
                    zombie_pos,
                    icon=folium.DivIcon(html="<div style='font-size:18px;text-shadow:1px 1px 2px black;opacity:0.7;'>🧟</div>")
                ).add_to(m)

    # Get base HTML
    map_html = m._repr_html_()
    
    # Inject cinematic JavaScript for smooth zoom + tilt
    if selected_zone and selected_zone in zone_data and cinematic:
        z = zone_data[selected_zone]
        coords = z["coords"]
        
        cinematic_js = f"""
        <script>
        setTimeout(function() {{
            // Get the Leaflet map instance
            var mapElement = document.querySelector('.folium-map');
            if (mapElement && mapElement._leaflet_map) {{
                var map = mapElement._leaflet_map;
                
                // Much higher zoom for intense focus
                map.flyTo([{coords[0]}, {coords[1]}], 18, {{
                    animate: true,
                    duration: 2.5,
                    easeLinearity: 0.1
                }});
                
                // Add tilt effect (pseudo-3D)
                setTimeout(function() {{
                    var mapContainer = map.getContainer();
                    mapContainer.style.transform = 'perspective(1000px) rotateX(15deg)';
                    mapContainer.style.transformOrigin = 'center bottom';
                    mapContainer.style.transition = 'transform 1s ease-out';
                    
                    // Add atmospheric glow
                    mapContainer.style.filter = 'contrast(1.1) saturate(1.2)';
                    mapContainer.style.boxShadow = 'inset 0 0 50px rgba(255,0,0,0.1)';
                }}, 1000);
                
                // Reset tilt after viewing
                setTimeout(function() {{
                    var mapContainer = map.getContainer();
                    mapContainer.style.transform = 'perspective(1000px) rotateX(5deg)';
                }}, 4000);
            }}
        }}, 500);
        </script>
        """
        
        # Inject the JavaScript
        map_html = map_html.replace('</div></body>', cinematic_js + '</div></body>')
    
    return map_html

def generate_sos_map(lat, lon, location_name):
    """Generate SOS map for user's location"""
    m = folium.Map(location=[lat, lon], zoom_start=15, tiles="CartoDB dark_matter")
    
    # Main SOS beacon
    folium.Marker(
        [lat, lon],
        icon=folium.DivIcon(html=f"""
        <div class="sos-beacon-main" style="
            background: radial-gradient(circle, #ff0000 0%, #cc0000 50%, #990000 100%);
            color: white;
            padding: 12px 16px;
            font-weight: bold;
            font-size: 12px;
            border-radius: 50%;
            text-align: center;
            animation: sos-pulse 1.5s infinite, sos-flicker 0.1s infinite;
            box-shadow: 
                0 0 30px #ff0000,
                0 0 60px rgba(255,0,0,0.6),
                inset 0 0 15px rgba(255,255,255,0.2);
            border: 3px solid rgba(255,255,255,0.4);
            position: relative;
            z-index: 1000;
        ">
        🆘 SOS<br><span style='font-size:10px;'>{location_name}</span>
        </div>
        <style>
        @keyframes sos-pulse {{
            0%, 100% {{ transform: scale(1); opacity: 1; }}
            50% {{ transform: scale(1.2); opacity: 0.8; }}
        }}
        @keyframes sos-flicker {{
            0%, 90%, 100% {{ opacity: 1; }}
            95% {{ opacity: 0.7; }}
        }}
        </style>
        """),
        popup=f"<b>🚨 SOS SIGNAL</b><br><b>{location_name}</b><br>Time: {time.strftime('%H:%M:%S')}<br>Priority: CRITICAL"
    ).add_to(m)
    
    # Emergency radius
    folium.Circle(
        location=[lat, lon],
        radius=1000,
        color="#FF0000",
        fill=True,
        fill_opacity=0.1,
        weight=2
    ).add_to(m)
    
    # Radio waves
    for i in range(3):
        folium.Circle(
            location=[lat, lon],
            radius=500 + (i * 300),
            color="rgba(255,0,0,0.3)",
            fill=False,
            weight=1
        ).add_to(m)
    
    # Add zombie markers around the edge of the emergency radius
    zombie_count = 12  # Number of zombies around the circle
    emergency_radius = 1000  # Same as the emergency circle radius
    
    for i in range(zombie_count):
        # Calculate position on the circle edge
        angle = (i * 360 / zombie_count) + random.uniform(-15, 15)  # Slight random variation
        angle_rad = math.radians(angle)
        
        # Position zombies on the edge of the emergency radius
        zombie_lat = lat + (emergency_radius / 111000) * math.cos(angle_rad)  # Convert meters to degrees
        zombie_lon = lon + (emergency_radius / (111000 * math.cos(math.radians(lat)))) * math.sin(angle_rad)
        
        folium.Marker(
            [zombie_lat, zombie_lon],
            icon=folium.DivIcon(html="""
            <div style="
                font-size: 18px;
                text-shadow: 2px 2px 4px black;
                color: #FF0000;
            ">🧟</div>
            """),
            popup=f"Zombie on perimeter - Distance: {emergency_radius}m from SOS"
        ).add_to(m)
    
    return m._repr_html_()

def generate_aid_map(sos_zones):
    """Generate map showing all SOS zones"""
    m = folium.Map(location=[24.8607, 67.0011], zoom_start=11, tiles="CartoDB dark_matter")
    
    for zone in sos_zones:
        lat, lon = zone['coords']
        priority = zone['priority']
        survivors = zone['survivors']
        
        # Color based on priority
        color_map = {"CRITICAL": "#FF0000", "HIGH": "#FF6600", "MEDIUM": "#FFAA00"}
        color = color_map.get(priority, "#FF0000")
        
        # SOS marker
        folium.Marker(
            [lat, lon],
            icon=folium.DivIcon(html=f"""
            <div class="aid-sos-beacon" style="
                background: radial-gradient(circle, {color} 0%, {color}80 50%, {color}60 100%);
                color: white;
                padding: 8px 12px;
                font-weight: bold;
                font-size: 10px;
                border-radius: 50%;
                text-align: center;
                animation: aid-pulse 2s infinite;
                box-shadow: 
                    0 0 20px {color},
                    0 0 40px rgba(255,0,0,0.4);
                border: 2px solid rgba(255,255,255,0.3);
            ">
            🆘<br><span style='font-size:8px;'>{priority}</span>
            </div>
            <style>
            @keyframes aid-pulse {{
                0%, 100% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.1); opacity: 0.8; }}
            }}
            </style>
            """),
            popup=f"<b>🚨 {zone['name']}</b><br>Priority: {priority}<br>Survivors: {survivors}<br>Time: {zone['time']}"
        ).add_to(m)
        
        # Priority radius
        radius_map = {"CRITICAL": 800, "HIGH": 600, "MEDIUM": 400}
        radius = radius_map.get(priority, 500)
        
        folium.Circle(
            location=[lat, lon],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.2,
            weight=2
        ).add_to(m)
        
        # Add zombie markers for HIGH and CRITICAL priority areas
        if priority in ["HIGH", "CRITICAL"]:
            # More zombies for CRITICAL, fewer for HIGH
            zombie_count = 8 if priority == "CRITICAL" else 5
            
            for i in range(zombie_count):
                # Random positions within the priority radius
                angle = (i * 360 / zombie_count) + random.uniform(-30, 30)
                distance = random.uniform(0.001, 0.003)  # Within 100-300m
                
                zombie_lat = lat + distance * math.cos(math.radians(angle))
                zombie_lon = lon + distance * math.sin(math.radians(angle))
                
                folium.Marker(
                    [zombie_lat, zombie_lon],
                    icon=folium.DivIcon(html=f"""
                    <div style="
                        font-size: 16px;
                        text-shadow: 1px 1px 2px black;
                        color: {'#FF0000' if priority == 'CRITICAL' else '#FF6600'};
                    ">🧟</div>
                    """),
                    popup=f"Zombie near {zone['name']} ({priority} priority)"
                ).add_to(m)
    
    return m._repr_html_()

# ========================
# ENHANCED CHATBOT RESPONSE FUNCTION WITH AI
# ========================
def chatbot_response(message, history):
    message_original = message.strip()
    message = message.strip().lower()
    
    # Check for zone requests first (maintain existing functionality)
    for zone in zone_data:
        if message == zone.lower() or zone.lower() in message:
            data = zone_data[zone]
            
            # Get AI-enhanced zone response
            ai_response = survival_ai.get_ai_response(
                f"User is asking about {zone}. Provide tactical intel and survival advice.",
                data
            )
            
            # Combine structured data with AI response
            reply = (
                f"🎯 *{data['name']}*\n\n"
                f"📦 *Resources Available:*\n{chr(10).join('   • ' + r for r in data['resources'])}\n\n"
                f"🚨 *Current Status:* {data['alert']}\n\n"
                f"🤖 *ARIA Analysis:*\n{ai_response}\n\n"
                f"📡 Zooming to location..."
            )
            history.append((message_original, reply))
            return history, generate_map(zone, cinematic=True)
    
    # Special commands with AI enhancement
    if "help" in message:
        ai_help = survival_ai.get_ai_response("User needs help with system commands. Explain available features and provide survival tips.")
        reply = (
            f"🆘 *SurviveTrack Commands:*\n\n"
            f"• Type *Zone A*, *Zone B*, or *Zone C* for location intel\n"
            f"• Use *Generate Map* for city overview\n"
            f"• Send *status* for system check\n"
            f"• Ask me anything about survival, tactics, or zones!\n\n"
            f"🤖 *ARIA says:* {ai_help}"
        )
    elif "status" in message:
        ai_status = survival_ai.get_ai_response("User is checking system status. Provide current threat assessment and system operational status.")
        reply = (
            f"📡 *SurviveTrack System Status:*\n\n"
            f"🟢 Satellite Connection: ACTIVE\n"
            f"🟡 Zone Monitoring: OPERATIONAL\n"
            f"🔴 Threat Level: CRITICAL\n"
            f"🤖 ARIA AI: ONLINE\n\n"
            f"💀 Zombie Activity Detected Citywide\n\n"
            f"🤖 *ARIA Analysis:* {ai_status}"
        )
    elif "analysis" in message or "tactical" in message:
        # Enhanced tactical analysis mode
        zone_mentioned = None
        for zone in zone_data:
            if zone.lower() in message:
                zone_mentioned = zone
                break
        
        if zone_mentioned:
            analysis = survival_ai.get_zone_analysis(zone_mentioned)
            reply = f"🎯 *Tactical Analysis - {zone_data[zone_mentioned]['name']}*\n\n{analysis}"
            history.append((message_original, reply))
            return history, generate_map(zone_mentioned, cinematic=True)
        else:
            analysis = survival_ai.get_ai_response("Provide general tactical analysis of the current situation in Karachi. Include threat assessment and survival recommendations.")
            reply = f"🎯 *General Tactical Analysis*\n\n{analysis}"
    else:
        # General AI response for any other query
        ai_response = survival_ai.get_ai_response(message_original)
        reply = f"🤖 *ARIA Response:*\n\n{ai_response}"
    
    history.append((message_original, reply))
    return history, generate_map(show_welcome=False, cinematic=False)

# ========================
# BUTTON FUNCTIONS
# ========================
def generate_resource_map(history):
    """Generate map showing all resources across all zones"""
    m = folium.Map(location=[24.8607, 67.0011], zoom_start=11, tiles="CartoDB dark_matter")
    
    # Add zone markers and all resources
    for zone_key, zone_info in zone_data.items():
        color_map = {"low": "green", "medium": "orange", "high": "red"}
        marker_color = color_map.get(zone_info["danger"], "red")
        
        # Zone marker
        folium.Marker(
            zone_info["coords"],
            popup=f"<b>{zone_info['name']}</b><br>{zone_info['alert']}<br>Resources: {', '.join(zone_info['resources'])}",
            icon=folium.Icon(color=marker_color, icon="info-sign"),
            tooltip=zone_info["name"]
        ).add_to(m)
        
        # Zone circle
        folium.CircleMarker(
            location=zone_info["coords"],
            radius=40,
            color=marker_color,
            fill=True,
            fill_opacity=0.2,
            weight=2
        ).add_to(m)
        
        # Add ALL resources for this zone
        add_resource_markers(m, zone_info["coords"], zone_info, selected_zone=False)
    
    # AI analysis for resource locator
    ai_analysis = survival_ai.get_ai_response("All resource locations are now visible across Karachi. Provide tactical analysis of resource distribution patterns and survival recommendations for resource gathering missions.")
    
    reply = (
        f"📦 *RESOURCE LOCATOR SCAN COMPLETE*\n\n"
        f"🌍 *Scan Radius:* Full Karachi Zone\n"
        f"📍 *Zones Scanned:* 3 Active\n"
        f"⏰ *Scan Time:* {time.strftime('%H:%M:%S')}\n\n"
        f"📦 *Resource Summary:*\n"
        f"   • Zone A (Boat Basin): HIGH density - Water, Food, Shelter, Fuel, Tools\n"
        f"   • Zone B (Lyari): MEDIUM density - Medicine, Equipment, Batteries\n"
        f"   • Zone C (Railway): LOW density - Weapons, Military Supplies\n\n"
        f"🤖 *ARIA Resource Analysis:*\n{ai_analysis}"
    )
    history.append(("[RESOURCE LOCATOR]", reply))
    return history, m._repr_html_()

def quick_zone_select(zone, history):
    data = zone_data[zone]
    
    # Get AI insight for quick zone access
    ai_insight = survival_ai.get_ai_response(f"Provide a quick tactical brief for {zone} access.", data)
    
    reply = (
        f"⚡ *Quick Access: {data['name']}*\n\n"
        f"📦 Resources: {', '.join(data['resources'])}\n"
        f"🚨 Status: {data['alert']}\n\n"
        f"🤖 *ARIA Brief:* {ai_insight}\n\n"
        f"🎯 Initiating tactical zoom..."
    )
    history.append((f"[Quick Select {zone}]", reply))
    return history, generate_map(zone, cinematic=True)

def request_aid(history):
    # Use specific location coordinates instead of random generation
    live_lat = 24.87366765011169
    live_lon = 67.073671736837
    
    # Get AI assessment of the SOS situation
    sos_assessment = survival_ai.get_ai_response(f"A survivor is requesting emergency aid at coordinates {live_lat:.4f}, {live_lon:.4f}. Provide emergency response guidance and survival tips for this critical situation.")
    
    reply = (
        f"🚨 *SOS SIGNAL TRANSMITTED*\n\n"
        f"📍 *Your Location:* {live_lat:.4f}, {live_lon:.4f}\n"
        f"⏰ *Time:* {time.strftime('%H:%M:%S')}\n"
        f"📡 *Signal Strength:* EXCELLENT\n"
        f"🆘 *Aid Request:* ACTIVE\n\n"
        f"💬 *Message:* 'Survivor in distress. Need immediate assistance.'\n"
        f"🎯 *Priority:* CRITICAL\n\n"
        f"🤖 *ARIA Emergency Protocol:*\n{sos_assessment}\n\n"
        f"⚠️ *Warning:* Stay hidden. Help is on the way."
    )
    history.append(("[SOS REQUEST]", reply))
    return history, generate_sos_map(live_lat, live_lon, "YOUR LOCATION")

def locate_aid(history):
    # Generate random SOS zones across Karachi
    sos_zones = []
    for i in range(5):
        lat = 24.8607 + random.uniform(-0.1, 0.1)
        lon = 67.0011 + random.uniform(-0.1, 0.1)
        sos_zones.append({
            'coords': [lat, lon],
            'name': f"Distress Signal #{i+1}",
            'time': f"{random.randint(0, 23):02d}:{random.randint(0, 59):02d}",
            'priority': random.choice(['CRITICAL', 'HIGH', 'MEDIUM']),
            'survivors': random.randint(1, 8)
        })
    
    # Get AI recommendation for aid response
    aid_analysis = survival_ai.get_ai_response(f"Multiple SOS signals detected across Karachi. {len(sos_zones)} active distress calls with varying priority levels. Provide tactical recommendation for aid response prioritization.")
    
    reply = (
        f"🔍 *AID LOCATION SCAN COMPLETE*\n\n"
        f"📡 *Active SOS Signals:* {len(sos_zones)}\n"
        f"🌍 *Scan Radius:* 20km\n"
        f"⏰ *Scan Time:* {time.strftime('%H:%M:%S')}\n\n"
        f"🚨 *Priority Signals:*\n"
    )
    
    for i, zone in enumerate(sos_zones[:3]):
        reply += f"   • {zone['name']} - {zone['priority']} - {zone['survivors']} survivors\n"
    
    reply += f"\n🤖 *ARIA Tactical Recommendation:*\n{aid_analysis}"
    history.append(("[AID LOCATOR]", reply))
    return history, generate_aid_map(sos_zones)

# ========================
# UI LAYOUT WITH THE LAST OF US STYLING
# ========================
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@300;400;500;600;700&family=Share+Tech+Mono&display=swap');

body {
    margin: 0;
    padding: 0;
    overflow-x: hidden;
}

.gradio-container {
    background: 
        linear-gradient(135deg, 
            rgba(20, 15, 10, 0.95) 0%, 
            rgba(40, 25, 15, 0.90) 25%,
            rgba(25, 20, 15, 0.95) 50%,
            rgba(35, 20, 10, 0.90) 75%,
            rgba(20, 15, 10, 0.95) 100%
        ),
        radial-gradient(circle at 20% 80%, rgba(139, 69, 19, 0.1) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(160, 82, 45, 0.05) 0%, transparent 50%);
    background-attachment: fixed;
    font-family: 'Rajdhani', 'Share Tech Mono', monospace;
    color: #d4af37;
    min-height: 100vh;
    position: relative;
}

/* Dust particles effect */
.gradio-container::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(2px 2px at 20% 30%, rgba(218, 165, 32, 0.3), transparent),
        radial-gradient(1px 1px at 40% 70%, rgba(205, 133, 63, 0.2), transparent),
        radial-gradient(1px 1px at 90% 40%, rgba(210, 180, 140, 0.3), transparent);
    background-size: 300px 300px, 200px 200px, 400px 400px;
    animation: dust-float 20s linear infinite;
    pointer-events: none;
    z-index: 1;
}

@keyframes dust-float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-20px) rotate(180deg); }
}

/* Film grain texture */
.gradio-container::after {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: 
        repeating-linear-gradient(
            0deg,
            rgba(0,0,0,0.03) 0px,
            rgba(0,0,0,0.03) 1px,
            transparent 1px,
            transparent 2px
        );
    animation: film-grain 0.2s steps(5) infinite;
    pointer-events: none;
    z-index: 2;
}

@keyframes film-grain {
    0%, 100% { opacity: 0.02; }
    50% { opacity: 0.05; }
}

.gr-button {
    background: linear-gradient(145deg, 
        rgba(139, 69, 19, 0.8) 0%, 
        rgba(160, 82, 45, 0.9) 50%, 
        rgba(101, 67, 33, 0.8) 100%) !important;
    border: 2px solid rgba(218, 165, 32, 0.6) !important;
    color: #f5deb3 !important;
    font-weight: 600 !important;
    font-family: 'Rajdhani', monospace !important;
    text-shadow: 0 1px 3px rgba(0,0,0,0.8) !important;
    box-shadow: 
        0 4px 15px rgba(139, 69, 19, 0.4),
        inset 0 1px 0 rgba(255,255,255,0.1) !important;
    transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
    position: relative !important;
    overflow: hidden !important;
    z-index: 10 !important;
}

.gr-button::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent, rgba(218, 165, 32, 0.1), transparent);
    transform: rotate(45deg);
    transition: all 0.5s;
    opacity: 0;
}

.gr-button:hover::before {
    animation: shine 0.6s ease-out;
    opacity: 1;
}

@keyframes shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.gr-button:hover {
    background: linear-gradient(145deg, 
        rgba(160, 82, 45, 0.9) 0%, 
        rgba(218, 165, 32, 0.8) 50%, 
        rgba(139, 69, 19, 0.9) 100%) !important;
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 
        0 8px 25px rgba(218, 165, 32, 0.3),
        0 4px 15px rgba(139, 69, 19, 0.6),
        inset 0 1px 0 rgba(255,255,255,0.2) !important;
    border-color: rgba(218, 165, 32, 0.9) !important;
}

.gr-button:active {
    transform: translateY(-1px) scale(0.98) !important;
    box-shadow: 
        0 4px 12px rgba(139, 69, 19, 0.4),
        inset 0 2px 4px rgba(0,0,0,0.2) !important;
}

.gr-textbox {
    background: linear-gradient(135deg, 
        rgba(25, 25, 25, 0.95) 0%, 
        rgba(40, 30, 20, 0.90) 100%) !important;
    border: 2px solid rgba(218, 165, 32, 0.4) !important;
    color: #d4af37 !important;
    font-family: 'Share Tech Mono', monospace !important;
    box-shadow: 
        0 0 20px rgba(218, 165, 32, 0.1),
        inset 0 2px 4px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease !important;
}

.gr-textbox:focus {
    border-color: rgba(218, 165, 32, 0.8) !important;
    box-shadow: 
        0 0 30px rgba(218, 165, 32, 0.2),
        inset 0 2px 4px rgba(0,0,0,0.3) !important;
}

.gr-chatbot {
    background: linear-gradient(135deg, 
        rgba(20, 15, 10, 0.95) 0%, 
        rgba(30, 20, 15, 0.90) 100%) !important;
    border: 1px solid rgba(139, 69, 19, 0.4) !important;
    box-shadow: 
        0 0 30px rgba(139, 69, 19, 0.2),
        inset 0 2px 10px rgba(0,0,0,0.3) !important;
    backdrop-filter: blur(5px) !important;
}

.gr-markdown h1 {
    font-family: 'Rajdhani', monospace !important;
    font-weight: 700 !important;
    background: linear-gradient(45deg, 
        #d4af37 0%, 
        #f4e4bc 25%, 
        #daa520 50%, 
        #b8860b 75%, 
        #d4af37 100%) !important;
    background-size: 200% 200% !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    animation: title-glow 4s ease-in-out infinite !important;
    text-shadow: 0 0 30px rgba(212, 175, 55, 0.5) !important;
    filter: drop-shadow(2px 2px 4px rgba(0,0,0,0.8));
}

@keyframes title-glow {
    0%, 100% { 
        background-position: 0% 50%;
        filter: brightness(1) drop-shadow(2px 2px 4px rgba(0,0,0,0.8));
    }
    50% { 
        background-position: 100% 50%;
        filter: brightness(1.2) drop-shadow(4px 4px 8px rgba(0,0,0,0.6));
    }
}

.gr-markdown h3 {
    color: #daa520 !important;
    font-family: 'Rajdhani', monospace !important;
    font-weight: 500 !important;
    text-shadow: 
        0 0 10px rgba(218, 165, 32, 0.4),
        2px 2px 4px rgba(0,0,0,0.8) !important;
    animation: subtitle-flicker 6s ease-in-out infinite !important;
}

@keyframes subtitle-flicker {
    0%, 95%, 100% { opacity: 1; }
    96%, 98% { opacity: 0.8; }
    97% { opacity: 0.9; }
}

/* Weathered border effects */
.gr-column {
    position: relative;
}

.gr-column::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: 
        linear-gradient(90deg, rgba(139, 69, 19, 0.1) 0%, transparent 20%, transparent 80%, rgba(139, 69, 19, 0.1) 100%),
        linear-gradient(0deg, rgba(160, 82, 45, 0.05) 0%, transparent 20%, transparent 80%, rgba(160, 82, 45, 0.05) 100%);
    pointer-events: none;
    z-index: -1;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 12px;
}

::-webkit-scrollbar-track {
    background: linear-gradient(45deg, rgba(20, 15, 10, 0.8), rgba(25, 20, 15, 0.8));
    border-radius: 6px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, rgba(139, 69, 19, 0.8), rgba(160, 82, 45, 0.8));
    border-radius: 6px;
    border: 1px solid rgba(218, 165, 32, 0.3);
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(45deg, rgba(160, 82, 45, 0.9), rgba(218, 165, 32, 0.8));
}

/* Loading animation for map */
.map-loading::before {
    content: 'SCANNING TERRITORY...';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #d4af37;
    font-family: 'Share Tech Mono', monospace;
    font-weight: bold;
    z-index: 1000;
    animation: loading-pulse 2s ease-in-out infinite;
}

@keyframes loading-pulse {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}

/* Enhanced Status Panel Styling */
.survival-status-panel {
    background: linear-gradient(135deg, 
        rgba(15, 10, 5, 0.98) 0%, 
        rgba(25, 15, 10, 0.95) 50%,
        rgba(20, 12, 8, 0.98) 100%);
    border: 2px solid rgba(218, 165, 32, 0.6);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
    box-shadow: 
        0 0 25px rgba(218, 165, 32, 0.3),
        inset 0 2px 10px rgba(0,0,0,0.4);
    position: relative;
    overflow: hidden;
    font-family: 'Share Tech Mono', monospace;
}

.survival-status-panel::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, 
        transparent 0%,
        rgba(218, 165, 32, 0.8) 50%,
        transparent 100%);
    animation: scan-line 3s ease-in-out infinite;
}

@keyframes scan-line {
    0% { left: -100%; }
    50% { left: 100%; }
    100% { left: 100%; }
}

.status-header {
    display: flex;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid rgba(218, 165, 32, 0.3);
}

.status-icon {
    font-size: 18px;
    margin-right: 12px;
    animation: comm-pulse 2s ease-in-out infinite;
}

@keyframes comm-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
}

.status-title {
    flex-grow: 1;
    color: #d4af37;
    font-weight: bold;
    font-size: 14px;
    letter-spacing: 1px;
    text-shadow: 0 0 8px rgba(212, 175, 55, 0.5);
}

.status-indicator {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    position: relative;
}

.status-indicator.online {
    background: #00ff41;
    box-shadow: 
        0 0 10px #00ff41,
        inset 0 0 5px rgba(255,255,255,0.3);
    animation: online-blink 2s ease-in-out infinite;
}

@keyframes online-blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

.status-content {
    margin: 12px 0;
}

.status-line {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 6px 0;
    padding: 4px 0;
}

.status-label {
    color: #cd853f;
    font-size: 12px;
    font-weight: 600;
    text-shadow: 0 1px 2px rgba(0,0,0,0.8);
}

.status-value {
    color: #f5deb3;
    font-size: 12px;
    font-weight: bold;
    text-align: right;
    text-shadow: 0 1px 2px rgba(0,0,0,0.8);
}

.status-value.operational {
    color: #90ee90;
    text-shadow: 0 0 5px rgba(144, 238, 144, 0.5);
}

.status-value.online {
    color: #00ff41;
    text-shadow: 0 0 5px rgba(0, 255, 65, 0.5);
    animation: online-glow 3s ease-in-out infinite;
}

@keyframes online-glow {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.status-value.critical {
    color: #ff4444;
    text-shadow: 0 0 8px rgba(255, 68, 68, 0.6);
    animation: critical-pulse 1.5s ease-in-out infinite;
}

@keyframes critical-pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.05); }
}

.status-footer {
    border-top: 1px solid rgba(218, 165, 32, 0.3);
    padding-top: 8px;
    margin-top: 12px;
}

.ticker {
    overflow: hidden;
    white-space: nowrap;
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(218, 165, 32, 0.2);
    border-radius: 4px;
    padding: 4px 8px;
}

.ticker-text {
    display: inline-block;
    color: #daa520;
    font-size: 10px;
    font-weight: 500;
    animation: ticker-scroll 20s linear infinite;
    text-shadow: 0 1px 2px rgba(0,0,0,0.8);
}

@keyframes ticker-scroll {
    0% { transform: translateX(100%); }
    100% { transform: translateX(-100%); }
}

/* Hover effects for the status panel */
.survival-status-panel:hover {
    border-color: rgba(218, 165, 32, 0.8);
    box-shadow: 
        0 0 35px rgba(218, 165, 32, 0.4),
        inset 0 2px 15px rgba(0,0,0,0.3);
    transform: translateY(-2px);
    transition: all 0.3s ease;
}

.survival-status-panel:hover .status-title {
    text-shadow: 0 0 12px rgba(212, 175, 55, 0.8);
}
"""

with gr.Blocks(css=custom_css, title="SurviveTrack - The Last of Us: Karachi", theme=gr.themes.Base()) as demo:
    gr.Markdown("""
    # ☣ SurviveTrack – Post-Apocalyptic Karachi Intelligence System
    ### 🏚 Twenty years after the outbreak. The city remembers.
    ### 🗺 Military-grade tactical mapping for the infected zones of Karachi 🧟‍♂
    ### 🤖 **NEW:** ARIA AI Assistant - Powered by Anthropic Claude
    ### 📦 **UPDATED:** Resource Tracking System - Supplies mapped by zone safety
    """)
    
    with gr.Row():
        with gr.Column(scale=2):
            # Enhanced status display above chatbot
            gr.HTML("""
            <div class="survival-status-panel">
                <div class="status-header">
                    <div class="status-icon">🎙️</div>
                    <div class="status-title">COMMUNICATION LINK ESTABLISHED</div>
                    <div class="status-indicator online"></div>
                </div>
                <div class="status-content">
                    <div class="status-line">
                        <span class="status-label">📡 SYSTEM STATUS:</span>
                        <span class="status-value operational">OPERATIONAL</span>
                    </div>
                    <div class="status-line">
                        <span class="status-label">🤖 ARIA AI:</span>
                        <span class="status-value online">ONLINE</span>
                    </div>
                    <div class="status-line">
                        <span class="status-label">📦 RESOURCE TRACKER:</span>
                        <span class="status-value online">ACTIVE</span>
                    </div>
                    <div class="status-line">
                        <span class="status-label">🌍 SCAN RADIUS:</span>
                        <span class="status-value">50km KARACHI ZONE</span>
                    </div>
                    <div class="status-line">
                        <span class="status-label">⚠️ THREAT LEVEL:</span>
                        <span class="status-value critical">CRITICAL</span>
                    </div>
                </div>
                <div class="status-footer">
                    <div class="ticker">
                        <span class="ticker-text">🔴 LIVE FEED: Resource markers now active • Zone A: High supply density • Zone B: Medical caches located • Zone C: Military equipment detected • Weather: Clear, visibility good</span>
                    </div>
                </div>
            </div>
            """)
            
            chatbot = gr.Chatbot(
                height=400,
                placeholder="🎙 [RADIO STATIC] ...SurviveTrack operational...\n📡 This is your lifeline in the quarantine zone.\n🤖 ARIA AI Assistant online and ready.\n📦 Resource tracking system now active.\n🔍 Query zones for survivor intel and supply caches.",
                show_label=False
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    placeholder="🎯 [ENCRYPTED COMMS] Zone designation (A|B|C) or tactical query...", 
                    scale=6,
                    container=False,
                    show_label=False
                )
                send_btn = gr.Button("📻 RELAY", scale=1, variant="primary")
            
            with gr.Row():
                zone_a_btn = gr.Button("⚠ SECTOR-A", scale=1, variant="secondary")
                zone_b_btn = gr.Button("☢ SECTOR-B", scale=1, variant="secondary") 
                zone_c_btn = gr.Button("🚂 SECTOR-C", scale=1, variant="secondary")
                resource_btn = gr.Button("📦 RESOURCES", scale=1, variant="secondary")
            
            with gr.Row():
                request_aid_btn = gr.Button("🆘 REQUEST AID", scale=1, variant="stop")
                locate_aid_btn = gr.Button("🔍 LOCATE AID", scale=1, variant="secondary")
        
        with gr.Column(scale=3):
            gr.Markdown("### 🗺 *[TACTICAL OVERVIEW] Infected Territory Mapping System*")
            gr.Markdown("#### 📦 Resource markers: 💧🍞🏠 (Zone A) | 💊🔦 (Zone B) | 🔫🩺 (Zone C)")
            map_output = gr.HTML(
                generate_map(show_welcome=True)
            )

    # Event handlers
    send_btn.click(chatbot_response, inputs=[msg, chatbot], outputs=[chatbot, map_output])
    msg.submit(chatbot_response, inputs=[msg, chatbot], outputs=[chatbot, map_output])
    
    # Quick zone buttons
    zone_a_btn.click(lambda h: quick_zone_select("Zone A", h), inputs=[chatbot], outputs=[chatbot, map_output])
    zone_b_btn.click(lambda h: quick_zone_select("Zone B", h), inputs=[chatbot], outputs=[chatbot, map_output])
    zone_c_btn.click(lambda h: quick_zone_select("Zone C", h), inputs=[chatbot], outputs=[chatbot, map_output])
    
    # Resource locator button
    resource_btn.click(generate_resource_map, inputs=[chatbot], outputs=[chatbot, map_output])
    
    # Aid buttons
    request_aid_btn.click(request_aid, inputs=[chatbot], outputs=[chatbot, map_output])
    locate_aid_btn.click(locate_aid, inputs=[chatbot], outputs=[chatbot, map_output])
    
    # Clear message box after sending
    msg.submit(lambda: "", outputs=[msg])
    send_btn.click(lambda: "", outputs=[msg])

if __name__ == "__main__":
    demo.launch(
        share=True,
        server_port=7860,
        show_error=True
    )