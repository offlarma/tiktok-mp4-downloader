# Google AdSense Configuration
# Replace these with your actual AdSense IDs

GOOGLE_ADSENSE_CONFIG = {
    # Your Google AdSense Publisher ID
    "publisher_id": "ca-pub-XXXXXXXXXX",  # Replace with your actual publisher ID
    
    # Ad Unit IDs for different ad placements
    "ad_units": {
        "top_banner": "XXXXXXXXXX",      # Top banner 728x90
        "middle_rectangle": "XXXXXXXXXX", # Middle rectangle 300x250
        "bottom_banner": "XXXXXXXXXX",    # Bottom banner 728x90
        "footer_large": "XXXXXXXXXX",     # Footer large rectangle 336x280
    }
}

# Ad Sizes (Google AdSense standard sizes)
AD_SIZES = {
    "banner": "728x90",
    "rectangle": "300x250", 
    "large_rectangle": "336x280",
    "leaderboard": "728x90",
    "mobile_banner": "320x50",
    "mobile_rectangle": "300x250"
}

# Instructions for setup:
"""
1. Go to https://www.google.com/adsense/
2. Create an account and get approved
3. Create ad units for each placement
4. Replace the XXXXXXXXXX placeholders with your actual IDs
5. Update the simple_main.py file with your real IDs

Example:
- publisher_id: "ca-pub-1234567890123456"
- ad_units: {"top_banner": "1234567890"}
""" 