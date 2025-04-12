Notes:
 - DO NOT commit config.ini to Github. Add it to .gitignore


# Project README

## Troubleshooting: Import Errors in Tests (PYTHONPATH Issue)

If you're running tests in PowerShell and encountering import errors like the following:

```
ModuleNotFoundError: No module named 'db'
```

This issue is usually caused by Python not being able to find the `src` directory, where your main application code resides. This happens because the `PYTHONPATH` is not set properly in PowerShell.

### Solution

To resolve this issue, you need to set the `PYTHONPATH` to include the `src/` directory. Here's how you can do this in PowerShell:

1. Open PowerShell in your project directory.

2. Run the following command to set the `PYTHONPATH`:

   ```powershell
   $env:PYTHONPATH=".\src;$env:PYTHONPATH"
   ```

   This command prepends the `src/` directory to your `PYTHONPATH`, ensuring that Python can locate your application code.

3. After setting the `PYTHONPATH`, you can run your tests again using:

   ```powershell
   poetry run python -m unittest discover -s tests -p "test_*.py"
   ```

This should allow your tests to run without import errors. Make sure to set the `PYTHONPATH` each time you open a new PowerShell session.

### Poetry Virtual Environment Configuration

In this project, I have configured Poetry to **not create a new virtual environment** by running the following command:

```bash
poetry config virtualenvs.create false
