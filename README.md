# IST105 Assignment 8 - DHCP Simulator

Django web application that simulates a DHCP server with DHCPv4 and DHCPv6 support, using bitwise operations for MAC address manipulation and EUI-64 for IPv6 generation.

## 🏗️ Architecture

```
Web Browser
    ↓
WebServer-EC2 (Amazon Linux 2)
├── Django App (Port 8000)
└── Private IP: 172.31.33.60
    ↓
MongoDB-EC2 (Ubuntu 22.04)
├── MongoDB 7.0 (Port 27017)
└── Private IP: 172.31.44.88
```

## 🚀 Quick Start - Local Setup

```bash
# Clone repository
git clone https://github.com/your-username/IST105-Assignment8.git
cd IST105-Assignment8

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install django pymongo

# Start MongoDB (Docker)
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Run Django server
python manage.py runserver

# Access: http://127.0.0.1:8000
```

## ☁️ AWS Deployment

### EC2 Instances

| Instance | OS | Purpose | Private IP Example |
|----------|-------|---------|-------------------|
| MongoDB-EC2 | Ubuntu 22.04 | Database Server | 172.31.44.88 |
| WebServer-EC2 | Amazon Linux 2 | Django Application | 172.31.33.60 |

### Security Groups Configuration

#### MongoDB-SG (Inbound Rules)
```
Type         Protocol   Port    Source              Description
SSH          TCP        22      0.0.0.0/0           SSH Access
Custom TCP   TCP        27017   172.31.33.60/32     MongoDB from WebServer
```

#### WebServer-SG (Inbound Rules)
```
Type         Protocol   Port    Source         Description
SSH          TCP        22      0.0.0.0/0      SSH Access
Custom TCP   TCP        8000    0.0.0.0/0      Django Application
HTTP         TCP        80      0.0.0.0/0      HTTP Access
```

⚠️ **Critical**: Replace `172.31.33.60` with YOUR actual WebServer private IP.

### Setup MongoDB-EC2

```bash
# Connect to MongoDB-EC2
ssh -i "your-key.pem" ubuntu@[MONGODB-PUBLIC-IP]

# Install MongoDB
sudo apt update && sudo apt upgrade -y
sudo apt install gnupg curl -y

curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg --dearmor

echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | \
   sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify status
sudo systemctl status mongod
```

#### Configure Remote Access

```bash
# Edit MongoDB configuration
sudo nano /etc/mongod.conf

# Change the following:
net:
  port: 27017
  bindIp: 0.0.0.0    # Change from 127.0.0.1 to 0.0.0.0

# Save and exit (Ctrl+O, Enter, Ctrl+X)

# Restart MongoDB
sudo systemctl restart mongod

# Verify it's listening on all interfaces
sudo netstat -tulpn | grep 27017
# Should show: 0.0.0.0:27017 (not 127.0.0.1:27017)
```

### Setup WebServer-EC2

```bash
# Connect to WebServer-EC2
ssh -i "your-key.pem" ec2-user@[WEBSERVER-PUBLIC-IP]

# Install dependencies
sudo yum update -y
sudo yum install python3 python3-pip git -y

# Clone repository
cd ~
git clone https://github.com/your-username/IST105-Assignment8.git
cd IST105-Assignment8

# Install Python packages
pip3 install django pymongo --user
```

#### Configure MongoDB Connection

Edit `assignment8/settings.py`:

```python
# MongoDB Configuration
MONGODB_CONFIG = {
    'host': '172.31.44.88',  # Replace with YOUR MongoDB-EC2 Private IP
    'port': 27017,
    'database': 'dhcp_leases',
    'collection': 'leases'
}

# Allowed hosts
ALLOWED_HOSTS = ['*']
```

⚠️ **Important**: Replace `172.31.44.88` with YOUR MongoDB-EC2 private IP.

#### Run Application

```bash
# Run Django server
python3 manage.py runserver 0.0.0.0:8000

# Or run in background:
nohup python3 manage.py runserver 0.0.0.0:8000 &

# View logs
tail -f nohup.out
```

