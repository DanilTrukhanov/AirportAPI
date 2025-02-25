## Disclaimer
Please note that this project may contain bugs and is not yet fully completed. It is a work in progress :)

# AirportAPI
API service for airport managment written on DRF, using PostgreSQL and Docker.

![img.png](scheme.png)

## Features

- **User Authentication**: 
  - Registration, login, and logout functionality for users with JWT Authentication.
  - Role-based access control (Admin, Authorized User, Unauthorized User).
  
- **PostgreSQL Integration**: 
  - Dockerized PostgreSQL database for persistent data storage.
  - Easy configuration through environment variables for secure database access.

- **Email Notification**: 
  - SMTP email integration for sending registration confirmation emails.

- **Permissions System**:
  - Unauthorized users can view flights, countries, routes and cities but cannot access orders or place an order.
  - Authorized users (non-admin) can place orders and view their own orders, but cannot access airplane-related information or employees.
  - Admin users have full access, including management of airplanes, employees, and all data, but they can't delete anything.
  
- **Dockerized Application**:
  - The entire application (including the database) is containerized using Docker for easy deployment.
  - Simplified setup and environment management using `docker-compose`.

## Setup
#### 1. Clone the project
```bash
git clone https://github.com/DanilTrukhanov/AirportAPI/tree/main
cd AirportAPI
```
#### 2. Configure Enviroment Variables
Copy the sample environment file and update it with your actual credentials:
```bash
cp .env.sample .env
```
#### 3. Build and start the Containers
```bash
docker-compose build
docker-compose up
```
#### 4. Access the Application
Go to http://localhost:8000/api/
#### 5. Getting access
- create user via /api/users/registration/
- get access token via /api/users/token/
