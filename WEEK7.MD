# WEEK 7 COMPLETION REPORT

## Week 7 Objective

Implement real PostgreSQL-based account storage and authentication, remove mock user behavior, and update the application interface to reflect Week 7 delivery.

## What Was Completed

1. PostgreSQL configuration was fully enabled.
2. Database-backed user registration and login were implemented.
3. Python startup now auto-creates and validates the required user table.
4. User table name was finalized as secure_file_users.
5. Mock account display and old Week 6 interface text were removed.

## Exact Files Changed And Where

### 1) Configuration and environment

- Added and validated DATABASE_URL in [config.py](config.py#L72).
- Set storage mode default to database in [config.py](config.py#L87).
- Added PostgreSQL URL validation rules in [config.py](config.py#L150).
- Exposed database_url in config output dictionary in [config.py](config.py#L201).
- Set runtime environment values in [.env](.env#L45) and [.env](.env#L48).
- Updated template environment values in [.env.example](.env.example#L69) and [.env.example](.env.example#L72).
- Added psycopg2-binary dependency in [requirements.txt](requirements.txt#L4).

### 2) Database module and schema

- Added database manager class in [app/modules/database.py](app/modules/database.py#L16).
- Set the table constant to secure_file_users in [app/modules/database.py](app/modules/database.py#L19).
- Implemented CREATE TABLE IF NOT EXISTS secure_file_users in [app/modules/database.py](app/modules/database.py#L32).
- Added table existence checker using to_regclass in [app/modules/database.py](app/modules/database.py#L47) and [app/modules/database.py](app/modules/database.py#L49).
- Registration insert now writes to secure_file_users in [app/modules/database.py](app/modules/database.py#L63).
- Login user fetch now reads from secure_file_users in [app/modules/database.py](app/modules/database.py#L88).

### 3) Authentication flow

- Registration entry point remains in [app/modules/auth.py](app/modules/auth.py#L90) and now writes through database manager.
- Login entry point in [app/modules/auth.py](app/modules/auth.py#L114) now retrieves users from PostgreSQL.
- User retrieval method in [app/modules/auth.py](app/modules/auth.py#L211) delegates to database manager in [app/modules/auth.py](app/modules/auth.py#L224).
- Authentication singleton uses database manager in [app/modules/auth.py](app/modules/auth.py#L309).

### 4) Application startup and validation

- App binds DATABASE_URL in [app/**init**.py](app/__init__.py#L39).
- App fails fast if DB manager is missing in [app/**init**.py](app/__init__.py#L49).
- App auto-initializes database schema at startup in [app/**init**.py](app/__init__.py#L50).
- Startup validator checks table setup in [validate_startup.py](validate_startup.py#L112).
- Startup validator confirms secure_file_users existence in [validate_startup.py](validate_startup.py#L122).
- Validation summary updated to 7 checks in [validate_startup.py](validate_startup.py#L160).

### 5) Frontend updates

- Header text changed to Week 7 in [app/templates/index.html](app/templates/index.html#L14).
- Login username placeholder made neutral in [app/templates/index.html](app/templates/index.html#L32).
- Week 7 footer text updated in [app/templates/index.html](app/templates/index.html#L246).
- Hardcoded sample account card was removed from login panel in [app/templates/index.html](app/templates/index.html).

## Verification Performed

Startup validation was executed and passed all checks.

- DATABASE_URL configured for PostgreSQL
- secure_file_users table exists
- Final validation summary passed 7 out of 7 checks

Validated through [validate_startup.py](validate_startup.py).

## Final Week 7 State

- User registration saves records into secure_file_users.
- Login reads users from secure_file_users.
- Python startup ensures the table exists before serving requests.
- Mock account references were removed from active runtime and login UI.
- Interface reflects Week 7 PostgreSQL integration.

## Week 8 Plan

1. Migrate file metadata and sharing records into PostgreSQL tables.
2. Add database migrations for schema versioning and repeatable deployment.
3. Enforce stronger password policy and email uniqueness error messaging.
4. Add integration tests for register, login, and persistence across restarts.
5. Add API endpoint for admin-level health and user count checks.
6. Improve observability with structured auth and DB operation logs.
7. Update README and technical reports with finalized database architecture.