**Access Application:** `http://[WEBSERVER-PUBLIC-IP]:8000`

## 🧪 Test Connectivity

### From WebServer-EC2 to MongoDB-EC2

```bash
# Test with netcat
nc -zv 172.31.44.88 27017

# Test with Python
python3 << EOF
from pymongo import MongoClient
try:
    client = MongoClient('172.31.44.88', 27017, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ Connected successfully to MongoDB")
except Exception as e:
    print(f"❌ Error: {e}")
EOF
```

## 🔧 Bitwise Operations Implemented

### 1. EUI-64 Universal/Local Bit Toggle

```python
def toggle_universal_bit(byte):
    """
    Toggles the 7th bit using XOR
    0x02 = 00000010 in binary
    """
    return byte ^ 0x02
```

**Example:**
- MAC: `AA:BB:CC:DD:EE:FF`
- AA (10101010) XOR 00000010 = 10101000 (A8)
- Result: `A8:BB:CC:FF:FE:DD:EE:FF`

### 2. MAC Address Parity Check

```python
def check_mac_sum_parity(mac_bytes):
    """
    Checks if sum of bytes is odd or even
    Uses AND bitwise with 1 to check LSB
    """
    total = sum(mac_bytes)
    is_odd = total & 1
    return "odd" if is_odd else "even"
```

**Example:**
- MAC: `00:1A:2B:3C:4D:5E`
- Sum: 0+26+43+60+77+94 = 300
- 300 & 1 = 0 → Even

## 🌿 Git Branch Strategy

```
main              ← Production-ready code
└── development   ← Integration testing
    └── feature1  ← Feature development
```

### Workflow

```bash
# Work on feature1
git checkout feature1
git add .
git commit -m "Add IPv6 EUI-64 generation"
git push origin feature1

# Merge to development
git checkout development
git merge feature1
git push origin development

# Merge to main (production)
git checkout main
git merge development
git push origin main
```

## 🗄️ MongoDB Schema

### Collection: `leases`

```javascript
{
  "mac_address": "00:1A:2B:3C:4D:5E",
  "dhcp_version": "DHCPv4",
  "assigned_ip": "192.168.1.10",
  "lease_time": "3600 seconds",
  "timestamp": "2025-11-09T15:30:45Z",
  "mac_sum_parity": "even"
}
```

### Useful MongoDB Commands

```bash
# Connect to MongoDB
mongosh --host 172.31.44.88 --port 27017

# Use database
use dhcp_leases

# View all leases
db.leases.find().pretty()

# Filter by DHCP version
db.leases.find({dhcp_version: "DHCPv4"}).pretty()
db.leases.find({dhcp_version: "DHCPv6"}).pretty()

# Search by MAC address
db.leases.find({mac_address: "00:1A:2B:3C:4D:5E"}).pretty()

# Count documents
db.leases.countDocuments()

# Clear collection
db.leases.deleteMany({})
```

## 📂 Project Structure

```
IST105-Assignment8/
│
├── assignment8/
│   ├── settings.py          # Django & MongoDB config
│   ├── urls.py
│   └── wsgi.py
│
├── network/
│   ├── templates/
│   │   └── network/
│   │       ├── base.html
│   │       ├── dhcp_request.html
│   │       └── view_leases.html
│   ├── forms.py             # DHCP request form
│   ├── utils.py             # Network logic & bitwise operations
│   ├── views.py             # View controllers
│   └── urls.py
│
├── manage.py
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

### Error: Connection refused (MongoDB)

```bash
# Check MongoDB service
sudo systemctl status mongod

# Check bindIp configuration
sudo cat /etc/mongod.conf | grep bindIp
# Should be: bindIp: 0.0.0.0

# Check listening port
sudo netstat -tulpn | grep 27017
# Should show: 0.0.0.0:27017

# Restart if needed
sudo systemctl restart mongod

