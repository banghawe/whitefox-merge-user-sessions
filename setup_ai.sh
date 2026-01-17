#!/bin/bash
set -e

echo "🚀 Setting up AI workspace..."

# 1. Create folders
mkdir -p ai/{agents,workflows,presets,tools}

# 2. Create files
touch \
ai/agents/core.md \
ai/agents/backend.md \
ai/agents/reviewer.md \
ai/workflows/strict.md \
ai/workflows/exploration.md \
ai/presets/backend.txt \
ai/presets/review.txt \
ai/presets/explore.txt \
ai/tools/load.sh \
ai/tools/ai-backend \
ai/tools/ai-review \
ai/tools/ai-explore

# 3. Presets
cat > ai/presets/backend.txt << 'EOF'
ai/agents/core.md
ai/workflows/strict.md
ai/agents/backend.md
EOF

cat > ai/presets/review.txt << 'EOF'
ai/agents/core.md
ai/agents/reviewer.md
EOF

cat > ai/presets/explore.txt << 'EOF'
ai/agents/core.md
ai/workflows/exploration.md
EOF

# 4. Loader
cat > ai/tools/load.sh << 'EOF'
#!/bin/bash
set -e

PRESET=$1

if [ -z "$PRESET" ]; then
  echo "Usage: load.sh <preset-file>"
  exit 1
fi

while read -r file; do
  echo ""
  echo "### SOURCE: $file"
  echo ""
  cat "$file"
  echo ""
done < "$PRESET"
EOF

# 5. One-command agents
cat > ai/tools/ai-backend << 'EOF'
#!/bin/bash
./ai/tools/load.sh ai/presets/backend.txt | pbcopy
echo "✅ Backend agent loaded into clipboard"
EOF

cat > ai/tools/ai-review << 'EOF'
#!/bin/bash
./ai/tools/load.sh ai/presets/review.txt | pbcopy
echo "✅ Review agent loaded into clipboard"
EOF

cat > ai/tools/ai-explore << 'EOF'
#!/bin/bash
./ai/tools/load.sh ai/presets/explore.txt | pbcopy
echo "✅ Exploration agent loaded into clipboard"
EOF

# 6. Make executable
chmod +x ai/tools/*

echo "🎉 AI workspace ready."
echo "Next steps:"
echo "  - Fill ai/agents/core.md"
echo "  - Fill ai/workflows/strict.md"
echo "  - Fill ai/agents/backend.md"
echo "  - Fill ai/agents/reviewer.md"
echo "  - Fill ai/workflows/exploration.md"
