import asyncio
import curses
import aiohttp

async def curses_input_task(stdscr, keyboard_queue):
    while True:
        key = stdscr.getch()
        if key == curses.KEY_UP:
            await keyboard_queue.put('up')
        elif key == curses.KEY_DOWN:
            await keyboard_queue.put('down')
        elif key == curses.KEY_LEFT:
            await keyboard_queue.put('left')
        elif key == curses.KEY_RIGHT:
            await keyboard_queue.put('right')
        elif key != -1:
            await keyboard_queue.put(f'key: {key}')
        elif key == 27:  # ESC key
            await keyboard_queue.put('exit')  # Signal to exit
            break

        await asyncio.sleep(0.1)

async def websocket_send_and_recieve_task(stdscr, uri, messages_recieve_queue, message_send_queue, keyboard_queue):
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(uri) as ws:
            try:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        await messages_recieve_queue.put(msg.data)
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        break

                    await asyncio.sleep(0.1)

                    # Process all available keyboard input
                    while not keyboard_queue.empty():
                        direction = await keyboard_queue.get()
                        process_curses_input(direction, keyboard)

                    # Send messages
                    while not message_send_queue.empty():
                        message = await message_send_queue.get()
                        await ws.send_str(message)


async def clear_messages(messages_queue):
    if not messages_queue.empty():
        messages_queue._queue.clear()

async def clear_keyboard_queue(keyboard_queue):
    if not keyboard_queue.empty():
        keyboard_queue._queue.clear()

def draw_cube(stdscr, x, y, frame_count):
    # Get size of the terminal window
    height, width = stdscr.getmaxyx()

    # Alternate between 'o' and 'x' in each frame
    ball_char = 'o' if frame_count % 2 == 0 else 'x'

    # Draw the cube if it is within the terminal window
    if x >= 0 and x < width and y >= 0 and y < height:
        stdscr.addstr(y, x, ball_char)


def print_messages(stdscr, messages_queue):
    for i, message in enumerate(messages_queue._queue):
        stdscr.addstr(i, 0, message)

def print_keyboard(stdscr, keyboard_queue):
    for i, message in enumerate(keyboard_queue._queue):
        stdscr.addstr(i, 0, message)

def process_curses_input(direction, keyboard, message_send_queue):
    try:
        if direction == 'up':
            keyboard['y'] -= 1
        elif direction == 'down':
            keyboard['y'] += 1
        elif direction == 'left':
            keyboard['x'] -= 1
        elif direction == 'right':
            keyboard['x'] += 1

        elif direction == 'exit':
            raise KeyboardInterrupt

    except KeyboardInterrupt:
        raise KeyboardInterrupt
    
    except Exception as e:
        print(f'Error: {e}')


async def run_curses_app(stdscr, keyboard_queue, messages_recieve_queue, message_send_queue, keyboard):
    frame_rate = 60  # Adjust the frame rate as needed (frames per second)
    frame_delay = 1 / frame_rate
    frame_count = 0

    while True:
        stdscr.clear()

        # Process all available keyboard input
        while not keyboard_queue.empty():
            direction = await keyboard_queue.get()
            process_curses_input(direction, keyboard)

        # Draw the cube
        draw_cube(stdscr, keyboard['x'], keyboard['y'], frame_count)

        # Display messages
        while not messages_recieve_queue.empty():
            message = await messages_recieve_queue.get()
            stdscr.addstr(0, 0, message)

        stdscr.refresh()

        # Increment frame count
        frame_count += 1

        # Add a delay to control the frame rate
        await asyncio.sleep(frame_delay)


async def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    curses.halfdelay(1)  # Make getch() non-blocking
    curses.noecho()  # Don't echo keyboard input
    curses.start_color()  # Enable color mode
    curses.use_default_colors()  # Use default colors

    # List of WebSocket URIs to connect to
    websocket_uris = ['ws://localhost:8001/ws/lobby2/?client_id=1']

    # Create a queue for keyboard input
    keyboard_queue = asyncio.Queue()

    # Create a queue for WebSocket messages
    messages_recieve_queue = asyncio.Queue()
    message_send_queue = asyncio.Queue()

    # Initialize the cube position
    keyboard = {'x': 0, 'y': 0}

    # Create tasks for curses input, WebSocket message reception, sending messages, and curses app
    curses_input_task_instance = asyncio.create_task(curses_input_task(stdscr, keyboard_queue))
    websocket_receive_task_instance = asyncio.create_task(websocket_receive_task(stdscr, websocket_uris[0], messages_recieve_queue, keyboard_queue))
    websocket_send_task_instance = asyncio.create_task(websocket_send_task(stdscr, websocket_uris[0], message_send_queue, keyboard_queue))
    run_curses_app_task_instance = asyncio.create_task(run_curses_app(stdscr, keyboard_queue, messages_recieve_queue, message_send_queue, keyboard))

    try:
        # Run the tasks concurrently
        await asyncio.gather(
            curses_input_task_instance,
            websocket_receive_task_instance,
            websocket_send_task_instance,
            run_curses_app_task_instance
        )

    except KeyboardInterrupt:
        # Cancel tasks on KeyboardInterrupt
        curses_input_task_instance.cancel()
        websocket_receive_task_instance.cancel()
        websocket_send_task_instance.cancel()
        run_curses_app_task_instance.cancel()

        # Wait for the tasks to be canceled
        await asyncio.gather(
            curses_input_task_instance,
            websocket_receive_task_instance,
            websocket_send_task_instance,
            run_curses_app_task_instance,
            return_exceptions=True
        )

    # Cleanup
    curses.curs_set(1)
    curses.echo()
    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(lambda stdscr: asyncio.run(main(stdscr)))
    print("Done!")
