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
    merged_features = {}
    merged_ips = defaultdict(int)
    
    # Group features by merged province name
    province_features = defaultdict(list)
    for feature in geojson['features']:
        old_name = feature['properties'].get('Name_EN') or feature['properties'].get('Name_VI', 'Unknown')
        new_name = get_merged_name(old_name)
        province_features[new_name].append(feature)
    
    # Merge geometries
    for new_name, features in province_features.items():
        if len(features) == 1:
            # Single province, no merge needed
            merged_features[new_name] = features[0]
        else:
            # Merge multiple provinces
            geometries = []
            for f in features:
                try:
                    geom = shape(f['geometry'])
                    if geom.is_valid:
                        geometries.append(geom)
                    else:
                        geometries.append(geom.buffer(0))  # Fix invalid geometry
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
                    merged_features[new_name] = merged_feature
                except Exception as e:
                    print(f"Warning: Could not merge geometries for {new_name}: {e}")
                    merged_features[new_name] = features[0]  # Use first feature as fallback
    
    # Aggregate IP data
    for old_name, ip_count in ip_data.items():
        new_name = get_merged_name(old_name)
        merged_ips[new_name] += ip_count
    
    # Create new GeoJSON
    new_geojson = {
        'type': 'FeatureCollection',
        'features': list(merged_features.values())
    }
    
    return new_geojson, dict(merged_ips)

def create_visualization(geojson, ip_data, output_path):
    """Create Folium map with merged provinces - matching original style"""
    # Create base map centered on Vietnam
    m = folium.Map(location=[16.0, 108.0], zoom_start=6, tiles='cartodbpositron')
    
    # Calculate max IPs for color scaling
    max_ips = max(ip_data.values()) if ip_data else 1
    min_ips = min(ip_data.values()) if ip_data else 0
    
    # YlOrRd color palette (matching original visualization.html)
    def get_color(ips):
        if ips == 0:
            return 'black'  # No data - black like original
        
        # Normalize to 0-1 range
        ratio = min(1.0, ips / max_ips)
        
        # YlOrRd gradient: #ffffcc -> #fed976 -> #fd8d3c -> #e31a1c -> #bd0026
        if ratio < 0.01:
            return '#ffffb2'  # Very light yellow
        elif ratio < 0.05:
            return '#fed976'  # Light orange
        elif ratio < 0.1:
            return '#feb24c'  # Orange
        elif ratio < 0.2:
            return '#fd8d3c'  # Darker orange
        elif ratio < 0.4:
            return '#fc4e2a'  # Red-orange
        elif ratio < 0.6:
            return '#e31a1c'  # Red
        else:
            return '#bd0026'  # Dark red
    
    # Define style function for provinces
    def style_function(feature):
        province_name = feature['properties'].get('Name_EN', 'Unknown')
        ips = ip_data.get(province_name, 0)
        fill_color = get_color(ips)
        
        return {
            'fillColor': fill_color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.7,
            'opacity': 0.2
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
                
                # Color based on IP count (matching YlOrRd)
                marker_color = get_color(ips)
                
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
    """Add D3 color legend to the HTML file matching original visualization.html"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add D3.js library if not present
    if 'd3.min.js' not in content:
        d3_script = '<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>\n'
        content = content.replace('</head>', d3_script + '</head>')
    
    # Generate legend values
    num_steps = 8
    step = (max_ips - 1) / num_steps
    tick_values = [1.0]
    for i in range(1, num_steps + 1):
        tick_values.append(round(1 + step * i, 1))
    
    # D3 legend code matching original
    legend_code = f'''
    <script>
    // Color legend
    var color_map = {{}};
    
    color_map.color = d3.scale.threshold()
        .domain([1, {max_ips * 0.01}, {max_ips * 0.05}, {max_ips * 0.1}, {max_ips * 0.2}, {max_ips * 0.4}, {max_ips * 0.6}, {max_ips}])
        .range(['black', '#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026']);
    
    color_map.x = d3.scale.linear()
        .domain([1, {max_ips}])
        .range([0, 400]);

    color_map.legend = L.control({{position: 'topright'}});
    color_map.legend.onAdd = function (map) {{
        var div = L.DomUtil.create('div', 'legend');
        div.innerHTML = '<div style="background: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.2);">' +
            '<div style="font-weight: bold; margin-bottom: 5px;">Number of IPs by Province</div>' +
            '<svg id="legend" width="420" height="50"></svg></div>';
        return div;
    }};
    
    // Wait for map to be ready
    setTimeout(function() {{
        // Find the map object
        var mapObj = null;
        for (var key in window) {{
            if (key.startsWith('map_') && window[key]._leaflet_id) {{
                mapObj = window[key];
                break;
            }}
        }}
        
        if (mapObj) {{
            color_map.legend.addTo(mapObj);
            
            var svg = d3.select("#legend");
            var g = svg.append("g")
                .attr("class", "key")
                .attr("transform", "translate(10,20)");
            
            // Color rectangles
            var colors = ['black', '#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026'];
            var labels = ['No data', '1-{int(max_ips*0.01)}', '{int(max_ips*0.01)}-{int(max_ips*0.05)}', '{int(max_ips*0.05)}-{int(max_ips*0.1)}', '{int(max_ips*0.1)}-{int(max_ips*0.2)}', '{int(max_ips*0.2)}-{int(max_ips*0.4)}', '{int(max_ips*0.4)}-{int(max_ips*0.6)}', '>{int(max_ips*0.6)}'];
            
            g.selectAll("rect")
                .data(colors)
                .enter().append("rect")
                .attr("x", function(d, i) {{ return i * 50; }})
                .attr("width", 48)
                .attr("height", 15)
                .style("fill", function(d) {{ return d; }});
            
            g.selectAll("text")
                .data(labels)
                .enter().append("text")
                .attr("x", function(d, i) {{ return i * 50 + 24; }})
                .attr("y", 28)
                .attr("text-anchor", "middle")
                .style("font-size", "9px")
                .text(function(d) {{ return d; }});
        }}
    }}, 1000);
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
