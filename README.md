# Device Readings API

The Device Readings project implements a web API that receives, stores, and retrieves in-memory device readings, with endpoints for fetching the latest reading timestamp and cumulative count, while handling duplicate and out-of-order data.

## Features

- **Feature1** : Description

## Installation

### Prerequisites

- Python 3.x (tested on Python 3.9)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/dharmaraopv/device_reader
   cd device_reader
   ```

2. Create and activate a virtual environment:
   ```bash
   python3.9 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the application:
   a. In-memory store:
   ```bash
   ENV=in_mem uvicorn main:app --reload
   ```
   b. Redis store:
   ```bash
    ENV=redis uvicorn main:app --reload
   ```
   
7. Read the API documentation and try apis via [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API Endpoints

### 1. Update device counts

**POST** `/api/devices/`

- **Description**: Updates counts for a given device
- **Request Body**: 
  

### 2. Get Latest timestamp for a device

**GET** `/api/devices/{device_id}/timestamp`

- **Description**: Fetch the timestamp of the latest reading for a specific device
- **Path Parameter**:
  - `device_id` (string): A unique identifier for the device in UUID format.
  
- **Response**: `latest_timestamp` in json format.

### 2. Get Cumulative Count for a device

**GET** `/api/devices/{device_id}/total-count`

- **Description**: Fetch the cumulative count for for a specific device
- **Path Parameter**:
  - `device_id` (string): A unique identifier for the device in UUID format.
  
- **Response**: `total_count` in json format.


## Project Structure

```plaintext
├── device_reader/
│   ├── __pycache__/
│   ├── stores/
│   ├── tests/
│   ├── main.py
│   ├── device_reader.py
│   ├── settings.py
│   └── requirements.txt
```

- **`main.py`**: The main entry point for the FastAPI application.
- **`tests/`**: Test cases for the application.

## Documentation
[Here's](https://dharmapv.notion.site/Design-Document-Device-Readings-Service-11b8ba76658780918c4cede1a7decd0a?pvs=4) more detailed design document.
Links to specific sections:
* [Design considerations]()
* [Request flow]()
* [Edge Cases]()

## Testing

To run the tests:

```bash
ENV=test pytest -v
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

