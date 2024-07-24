# **INCIT-EV-DSS**
Complete system for the Horizon 2020 INCITEV project, featuring a Decision Support System (DSS) backend with User Behaviour, Mobility, Charging Infrastructure, and Power Modules, along with a frontend user interface.

# **Project Structure**
The project is divided into two main parts: frontend and backend.

## **BACKEND**
The backend is structured into different folders and modules, each with a specific function. Here is an overview of the main folders and modules:

### **Main Folders**


* **Data-Model**: This folder contains the classes and data models used throughout the project. These classes define the data structure and are essential for database interaction and data management in the project.

* **Dss**: This module provides APIs through FastAPI and MongoDB. These APIs allow the frontend to make requests to retrieve, create, update, or delete data. FastAPI is used to create and manage the API routes, while MongoDB is the database used to store the data.

* **Integration**: This module is responsible for integrating various modules and managing simulations. It allows combining the functionalities of the **Ci**, **Power**, and **UBM** modules to run simulations and obtain comprehensive results.

### Modules

* **CI**: 

* **Power**:

* **UBM**: It allows the user to calculate Mobility and User Charging Behaviour by using very simple user inputs and a set of
dataset publicly available.

## **Frontend**
A brief description of the **FRONTEND.

# **Running the Project** 

## **Start the API Server using Docker**
To start the FastAPI server using Docker, follow these steps:

**1.** Make sure you have [**Docker Desktop**](https://www.docker.com/products/docker-desktop/) installed on your machine.

**2.** Navigate to the Docker setup directory:
```sh
    cd backend/dss/docker
```

**3.** Run the following command to start the containers::
```sh
    docker-compose up
```

This will build and start the Docker containers for the FastAPI server and MongoDB.

# **API Documentation**
The APIs provided by the dss module can be automatically documented using FastAPI. Once the server is started, the interactive API documentation is available at:
```arduino
   http://localhost:5000/docs
```

# **Contributing**
If you want to contribute to the project, please follow these steps:

**1.** Fork the repository.

**2.** Create a new branch for your changes:
```sh
   git checkout -b branch-name
```

**3.** Make your changes and commit them:
```sh
   git commit -m "Description of changes"
```

**4.** Push the branch to your fork:
```sh
   git push origin branch-name
```

**5.** Create a Pull Request describing the changes made.

# **License**
This project is licensed under the terms of the  [**LICENSE**](LICENSE) file.

# **Contact**
For any questions or suggestions, you can contact us at:
* lucio.inglese@linksfoundation.com