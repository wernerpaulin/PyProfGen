

# PyProfGen
 Speed and position profile generator made in Python
 <br />
 Link to Repository: https://github.com/wernerpaulin/PyProfGen

<!-- APP SHIELDS -->
[![GitHub issues](https://img.shields.io/github/issues/wernerpaulin/PyProfGen)](https://github.com/wernerpaulin/PyProfGen/issues)
[![GitHub forks](https://img.shields.io/github/forks/wernerpaulin/PyProfGen)](https://github.com/wernerpaulin/PyProfGen/network)
[![GitHub stars](https://img.shields.io/github/stars/wernerpaulin/PyProfGen)](https://github.com/wernerpaulin/PyProfGen/stargazers)
[![GitHub license](https://img.shields.io/github/license/wernerpaulin/PyProfGen)](https://github.com/wernerpaulin/PyProfGen/blob/main/LICENSE)


<!-- APP LOGO -->
<br />
<p align="center">
  <a href="https://github.com/wernerpaulin/PyProfGen">
    <img src="images/icon.png" alt="Logo" width="200" height="200">
  </a>

  <h3 align="center">PyProfGen</h3>

  <p align="center">
    This profile generator is written in Python® 3. It generates a velocity and position profile depending on set parameters like target position, velocity and acceleration.
  </p>
</p>


<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-app">About The App</a>
      <ul>
        <li><a href="#gallery">Gallery</a></li>
        <li><a href="#features">Features</a></li>
        <li><a href="#operating-modes">Operating Modes</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#usage">Usage</a></li>
      </ul>
    </li>
    <li><a href="#communication">Communication</a>
      <ul>
        <li><a href="#interfaces">Interfaces</a></li>
        <li><a href="#published-ports">Ports Published By This App</a></li>
      </ul>
    </li>
    <li><a href="#data-management">Data Management</a></li>
      <ul>
        <li><a href="#environmental-variables">Environmental Variables</a></li>
        <li><a href="#volumes">Volumes</a></li>
      </ul>
    <li><a href="#information">Information</a></li>
    <li><a href="#legal-statemets">Legal Statements</a></li>
  </ol>
</details>

<!-- ABOUT THE APP -->
## About The App
### Gallery
<img src="images/gallery1.png" 
     alt="Gallery 1" 
     style="float:left; margin-right: 10px;" 
     width="200"/>
<img src="images/gallery2.png" 
     alt="Gallery 2" 
     style="float:left; margin-right: 10px;" 
     width="200"/>
<img src="images/gallery3.png" 
     alt="Gallery 3" 
     style="float:left; margin-right: 10px;" 
     width="200"/>
<img src="images/gallery4.png" 
     alt="Gallery 4" 
     style="float:left; margin-right: 10px;" 
     width="200"/>

### Features
* 100ms scan interval 
* Generates a velocity and rotary speed profile
* Generates position profile
* Dynamic deceleration ramp calculation in position control mode

### Operating Modes
* Velocity control
* Absolute position control
* Relative position control
* Automatic mode: cases the profile generator to initiate relative movements 
* Stop movement

### Built With
| Technology | Description |
| -------------- | ----------- |
| [Python®](https://www.python.org/) | asyncio for concurrent execution of coroutines |
| [Eclipse Paho®](https://www.eclipse.org/paho/) | MQTT client |
| [Docker®](https://www.docker.com/) | Container technology |


<!-- GETTING STARTED -->
## Getting Started

Find this app in the App Store and use it in a machine.

### Prerequisites
This app requires a MQTT broker which can either run as an app or on a different host but in the same network of the Runtime.

### Usage
1. This app is per default connecting to the Eclipse Mosquitto MQTT broker app on the Runtime. If you choose to use another broker change the <a href="#environmental-variables">environmental variable "MQTT_BROKER_IP"</a>.
2. This app is per default connecting to the broker via port 1883 which is the default port for MQTT. If you have multiple brokers running in parallel each of these brokers require a separate port. Please set the <a href="#environmental-variables">environmental variable "MQTT_BROKER_PORT"</a> accordingly.
3. An easy way to control this app is using the Node-RED app.


<!-- COMMUNICATION -->
## Communication
### Interfaces
The app publishes the following MQTT topics:

| Topic | Value Example |
| -------------- | ----------- |
| pyprofgen.lenze.mosaiq/parameteronconnect | ``` "{"setDistance": 200, "setVelocity": 300, "setAcceleration": 200, "maxPosition": 1000000000, "minPosition": -1000000000, "maxVelocity": 500, "maxAccleration": 1000.0, "maxMotorRotarySpeed": 2000.0, "automaticCycleStopTime": 1.0}" ``` |
| pyprofgen.lenze.mosaiq/monitor | ``` "{"actVelocity": 0, "actPosition": 0, "actRotarySpeed": 0.0}" ``` |
| pyprofgen.lenze.mosaiq/parameter | ``` "{"setDistance": 200, "setVelocity": 300, "setAcceleration": 200, "maxPosition": 1000000000, "minPosition": -1000000000, "maxVelocity": 500, "maxAccleration": 1000.0, "maxMotorRotarySpeed": 2000.0, "automaticCycleStopTime": 1.0}" ``` |
| pyprofgen.lenze.mosaiq/command | Stop: "MC_MoveStop" <br /> Move relative: MC_MoveRelative <br /> Move absolute: MC_MoveAbsolute <br /> Automatic mode: MC_LE_AutomaticMode |


### Published Ports By This App
| Container Port | Protocol | Description |
| -------------- | -------- | ----------- |
| n.a. | | |

**Please note: Ports can be mapped to different host ports in the machine settings**

<!-- DATA MANAGEMENT -->
## Data Management

### Environmental Variables
Environmental variables are used to initialize or define a certain functionality of an app and can be changed in the machine settings:
| Variable | Default Value | Changeable by User | Description | 
| -------- | ------------- | ------------------ | ----------- |
| MQTT_BROKER_IP | localhost | yes | Hostname or IP address of MQTT broker | 
| MQTT_BROKER_PORT | 1883 | yes | Port used by the MQTT broker |
| MQTT_BROKER_KEEPALIVE | 60 | yes | Maximum time that this app does not communicate with the broker |

### Volumes
Mount points are access points to volumes (like paths) provided to the app to read and write data:

| Mount Point | Default Data | Changeable by User | Description | 
| -------- | ------------- | ------------------ | ----------- |
| n.a. | | |


<!-- INFORMATION -->
## Information
| Developer | Compatibility | Size on Runtime | Copyright | License |
| ----------| ------------- |---------------- | --------- | ------- |
| [Lenze SE](https://www.lenze.com/) | Requires Runtime 1.0 or later | 61.7 MB | © 2021- [Lenze SE](https://www.lenze.com/) | MIT License. See `LICENSE` for more information. |


## Legal Statements
* "Python®" and the Python logos are trademarks or registered trademarks of the Python Software Foundation.
* "Eclipse®", "Mosquitto®", Paho® and the respective logos are trademarks or registered trademarks of the Eclipse Foundation.
* "Docker®" and "Docker Hub®" are trademarks or registered trademarks of Docker.
