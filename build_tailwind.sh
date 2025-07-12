#!/bin/bash

# Build script for Tailwind CSS
# This script downloads the latest Tailwind CSS from CDN and saves it locally

echo "Building Tailwind CSS..."

# Download Tailwind CSS from CDN with follow redirects
curl -L https://cdn.tailwindcss.com -o src/res/tailwind.css

echo "Tailwind CSS built successfully!"
echo "File saved to: src/res/tailwind.css" 