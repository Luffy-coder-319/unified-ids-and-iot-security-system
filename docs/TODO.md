# Dashboard Frontend Development Tasks

- [x] Create React app in src/frontend/ using npm create vite@latest
- [x] Install Tailwind CSS in the React app
- [x] Update App.js to include dashboard layout with sections for alerts and flows
- [x] Implement WebSocket connection in React to receive real-time alerts
- [x] Add API fetch for initial flows data
- [x] Style components with Tailwind CSS for a clean UI
- [x] Build the React app to generate static files
- [x] Update src/api/main.py to serve static files from the build directory
- [x] Test the dashboard by running the FastAPI server and opening the frontend

# Improvements Implemented

- [x] Fix byte_count accumulation bug in device_profiler.py
- [x] Improve alerts display in frontend to show detailed information
- [x] Implement train.py with basic model training logic
- [x] Implement data_loader.py for loading datasets
- [x] Implement preprocessor.py for data preprocessing
- [x] Implement mqtt_security.py for MQTT monitoring
- [x] Add logging setup to main.py
- [x] Create config.yaml for configuration management
- [x] Fix typo in config_loader.py
- [x] Retrain the model with updated train.py to fix sklearn warnings
- [x] Suppress TensorFlow warnings in predict.py
- [x] Add dummy flows for demonstration when no live traffic
- [x] Implement real-time updates for flows using WebSocket
- [x] Increase Vite chunk size warning limit to suppress build warnings
- [x] Suppress TensorFlow retracing warnings by setting TF_CPP_MIN_LOG_LEVEL to 3
- [x] Make the flow line graph more appealing with dark theme styling
- [x] Change alerts display to show "Normal" instead of "No threats detected"
