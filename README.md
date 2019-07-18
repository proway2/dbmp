[![Build Status](https://travis-ci.org/proway2/dbmp.svg?branch=master)](https://travis-ci.org/proway2/dbmp)

# dbmp

**PostgreSQL - yet to be tested.**

Simple database browser with pagination support, easily handles millions of rows. SQLite and PostgreSQL supported, possible to support all DB-API 2.0 (PEP 249) compliants.

# Features

- Single query mode.    
- Ctrl+Enter executes query.    
- Walking thru the pages with PgUp/PgDown, arrows, mouse wheel.    


# Installation

- Requires Python 3.6+.
- Clone and run ```pip install -r requirements.txt```.

# Usage
```python3 app.py``` or ```./app.py```

# Tests
From project's folder run: ```python3 -m unittest -v tests/test_*.py```

# License
GPL v3
