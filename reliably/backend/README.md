# Backend service of Reliably

## Development

### Setting up

You will need the following installed:

* Python 3.12+ and a local virtual environment
* Docker
* Docker-compose
* The postgresql 17 docker image

In your virtual environment, from the `backend` directory,
run the following command:

```bash
curl -sSL https://raw.githubusercontent.com/pdm-project/pdm/main/install-pdm.py | python3 -
pdm sync
```

### Running tests

To run all the tests, use:

```bash
pdm run test
```

To run a single test file:

```bash
pdm run test tests/test_router.py
```

To run a single test:

```bash
pdm run test tests/test_router.py::test_load_all_routers
```

Tests will output the coverage, please try to keep a 100% code coverage or
close to that.

### Linting

Before pushing, make sure to run the following:

```bash
pdm run format
pdm run lint
```

The linting also evaluates the compliance with typing annotation (using `mypy`).
You need an OK from mypy before you push (or the CI will fail anyway).

When a particular line is complicated to type properly, you can add a comment
to that line:

```python
  # type: ignore
```

(preserve the two leading spaces)

### Migration

Creating a new migration step is done as follows:

1. Start a PostgreSQL server as a local container:

```bash
docker run \
    --name postgres \
    -e POSTGRES_PASSWORD=secret \
    -e POSTGRES_USER=test \
    -e POSTGRES_DB=test \
    -p 5432:5432 \
    --rm postgres
```

2. Go to the migrations subdirectory and run:

```bash
alembic upgrade head
```

3. Now create a new migration:

```bash
alembic revision --autogenerate -m "Add XYZ"
```

Set an appropriate message.

4. You can now run your migration and see if it applies:

```bash
alembic upgrade head
```

5. Teardown the docker container:

```bash
docker rm -f postgres
```

Once pushed to the remote upstream, you can trigger the GH action that will
apply the migrations against the correct environment.

Note, if you have added a table, you will need to re-apply the infrastructure
terraform plan so it gives grant to it from the postgresql user of the
environment.
