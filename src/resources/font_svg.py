from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import ControlBoundsPen
import svgwrite

def save_letter_as_svg(font_path, letter, output_file):
    font = TTFont(font_path)
    glyph_set = font.getGlyphSet()
    
    # 1. Get the glyph name
    cmap = font.getBestCmap()
    if ord(letter) not in cmap:
        print(f"Character '{letter}' not found in font.")
        return
        
    glyph_name = cmap[ord(letter)]
    glyph = glyph_set[glyph_name]
    
    # 2. Calculate bounds using the ControlBoundsPen
    # This pen calculates the bounding box as it "draws" the glyph
    bounds_pen = ControlBoundsPen(glyph_set)
    glyph.draw(bounds_pen)
    bbox = bounds_pen.bounds  # Returns (xMin, yMin, xMax, yMax)
    
    if not bbox:
        print("Glyph has no bounds.")
        return

    x_min, y_min, x_max, y_max = bbox
    width = x_max - x_min
    height = y_max - y_min
    
    # 3. Convert glyph to SVG path data
    svg_pen = SVGPathPen(glyph_set)
    glyph.draw(svg_pen)
    path_data = svg_pen.getCommands()
    
    # 4. Create the SVG
    dwg = svgwrite.Drawing(output_file, profile='tiny', size=(width, height))
    
    # Handle the Y-flip in the viewbox:
    # Font coordinates: Y is up. SVG coordinates: Y is down.
    # When we scale(1, -1), the top of the letter (y_max) becomes the bottom (-y_max)
    dwg.viewbox(minx=x_min, miny=-y_max, width=width, height=height)
    
    # 5. Add the path with the vertical flip
    group = dwg.g(transform="scale(1, -1)")
    group.add(dwg.path(d=path_data, fill='#3473ad'))
    
    dwg.add(group)
    dwg.save()
    print(f"Successfully saved {output_file} ({int(width)}x{int(height)})")

save_letter_as_svg("BinaryWaters.ttf", "T", "tiders_logo.svg")