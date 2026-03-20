from PIL import Image, ImageDraw, ImageFont

# Settings
text = "Tiders"
font_path = "BinaryWaters.ttf"  # Ensure the file is in your folder
font_size = 100
font_color = (52, 115, 173, 255)  # RGBA (Red in this example)

# Load font
font = ImageFont.truetype(font_path, font_size)

# Calculate text size for the canvas
# getbbox returns (left, top, right, bottom)
left, top, right, bottom = font.getbbox(text)
width = right - left
height = bottom - top

# Create image with transparent background (0 alpha)
img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw text (offsetting by 'left' and 'top' to avoid clipping)
draw.text((-left, -top), text, font=font, fill=font_color)

# Save
img.save("tiders_logo.png")
