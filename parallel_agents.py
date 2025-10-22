# parallel_agents.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Any, Dict

def run_parallel_agents(agents: List[Callable[[], Any]], max_workers: int = 6) -> List[Any]:
    """
    Run a list of zero-arg callables in parallel and return their results in completion order.
    Each agent should be a small wrapper that performs a sub-query / tool call and returns a dict/result.
    """
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(agent): agent for agent in agents}
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as e:
                # Return error info for that agent rather than crashing everything
                results.append({"error": str(e)})
    return results

# Helper to create agent wrappers easily
def agent_from_fn(fn: Callable[..., Any], *args, **kwargs):
    def wrapper():
        return fn(*args, **kwargs)
    return wrapper
