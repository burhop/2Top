#!/usr/bin/env python3
"""
Generate PNG images from PlantUML files using a simpler approach.
"""

import os
import subprocess
import urllib.request

def download_plantuml_jar():
    """Download PlantUML JAR if not present."""
    jar_file = "plantuml.jar"
    if os.path.exists(jar_file):
        print(f"PlantUML JAR already exists: {jar_file}")
        return jar_file
    
    print("Downloading PlantUML JAR...")
    url = "https://github.com/plantuml/plantuml/releases/download/v1.2024.6/plantuml-1.2024.6.jar"
    
    try:
        urllib.request.urlretrieve(url, jar_file)
        print(f"Downloaded: {jar_file}")
        return jar_file
    except Exception as e:
        print(f"Error downloading PlantUML JAR: {e}")
        return None

def generate_with_jar(jar_file):
    """Generate diagrams using local PlantUML JAR."""
    puml_files = [f for f in os.listdir('.') if f.endswith('.puml')]
    
    if not puml_files:
        print("No .puml files found")
        return False
    
    print(f"Generating diagrams for {len(puml_files)} files using JAR...")
    
    try:
        # Run PlantUML on all .puml files
        cmd = ["java", "-jar", jar_file] + puml_files
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Successfully generated diagrams with JAR")
            return True
        else:
            print(f"JAR generation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Error running JAR: {e}")
        return False

def generate_simple_text_diagrams():
    """Create simple text-based diagram descriptions as fallback."""
    puml_files = [f for f in os.listdir('.') if f.endswith('.puml')]
    
    print("Creating text descriptions of diagrams...")
    
    for puml_file in puml_files:
        base_name = os.path.splitext(puml_file)[0]
        txt_file = f"{base_name}_description.txt"
        
        with open(puml_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title and basic structure
        lines = content.split('\n')
        title = "Diagram"
        elements = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('title '):
                title = line[6:]
            elif 'usecase ' in line or 'component ' in line or 'class ' in line:
                elements.append(line)
        
        description = f"# {title}\n\n"
        description += f"Source file: {puml_file}\n\n"
        description += "Key elements:\n"
        for element in elements[:10]:  # Limit to first 10 elements
            description += f"- {element}\n"
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(description)
        
        print(f"Created description: {txt_file}")

def main():
    """Main function to generate diagrams."""
    print("PlantUML Diagram Generator")
    print("=" * 30)
    
    # Try to download and use JAR first
    jar_file = download_plantuml_jar()
    
    if jar_file and generate_with_jar(jar_file):
        print("\n✓ Diagrams generated successfully using JAR!")
    else:
        print("\n⚠ JAR method failed, creating text descriptions instead...")
        generate_simple_text_diagrams()
    
    # List generated files
    png_files = [f for f in os.listdir('.') if f.endswith('.png') and 'UML_' in f]
    txt_files = [f for f in os.listdir('.') if f.endswith('_description.txt')]
    
    if png_files:
        print(f"\nGenerated PNG files:")
        for f in png_files:
            print(f"  - {f}")
    
    if txt_files:
        print(f"\nGenerated description files:")
        for f in txt_files:
            print(f"  - {f}")

if __name__ == "__main__":
    main()
