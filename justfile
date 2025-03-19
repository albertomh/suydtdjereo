# suydtdjereo - local development tooling

set positional-arguments

call_recipe := just_executable() + " --justfile=" + justfile()

default:
  @just --list

collectstatic:
  #!/usr/bin/env bash
  # It would be simpler to use just's `dotenv-load`. However, this is not a viable
  # approach since this would also load `.env` for the `test` recipe. Meaning the
  # environment `test` runs in would be polluted instead of using values from `.env.test`.
  set -euo pipefail
  DEBUG_VALUE=$(awk -F= '/^DEBUG=/{gsub(/["'\'' ]/, "", $2); print tolower($2)}' .env)
  if [ "$DEBUG_VALUE" = "false" ]; then
    rm -rf static/;
    uv run manage.py collectstatic --noinput;
  fi

_dev_setup:
  @test -d .venv/ || uv venv
  @test -x .venv/bin/django-admin || uv sync --dev
  @uv pip install -e .
  {{call_recipe}} collectstatic

manage +args='help': _dev_setup
  @uv run manage.py "$@"

runserver $PYTHONDEVMODE="1": _dev_setup
  # Disable PYTHONDEVMODE by passing an empty string ie. `just runserver ""`
  @uv run manage.py runserver

shell: _dev_setup
  @uv run manage.py shell

test +args='.':
  @test -d .venv/ || uv venv
  @test -x .venv/bin/coverage || uv sync --group test
  @uv pip install -e .
  @uv run coverage erase
  @uv run python -m coverage run --source="." \
    manage.py test "$@" --failfast --pdb --shuffle --verbosity=3
  @uv run coverage report
  @uv run coverage html
