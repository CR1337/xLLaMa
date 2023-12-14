# xLLaMa

## Setup

### 1. Install Docker
See [Docker Installation](https://docs.docker.com/engine/install/) (if not already installed)
### 2. Install Python 3
Install at least Python 3.10 (if not already installed). Earlier versions might work but are not tested.
### 3. Clone this Repository
```bash
git clone https://github.com/CR1337/xLLaMa.git
```
### 4. Change into the Repository
```bash
cd xLLaMa
```
### 5. Create a virtual environment (optional)
```bash
python3 -m venv .venv
```
### 6. Activate the virtual environment (optional)
```bash
source .venv/bin/activate
```
### 7. Install dependencies
```bash
pip3 install -r requirements.txt
```
### 8. Build docker images
```bash
bin/build
```
### 9. Run tests (optional)
```bash
bin/test
```

## Usage
### 1. Run the application
For running in the background (recommended for production):
```bash
bin/run
```
For seeing terminal output (recommended for development):
```bash
bin/run-blocking
```
### 2. Open the application
Open the application in a browser at http://host:8080 where **host** is the address of the machine running the application.
### 3. Stop the application
```bash
bin/stop
```
