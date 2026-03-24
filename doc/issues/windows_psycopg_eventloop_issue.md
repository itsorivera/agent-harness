# Issue: Psycopg with ProactorEventLoop on Windows

## Symptom
Error when attempting to use the asynchronous PostgreSQL checkpointer with LangGraph on Windows systems:

```text
error connecting in 'pool-1': Psycopg cannot use the 'ProactorEventLoop' to run in async mode. Please use a compatible event loop, for instance by setting 'asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())'
```

## Cause
Since Python 3.8, the default event loop on Windows is `ProactorEventLoop`. However, `psycopg` uses internal selectors that are only compatible with `SelectorEventLoop`. Uvicorn, when starting, tends to force the use of `ProactorEventLoop` if not explicitly configured.

## Implemented Solution

To resolve this persistently in the project without modifying the installed libraries in `site-packages`:

1.  **Policy Configuration**: The `asyncio` policy is set at the beginning of the entry points (`run.py` and `src/app.py`).
    ```python
    import sys
    import asyncio
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    ```

2.  **Using uvicorn.Server**: Instead of using `uvicorn.run("src.app:app")` (which can initialize its own loop internally and ignore the configured policy), `uvicorn.Server` is used within an `asyncio.run()` block. This ensures that `uvicorn` reuses the loop created by `asyncio` under the `SelectorEventLoop` policy.

    In `run.py`:
    ```python
    async def main():
        config = uvicorn.Config(
            app,
            host=os.getenv("UVICORN_HOST", "127.0.0.1"),
            port=int(os.getenv("UVICORN_PORT", 8000)),
            loop="asyncio",
        )
        server = uvicorn.Server(config)
        await server.serve()

    if __name__ == "__main__":
        asyncio.run(main())
    ```
