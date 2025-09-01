#!/bin/bash

# EPG Update Script
# Converted from GitHub Actions workflow
# Enhanced with --stop-at functionality

set -e  # Exit on any error

# Available steps
STEPS=(
    "download-database"
    "install-python-deps"
    "install-package"
    "get-channels"
    "download-epg"
    "filter-channels"
    "install-js-deps"
    "fetch-programs"
    "fix-document"
    "merge-programs"
    "minify-xml"
    "commit-changes"
)

# Function to show usage
show_usage() {
    echo "Usage: $0 [--stop-at STEP]"
    echo ""
    echo "Options:"
    echo "  --stop-at STEP    Stop execution after the specified step"
    echo ""
    echo "Available steps:"
    for step in "${STEPS[@]}"; do
        echo "  - $step"
    done
    echo ""
    echo "Examples:"
    echo "  $0                                # Run all steps"
    echo "  $0 --stop-at get-channels        # Stop after getting channels"
    echo "  $0 --stop-at fetch-programs       # Stop after fetching programs"
}

# Parse command line arguments
STOP_AT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --stop-at)
            STOP_AT="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate stop-at argument if provided
if [[ -n "$STOP_AT" ]]; then
    valid_step=false
    for step in "${STEPS[@]}"; do
        if [[ "$step" == "$STOP_AT" ]]; then
            valid_step=true
            break
        fi
    done
    
    if [[ "$valid_step" == false ]]; then
        echo "Error: Invalid step '$STOP_AT'"
        echo ""
        show_usage
        exit 1
    fi
    
    echo "ℹ️  Will stop execution after step: $STOP_AT"
fi

# Function to check if we should stop
should_stop() {
    local current_step="$1"
    if [[ -n "$STOP_AT" && "$current_step" == "$STOP_AT" ]]; then
        echo "🛑 Stopping execution after step: $current_step"
        echo "✅ Partial EPG Update completed successfully!"
        exit 0
    fi
}

echo "Starting EPG Update process..."

# Check if required tools are available
command -v git >/dev/null 2>&1 || { echo "git is required but not installed. Aborting." >&2; exit 1; }
command -v uv >/dev/null 2>&1 || { echo "uv is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "node is required but not installed. Aborting." >&2; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "npm is required but not installed. Aborting." >&2; exit 1; }

# Clean up function
cleanup() {
    echo ""
    echo "🧹 Ready to clean up temporary directories..."
    echo "Temporary directories that will be removed:"
    if [ -d "database" ]; then
        echo "  - database/"
    fi
    if [ -d "epg" ]; then
        echo "  - epg/"
    fi
    
    # Only prompt if we have directories to clean
    if [ -d "database" ] || [ -d "epg" ]; then
        echo ""
        read -p "Press Enter to continue with cleanup (or Ctrl+C to cancel)..." -r
        echo ""
        echo "Cleaning up temporary directories..."
        
        if [ -d "database" ]; then
            echo "Removing 'database'"
            rm -rf database
        fi
        if [ -d "epg" ]; then
            echo "Removing 'epg'"
            rm -rf epg
        fi
        echo "✅ Cleanup completed"
    else
        echo "No temporary directories to clean up"
    fi
}

# Set up trap to cleanup on exit
trap cleanup EXIT

# Step 1: Download database
echo "📦 Downloading the channels database..."
if [ -d "database" ]; then
    echo "Database directory already exists, removing it first..."
    rm -rf database
fi
git clone --depth 1 https://github.com/iptv-org/database.git database
should_stop "download-database"

# Step 2: Install Python dependencies
echo "🔧 Installing Python dependencies..."
uv sync
should_stop "install-python-deps"

# Step 3: Install package
echo "📦 Installing the package..."
uv pip install -e .
should_stop "install-package"

# Step 4: Get channels ID
echo "🔍 Getting the channels ID..."
uv run filter --channels database/data/channels.csv --feeds database/data/feeds.csv --language="jpn" --country="JP" --minify channels.json
should_stop "get-channels"

# Step 5: Download EPG fetchers
echo "📡 Downloading the EPG fetchers..."
if [ -d "epg" ]; then
    echo "EPG directory already exists, removing it first..."
    rm -rf epg
fi
git clone --depth 1 https://github.com/iptv-org/epg.git epg
should_stop "download-epg"

# Step 6: Filter channels
echo "🔧 Filtering the channels..."
uv run fetcher --input channels.json --sites epg/sites japanterebi.channels.xml
should_stop "filter-channels"

# Step 7: Install JavaScript dependencies
echo "📦 Installing JavaScript dependencies..."
cd epg
npm install
cd ..
should_stop "install-js-deps"

# Step 8: Fetch programs data
echo "📺 Fetching the programs data..."
cd epg
NODE_OPTIONS=--max-old-space-size=5000 npm run grab -- --channels=../japanterebi.channels.xml --maxConnections=10 --output="../guide.xml"
cd ..
should_stop "fetch-programs"

# Step 9: Fix document
echo "🔧 Fixing the document..."
uv run fix --input guide.xml guide.xml
should_stop "fix-document"

# Step 10: Merge redundant programs
echo "🔀 Merging redundant programs..."
uv run merger --input guide.xml guide.xml
should_stop "merge-programs"

# Step 11: Minify XML
echo "📦 Minifying XML..."
uv run minify --input guide.xml guide.xml
should_stop "minify-xml"

# Step 12: Commit changes
echo "💾 Committing the new data..."
git config --global user.name 'Japan Terebi [Local Script]'
git config --global user.email 'japanterebi@users.noreply.github.com'
NOW=$(date +'%Y-%m-%dT%H:%M:%S')
git add guide.xml
git add channels.json
git add japanterebi.channels.xml

# Check if there are changes to commit
if git diff --staged --quiet; then
    echo "No changes to commit"
else
    git commit -m "Automated guide.xml update ($NOW)"
    
    # Ask user if they want to push changes
    read -p "Do you want to push changes to remote repository? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push
        echo "✅ Changes pushed successfully!"
    else
        echo "📝 Changes committed locally but not pushed"
    fi
fi
should_stop "commit-changes"

echo "🎉 EPG Update completed successfully!"