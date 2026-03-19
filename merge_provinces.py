#!/usr/bin/env python3
"""
merge_provinces.py - Merge 63 Vietnamese provinces to 34 based on Resolution 60-NQ/TW

This script:
1. Extracts GeoJSON and IP data from visualization.html
2. Merges polygons for provinces being combined
3. Aggregates IP counts for merged provinces
4. Generates new visualization_34provinces.html
"""

import json
import re
from shapely.geometry import shape, mapping, MultiPolygon
from shapely.ops import unary_union
import folium
from collections import defaultdict

# Province merger mapping: new_name -> [list of old names from GeoJSON]
# All 67 unique names from GeoJSON mapped to 34 new provinces
PROVINCE_MAPPING = {
    # 6 Centrally-governed cities
    "Ha Noi": ["Ha Noi"],
    "TP. Ho Chi Minh": ["TP. Ho Chi Minh", "Ba Ria - Vung Tau", "Con Dao (Ba Ria - Vung Tau)", "Binh Duong"],
    "Hai Phong": ["Hai Phong", "Hai Duong"],
    "Da Nang": ["Da Nang", "Quang Nam", "Hoang Sa (Da Nang)"],
    "Can Tho": ["Can Tho", "Soc Trang", "Hau Giang"],
    "Hue": ["Thua Thien - Hue"],
    
    # Provinces - unchanged (11 provinces)
    "Lai Chau": ["Lai Chau"],
    "Dien Bien": ["Dien Bien"],
    "Son La": ["Son La"],
    "Lang Son": ["Lang Son"],
    "Cao Bang": ["Cao Bang"],
    "Quang Ninh": ["Quang Ninh"],
    "Thanh Hoa": ["Thanh Hoa"],
    "Nghe An": ["Nghe An"],
    "Ha Tinh": ["Ha Tinh"],
    "Gia Lai": ["Gia Lai", "Binh Dinh"],
    # "Binh Dinh": ["Binh Dinh"],
    # "Binh Duong": ["Binh Duong"],
    # "Ba Ria - Vung Tau": ["Ba Ria - Vung Tau", "Con Dao (Ba Ria - Vung Tau)"],
    
    # Merged provinces (15 merged provinces = 34 total)
    "Tuyen Quang": ["Tuyen Quang", "Ha Giang"],
    "Lao Cai": ["Lao Cai", "Yen Bai"],
    "Thai Nguyen": ["Thai Nguyen", "Bac Kan"],
    "Phu Tho": ["Phu Tho", "Vinh Phuc", "Hoa Binh"],
    "Bac Ninh": ["Bac Ninh", "Bac Giang"],
    "Hung Yen": ["Hung Yen", "Thai Binh"],
    "Ninh Binh": ["Ninh Binh", "Nam Dinh", "Ha Nam"],
    "Quang Tri": ["Quang Tri", "Quang Binh"],
    "Quang Ngai": ["Quang Ngai", "Kon Tum"],
    "Khanh Hoa": ["Khanh Hoa", "Ninh Thuan", "Truong Sa (Khanh Hoa)"],
    "Dak Lak": ["Dak Lak", "Phu Yen"],
    "Lam Dong": ["Lam Dong", "Dak Nong", "Binh Thuan"],
    "Dong Nai": ["Dong Nai", "Binh Phuoc"],
    "Tay Ninh": ["Tay Ninh", "Long An"],
    "Vinh Long": ["Vinh Long", "Ben Tre", "Tra Vinh"],
    "Dong Thap": ["Dong Thap", "Tien Giang"],
    "An Giang": ["An Giang", "Kien Giang", "Phu Quoc (Kien Giang)"],
    "Ca Mau": ["Ca Mau", "Bac Lieu"],
}



def normalize_name(name):
    """Normalize province name for matching"""
    return name.strip().lower().replace("-", " ").replace("  ", " ")

def get_merged_name(old_name):
    """Get the new merged province name for an old province name"""
    normalized = normalize_name(old_name)
    for new_name, old_names in PROVINCE_MAPPING.items():
        for n in old_names:
            if normalize_name(n) == normalized:
                return new_name
    return old_name  # Return original if not found in mapping