# Check logs
sudo tail -50 /var/log/mongodb/mongod.log
```

### Error: Security Group Configuration

**Common Issues:**
- Port 27017 in MongoDB-SG must allow WebServer **private IP** (not public)
- Use `/32` suffix (e.g., `172.31.33.60/32`)
- Don't use `0.0.0.0/0` for MongoDB port (security risk)

**How to get Private IP:**
1. Go to EC2 Dashboard
2. Select WebServer-EC2 instance
3. Copy **Private IPv4 address** from details
4. Add `/32` at the end

### Error: No module named 'pymongo'

```bash
pip3 install pymongo --user
```

### Error: Django not accessible from browser

```bash
# Make sure to run on all interfaces
python3 manage.py runserver 0.0.0.0:8000

# Check Security Group allows port 8000
# Verify ALLOWED_HOSTS in settings.py
```

### Error: Invalid MAC address format

**Valid format:** `XX:XX:XX:XX:XX:XX`
- Exactly 6 octets
- Separated by colons `:`
- Hexadecimal values (0-9, A-F)

**Examples:**
- ✅ `00:1A:2B:3C:4D:5E`
- ✅ `AA:BB:CC:DD:EE:FF`
- ❌ `00-1A-2B-3C-4D-5E` (wrong separator)
- ❌ `001A2B3C4D5E` (missing colons)

## 📋 Test Cases

### Test 1: DHCPv4 Assignment

```
Input:
  MAC Address: 00:1A:2B:3C:4D:5E
  DHCP Version: DHCPv4

Expected Output:
  Assigned IP: 192.168.1.10
  Lease Time: 3600 seconds
  MAC Sum Parity: even
```

### Test 2: DHCPv6 with EUI-64

```
Input:
  MAC Address: AA:BB:CC:DD:EE:FF
  DHCP Version: DHCPv6

Expected Output:
  Assigned IP: 2001:db8::a8bb:ccff:fedd:eeff
  Lease Time: 3600 seconds
  MAC Sum Parity: odd
```

### Test 3: Lease Reassignment

```
Steps:
1. Request IP with MAC: 00:1A:2B:3C:4D:5E (DHCPv4)
2. Note the assigned IP (e.g., 192.168.1.10)
3. Request IP again with same MAC
4. Should receive the same IP if lease hasn't expired
```

## 📦 Dependencies

```txt
Django>=4.2.0
pymongo>=4.6.0
```

Create `requirements.txt`:

```bash
echo "Django>=4.2.0" > requirements.txt
echo "pymongo>=4.6.0" >> requirements.txt
```

## 📸 Required Screenshots

### 1. Application Running
- Access `http://[WEBSERVER-PUBLIC-IP]:8000`
- Submit a DHCP request
- Capture screenshot showing IP assignment

### 2. MongoDB Service Status
```bash
# On MongoDB-EC2
sudo systemctl status mongod
```

### 3. MongoDB Data
```bash
# On MongoDB-EC2
mongosh
use dhcp_leases
db.leases.find().pretty()
```

### 4. Security Groups
- AWS Console → EC2 → Security Groups
- Capture inbound rules for both `WebServer-SG` and `MongoDB-SG`

## 🔗 Important IP Addresses Reference

Replace these with your actual IPs:

| Component | Public IP | Private IP | Used For |
|-----------|-----------|------------|----------|
| MongoDB-EC2 | SSH connection | 172.31.44.88 | Django settings.py |
| WebServer-EC2 | Browser access | 172.31.33.60 | MongoDB Security Group |

## 📚 Key Concepts

### EUI-64 (Extended Unique Identifier)
- Method to generate IPv6 address from MAC address
- Inserts `FF:FE` in the middle of MAC address
- Toggles universal/local bit (7th bit of first octet)

### DHCP Lease Management
- IPv4: Assigns from pool 192.168.1.10-254
- IPv6: Generates using EUI-64 under 2001:db8::/64
- Lease time: 3600 seconds (1 hour)
- Same MAC gets same IP if lease is active

### Bitwise Operations
- **XOR (^)**: Toggle bits
- **AND (&)**: Check specific bits
- **OR (|)**: Set bits

## 👤 Author

**Josue Alvarez**  
Student No.: CT1011021  
Course: IST105 - Introduction to Programming

## 📄 License

Academic project for IST105 Assignment 8

---

**Last Updated:** November 2025