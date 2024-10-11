# Device Readings API

The Device Readings project implements a web API that receives, stores, and retrieves in-memory device readings, with endpoints for fetching the latest reading timestamp and cumulative count, while handling duplicate and out-of-order data.

## Features

- **Device Readings API**: A web API that receives, stores, and retrieves in-memory device readings.
- **Latest Reading Timestamp**: An endpoint for fetching the latest reading timestamp for a specific device.
- **Cumulative Count**: An endpoint for fetching the cumulative count of readings for a specific device.
- **Duplicate and Out-of-Order Data Handling**: The system handles duplicate and out-of-order data.
- **In-Memory Timestamp Store**: An in-memory store for timestamps per device id, maintaining a fixed capacity and evicting the oldest timestamp if the capacity is exceeded.
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
```json
    Example JSON payload:
    {
        "id": "6e7b58d7-0e4f-4b6c-8b9a-0b9f9b9c9d6f",
        "readings": [
            {
                "timestamp": "2021-09-30T12:00:00",
                "count": 5
            },
            {
                "timestamp": "2021-09-30T12:05:00",
                "count": 3
            }
        ]
    }
```
- **Response**: A success message or an error message with 500 status if the update fails.
  

### 2. Get Latest timestamp for a device

**GET** `/api/devices/{device_id}/timestamp`

- **Description**: Fetch the timestamp of the latest reading for a specific device
- **Path Parameter**:
  - `device_id` (string): A unique identifier for the device in UUID format.
  
- **Response**: `latest_timestamp` in json format.

### 2. Get Cumulative Count for a device

**GET** `/api/devices/{device_id}/cumulative_count`

- **Description**: Fetch the cumulative count for for a specific device
- **Path Parameter**:
  - `device_id` (string): A unique identifier for the device in UUID format.
  
- **Response**: `cumulative_count` in json format.


## Project Structure

```plaintext
├── device_readings/
│   ├── stores/
│   ├── tests/
│   ├── config/
│   ├── main.py
│   ├── device_readings_service.py
│   └── requirements.txt
```

- **`main.py`**: The main entry point for the FastAPI application.
- **`device_readings_service.py`**: The core logic for the device readings service.
- **`stores/`**: Contains the data store implementations.
- **`tests/`**: Test cases for the application.

## Docuemntation
### Class design
![Screenshot 2024-10-11 at 9.25.01 AM.png](images%2FScreenshot%202024-10-11%20at%209.25.01%E2%80%AFAM.png)

## Testing
### To run the tests:

```bash
MODE=TEST pytest -v
```

The tests for this project are located in the `tests/` directory. They are designed to validate the functionality and robustness of the system. Here's an overview:
### Unit Tests 
These tests are designed to test individual components of the application in isolation. All the business logic is tested in these unit tests. Mocks are utilized to isolate the components being tested from external dependencies. Following are the various unit tests suites:
1. `test_main.TestMain`: This test suite tests the main FastAPI application and its endpoints. Input validation tests are covered in these tests.
2. `**test_device_readings_service.TestDeviceReadingsService**`: This test suite tests the core logic of the device readings service. It covers the handling of duplicate and out-of-order data, updating the device counts, and fetching the latest timestamp and cumulative count for a device.
3. `**test_stores.TestInMemoryTimestampStore**`: This test suite tests the in-memory timestamp store implementation. It covers adding and updating timestamps, evicting old timestamps, and fetching the latest timestamp for a device.
4. `**test_stores.TestDeviceReadingsStore**`: This test suite tests the device readings store implementation. It covers adding and updating device counts, fetching the cumulative count for a device, and handling errors.

### Functional Tests
These tests are designed to test a module as a whole including components the module depends on. `test_device_readings_service.TestDeviceReadingsServiceFunctional` tests the device readings service with the in-memory timestamp store and device readings store.

### End-to-End Tests
This test suite implemented in `tests_e2e.E2ETests` verifies the integration and functionality of the main API endpoints in the application.
It uses FastAPI's TestClient to simulate HTTP requests and tests scenarios such as:

- Adding device readings and retrieving cumulative counts and timestamps.
- Handling duplicate timestamps both within the same request and across multiple requests.
- Enforcing device store capacity limits and verifying error messages when exceeded.
- Ensuring each device maintains independent readings and can handle multiple devices simultaneously.
- Validating correct responses for unknown device requests.
- Ensuring the correct handling of out-of-order timestamps without overriding the most recent entry.


## Connecting to external services
The system is designed to be easily extensible to connect to external services for persistence of data.
This can be achieved by implementing the DeviceReadingsStore interface and the TimestampStore interface in the stores module. 
The implementation of these interfaces can interact with external services like databases, cloud storage, or other data stores.

Here are few considerations for designing the external service connection:
1. Addition of a new device to the store should be atomic.
2. Updation of the device count and timestamp should be atomic.


## Future Improvements
Following are additional improvements that can be made to the system:
### Processing addition of records in a background task
Implement a background task to process the addition of records to the timestamp store. This will allow the system to handle a large number of requests concurrently without blocking the main thread.
### Additional edge case handling
Identify and handle additional edge cases that may arise in the system. Here are a few cases that are not handled:
- Negative counts are not handled. Ideally an error should be raised
- Invalid timestamps are possible (ex: dst change, leap seconds, etc.). Currently, the system allows invalid timestamps.
### Data Persistence
Implement a persistent data store (e.g., a database) to store device readings and timestamps. This will allow the system to maintain data across restarts and scale to handle larger volumes of data.
### Logging and monitoring
Implement logging to record important events and errors in the system. This will help in debugging issues and monitoring the system's behavior.
### Additional tests
Identify and add additional test cases to cover edge cases and unusual conditions. This will help ensure the system's robustness and reliability.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

