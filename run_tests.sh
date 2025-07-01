#!/bin/bash

# Version System - Test Runner Script
# Usage: ./run_tests.sh [option]
# Options: unit, integration, coverage, all, report

set -e

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

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -d "tests" ]; then
    print_error "Please run this script from the improvements directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    print_warning "Virtual environment not detected. Attempting to activate..."
    if [ -f "../venv/bin/activate" ]; then
        source ../venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found. Please activate it manually."
        exit 1
    fi
fi

# Function to run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    python -m pytest tests/unit/ -v
    if [ $? -eq 0 ]; then
        print_success "Unit tests passed"
        return 0
    else
        print_error "Unit tests failed"
        return 1
    fi
}

# Function to run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    python test_integration.py
    if [ $? -eq 0 ]; then
        print_success "Integration tests passed"
        return 0
    else
        print_error "Integration tests failed"
        return 1
    fi
}

# Function to run coverage tests
run_coverage_tests() {
    print_status "Running tests with coverage..."
    python -m pytest tests/unit/ --cov=src --cov-report=term-missing --cov-report=html
    if [ $? -eq 0 ]; then
        print_success "Coverage tests completed"
        print_status "HTML coverage report generated in htmlcov/"
        return 0
    else
        print_error "Coverage tests failed"
        return 1
    fi
}

# Function to generate full report
generate_report() {
    print_status "Generating comprehensive test report..."
    python generate_test_report.py
    if [ $? -eq 0 ]; then
        print_success "Test report generated"
        return 0
    else
        print_error "Test report generation failed"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status "Running all tests..."
    
    # Run unit tests
    if ! run_unit_tests; then
        return 1
    fi
    
    # Run integration tests
    if ! run_integration_tests; then
        return 1
    fi
    
    # Run coverage
    if ! run_coverage_tests; then
        return 1
    fi
    
    print_success "All tests completed successfully!"
    return 0
}

# Function to show usage
show_usage() {
    echo "Version System - Test Runner"
    echo ""
    echo "Usage: $0 [option]"
    echo ""
    echo "Options:"
    echo "  unit        Run unit tests only"
    echo "  integration Run integration tests only"
    echo "  coverage    Run tests with coverage report"
    echo "  all         Run all tests (default)"
    echo "  report      Generate comprehensive test report"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all tests"
    echo "  $0 unit         # Run only unit tests"
    echo "  $0 coverage     # Run with coverage"
    echo "  $0 report       # Generate full report"
}

# Main script logic
case "${1:-all}" in
    "unit")
        run_unit_tests
        exit $?
        ;;
    "integration")
        run_integration_tests
        exit $?
        ;;
    "coverage")
        run_coverage_tests
        exit $?
        ;;
    "all")
        run_all_tests
        exit $?
        ;;
    "report")
        generate_report
        exit $?
        ;;
    "help"|"-h"|"--help")
        show_usage
        exit 0
        ;;
    *)
        print_error "Unknown option: $1"
        show_usage
        exit 1
        ;;
esac
