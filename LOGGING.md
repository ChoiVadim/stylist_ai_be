# Logging Guide

This document describes the logging system implemented in the Hack Seoul API.

## Overview

The application uses Python's `logging` module with a structured logging setup that includes:
- Console output (stdout) for real-time monitoring
- Rotating file logs for persistence and analysis
- Hierarchical logger names for better organization
- Configurable log levels via environment variables

## Logger Configuration

### Log Levels

Set the log level using the `LOG_LEVEL` environment variable:
- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical errors

Example:
```bash
export LOG_LEVEL=DEBUG
```

### Log Files

Logs are written to the `logs/` directory with the following naming:
- Format: `app_YYYYMMDD.log`
- Example: `app_20250114.log`

### Log Rotation

- Maximum file size: 10MB per log file
- Backup count: 5 files (keeps 5 rotated files)
- Automatic rotation when size limit is reached

## Logger Hierarchy

Loggers are organized hierarchically:

```
hackseoul                    # Root logger
├── app                      # Application lifecycle
├── api.auth                 # Authentication endpoints
├── api.color                # Color analysis endpoints
├── database                 # Database operations
├── database.products       # Product queries
└── utils.auth               # Authentication utilities
```

## Usage Examples

### Getting a Logger

```python
from src.utils.logger import get_logger

# Get root logger
logger = get_logger()

# Get a named logger (creates child logger)
logger = get_logger("api.auth")
logger = get_logger("database")
```

### Logging Messages

```python
logger.debug("Detailed debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred", exc_info=True)  # Include stack trace
logger.critical("Critical error")
```

## What Gets Logged

### Application Lifecycle
- Startup and shutdown events
- Database initialization
- Configuration loading

### HTTP Requests
- All incoming requests (method, path, client IP)
- Response status codes and processing time
- Request errors with stack traces

### Authentication
- User registration attempts (success/failure)
- Login attempts (success/failure)
- JWT token creation and validation
- Authentication failures with reasons

### API Endpoints
- Color analysis requests and results
- Processing times for expensive operations
- Error conditions with full context

### Database Operations
- Database initialization
- Query operations (when needed)
- Database errors

## Log Format

### Console Format (stdout)
```
2025-01-14 10:30:45 - hackseoul.api.auth - INFO - Login attempt for email: user@example.com
```

### File Format (detailed)
```
2025-01-14 10:30:45 - hackseoul.api.auth - INFO - [auth.py:92] - login() - Login attempt for email: user@example.com
```

## Docker Integration

Logs are persisted via Docker volumes:
- Logs directory is mounted: `./logs:/app/logs`
- Logs persist across container restarts
- Access logs from host: `docker-compose logs -f`

## Viewing Logs

### Local Development
```bash
# View logs in real-time
tail -f logs/app_$(date +%Y%m%d).log

# View all logs
cat logs/*.log

# Search logs
grep "ERROR" logs/*.log
```

### Docker
```bash
# View container logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f api

# View last 100 lines
docker-compose logs --tail=100 api
```

## Best Practices

1. **Use appropriate log levels**:
   - `DEBUG`: Detailed debugging information
   - `INFO`: Normal operations and important events
   - `WARNING`: Something unexpected but handled
   - `ERROR`: Errors that need attention
   - `CRITICAL`: System failures

2. **Include context**:
   ```python
   logger.info(f"User registered: user_id={user.id}, email={user.email}")
   ```

3. **Log errors with stack traces**:
   ```python
   logger.error(f"Operation failed: {str(e)}", exc_info=True)
   ```

4. **Log timing for expensive operations**:
   ```python
   start_time = time.time()
   result = expensive_operation()
   logger.info(f"Operation completed in {time.time() - start_time:.2f}s")
   ```

5. **Don't log sensitive information**:
   - Never log passwords, tokens, or API keys
   - Be careful with user data (email is OK, full profile might not be)

## Environment Variables

- `LOG_LEVEL`: Set the logging level (default: `INFO`)
- `SECRET_KEY`: JWT secret key (logged on startup if loaded)

## Troubleshooting

### No logs appearing
- Check that `logs/` directory exists and is writable
- Verify `LOG_LEVEL` is set appropriately
- Check Docker volume mounts if using containers

### Logs too verbose
- Set `LOG_LEVEL=WARNING` or `LOG_LEVEL=ERROR`
- Restart the application

### Logs missing information
- Set `LOG_LEVEL=DEBUG` for more detail
- Check file permissions on logs directory

