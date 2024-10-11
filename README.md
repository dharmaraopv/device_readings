# Device Readings API

The Device Readings project implements a web API that receives, stores, and retrieves in-memory device readings, with endpoints for fetching the latest reading timestamp and cumulative count, while handling duplicate and out-of-order data.

## Features

- **In-Memory Timestamp Store**: An in-memory store for timestamps per device id, maintaining a fixed capacity and evicting the oldest timestamp if the capacity is exceeded.
- **Device Readings API**: A web API that receives, stores, and retrieves in-memory device readings.
- **Latest Reading Timestamp**: An endpoint for fetching the latest reading timestamp for a specific device.
- **Cumulative Count**: An endpoint for fetching the cumulative count of readings for a specific device.
- **Duplicate and Out-of-Order Data Handling**: The system handles duplicate and out-of-order data.
- **Configurable Store Capacity**: The capacity of the timestamp store can be configured via settings.

## Installation

### Prerequisites

- Python 3.x (tested on Python 3.9)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/dharmaraopv/device_readings
   cd device_readings
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
    ```bash
   MODE=PROD uvicorn main:app --reload
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
├── device_readings/
│   ├── stores/
│   ├── tests/
│   ├── config/
│   ├── main.py
│   ├── device_readins_service.py
│   └── requirements.txt
```

- **`main.py`**: The main entry point for the FastAPI application.
- **`device_readings_service.py`**: The core logic for the device readings service.
- **`stores/`**: Contains the data store implementations.
- **`tests/`**: Test cases for the application.

## Documentation
[Here's](https://dharmapv.notion.site/Design-Document-Device-Readings-Service-11b8ba76658780918c4cede1a7decd0a?pvs=4) more detailed design document.
Links to specific sections:
* [Design considerations]()
* [Request flow]()
* [Edge Cases]()
* [Future Improvements]()

## Testing
The tests for this project are located in the `tests/` directory. They are designed to validate the functionality and robustness of the system. Here's an overview:

1. **Unit Tests**: These tests are designed to test individual components of the application in isolation. In the provided example, the unit tests are mocking the `device_readings_service` to isolate the tests to the FastAPI routes. They are checking the behavior of the endpoints under normal conditions and when the service returns an error.

2. **Validation Tests**: These tests are part of the unit tests and are specifically designed to test the behavior of the system when `device_readings_service` returns an error. They are checking the HTTP status code and the error message returned by the endpoints.

3. **End-to-End Tests**: These tests are designed to test the system as a whole, from start to finish. They are running the actual server and making requests to it. In the provided example, they are checking the behavior of the endpoints under normal conditions.

4. **Edge Cases**: These tests are designed to test the behavior of the system under unusual or extreme conditions. In the provided example, they are checking the behavior of the endpoints when trying to get the cumulative count or latest timestamp for a device that doesn't exist.

Special cases in the tests include handling of errors returned by the `device_readings_service` and handling of non-existent devices. These cases are important to ensure that the system behaves correctly under all possible conditions.

### To run the tests:

```bash
MODE=TEST pytest -v
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

