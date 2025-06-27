# Development Guide

This guide provides detailed instructions for setting up and working with the SQLFluff.com website.

## Prerequisites

- [Hugo](https://gohugo.io/) v0.125.4 or later
- Git
- Text editor (VS Code, Cursor, etc.)

## Initial Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/sqlfluff/sqlfluff.com.git
   cd sqlfluff.com
   ```

2. **Initialize the theme submodule:**

   ```bash
   git submodule update --init --recursive
   ```

3. **Install Hugo:**
   - macOS: `brew install hugo`
   - Windows: `choco install hugo` or download from [releases](https://github.com/gohugoio/hugo/releases)
   - Linux: `sudo apt install hugo` or download from releases

4. **Verify installation:**

   ```bash
   hugo version
   ```

## Development Workflow

### Start Development Server

```bash
hugo server
```

- Opens at `http://localhost:1313`
- Auto-reloads on file changes
- Includes draft content

### Build for Production

```bash
hugo --gc --minify
```

- Outputs to `public/` directory
- Garbage collects unused cache files
- Minifies CSS, JS, and HTML

## Project Structure

```
sqlfluff.com/
├── hugo.toml          # Main configuration
├── layouts/           # Custom templates
│   └── index.html     # Homepage override
├── static/            # Static assets
│   ├── css/          # Custom stylesheets
│   ├── img/          # Images and logos
│   └── svg/          # SVG icons
├── themes/gokarna/    # Theme submodule
└── netlify.toml      # Deployment config
```

## Common Tasks

### Update Theme

```bash
git submodule update --remote themes/gokarna
git add themes/gokarna
git commit -m "Update Gokarna theme"
```

### Add New Content

1. Create markdown files in `content/` directory
2. Use Hugo front matter for metadata
3. Test locally with `hugo server`

### Modify Styling

- Edit `static/css/sqlfluff.css` for custom styles
- Changes auto-reload in development mode
- Follow existing naming conventions

### Update Configuration

- Edit `hugo.toml` for site-wide settings
- Restart development server after config changes

## Deployment

- Automatic deployment via Netlify on push to `main`
- Build command: `hugo --gc --minify`
- Deploy previews available for pull requests

## Troubleshooting

### Theme Issues

- Ensure submodule is initialized: `git submodule status`
- Update submodule: `git submodule update --remote`

### Build Failures

- Check Hugo version compatibility
- Verify all required files are present
- Review Netlify build logs

### Local Development Issues

- Clear Hugo cache: `rm -rf resources/`
- Restart development server
- Check for syntax errors in templates

## Code Style

- Use 2 spaces for indentation
- Follow semantic HTML5 practices
- Maintain accessibility standards
- Keep CSS organized and well-commented
- Use meaningful commit messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

For questions or help, join the SQLFluff Slack community or open an issue on GitHub. 
