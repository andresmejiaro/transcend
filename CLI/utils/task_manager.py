# utils/task_manager.py

import asyncio
import logging

from utils.logger import log_message

class TaskManager:
    def __init__(self):
        self._tasks = {}  # Use a dictionary to map task names to tasks
        self._running = True

    def create_task(self, task_name, task_func, data=None):
        task = asyncio.create_task(task_func(data))
        self._tasks[task_name] = {"task": task, "data": data}  # Save task and its data with the given name
        return task
        
    def get_task_data_by_name(self, task_name):
        # Retrieve data for a task by its name
        task_info = self._tasks.get(task_name)
        if task_info:
            return task_info["data"]
        else:
            return None

    def get_task_by_name(self, task_name):
        # Retrieve the task itself by its name
        task_info = self._tasks.get(task_name)
        if task_info:
            return task_info["task"]
        else:
            return None

    def remove_task_by_name(self, task_name):
        # Remove a task by its name
        task_info = self._tasks.pop(task_name, None)
        if task_info:
            task_info["task"].cancel()

    def start_task_by_name(self, task_name):
        # Start a task by its name
        task = self.get_task_by_name(task_name)
        if task:
            if task.cancelled():
                new_task = asyncio.create_task(task._coro)
                self._tasks[task_name]["task"] = new_task
                task = new_task
            task.add_done_callback(self._task_done_callback)

    def stop_task_by_name(self, task_name):
        # Stop a task by its name
        task = self.get_task_by_name(task_name)
        if task:
            task.cancel()
            # Delete the task from the dictionary and its data
            self._tasks.pop(task_name, None)

    def start_all_tasks(self):
        # Start all tasks in the loop
        for task_name in self._tasks:
            self.start_task_by_name(task_name)

    def stop_all_tasks(self):
        # Stop all tasks
        for task_info in self._tasks.values():
            task_info["task"].cancel()

    def get_task_names(self):
        # Retrieve the names of all tasks
        return list(self._tasks.keys())

    def is_running(self):
        return self._running
    
    def cleanup(self):
        self._running = False
        self._tasks.clear()
        
    def _task_done_callback(self, task):
        if not task.cancelled():
            exception = task.exception()
            if exception:
                log_message(f"Task {task.get_name()} raised an exception: {exception}", level=logging.ERROR)


