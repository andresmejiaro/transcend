# utils/task_manager.py

import asyncio
import logging

from utils.logger import log_message
from utils.config_manager import ConfigurationManager
from utils.file_manager import FileManager

class TaskManager:
    def __init__(self):
        self._tasks = set()
        self._running = False

    def create_task(self, task_name, task_func, data=None):
        task = asyncio.create_task(task_func(data))
        self._tasks.add(task)
        return task

    def remove_task(self, task):
        task.cancel()
        self._tasks.discard(task)

    def start_task(self, task):
        if task in self._tasks:
            if task.cancelled():
                task = asyncio.create_task(task._coro)
            task.add_done_callback(self._task_done_callback)

    def stop_task(self, task):
        if task in self._tasks:
            task.cancel()

    def get_tasks(self):
        return self._tasks.copy()

    def start_all_tasks(self):
        self._running = True
        for task in self._tasks.copy():
            if not task.cancelled():
                task.add_done_callback(self._task_done_callback)
            else:
                new_task = asyncio.create_task(task._coro)
                new_task.add_done_callback(self._task_done_callback)
                self._tasks.remove(task)
                self._tasks.add(new_task)

    def stop_all_tasks(self):
        self._running = False
        for task in self._tasks.copy():
            task.cancel()

    def _task_done_callback(self, task):
        if not task.cancelled():
            exception = task.exception()
            if exception:
                log_message(f'Task failed: {exception}', level=logging.ERROR)
            self._tasks.discard(task)
