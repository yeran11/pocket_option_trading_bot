#!/usr/bin/env python3
"""
Generate favicon files from logo image
"""

from PIL import Image
import os

def create_favicon():
    """Create multiple favicon sizes from logo"""

    logo_path = 'static/images/logo.png'

    if not os.path.exists(logo_path):
        print(f"❌ Logo not found at {logo_path}")
        return False

    print(f"📸 Loading logo from {logo_path}")

    try:
        # Open the logo
        img = Image.open(logo_path)
        print(f"✅ Loaded logo: {img.size} pixels, mode: {img.mode}")

        # Convert to RGBA if needed
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Create different favicon sizes
        sizes = [16, 32, 48, 64, 128, 256]

        # Save as ICO (multi-size)
        icon_images = []
        for size in sizes:
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            icon_images.append(resized)

        favicon_path = 'static/favicon.ico'
        icon_images[0].save(
            favicon_path,
            format='ICO',
            sizes=[(s, s) for s in sizes],
            append_images=icon_images[1:]
        )
        print(f"✅ Created favicon.ico with sizes: {sizes}")

        # Also create PNG favicons for modern browsers
        for size in [16, 32, 192, 512]:
            png_path = f'static/favicon-{size}x{size}.png'
            resized = img.resize((size, size), Image.Resampling.LANCZOS)
            resized.save(png_path, format='PNG')
            print(f"✅ Created {png_path}")

        # Create apple-touch-icon
        apple_icon = img.resize((180, 180), Image.Resampling.LANCZOS)
        apple_icon.save('static/apple-touch-icon.png', format='PNG')
        print(f"✅ Created apple-touch-icon.png")

        print("\n🎉 All favicon files created successfully!")
        return True

    except Exception as e:
        print(f"❌ Error creating favicons: {e}")
        return False

if __name__ == "__main__":
    create_favicon()
