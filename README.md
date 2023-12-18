<div align="center">

## PIXEL PONG


[![GitHub last commit](https://img.shields.io/github/last-commit/andresmejiaro/transcend?color=blue&label=Last%20commit&logo=git&maxAge=3600)](https://github.com/andresmejiaro/transcend/commits)
[![GitHub issues](https://img.shields.io/github/issues/andresmejiaro/transcend?label=Issues&color=blue&maxAge=3600)](https://github.com/andresmejiaro/transcend/issues)
[![GitHub forks](https://img.shields.io/github/forks/andresmejiaro/transcend?label=Forks&color=blue&maxAge=3600)](https://github.com/andresmejiaro/transcend/network)

[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/andresmejiaro/transcend?label=Code%20size&maxAge=3600)](https://github.com/andresmejiaro/transcend)

</div>


# Ft_trascendence

This project is about creating a website where users will play Pong with others. It has to provide a nice
user interface and real-time multiplayer online games!

![Pong Game GIF](https://media.giphy.com/media/l46CAEUwLewax0LTy/giphy.gif)

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Arquitecture](#arquitecture)
- [Installation](#installation)
- [Web](#web)
- [Chat](#chat)
- [Game](#game)
- [Multiplayer](#multiplayer)
- [Tournament](#tournament)	
- [AI](#ai)
- [Database](#database)
- [Concepts](#concepts)
- [Contribution](#contribution)

## Description

# Ft_trascendence

Welcome to The Ultimate Pong Tournament!!!

A thrilling single page web application that brings the classic Pong game to life in an interactive and engaging multiplayer environment.

![Pong Game GIF](https://potduggans.com/wp-content/uploads/2019/02/PING-PONG-GIF.gif)

Ft_trascendence is an ambitious project that endeavors to create an immersive web-based gaming platform. Our mission is to enable users to experience the joy of playing Pong in real-time against other players or alone against the IA while offering a seamless and visually appealing user interface.

## Features

- **Real-time Multiplayer Pong:** Engage in exciting Pong matches with friends or other online players in a real-time multiplayer setup.
  
- **Secure User Management:** Robust user authentication and management system ensuring secure access to the gaming platform.

- **Alone against the machine:** A working IA to  give you the oportunity to improve your gaming to impress your friends.

- **Users data base:** 

## Arquitecture

### Project Structure Overview

The project comprises various folders and files, each serving a distinct purpose:

![estructure]()


The project structure segregates functionalities and components, dividing them into backend, frontend, testing, AI implementation, and configurations. Each directory contains specific updates and functionalities based on recent commits, aiming to enhance the overall user experience, server logic, and game functionalities.

- **APItests:** Contains CLI clients for API testing, primarily focused on the CLI game.

  `CLItester.py` is a Python script responsible for managing WebSocket connections, handling game updates, and rendering a terminal-based Pong game. It enables communication with a WebSocket server, updates the game canvas based on incoming data, draws game components, and performs essential terminal actions such as screen clearing. Customizations or enhancements might be necessary depending on specific use cases.

  The `apitester.py` Python script is a utility tool designed for making HTTP requests to an API. It handles functionalities like obtaining CSRF tokens, signing up users, and executing various API calls (GET, POST, PUT, DELETE) using the requests library. The script supports CLI usage and requires proper endpoint specifications along with optional data for POST and PUT requests.

  The `wstester.py` Python script acts as a WebSocket client, allowing users to interact with a WebSocket server. It prompts for user input to specify the Tournament ID and Client ID, establishes a WebSocket connection to the provided URI, and enables users to send and receive messages in JSON format, facilitating communication with the WebSocket server through command inputs.

- **Backend:** Handles the server-side logic and functionalities. Recent updates include enhancements related to lobby WebSocket and online status. Using as image base `python:3.7-alpine` and exposes de port 8000 to allow backend communication.
  
  The `settings.py` file determine the server's particular behavior, Dockerized environments, application management, database, the utilization of channels for real-time communication, and CORS to enable requests between different origins.
Entails specific decisions regarding the server's implementation in a Dockerized environment, channel layers for asynchronous and real-time communication, and permitted origins for requests between domains.
  
  The `urls.py` file manages URL routing by mapping specific URLs to corresponding views or endpoints within the Django server. It configures the admin panel, API endpoints, WebSocket URLs, and serves static media files, controlling the handling of incoming requests in the web application.

  The `manage.py` script is Django's command-line tool used for administrative tasks. It configures the Django environment, executes management commands, and serves as the entry point for interacting with the Django project via the command line, facilitating tasks like database operations, server startup, and project management.

- **Frontend:** Manages the client-side interface and user experience. Recent updates involve improvements associated with lobby WebSocket and online status.

- **Nginx:** Includes configurations and updates related to the NGINX web server, particularly in merging the develop branch.

- **Python-pong:** Incorporates features related to the AI option within the Pong game, added recently.

- **Makefile:** Manages compilation and build operations. Recent fixes include cleaning functionalities.

- **docker-compose.yml:** Specifies the services and configurations for Docker Compose.

### Installation
1. Clone the repository.
2. Navigate to the project directory.
3. Run `npm install` to install dependencies.
4. Configure environment variables.
5. Start the server using `npm start`.

1. Access the website through the provided URL.
2. Sign up or log in securely.
3. Choose the Pong game option to start playing.
4. Interact with friends, other users or the evil IA in real-time gameplay.

## Web
sdgzdg

## Chat
Describe la implementación del chat en tiempo real, las tecnologías utilizadas (por ejemplo, WebSockets), cómo los usuarios se comunican entre sí, etc.

## Game
Detalla cómo se implementó el juego de Pong, los controles, la lógica del juego, etc.

## Multiplayer
Explica cómo se gestionan las partidas multijugador, la sincronización entre jugadores, etc.

## Tournament
Si está implementado, describe cómo se estructuran los torneos, cómo los jugadores participan, las reglas, etc.

## AI
Explica la implementación del modo de juego contra la IA, cómo se diseñó y qué estrategias sigue la IA.

## Database
Detalla la estructura de la base de datos utilizada para almacenar la información de los usuarios, partidas, registros, etc. Puedes incluir:

Tipo de base de datos: Si es relacional o no relacional.
Esquema de la base de datos: Describe las tablas (en caso de bases de datos relacionales), colecciones (en caso de bases de datos no relacionales), y cómo están relacionadas entre sí.
Seguridad y gestión de datos: Si se implementan medidas de seguridad, como cifrado de contraseñas, y cómo se manejan los datos de los usuarios.

## Concepts
términos o tecnologías clave utilizadas en el proyecto.
asgiref==3.7.2
asttokens==2.4.1
async-timeout==4.0.3
channels==4.0.0
channels-redis==4.1.0
colorama==0.4.6
Django==3.2.23
django-cors-headers==4.1.0
executing==2.0.1
icecream==2.1.3
importlib-metadata==6.7.0
msgpack==1.0.5
passlib==1.7.4
Pillow==9.5.0
psycopg2-binary==2.9.9
Pygments==2.17.2
pyotp==2.9.0
pypng==0.20220715.0
pytz==2023.3.post1
qrcode==7.4.2
redis==5.0.1
six==1.16.0
sqlparse==0.4.4
typing_extensions==4.7.1
zipp==3.15.0