def extract_geojson_from_html(html_path):
    """Extract GeoJSON data from visualization.html"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find GeoJSON data - look for geo_json_*_add pattern
    pattern = r'geo_json_[a-f0-9]+_add\((\{.*?\})\);'
    matches = re.findall(pattern, content, re.DOTALL)
    
    if matches:
        # Parse the GeoJSON
        geojson_str = matches[0]
        geojson = json.loads(geojson_str)
        return geojson
    
    return None

def extract_ip_data_from_html(html_path):
    """Extract IP data from CircleMarker popups"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to extract province and IP count from popup HTML
    # Format: Province: Da Nang<br>IPs: 14
    pattern = r'Province:\s*([^<]+)<br>IPs:\s*(\d+)'
    matches = re.findall(pattern, content)
    
    ip_data = defaultdict(int)
    for province, ip_count in matches:
        province = province.strip()
        ip_data[province] += int(ip_count)
    
    return dict(ip_data)

def merge_provinces(geojson, ip_data):
    """Merge province polygons and aggregate IP data"""
    final_features = []
    merged_ips = defaultdict(int)
    
    # Group features by merged province name
    province_features = defaultdict(list)
    for feature in geojson['features']:
        old_name = feature['properties'].get('Name_EN') or feature['properties'].get('Name_VI', 'Unknown')
        new_name = get_merged_name(old_name)
        province_features[new_name].append(feature)
    
    # Merge geometries
    for new_name, features in province_features.items():
        # Update properties for all features in this group to the new name
        # (This helps if we fallback to keeping originals)
        for f in features:
            f['properties']['Name_EN'] = new_name
            f['properties']['Name_VI'] = new_name

        if len(features) == 1:
            # Single province, no merge needed
            final_features.append(features[0])
        else:
            # Merge multiple provinces
            geometries = []
            valid_features = []
            
            for f in features:
                try:
                    geom = shape(f['geometry'])
                    if geom.is_valid:
                        geometries.append(geom)
                        valid_features.append(f)
                    else:
                        g_fixed = geom.buffer(0)
                        if not g_fixed.is_empty:
                            geometries.append(g_fixed)
                            valid_features.append(f)
                        else:
                             print(f"Warning: Geometry became empty after fix for {f['properties'].get('Name_EN', 'Unknown')}")
                except Exception as e:
                    print(f"Warning: Could not process geometry for {f['properties'].get('Name_EN', 'Unknown')}: {e}")
            
            if geometries:
                try:
                    merged_geom = unary_union(geometries)
                    # Create merged feature
                    merged_feature = {
                        'type': 'Feature',
                        'id': str(hash(new_name) % 10000),
                        'properties': {
                            'Name_EN': new_name,
                            'Name_VI': new_name,
                        },
                        'geometry': mapping(merged_geom)
                    }
                    final_features.append(merged_feature)
                except Exception as e:
                    print(f"Warning: Could not merge geometries for {new_name}: {e}. Keeping original features.")
                    # Fallback: keep all valid features separately
                    final_features.extend(valid_features)
            else:
                 print(f"Warning: No valid geometries for {new_name}. Keeping original features.")
                 final_features.extend(features)
    
    # Aggregate IP data
    for old_name, ip_count in ip_data.items():
        new_name = get_merged_name(old_name)
        merged_ips[new_name] += ip_count
    
    # Create new GeoJSON
    new_geojson = {
        'type': 'FeatureCollection',
        'features': final_features
    }
    
    return new_geojson, dict(merged_ips)

