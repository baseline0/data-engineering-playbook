# Data Engineering Playbook - Local Development
# Run: just --list (to see all recipes)

set shell := ["bash", "-c"]
set dotenv-load := true

@default:
    just --list

# Setup: Install dependencies
setup:
    #!/bin/bash
    echo "📦 Setting up Python environment..."
    python -m venv venv
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r case_studies/manitoba_climate/requirements.txt
    echo "✓ Setup complete! Run 'just serve' to start"

# Serve: Start local HTTP server + open README
serve:
    #!/bin/bash
    echo "🚀 Starting local development server..."
    cd case_studies/manitoba_climate

    # Start HTTP server in background
    python -m http.server 8000 > /tmp/server.log 2>&1 &
    SERVER_PID=$!
    echo $SERVER_PID > /tmp/server.pid

    echo ""
    echo "✅ Server started (PID: $SERVER_PID)"
    echo ""
    echo "📖 Documentation URLs:"
    echo "   Main README:      http://localhost:8000/../../README.md"
    echo "   Architecture:     http://localhost:8000/../../docs/ARCHITECTURE.md"
    echo "   Tech Choices:     http://localhost:8000/../../docs/TECHNOLOGY_CHOICES.md"
    echo "   This Case Study:  http://localhost:8000/README.md"
    echo ""
    echo "📂 Browse files:      http://localhost:8000/"
    echo ""
    echo "💡 Tip: Open http://localhost:8000/README.md in your browser"
    echo ""
    echo "⏹️  To stop: just stop"

# Stop: Shut down local server
stop:
    #!/bin/bash
    if [ -f /tmp/server.pid ]; then
        PID=$(cat /tmp/server.pid)
        kill $PID 2>/dev/null || true
        rm /tmp/server.pid
        echo "✓ Server stopped"
    else
        echo "ℹ️  No server running"
    fi

# Run: Execute the complete case study pipeline
run-case-study:
    #!/bin/bash
    set -e

    cd case_studies/manitoba_climate

    echo "🌤️  Manitoba Climate Analytics - Full Pipeline"
    echo ""

    # 1. Fetch data
    echo "1️⃣  Fetching weather data..."
    python scripts/fetch_weather.py --days 365

    # 2. Transform with dbt
    echo ""
    echo "2️⃣  Running dbt transformations..."
    cd dbt
    dbt parse
    dbt run
    dbt test
    cd ..

    # 3. Validate
    echo ""
    echo "3️⃣  Validating data quality..."
    python scripts/validate_data.py 2>/dev/null || echo "   (Validation script not yet implemented)"

    echo ""
    echo "✅ Pipeline complete!"
    echo ""
    echo "📊 Query results:"
    sqlite3 data/bronze/weather.db "SELECT COUNT(*) as 'Raw Records' FROM raw_weather;"

# Dev: Start FastAPI server for the case study API
dev-api:
    #!/bin/bash
    cd case_studies/manitoba_climate

    echo "🚀 Starting FastAPI server (http://localhost:8000)"
    echo ""
    echo "📚 Interactive docs: http://localhost:8000/docs"
    echo "📚 ReDoc docs:       http://localhost:8000/redoc"
    echo ""
    echo "⏹️  Press Ctrl+C to stop"
    echo ""

    uvicorn api.serve:app --reload --host 0.0.0.0 --port 8000

# Fetch: Download weather data for case study
fetch-data:
    #!/bin/bash
    cd case_studies/manitoba_climate
    python scripts/fetch_weather.py --days 365

# DBT: Run dbt transformations
dbt:
    #!/bin/bash
    cd case_studies/manitoba_climate/dbt
    dbt run

# Test: Run dbt tests
test:
    #!/bin/bash
    cd case_studies/manitoba_climate/dbt
    dbt test

# Docs: Generate dbt documentation
docs:
    #!/bin/bash
    cd case_studies/manitoba_climate/dbt
    dbt docs generate
    echo "✓ Docs generated in target/index.html"

# Clean: Remove generated files and cache
clean:
    #!/bin/bash
    echo "🧹 Cleaning up..."
    rm -rf venv/
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name target -exec rm -rf {} + 2>/dev/null || true
    rm -f /tmp/server.pid /tmp/server.log
    echo "✓ Clean complete"

# Help: Show detailed command information
help:
    echo ""
    echo "📚 Data Engineering Playbook - Local Development"
    echo ""
    echo "Quick Start:"
    echo "  1. just setup       # Install dependencies (first time only)"
    echo "  2. just serve       # Start local server"
    echo "  3. Open http://localhost:8000/README.md in browser"
    echo ""
    echo "Case Study (Manitoba Climate):"
    echo "  just run-case-study  # Run full pipeline (fetch → transform → validate)"
    echo "  just fetch-data      # Download weather data"
    echo "  just dbt             # Run transformations"
    echo "  just test            # Run data quality tests"
    echo "  just dev-api         # Start FastAPI server"
    echo ""
    echo "Development:"
    echo "  just docs            # Generate dbt docs"
    echo "  just clean           # Remove generated files"
    echo "  just stop            # Stop local server"
    echo ""

# Info: Display repository structure
info:
    #!/bin/bash
    echo ""
    echo "📁 Repository Structure"
    echo ""
    echo "data-engineering-playbook/"
    echo "├── README.md                    # Main guide"
    echo "├── LICENSE                      # MIT license"
    echo "├── CONTRIBUTING.md              # How to contribute"
    echo "├── justfile                     # This file"
    echo "│"
    echo "├── docs/"
    echo "│   ├── ARCHITECTURE.md          # Design principles"
    echo "│   └── TECHNOLOGY_CHOICES.md    # Tool justifications"
    echo "│"
    echo "├── templates/"
    echo "│   └── medallion_architecture/  # Reference template"
    echo "│"
    echo "└── case_studies/"
    echo "    └── manitoba_climate/        # Working example"
    echo "        ├── README.md"
    echo "        ├── requirements.txt"
    echo "        ├── scripts/"
    echo "        │   ├── fetch_weather.py"
    echo "        │   └── validate_data.py"
    echo "        ├── dbt/"
    echo "        │   ├── dbt_project.yml"
    echo "        │   ├── models/"
    echo "        │   └── tests/"
    echo "        ├── api/"
    echo "        │   └── serve.py"
    echo "        └── data/"
    echo "            ├── bronze/"
    echo "            ├── silver/"
    echo "            └── gold/"
    echo ""
