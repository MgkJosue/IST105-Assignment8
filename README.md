# IST105 Assignment 8 - DHCP Simulator

## Description
A Django web application that simulates DHCP server functionality, supporting both DHCPv4 and DHCPv6 with EUI-64 address generation.

## Features
- MAC address validation
- IPv4 address assignment from 192.168.1.0/24 pool
- IPv6 EUI-64 address generation from MAC address
- Bitwise operations on MAC addresses
- MongoDB integration for lease storage
- Lease management and viewing

## Installation (Local)

1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `.\venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Ensure MongoDB is running on localhost:27017
6. Run server: `python manage.py runserver`
7. Access at: http://127.0.0.1:8000

## Branches
- `main`: Stable production code
- `development`: Integration testing
- `feature1`: Initial development of IP assignment logic