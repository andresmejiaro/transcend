# # network/ws_manager.py
#
# import asyncio
# import logging
# import aiohttp
#
# from utils.logger import log_message
#
# class WSManager:
#     def __init__(self, ui_controller, frame_rate, process_speed):
#         self.ui_controller = ui_controller
#         self.frame_rate = frame_rate
#         self.process_speed = process_speed
#
#         self.listeners = {}
#
#     def __str__(self):
#         return f"WSManager"
#
#     def create_ws_listener(self, ws_id, ws_url):
#         if ws_id in self.listeners:
#             return False
#
#         self.listeners[ws_id] = WSListener(self, ws_id, ws_url)
#         return True
#
#     def remove_ws_listener(self, ws_id):
#         if ws_id not in self.listeners:
#             return False
#
#         self.listeners[ws_id].close()
#         del self.listeners[ws_id]
#         return True
#
#     def get_ws_listener_by_id(self, ws_id):
#         if ws_id not in self.listeners:
#             return None
#
#         return self.listeners[ws_id]
#
#     def get_ws_listeners(self):
#         return self.listeners
#
#
# class WSListener:
#     def __init__(self, ws_manager, ws_id, ws_url):
#         self.ws_manager = ws_manager
#         self.ws_id = ws_id
#         self.ws_url = ws_url
#
#         data = {
#             "receive_queue": asyncio.Queue(),
#             "send_queue": asyncio.Queue(),
#             "receive_lock": asyncio.Lock(),
#             "send_lock": asyncio.Lock(),
#         }
#
#         self.ws_manager.ui_controller.add_shared_data(self.ws_id, data)
#
#         self.is_alive = False
#         self.is_running = False
#         self.is_closing = False
#
#         self.ws = None
#
#         self.connect_listen()
#         self.ws_manager.ui_controller.remove_shared_data(self.ws_id)
#
#     def __str__(self):
#         return f"WSListener({self.ws_id})"
#
#     async def connect_listen(self):
#         self.is_running = True
#         self.is_alive = True
#         try:
#             async with aiohttp.ClientSession() as session:
#                 token_info = self.ws_manager.ui_controller.file_manager.load_data('token.json')
#                 token = token_info['token']
#                 uri = self.ws_url.format(token=token)
#                 log_message(f"Connecting to websocket: {uri}", level=logging.INFO)
#                 async with session.ws_connect(self.ws_url) as ws:
#                     try:
#                         async for msg in ws:
#                             if msg.type == aiohttp.WSMsgType.TEXT:
#                                 async with self.ws_manager.ui_controller.get_shared_data(self.ws_id)["receive_lock"]:
#                                     await self.ws_manager.ui_controller.get_shared_data(self.ws_id)["receive_queue"].put(msg.data)
#                                     log_message(f"Received message: {msg.data}", level=logging.DEBUG)
#                             elif msg.type == aiohttp.WSMsgType.ERROR:
#                                 break
#
#                             # Send messages
#                             while not self.ws_manager.ui_controller.get_shared_data(self.ws_id)["send_queue"].empty():
#                                 async with self.ws_manager.ui_controller.get_shared_data(self.ws_id)["send_lock"]:
#                                     message = await self.ws_manager.ui_controller.get_shared_data(self.ws_id)["send_queue"].get()
#                                     await ws.send_str(message)
#                                     log_message(f"Sent message: {message}", level=logging.DEBUG)
#
#                             await asyncio.sleep(1)
#
#                         log_message("Websocket task completed", level=logging.DEBUG)
#
#                     except (asyncio.CancelledError, GeneratorExit):
#                         log_message("Websocket task cancelled", level=logging.DEBUG)
#                         raise
#
#                     except Exception as e:
#                         log_message(f"Websocket task error: {e}", level=logging.ERROR)
#                         raise
#
#         except asyncio.CancelledError:
#             # Catch the cancellation when leaving the view
#             pass
#         except aiohttp.ClientError as e:
#             log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
#             self.exit_status = 1
#         except Exception as e:
#             log_message(f"An error occurred in Lobby Websocket Task: {e}", level=logging.ERROR)
#             self.exit_status = 1
#
#         self.is_alive = False
#         self.is_running = False
#
#
#
