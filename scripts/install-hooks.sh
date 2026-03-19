#!/bin/bash
# Install post-commit hook for plugin cache sync
# Run once: bash scripts/install-hooks.sh

HOOK=".git/hooks/post-commit"

# Dynamically find the plugin cache directory
CACHE_DIR=$(find "$HOME/.claude/plugins/cache" -path "*/superscraper/*/skills" -maxdepth 5 2>/dev/null | head -1 | sed 's|/skills$||')

if [ -z "$CACHE_DIR" ]; then
    echo "⚠ Plugin cache not found. Skipping hook installation."
    echo "  Make sure the plugin is installed via Claude Code first."
    exit 0
fi

cat > "$HOOK" << EOF
#!/bin/bash
# Auto-sync plugin files to Claude Code cache after each commit
CACHE_DIR="$CACHE_DIR"
if [ -d "\$CACHE_DIR" ]; then
    cp -r skills agents commands hooks .claude-plugin "\$CACHE_DIR/" 2>/dev/null
    echo "✓ Plugin cache synced to \$CACHE_DIR"
fi
EOF

chmod +x "$HOOK"
echo "✓ Post-commit hook installed"
echo "  Cache: $CACHE_DIR"
echo "  Hook: $HOOK"
