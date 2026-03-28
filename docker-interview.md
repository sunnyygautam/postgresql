Docker:

What is the difference between args and env?
--args: temporary variable like if we want to pass version number on boot up. it wont use later.
--env: use for passing variable 

What is the difference between run and cmd?
--run: if we want to run any command like install npm package.
--cmd: if we want to pass multiple argument.

What is multistage docker file?
--Multistage file is the way to organise the dockerfile. First step is Installation all the required package, creating the jarfile, creating something else.

What are best practices during docker compose file?
--A Docker Compose file is a YAML file used to define and configure multi-container Docker applications.

What is the difference between CMD & Entrypoint?
--Entrypoint--if we want to run it everytime on boot up.
--CMD : if we want to pass the multiple argument
 
What is the difference between ADD and COPY command in Docker?
--add: if we want to fetch outside of the server, unzip, compress 
--copy: it does the local copy of the file.

Why container is called light weight?

What is Docker networking and its types?
--Bridge network
--Host network
--Overlay network
--macvlan network

What’s the use of multistage Docker file and write one multistage Docker file?
# -------- Stage 1: Build --------
FROM maven:3.9.4-eclipse-temurin-17 AS builder

# Set working directory inside the container
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline

# Copy the full source code
COPY src ./src

# Build the Java application (creates a JAR file)
RUN mvn clean package -DskipTests

# -------- Stage 2: Runtime --------
FROM eclipse-temurin:17-jre

# Set working directory
WORKDIR /app

# Copy the compiled JAR from the builder stage
COPY --from=builder /app/target/*.jar app.jar

# Set the JAR as the entry point
ENTRYPOINT ["java", "-jar", "app.jar"]


Does the docker container have the same ip as host in host network?

Write docker run command and mount the existing volume /var/log with the read permission.
--docker run --rm -it -v /var/log:/var/log:ro your-image-name
