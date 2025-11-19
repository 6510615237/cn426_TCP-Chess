# cn426_TCP-Chess

## Member

1. 6510615153 นิติพงษ์ ขัดสีทะลี
1. 6510615237 พลวิชญ์ วงษ์สุนทร
1. 6510615278 วงศธร ดีโรจนวงศ์
1. 6510615336 สุธีธร กาวิเนตร

## Project Description

TCP Chess is a Client - Server App for Users on the same network to play chess together.

## Download

You can download the binaries on the "Release" Tab on the right side.

We've already separated between Window and Linux executables.

Make sure to change permission of Linux executables to execute the app.

## Quick Guide

1. git clone https://github.com/6510615237/cn426_TCP-Chess \[your-dir]

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

```
**CERTIFICATE AND PRIVATE KEY MUST BE IN THE SAME DIRECTORY AS THE SERVER FILE.**

If your server is in directory:

./chess/test/server.py

Then that same directory must have:

/chess/test/cert.pem [Certificate]
/chess/test/key.pem [Private_Key]

With the same name.

Use openssl to generate certificate and private key.
```

Example

```bash
openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
```

### Client App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
python client/ui.py
```

**The Server App must be running on that IP Address to allow Client App to connect to that IP address.**

The chess game can start with 1 player waiting after making their first move, but will require another player to join to progress any further.

## Compile to executable files

If you want to compile python file into executables yourself, use Pyinstaller to compile python file into executable file.

```bash
pip install pyinstaller
```

### Server App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
pyinstaller --onefile --name server_chess --path=./server/ server/main.py
```

In this case, the executable file will be inside:

`./dist/server_chess.exe`

```
**CERTIFICATE AND PRIVATE KEY MUST BE IN THE SAME DIRECTORY AS THE SERVER FILE.**

If your server is in directory:

./chess/test/server_chess.exe

Then that same directory must have:

/chess/test/cert.pem [Certificate]
/chess/test/key.pem [Private_Key]

With the same name.

Use openssl to generate certificate and private key.
```

Example

```bash
openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem
```

### Client App

1. Open Terminal in the project directory.
2. Run the following code:

```bash
pyinstaller --noconsole --onefile --name client_chess --path=./client/ client/ui.py  
```

In this case, the executable file will be inside:

`./dist/client_chess.exe`

## In case of Linux

### **If you are on Linux, install python3-tkinter package via your distro's installer first**

**Example on Rocky Linux**

```bash
sudo dnf install -y python3-tkinter
```

Running the Server on Linux through double-clicking from UI will not cause console to pop up.

Please find the process running in the background and kill the process yourself.

It is recommended to execute the file from the terminal.