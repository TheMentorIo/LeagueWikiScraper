from PIL import Image, ImageDraw, ImageFilter

# Open your image
img = Image.open("test.jpg").convert("RGBA")
width, height = img.size

# Border and blur settings
border_thickness = 10
blur_radius = 10

# Create a black mask starting fully transparent
mask = Image.new("L", (width, height), 0)
draw = ImageDraw.Draw(mask)

# Draw a filled white rectangle slightly inset (the inner part stays bright)
draw.rectangle(
    [border_thickness, border_thickness, width - border_thickness, height - border_thickness],
    fill=255
)

# Apply Gaussian blur to fade from white (visible) to black (overlay)
mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

# Create a solid black overlay
black_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 255))

# Composite the original image and the black overlay using the mask
final = Image.composite(img, black_overlay, mask)

# Save the result
final.save("ahri_bordered.png")
