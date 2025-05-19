import threading
import concurrent.futures
import asyncio
import time
from execution_evaluation import ToyCallable

# This file extends the concurrent and asynchronous execution capabilities
# of the language, going beyond the basic parallel execution in the core.

class ToyThread:
    """Thread implementation for concurrent execution."""
    def __init__(self, target, args=None):
        self.target = target
        self.args = args or []
        self.thread = None
        self.result = None
        self.exception = None
    
    def start(self):
        """Start the thread."""
        def wrapper():
            try:
                if isinstance(self.target, ToyCallable):
                    self.result = self.target.call(None, self.args)
                else:
                    self.result = self.target(*self.args)
            except Exception as e:
                self.exception = e
        
        self.thread = threading.Thread(target=wrapper)
        self.thread.start()
    
    def join(self):
        """Wait for thread to complete."""
        if self.thread:
            self.thread.join()
            if self.exception:
                raise self.exception
            return self.result
        return None

class ToyConcurrentExecutor:
    """Executor for running multiple functions concurrently."""
    def __init__(self, max_workers=None):
        self.max_workers = max_workers
    
    def map(self, func, items):
        """Apply func to items concurrently."""
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all items for processing
            future_to_item = {executor.submit(func.call, None, [item]): item for item in items}
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Error processing {item}: {e}")
        
        return results
    
    def execute_all(self, functions):
        """Execute all functions concurrently."""
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all functions
            futures = [executor.submit(func.call, None, []) for func in functions]
            
            # Collect results
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    print(f"Error executing function: {e}")
        
        return results

class ToyAsync:
    """Support for async/await pattern."""
    @staticmethod
    async def run_async(func, *args):
        """Run a function asynchronously."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args)
        
        # Run non-async function in executor
        loop = asyncio.get_event_loop()
        if isinstance(func, ToyCallable):
            return await loop.run_in_executor(None, func.call, None, list(args))
        return await loop.run_in_executor(None, func, *args)
    
    @staticmethod
    async def gather(*coros):
        """Run coroutines concurrently and wait for all to complete."""
        return await asyncio.gather(*coros)
    
    @staticmethod
    def run_until_complete(coro):
        """Run a coroutine until it completes."""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro)

# Example of using concurrency features
def test_concurrency():
    print("Testing Concurrency Features:")
    
    # Define some functions for testing
    def slow_function(n):
        time.sleep(1)  # Simulate a slow operation
        return n * n
    
    # Create a ToyCallable wrapper for the slow function
    class SlowSquare(ToyCallable):
        def call(self, interpreter, arguments):
            return slow_function(arguments[0])
        
        def arity(self):
            return 1
        
        def __str__(self):
            return "<function: slow_square>"
    
    # Test basic threading
    print("\nBasic Threading:")
    slow_square = SlowSquare()
    
    thread1 = ToyThread(slow_square, [1])
    thread2 = ToyThread(slow_square, [2])
    
    start_time = time.time()
    
    thread1.start()
    thread2.start()
    
    result1 = thread1.join()
    result2 = thread2.join()
    
    duration = time.time() - start_time
    print(f"Thread results: {result1}, {result2}")
    print(f"Duration: {duration:.2f}s (should be ~1s for parallel execution)")
    
    # Test concurrent executor
    print("\nConcurrent Executor:")
    executor = ToyConcurrentExecutor(max_workers=4)
    
    numbers = [1, 2, 3, 4]
    start_time = time.time()
    results = executor.map(slow_square, numbers)
    duration = time.time() - start_time
    
    print(f"Mapped results: {results}")
    print(f"Duration: {duration:.2f}s (should be ~1s for parallel execution)")
    
    # Test async/await
    print("\nAsync/Await Pattern:")
    
    async def async_test():
        tasks = [ToyAsync.run_async(slow_function, n) for n in [1, 2, 3, 4]]
        results = await ToyAsync.gather(*tasks)
        return results
    
    start_time = time.time()
    async_results = ToyAsync.run_until_complete(async_test())
    duration = time.time() - start_time
    
    print(f"Async results: {async_results}")
    print(f"Duration: {duration:.2f}s (should be ~1s for parallel execution)")

if __name__ == "__main__":
    test_concurrency()
