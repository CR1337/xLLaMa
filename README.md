[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/CR1337/xLLaMa/blob/master/LICENSE)

# xLLaMa

## Abstract
Links to Presentation pdfs

## How to use
(Link to video)
Links to installation



## Repository Structure


## Architecture
### Component Diagrams
#### Frontend
#### Backend
### Sequence Diagrams



## Setup

### Installation

#### 1. Install Docker
See [Docker Installation](https://docs.docker.com/engine/install/) (if not already installed)

#### 2. Install Python 3
Install at least Python 3.10 with Pip (if not already installed). Earlier versions might work but are not tested.

#### 3. Clone this Repository
```bash
git clone https://github.com/CR1337/xLLaMa.git
```

#### 4. Change into the Repository
```bash
cd xLLaMa
```

#### 5. Create a virtual environment (optional)
```bash
python3 -m venv .venv
```

#### 6. Activate the virtual environment (optional)
```bash
source .venv/bin/activate
```

#### 7. Run setup script
If you are on the production server with GPUs 2 and 3, run
```bash
bin/setup
```
else run
```bash
bin/setup-local
```

### Usage
#### 1. Run the application
For running in the background (recommended for production):
```bash
bin/run
```
For seeing terminal output (recommended for development):
```bash
bin/run-blocking
```

If you are not on the production server with GPUs 2 and 3 use
```bash
bin/run-local
```
or
```bash
bin/run-blocking-local
```
respectively.

#### 2. Open the application
Open the application in a browser at http://localhost:8080. You can replace localhost with the IP of the server.

#### 3. Stop the application
```bash
bin/stop
```
or if you are not on the production server with GPUs 2 and 3
```bash
bin/stop-local
```


## Dependencies 


## Hardware Requirements