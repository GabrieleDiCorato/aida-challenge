# dbt Profiles Configuration Guide

## Overview

This document explains how to properly configure dbt profiles for this project, following best practices for both development and production environments.

## The Problem

The `profiles.yml` file contains connection information for dbt, including database paths. There are two main issues with committing this file:

1. **Absolute paths**: Machine-specific paths (e.g., `C:/Users/yourname/...`) won't work on other machines
2. **Security**: Profiles may contain sensitive credentials (passwords, API keys, etc.)

## Best Practices

### Option 1: Local Development Setup (Recommended for this project)

For local development with relative paths:

1. **Copy the example file**:
   ```bash
   cp dbt_project/profiles.yml.example dbt_project/profiles.yml
   ```

2. **Edit if needed**: The default configuration uses relative paths from the project root:
   ```yaml
   aida_insurance:
     target: dev
     outputs:
       dev:
         type: duckdb
         path: "data/aida_challenge.duckdb"
         schema: main
   ```

3. **Never commit**: The `profiles.yml` file is in `.gitignore` to prevent accidental commits

4. **How it works**: The Python wrapper functions in `src/aida_challenge/dbt_commands.py` automatically:
   - Change the working directory to the project root
   - Look for `profiles.yml` in `dbt_project/` directory
   - Use relative paths from there

### Option 2: Standard dbt Location (Recommended for production)

For a more standard dbt setup:

1. **Create profiles in home directory**:
   ```bash
   mkdir -p ~/.dbt
   cp dbt_project/profiles.yml.example ~/.dbt/profiles.yml
   ```

2. **Edit with absolute paths** (since dbt will run from any directory):
   ```yaml
   aida_insurance:
     target: dev
     outputs:
       dev:
         type: duckdb
         path: "/full/path/to/project/data/aida_challenge.duckdb"
         schema: main
   ```

3. **Benefits**:
   - Standard dbt convention
   - One profile works across multiple projects
   - Can have different profiles for dev/staging/prod

4. **How it works**: The Python wrapper automatically detects when `~/.dbt/profiles.yml` exists and uses it

### Option 3: Environment Variable Override

For CI/CD or shared environments:

```bash
# Set the profiles directory location
export DBT_PROFILES_DIR=/path/to/profiles

# Run dbt commands
uv run dbt-run
```

## File Structure

```
aida-challenge/
├── dbt_project/
│   ├── profiles.yml.example    # Template (committed to git)
│   ├── profiles.yml            # Local config (in .gitignore)
│   └── ...
├── data/
│   └── aida_challenge.duckdb
└── src/
    └── aida_challenge/
        └── dbt_commands.py     # Handles profile detection
```

## Profile Detection Logic

The `dbt_commands.py` automatically detects profiles in this order:

1. **Environment variable**: `DBT_PROFILES_DIR` if set
2. **Local project**: `dbt_project/profiles.yml` if exists
3. **Home directory**: `~/.dbt/profiles.yml` as fallback

## Security Best Practices

1. ✅ **DO**: Use `profiles.yml.example` as a template
2. ✅ **DO**: Add `profiles.yml` to `.gitignore`
3. ✅ **DO**: Use environment variables for sensitive data
4. ✅ **DO**: Document required configuration in README
5. ❌ **DON'T**: Commit `profiles.yml` to version control
6. ❌ **DON'T**: Store passwords or API keys in profiles
7. ❌ **DON'T**: Use absolute paths in committed files

## Example with Environment Variables

For production with sensitive credentials:

```yaml
aida_insurance:
  target: "{{ env_var('DBT_TARGET', 'dev') }}"
  outputs:
    dev:
      type: duckdb
      path: "{{ env_var('DUCKDB_PATH') }}"
      schema: main
    prod:
      type: postgres
      host: "{{ env_var('DB_HOST') }}"
      user: "{{ env_var('DB_USER') }}"
      password: "{{ env_var('DB_PASSWORD') }}"
      port: 5432
      dbname: analytics
      schema: public
```

## Troubleshooting

### Issue: "Profile not found"

**Solution**: Ensure you've copied `profiles.yml.example` to `profiles.yml` or `~/.dbt/profiles.yml`

### Issue: "Cannot open file" or path errors

**Solution**: 
- For local setup: Check that paths in `profiles.yml` are relative to project root
- For home directory setup: Use absolute paths in `~/.dbt/profiles.yml`

### Issue: Changes not taking effect

**Solution**: 
- Delete `dbt_project/target/` directory
- Run with `--no-partial-parse` flag: `uv run dbt run --no-partial-parse`

## Migration Guide

If you already have an existing `profiles.yml` with absolute paths:

1. Back up your current file:
   ```bash
   cp dbt_project/profiles.yml dbt_project/profiles.yml.backup
   ```

2. Copy the example:
   ```bash
   cp dbt_project/profiles.yml.example dbt_project/profiles.yml
   ```

3. Test it works:
   ```bash
   uv run dbt-run
   ```

4. Optional: Move to home directory for standard setup:
   ```bash
   mkdir -p ~/.dbt
   mv dbt_project/profiles.yml.backup ~/.dbt/profiles.yml
   # Edit paths to be absolute
   ```

## References

- [dbt profiles documentation](https://docs.getdbt.com/docs/core/connect-data-platform/profiles.yml)
- [dbt environment variables](https://docs.getdbt.com/docs/build/environment-variables)
- [dbt best practices](https://docs.getdbt.com/guides/best-practices)
