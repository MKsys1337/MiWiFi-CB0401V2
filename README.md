# MiWiFi-CB0401V2
![GitHub release (latest by date)(https://img.shields.io/github/v/release/MKsys1337/MiWiFi-CB0401V2?style=flat-square)](https://github.com/MKsys1337/MiWiFi-CB0401V2/releases/tag/v1.0.1)
![GitHub license(https://img.shields.io/github/license/MKsys1337/MiWiFi-CB0401V2.svg?style=for-the-badge)](https://github.com/MKsys1337/MiWiFi-CB0401V2#MIT-1-ov-file)
![HACS Custom(https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/MKsys1337/MiWiFi-CB0401V2)
![GitHub commit activity(https://img.shields.io/github/commit-activity/y/MKsys1337/MiWiFi-CB0401V2?style=for-the-badge)](https://github.com/MKsys1337/MiWiFi-CB0401V2)
# Xiaomi 5G CPE CB0401V2 Integration for Home Assistant

## Overview

The **Xiaomi 5G CPE CB0401V2 Integration** for Home Assistant allows users to monitor and access comprehensive data from their Xiaomi 5G CPE CB0401V2 router directly in Home Assistant. With this integration, you can display key information such as signal strength, network details, Wi-Fi status, and more within your smart home dashboard.

## Features

- **Signal Strength and Quality**: Monitor LTE and 5G signal strength (RSRP) and quality (RSRQ).
- **Network Information**: View the current network type, operator, reception band, and more.
- **Data Usage**: Track data usage in MB.

## Installation

### Requirements

- **Home Assistant**: Version 2021.6.0 or higher
- **Xiaomi 5G CPE CB0401V2 Router**: Firmware version 3.0.59 or higher
- **Python**: 3.8 or higher

### HACS Installation

1. **Install HACS** (if not already installed):
   - Follow the official [HACS installation guide](https://hacs.xyz/docs/installation/prerequisite).

2. **Add the custom repository**:
   - Go to **HACS** in the Home Assistant interface.
   - Click on **Integrations** and then the **+** icon at the bottom right.
   - Search for `Xiaomi 5G CPE CB0401V2` or directly add the repository URL:
     ```
     https://github.com/MKsys1337/MiWiFi-CB0401V2
     ```
   - Click **Add**.

3. **Restart Home Assistant**:
   - Go to **Settings** > **System** > **Restart** and restart Home Assistant.

### Manual Installation

1. **Clone the repository**:
   - Navigate to the `custom_components` directory of your Home Assistant installation:
     ```
     /config/custom_components/
     ```
   - Clone the repository:
     ```bash
     git clone https://github.com/MKsys1337/MiWiFi-CB0401V2 miwifi_cb0401v2
     ```

2. **Restart Home Assistant**:
   - Go to **Settings** > **System** > **Restart** and restart Home Assistant.

## Configuration

This integration uses a **Config Flow**, so no manual `configuration.yaml` changes are necessary.

1. **Add the integration**:
   - Go to **Settings** > **Devices & Services** > **Integrations**.
   - Click the **+** icon at the bottom right.
   - Search for `MiWiFi CB0401V2` and select it.

2. **Enter credentials**:
   - Input the router's IP address (default: `192.168.31.1`).
   - Enter the username (usally `admin` and password for the router.
   - Click **Submit**.

3. **Verify connection**:
   - If successful, the available sensors will be automatically added.

## Available Sensors

### General Router Information

- **Router Name**
- **Firmware Version**
- **Hardware Model**
- **Model Designation**
- **MAC Address**
- **Serial Number**
- **IMEI**

### Network Information

- **LTE Signal Strength (RSRP)**
- **LTE Signal Quality (RSRQ)**
- **5G Signal Strength (RSRP)**
- **5G Signal Quality (RSRQ)**
- **LTE Signal SNR**
- **5G Signal SNR**
- **Network Type**
- **Network Operator**
- **Data Usage**
- **LTE Reception Band**
- **5G Reception Band**
- **Frequency Bands**
- **Cell ID**
- **5G Cell ID**
- **WiFi SSID 2.4 GHz**
- **WiFi SSID 5 GHz**
- **WiFi Active Clients**

## Usage

### Adding Sensors to Your Dashboard

1. **Navigate to your dashboard**:
   - Go to **Overview** in Home Assistant.

2. **Edit your dashboard**:
   - Click the **three-dot menu** in the top right and select **Edit Dashboard**.

3. **Add a new card**:
   - Click **Add Card**.

4. **Select the desired card type**:
   - Choose **Entities**, **Glance**, **Gauge**, **History Graph**, etc.

5. **Select the desired sensors**:
   - Search for and add the sensors you want to display on the card.

6. **Save the card**:
   - Click **Save** to confirm the changes.

## Development

### Prerequisites

- **Python 3.8 or higher**
- **Home Assistant Core**
- **IDE** (e.g., Visual Studio Code recommended)
- **Git**

### Cloning the Repository

```bash
git clone https://github.com/MKsys1337/MiWiFi-CB0401V2.git
cd MiWiFi-CB0401V2
```

### Installing Dependencies

Ensure all necessary dependencies are installed. They are defined in the `manifest.json` file.

## Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**.
2. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Commit your changes**:
   ```bash
   git commit -m "Description of your changes"
   ```
4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Create a Pull Request** in the main repository.

Ensure your code follows PEP 8 guidelines and passes existing tests.

## Security

- **Confidentiality of credentials**: Never share your credentials publicly.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- **Home Assistant Community** for their excellent documentation and support.
- **Xiaomi** for providing powerful routers.
- **Open-Source Community** for the helpful tools and libraries.

