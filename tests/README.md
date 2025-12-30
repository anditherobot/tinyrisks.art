# Test Suite for TinyRisks.art

This directory contains comprehensive test cases for the TinyRisks.art Flask application.

## Test Coverage

### 1. Image Upload Tests (`test_image_upload.py`)
- **Valid image uploads**: Tests uploading PNG, JPG, JPEG, GIF, and WEBP files
- **Invalid uploads**: Tests rejection of invalid file types (TXT, PDF, EXE)
- **Edge cases**: Empty filenames, missing file parts, case-insensitive extensions
- **Unique filename generation**: Verifies that uploaded files get unique names
- **Image listing**: Tests the `/api/images` endpoint for listing uploaded images
- **Sorting**: Verifies images are sorted by newest first

### 2. Admin and Authentication Tests (`test_admin_auth.py`)
- **Admin panel access**: Tests accessibility of admin JavaScript resources
- **Authentication framework**: Placeholder tests for future login/logout implementation
  - Login with valid/invalid credentials
  - Logout functionality
  - Session management
  - Protected route access control
- **Upload access control**: Framework for future upload authentication

### 3. Basic App Tests (`test_app_basics.py`)
- **App configuration**: Verifies Flask app setup and testing mode
- **Route availability**: Tests that expected routes exist
- **File extension validation**: Tests the `allowed_file()` helper function
- **404 handling**: Verifies proper handling of non-existent routes

## Running the Tests

### Prerequisites
Install the required dependencies:
```bash
pip install -r requirements.txt
```

### Run All Tests
```bash
pytest
```

### Run Tests with Verbose Output
```bash
pytest -v
```

### Run Specific Test File
```bash
pytest tests/test_image_upload.py
pytest tests/test_admin_auth.py
pytest tests/test_app_basics.py
```

### Run Specific Test Class
```bash
pytest tests/test_image_upload.py::TestImageUpload
pytest tests/test_admin_auth.py::TestAuthenticationFramework
```

### Run Specific Test Method
```bash
pytest tests/test_image_upload.py::TestImageUpload::test_upload_valid_image
```

### Run Tests with Coverage Report
```bash
pytest --cov=app --cov-report=html
```

### Skip Tests Marked as Future Implementation
```bash
pytest -v
```
(Tests marked with `@pytest.mark.skip` are automatically skipped)

### Run Only Skipped Tests (to see what needs implementation)
```bash
pytest --collect-only -m skip
```

## Test Structure

### Fixtures (`conftest.py`)
- **app**: Creates a Flask app instance configured for testing
- **client**: Provides a test client for making HTTP requests
- **runner**: Provides a test CLI runner

### Test Organization
Tests are organized into classes based on functionality:
- `TestImageUpload`: Image upload functionality
- `TestImageListing`: Image retrieval and listing
- `TestAdminPanelAccess`: Admin panel resources
- `TestAuthenticationFramework`: Login/logout (future implementation)
- `TestAppConfiguration`: Basic app setup
- `TestBasicRoutes`: Route availability

## Authentication Tests

Several tests are currently marked with `@pytest.mark.skip` because authentication 
is not yet implemented in the application. These tests serve as:

1. **Documentation**: They document the expected authentication behavior
2. **Implementation guide**: They provide a specification for future authentication features
3. **Test-driven development**: Once authentication is added, simply remove the `@pytest.mark.skip` decorators

### To implement authentication:
1. Add Flask-Login or similar authentication library to `requirements.txt`
2. Implement `/api/login` and `/api/logout` endpoints in `app.py`
3. Add session management
4. Remove `@pytest.mark.skip` decorators from authentication tests
5. Run tests to verify implementation

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

```yaml
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest -v
```

## Contributing

When adding new features to the application:
1. Write tests first (TDD approach)
2. Ensure all existing tests pass
3. Add new tests for new functionality
4. Run full test suite before committing
