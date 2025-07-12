# Tailwind CSS Setup

## Overview
Tailwind CSS has been added to the SageMath website project for modern utility-first styling.

## Files Added/Modified

### Configuration Files
- `tailwind.config.js` - Tailwind configuration
- `src/res/tailwind.input.css` - Tailwind directives (for future use)
- `package.json` - Added build scripts and dependencies

### Build Scripts
- `build_tailwind.sh` - Downloads Tailwind CSS from CDN
- `test_tailwind.html` - Test file to verify Tailwind is working

### Template Changes
- `templates/base.html` - Added Tailwind CSS link

## Usage

### Building Tailwind CSS
```bash
# Using npm script
npm run build:css

# Or directly
./build_tailwind.sh
```

### Using Tailwind Classes
You can now use Tailwind utility classes in any HTML template:

```html
<div class="bg-blue-500 text-white p-4 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-2">Hello Tailwind!</h1>
    <p class="text-blue-100">This is styled with Tailwind CSS.</p>
</div>
```

### Testing
Open `test_tailwind.html` in a browser to verify Tailwind CSS is working correctly.

## Current Setup

### CDN Approach
Currently using Tailwind CSS from CDN for simplicity. The `build_tailwind.sh` script downloads the latest version.

### Future Improvements
1. **Local Build**: Set up proper local Tailwind build process
2. **Purge CSS**: Remove unused styles for production
3. **Custom Configuration**: Add custom colors, fonts, etc.
4. **Watch Mode**: Auto-rebuild on file changes

## Integration with Existing CSS

Tailwind CSS is loaded after the existing `sage.css` file, so:
- Tailwind utilities will override existing styles when needed
- Existing custom CSS remains intact
- You can use both approaches together

## Example Usage in Templates

```html
<!-- Modern button styling -->
<a href="{{ url }}" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200">
    Download {{ sage }}
</a>

<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    <div class="bg-white p-6 rounded-lg shadow-md">
        <!-- Content -->
    </div>
</div>

<!-- Modern card -->
<div class="max-w-sm mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
    <div class="p-6">
        <h3 class="text-xl font-semibold text-gray-800">Feature</h3>
        <p class="mt-2 text-gray-600">Description here.</p>
    </div>
</div>
```

## Notes

- The current setup uses the full Tailwind CSS (not purged)
- For production, consider setting up a proper build process with PostCSS
- Tailwind classes are available in all templates that extend `base.html` 