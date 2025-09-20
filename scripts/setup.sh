#!/bin/bash

# Legal Document Analysis AI System - Setup Script
# This script sets up the entire development environment

set -e  # Exit on any error

echo "🚀 Setting up Legal Document Analysis AI System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8+ is required but not installed"
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js installation..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_success "Node.js $NODE_VERSION found"
    else
        print_error "Node.js 18+ is required but not installed"
        exit 1
    fi
}

# Setup backend
setup_backend() {
    print_status "Setting up backend..."
    
    cd src/backend
    
    # Create virtual environment
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
        print_warning "Please update .env file with your OpenAI API key"
    fi
    
    print_success "Backend setup complete"
    cd ../..
}

# Setup frontend
setup_frontend() {
    print_status "Setting up frontend..."
    
    cd src/frontend
    
    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install
    
    print_success "Frontend setup complete"
    cd ../..
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p uploads
    mkdir -p results
    mkdir -p logs
    
    print_success "Directories created"
}

# Main setup function
main() {
    echo "=========================================="
    echo "Legal Document Analysis AI System Setup"
    echo "=========================================="
    echo
    
    # Check prerequisites
    check_python
    check_node
    echo
    
    # Create directories
    create_directories
    echo
    
    # Setup backend
    setup_backend
    echo
    
    # Setup frontend
    setup_frontend
    echo
    
    # Final instructions
    echo "=========================================="
    print_success "Setup complete! 🎉"
    echo "=========================================="
    echo
    echo "Next steps:"
    echo "1. Update your OpenAI API key in src/backend/.env"
    echo "2. Start the backend: cd src/backend && python main.py"
    echo "3. Start the frontend: cd src/frontend && npm run dev"
    echo "4. Open http://localhost:3000 in your browser"
    echo
    echo "For more information, see README.md"
}

# Run main function
main "$@"
