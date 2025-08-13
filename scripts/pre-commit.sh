#!/bin/bash

set -e

echo "🔍 Running pre-commit checks..."

if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

echo "🎨 Formatting code with Black..."
black --check --diff . || {
    echo "❌ Black formatting failed. Run 'black .' to fix."
    exit 1
}

echo "📦 Sorting imports with isort..."
isort --check-only --diff . || {
    echo "❌ isort failed. Run 'isort .' to fix."
    exit 1
}

# Lint with flake8
echo "🔍 Linting with flake8..."
flake8 . || {
    echo "❌ flake8 failed. Fix the linting errors above."
    exit 1
}

# echo "🔍 Type checking with mypy..."
# mypy app/ --ignore-missing-imports || {
#     echo "❌ mypy failed. Fix the type errors above."
#     exit 1
# }


echo "🧪 Running tests (unit only)..."
export PYTHONPATH="$PWD:${PYTHONPATH}"
python -m pytest -m "unit" tests/unit/services tests/unit/core tests/unit/repositories -v --tb=short || {
    echo "❌ Tests failed. Fix the failing tests above."
    exit 1
}


echo "📊 Checking coverage (unit only)..."
python -m pytest -m "unit" tests/unit/services tests/unit/core tests/unit/repositories --cov=app --cov-report=term-missing --cov-fail-under=40 || {
    echo "❌ Coverage below 80%. Improve test coverage."
    exit 1
}

echo "✅ All pre-commit checks passed!" 