# backend api

a REST API serving JSON for the backend of the application.

## developing

to work on this API or to run a version of it in development you'll need to install some prereqs & then run
the development server. instructions below.

### prereqs

you'll need [`uv`](https://docs.astral.sh/uv/getting-started/installation/) to setup you python environment. on
mac/linux, it can be installed quickly w/ `curl -LsSf https://astral.sh/uv/install.sh | sh`. confirm it's
installed correctly by running `uv` in your terminal.

### running

first, make sure you're in the `./backend` directory. then, to start the dev server, you should now be able to
just run the command `uv run fastapi dev src`. you'll see some output with something like the following at the end.
`uv` should handle dependencies, python versioning, & virtual environment for you.

```
andrew@topo: ~/college/cs_487-swe/prj/backend
$ uv run fastapi dev src

...  // might first get info about installing dependencies here if it's your first time

   FastAPI   Starting development server 🚀

             Searching for package file structure from directories with __init__.py files
             Importing from /home/andrew/college/cs_487-swe/prj/backend

    module   📁 src
             └── 🐍 __init__.py

      code   Importing the FastAPI app object from the module with the following code:

             from src import app

       app   Using import string: src:app

    server   Server started at http://127.0.0.1:8000
    server   Documentation at http://127.0.0.1:8000/docs

       tip   Running in development mode, for production use: fastapi run

             Logs:

      INFO   Will watch for changes in these directories: ['/home/andrew/college/cs_487-swe/prj/backend']
      INFO   Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
      INFO   Started reloader process [287385] using WatchFiles
      INFO   Started server process [287387]
      INFO   Waiting for application startup.
      INFO   Application startup complete.
```

note it says to go to [http://127.0.0.1:8000](http://127.0.0.1:8000) to access the api & to
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to explore the api w/ an interactive user interface.
you can also find the openapi schema file at [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json),
which might be useful when using codegen tools to help write code that needs to access the api.

## production

TODO!

- [ ] create Dockerfile to encapsulate application that takes care of setting up the environment & launching a
      server w/ appropriate ports exposed
- [ ] allow app to get database secrets/connection parameters from environment so it can be configured from a
      docker compose file
