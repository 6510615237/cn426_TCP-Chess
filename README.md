# cn426_TCP-Chess

## Member

1. 6510615153 นิติพงษ์ ขัดสีทะลี
1. 6510615237 พลวิชญ์ วงษ์สุนทร
1. 6510615278 วงศธร ดีโรจนวงศ์
1. 6510615336 สุธีธร กาวิเนตร

## Project Description

TCP Chess is a Client - Server App for Users on the same network to play chess together.

## Quick Guide

1. git clone https://github.com/NitipongK2546/trustyvote \[your-dir]

1. cd [your-dir]

Let's assume you are inside the project directory. Then it should have:

1. client
1. server

## How to run

### Server App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
python server/main.py
```

The server will now run on 0.0.0.0 port 60000.

### Client App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
python client/ui.py
```

**The Server App must be running on that IP Address to allow Client App to connect to that IP address.**

The chess game can start with 1 player waiting after making their first move, but will require another player to join to progress any further.

## Compile to executable files

Use Pyinstaller to compile python file into executable file.

### Client App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
pyinstaller --onefile --noconsole --name chess_client --path=./client/ ui.py  
```

In this case, the executable file will be inside:

`./dist/chess_client.exe`

**If you are on Linux, install python3-tkinter package via your distro's installer first**

Example on Rocky Linux

```bash
sudo dnf install -y python3-tkinter
```