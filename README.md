# Flask Project

## Overview

This is a Python Flask application for [briefly describe the purpose of the application]. 

## Getting Started

To get started with this Flask project, follow these steps:

### Prerequisites

- Python 3.x

### Installation

1. **Clone the Repository**

    ```bash
    git clone https://github.com/giaphupham/weather_app_server.git
    cd weather_app_server
    ```

2. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**

    ```bash
    python app.py
    ```

    The application will be available at `http://127.0.0.1:5000/`.

#### Using Docker

1. **Build the Docker Image**

    ```bash
    docker build -t weather_app_server .
    ```

2. **Run the Docker Container**

    ```bash
    docker run -p 5000:5000 weather_app_server
    ```

    The application will be available at `http://127.0.0.1:5000/`.