def create_visualization(geojson, ip_data, output_path):
    """Create Folium map with merged provinces - matching original style"""
    # Create base map centered on Vietnam
    m = folium.Map(location=[16.0, 108.0], zoom_start=6, tiles='cartodbpositron')
    
    # Calculate max IPs for color scaling
    max_ips = max(ip_data.values()) if ip_data else 1
    min_ips = min(ip_data.values()) if ip_data else 0
    
    # Blues color palette for province fill (8 colors matching legend)
    blues_colors = ['#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#084594']
    
    def get_color(ips):
        if ips == 0:
            return 'black'  # No data - black like original
        
        # Normalize to 0-1 range and map to 8 bins
        ratio = min(1.0, ips / max_ips)
        index = min(7, int(ratio * 8))  # 0-7 for 8 colors
        return blues_colors[index]
    
    # YlOrRd color palette for circle markers (8 colors matching legend)
    ylOrRd_colors = ['#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026']
    
    def get_marker_color(ips):
        if ips == 0:
            return 'black'  # No data
        
        # Normalize to 0-1 range and map to 8 bins
        ratio = min(1.0, ips / max_ips)
        index = min(7, int(ratio * 8))  # 0-7 for 8 colors
        return ylOrRd_colors[index]
    
    # Define style function for provinces
    def style_function(feature):
        province_name = feature['properties'].get('Name_EN', 'Unknown')
        ips = ip_data.get(province_name, 0)
        fill_color = get_color(ips)
        
        return {
            'fillColor': fill_color,
            'color': 'blue',
            'weight': 2,
            'fillOpacity': 0.7,
            'opacity': 0.8
        }
    
    # Add GeoJson layer with YlOrRd styling
    folium.GeoJson(
        geojson,
        name='Provinces',
        style_function=style_function,
        tooltip=folium.GeoJsonTooltip(
            fields=['Name_EN'],
            aliases=['Province:'],
            localize=True
        )
    ).add_to(m)
    
    # Calculate centroids and add circle markers for IP data
    for feature in geojson['features']:
        try:
            geom = shape(feature['geometry'])
            centroid = geom.centroid
            province_name = feature['properties'].get('Name_EN', 'Unknown')
            ips = ip_data.get(province_name, 0)
            
            if ips > 0:
                # Calculate radius based on IP count  
                radius = max(3, min(20, 3 + (ips / max_ips) * 17))
                
                # Color based on IP count (using Blues palette for markers)
                marker_color = get_marker_color(ips)
                
                folium.CircleMarker(
                    location=[centroid.y, centroid.x],
                    radius=radius,
                    color=marker_color,
                    fill=True,
                    fillColor=marker_color,
                    fillOpacity=0.6,
                    weight=3,
                    popup=f"<b>{province_name}</b><br>Total IPs: {ips:,}"
                ).add_to(m)
        except Exception as e:
            print(f"Warning: Could not add marker for {feature['properties'].get('Name_EN', 'Unknown')}: {e}")
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Save map
    m.save(output_path)
    
    # Add D3 legend to the saved file (matching original style)
    add_legend_to_html(output_path, min_ips, max_ips)
    
    print(f"Map saved to {output_path}")
    
    return m


