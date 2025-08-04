
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' 

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

show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -a, --all              Run all tests (unit + integration)"
    echo "  -u, --unit             Run only unit tests"
    echo "  -i, --integration      Run only integration tests"
    echo "  -c, --coverage         Run with coverage report"
    echo "  -v, --verbose          Run with verbose output"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --all               # Run all tests with coverage"
    echo "  $0 --unit              # Run only unit tests"
    echo "  $0 --integration -v    # Run integration tests with verbose output"
    echo "  $0 --unit --coverage   # Run unit tests with coverage report"
}

RUN_ALL=false
RUN_UNIT=false
RUN_INTEGRATION=false
WITH_COVERAGE=true
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--all)
            RUN_ALL=true
            shift
            ;;
        -u|--unit)
            RUN_UNIT=true
            shift
            ;;
        -i|--integration)
            RUN_INTEGRATION=true
            shift
            ;;
        -c|--coverage)
            WITH_COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

if [[ "$RUN_ALL" == false && "$RUN_UNIT" == false && "$RUN_INTEGRATION" == false ]]; then
    RUN_ALL=true
fi

# Build pytest command
PYTEST_CMD="PYTHONPATH=$PYTHONPATH:. pytest"


PYTEST_CMD="$PYTEST_CMD -q --tb=short"


if [[ "$VERBOSE" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD -v"
fi

if [[ "$WITH_COVERAGE" == true ]]; then
    PYTEST_CMD="$PYTEST_CMD --cov=app --cov-report=html --cov-report=term"
fi

run_tests() {
    local test_path="$1"
    local test_name="$2"
    
    print_status "Running $test_name..."
    echo "Command: $PYTEST_CMD $test_path"
    echo ""
    
    if eval "$PYTEST_CMD $test_path"; then
        print_success "$test_name completed successfully!"
        return 0
    else
        print_error "$test_name failed!"
        return 1
    fi
}

echo "=========================================="
echo "           EQ Test Backend Tests"
echo "=========================================="
echo ""

if [[ ! -d "tests" ]]; then
    print_error "Tests directory not found!"
    exit 1
fi

OVERALL_SUCCESS=true

if [[ "$RUN_ALL" == true ]]; then
    print_status "Running all tests..."
    echo ""
    
    if [[ -d "tests/unit" ]]; then
        if ! run_tests "tests/unit" "Unit Tests"; then
            OVERALL_SUCCESS=false
        fi
    else
        print_warning "Unit tests directory not found. Skipping unit tests."
    fi
    
    echo ""
    
    if [[ -d "tests/integration" ]]; then
        if ! run_tests "tests/integration" "Integration Tests"; then
            OVERALL_SUCCESS=false
        fi
    else
        print_warning "Integration tests directory not found. Skipping integration tests."
    fi
    
elif [[ "$RUN_UNIT" == true ]]; then
    if [[ -d "tests/unit" ]]; then
        run_tests "tests/unit" "Unit Tests"
        OVERALL_SUCCESS=$?
    else
        print_error "Unit tests directory not found!"
        exit 1
    fi
    
elif [[ "$RUN_INTEGRATION" == true ]]; then
    if [[ -d "tests/integration" ]]; then
        run_tests "tests/integration" "Integration Tests"
        OVERALL_SUCCESS=$?
    else
        print_error "Integration tests directory not found!"
        exit 1
    fi
fi

echo ""
echo "=========================================="

if [[ "$OVERALL_SUCCESS" == true ]]; then
    print_success "All tests completed successfully! 🎉"
    if [[ "$WITH_COVERAGE" == true ]]; then
        echo ""
        print_status "Coverage report generated in htmlcov/index.html"
    fi
    exit 0
else
    print_error "Some tests failed! ❌"
    exit 1
fi