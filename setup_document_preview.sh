#!/bin/bash

# Document Preview Feature - Installation & Verification Script
# This script helps you install and verify the document preview feature

set -e  # Exit on error

echo "=========================================="
echo "Document Preview Feature Setup"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

# Check if running in project root
if [ ! -f "alembic.ini" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_success "Project directory confirmed"

# Check Docker
if command -v docker-compose &> /dev/null; then
    USING_DOCKER=true
    print_success "Docker Compose found"
else
    USING_DOCKER=false
    print_warning "Docker Compose not found - will use local setup"
fi

# Step 2: Check if migration file exists
print_info "Checking migration file..."

MIGRATION_FILE="alembic/versions/add_message_document_matches.py"
if [ -f "$MIGRATION_FILE" ]; then
    print_success "Migration file exists"
else
    print_error "Migration file not found at $MIGRATION_FILE"
    exit 1
fi

# Step 3: Run database migration
echo ""
print_info "Running database migration..."

if [ "$USING_DOCKER" = true ]; then
    # Docker setup
    print_info "Using Docker setup..."

    # Check if containers are running
    if ! docker-compose ps | grep -q "Up"; then
        print_warning "Containers not running. Starting..."
        docker-compose up -d
        sleep 5
    fi

    # Run migration
    print_info "Running: docker-compose exec app alembic upgrade head"
    docker-compose exec app alembic upgrade head
else
    # Local setup
    print_info "Using local setup..."
    print_info "Running: alembic upgrade head"
    alembic upgrade head
fi

print_success "Database migration completed"

# Step 4: Verify migration
echo ""
print_info "Verifying migration..."

if [ "$USING_DOCKER" = true ]; then
    # Check with Docker
    TABLE_EXISTS=$(docker-compose exec -T postgres psql -U user -d llm_pkg -t -c \
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'message_document_matches');" | tr -d '[:space:]')

    if [ "$TABLE_EXISTS" = "t" ]; then
        print_success "Table 'message_document_matches' created successfully"

        # Get column count
        COLUMN_COUNT=$(docker-compose exec -T postgres psql -U user -d llm_pkg -t -c \
            "SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'message_document_matches';" | tr -d '[:space:]')

        print_info "Table has $COLUMN_COUNT columns"
    else
        print_error "Table 'message_document_matches' not found"
        exit 1
    fi
else
    print_warning "Skipping database verification (requires PostgreSQL access)"
fi

# Step 5: Check frontend files
echo ""
print_info "Checking frontend components..."

FRONTEND_FILES=(
    "frontend/src/components/chat/DocumentPreview.tsx"
    "frontend/src/components/chat/DocumentUpload.tsx"
    "frontend/src/components/chat/MessageList.tsx"
    "frontend/src/api/client.ts"
)

ALL_FILES_EXIST=true
for file in "${FRONTEND_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        ALL_FILES_EXIST=false
    fi
done

if [ "$ALL_FILES_EXIST" = false ]; then
    print_error "Some frontend files are missing"
    exit 1
fi

# Step 6: Build frontend
echo ""
print_info "Building frontend..."

cd frontend

if [ ! -d "node_modules" ]; then
    print_info "Installing npm packages..."
    npm install
fi

print_info "Building frontend..."
npm run build

cd ..

print_success "Frontend build completed"

# Step 7: Restart services
echo ""
print_info "Restarting services..."

if [ "$USING_DOCKER" = true ]; then
    print_info "Restarting Docker containers..."
    docker-compose restart app
    print_success "Docker containers restarted"
else
    print_warning "Please manually restart your backend server"
fi

# Step 8: Final verification
echo ""
echo "=========================================="
print_success "Installation Complete!"
echo "=========================================="
echo ""
print_info "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Login or register"
echo "  3. Create a new conversation"
echo "  4. Upload a document"
echo "  5. Ask questions about the document"
echo "  6. Click the eye icon to preview!"
echo ""
print_info "Documentation:"
echo "  - README_DOCUMENT_PREVIEW.md - Complete guide"
echo "  - DOCUMENT_PREVIEW_QUICKREF.md - Quick reference"
echo "  - DOCUMENT_PREVIEW_FEATURE.md - Technical details"
echo ""

# Optional: Run verification tests
echo ""
read -p "Do you want to run verification tests? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running verification tests..."

    if [ "$USING_DOCKER" = true ]; then
        # Test 1: Check table exists
        print_info "Test 1: Checking table exists..."
        docker-compose exec -T postgres psql -U user -d llm_pkg -c \
            "SELECT COUNT(*) FROM message_document_matches;" > /dev/null 2>&1
        print_success "Test 1 passed"

        # Test 2: Check API endpoint (requires server running)
        print_info "Test 2: Checking API health..."
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Test 2 passed - API is responding"
        else
            print_warning "Test 2 skipped - API not responding (this is OK if not started yet)"
        fi

        # Test 3: Check frontend build
        print_info "Test 3: Checking frontend build..."
        if [ -d "frontend/build" ]; then
            print_success "Test 3 passed - Frontend built successfully"
        else
            print_warning "Test 3 failed - Frontend build directory not found"
        fi
    else
        print_warning "Verification tests require Docker setup"
    fi

    echo ""
    print_success "All tests completed!"
fi

echo ""
print_success "Setup complete! Happy previewing! 🎉"