def add_legend_to_html(html_path, min_ips, max_ips):
    """Add D3 color legend to the HTML file matching original visualization.html - horizontal at top"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add D3.js library if not present
    if 'd3.min.js' not in content:
        d3_script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>\n'
        content = content.replace('</head>', d3_script + '</head>')
    
    # Calculate tick values for legend
    tick_values_province = [1]
    step = max_ips / 6
    for i in range(1, 7):
        tick_values_province.append(int(step * i))
    
    # D3 legend code - horizontal at top like original
    legend_code = f'''
    <style>
    .legend-top {{
        position: absolute;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 1000;
        background: rgba(255,255,255,0.9);
        padding: 5px 15px;
        border-radius: 4px;
        box-shadow: 0 1px 5px rgba(0,0,0,0.4);
        display: flex;
        gap: 20px;
    }}
    .legend-section {{
        display: flex;
        flex-direction: column;
        align-items: center;
    }}
    .legend-title {{
        font-size: 11px;
        font-weight: normal;
        margin-bottom: 2px;
        color: #333;
    }}
    .legend-bar {{
        display: flex;
        height: 10px;
    }}
    .legend-bar div {{
        width: 50px;
        height: 10px;
    }}
    .legend-labels {{
        display: flex;
        font-size: 9px;
        color: #666;
        position: relative;
        width: 400px;
        justify-content: space-between;
    }}
    .legend-labels span {{
        text-align: center;
        width: 0;
        display: flex;
        justify-content: center;
    }}
    </style>
    
    <script>
    // Wait for DOM to be ready
    document.addEventListener('DOMContentLoaded', function() {{
        // Create legend container
        var legendDiv = document.createElement('div');
        legendDiv.className = 'legend-top';
        legendDiv.innerHTML = `
            <div class="legend-section">
                <div class="legend-bar">
                    <div style="background: #deebf7;"></div>
                    <div style="background: #c6dbef;"></div>
                    <div style="background: #9ecae1;"></div>
                    <div style="background: #6baed6;"></div>
                    <div style="background: #4292c6;"></div>
                    <div style="background: #2171b5;"></div>
                    <div style="background: #08519c;"></div>
                    <div style="background: #084594;"></div>
                </div>
                <div class="legend-labels">
                    <span>1</span>
                    <span>{int(max_ips*0.125)}</span>
                    <span>{int(max_ips*0.25)}</span>
                    <span>{int(max_ips*0.375)}</span>
                    <span>{int(max_ips*0.5)}</span>
                    <span>{int(max_ips*0.625)}</span>
                    <span>{int(max_ips*0.75)}</span>
                    <span>{int(max_ips*0.875)}</span>
                    <span>{int(max_ips)}</span>
                </div>
                <div class="legend-title">Number of IPs by Province</div>
            </div>
            <div class="legend-section">
                <div class="legend-bar">
                    <div style="background: #ffffcc;"></div>
                    <div style="background: #ffeda0;"></div>
                    <div style="background: #fed976;"></div>
                    <div style="background: #feb24c;"></div>
                    <div style="background: #fd8d3c;"></div>
                    <div style="background: #fc4e2a;"></div>
                    <div style="background: #e31a1c;"></div>
                    <div style="background: #bd0026;"></div>
                </div>
                <div class="legend-labels">
                    <span>1</span>
                    <span>{int(max_ips*0.125)}</span>
                    <span>{int(max_ips*0.25)}</span>
                    <span>{int(max_ips*0.375)}</span>
                    <span>{int(max_ips*0.5)}</span>
                    <span>{int(max_ips*0.625)}</span>
                    <span>{int(max_ips*0.75)}</span>
                    <span>{int(max_ips*0.875)}</span>
                    <span>{int(max_ips)}</span>
                </div>
                <div class="legend-title">Number of IPs by AS</div>
            </div>
        `;
        
        // Find the map container and add legend
        var mapContainer = document.querySelector('.folium-map');
        if (mapContainer) {{
            mapContainer.style.position = 'relative';
            mapContainer.appendChild(legendDiv);
        }} else {{
            // Fallback: add to body
            document.body.insertBefore(legendDiv, document.body.firstChild);
            legendDiv.style.position = 'fixed';
        }}
    }});
    </script>
'''
    
    # Insert before </body>
    content = content.replace('</body>', legend_code + '</body>')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(content)



def main():

    html_path = '/home/twan/Downloads/quic-vn.github.io/visualization.html'
    output_path = '/home/twan/Downloads/quic-vn.github.io/visualization_34provinces.html'
    
    print("Extracting GeoJSON data...")
    geojson = extract_geojson_from_html(html_path)
    if not geojson:
        print("Error: Could not extract GeoJSON from HTML")
        return
    
    print(f"Found {len(geojson['features'])} province features")
    
    print("\nExtracting IP data...")
    ip_data = extract_ip_data_from_html(html_path)
    print(f"Found IP data for {len(ip_data)} provinces")
    
    print("\nMerging provinces...")
    merged_geojson, merged_ips = merge_provinces(geojson, ip_data)
    print(f"Merged to {len(merged_geojson['features'])} provinces")
    
    print("\nIP data after merge:")
    for name, ips in sorted(merged_ips.items(), key=lambda x: -x[1])[:10]:
        print(f"  {name}: {ips:,} IPs")
    
    print("\nCreating visualization...")
    create_visualization(merged_geojson, merged_ips, output_path)
    
    print("\nDone!")

if __name__ == "__main__":
    main()
