# Fixture registration fix

`qa_users`, `qa_pg`, `qa_redis`, `qa_es`, `qa_s3`, and `qa_settings` are real
integration-test fixtures declared in `_helpers.py`. Pytest automatically
collects fixtures from `conftest.py`, not from arbitrary helper modules.

`tests/integration/conftest.py` imports these fixtures explicitly so they are
available to every test module in this directory. No application code is
changed and no mocks are introduced.
