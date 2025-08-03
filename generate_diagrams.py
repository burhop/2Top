#!/usr/bin/env python3
"""
Generate PNG images from PlantUML files using the online PlantUML server.
"""

import os
import base64
import zlib
import urllib.request
import urllib.parse

def plantuml_encode(plantuml_text):
    """Encode PlantUML text for URL using deflate encoding."""
    # Use deflate compression (not zlib which adds headers)
    import zlib
    compressed = zlib.compress(plantuml_text.encode('utf-8'))[2:-4]  # Remove zlib headers
    # Base64 encode
    encoded = base64.b64encode(compressed).decode('ascii')
    # Replace characters for URL safety
    encoded = encoded.replace('+', '-').replace('/', '_')
    return encoded

def generate_diagram(puml_file, output_dir='.'):
    """Generate PNG from PlantUML file using online server."""
    print(f"Processing {puml_file}...")
    
    # Read the PlantUML file
    with open(puml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Encode for PlantUML server
    encoded = plantuml_encode(content)
    
    # Create URL for PlantUML server with deflate encoding
    url = f"http://www.plantuml.com/plantuml/png/~1{encoded}"
    
    # Generate output filename
    base_name = os.path.splitext(os.path.basename(puml_file))[0]
    output_file = os.path.join(output_dir, f"{base_name}.png")
    
    try:
        # Download the image
        urllib.request.urlretrieve(url, output_file)
        print(f"Generated: {output_file}")
        return True
    except Exception as e:
        print(f"Error generating {output_file}: {e}")
        return False

def main():
    """Generate all PlantUML diagrams in current directory."""
    puml_files = [f for f in os.listdir('.') if f.endswith('.puml')]
    
    if not puml_files:
        print("No .puml files found in current directory")
        return
    
    print(f"Found {len(puml_files)} PlantUML files:")
    for f in puml_files:
        print(f"  - {f}")
    
    print("\nGenerating diagrams...")
    success_count = 0
    
    for puml_file in puml_files:
        if generate_diagram(puml_file):
            success_count += 1
    
    print(f"\nCompleted: {success_count}/{len(puml_files)} diagrams generated successfully")

if __name__ == "__main__":
    main()
