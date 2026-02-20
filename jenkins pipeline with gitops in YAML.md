>>CI Pipeline YAML (Build → Docker → Push → Trigger CD)

pipeline:
  agent:
    label: jenkins-agent

  environment:
    APP_NAME: complete-prodcution-e2e-pipeline
    DOCKER_USER: dmancloud
    IMAGE: "${DOCKER_USER}/${APP_NAME}:${BUILD_NUMBER}"

  stages:

    - stage: Clean Workspace
      steps:
        - cleanWs

    - stage: Checkout Code
      steps:
        - git:
            url: https://github.com/sunnyygautam/complete-prodcution-e2e-pipeline
            branch: main
            credentialsId: github

    - stage: Build & Test
      steps:
        - sh: mvn clean package

    - stage: Build Docker Image
      steps:
        - sh: docker build -t ${IMAGE} .

    - stage: Push Docker Image
      steps:
        - withCredentials:
            - usernamePassword:
                credentialsId: dockerhub
                usernameVariable: USER
                passwordVariable: PASS
        - sh: docker login -u $USER -p $PASS
        - sh: docker push ${IMAGE}

    - stage: Trigger CD Pipeline
      steps:
        - sh: |
            curl -k -u admin:${JENKINS_API_TOKEN} \
            -X POST \
            -d IMAGE_TAG=${BUILD_NUMBER} \
            "https://jenkins.dev.dman.cloud/job/gitops-complete-pipeline/buildWithParameters?token=gitops-token"

  post:
    success:
      - echo: Pipeline executed successfully!
    failure:
      - echo: Pipeline failed!
	  
>>GitOps CD Pipeline YAML

pipeline:
  agent:
    label: Jenkins-Master

  environment:
    APP_NAME: complete-prodcution-e2e-pipeline
    IMAGE_TAG: "${BUILD_NUMBER}"

  stages:

    - stage: Clean Workspace
      steps:
        - cleanWs

    - stage: Checkout Repo
      steps:
        - git:
            url: https://github.com/sunnyygautam/gitops-complete-prodcution-e2e-pipeline
            branch: main
            credentialsId: github

    - stage: Update Deployment Tag
      steps:
        - sh: |
            sed -i 's#${APP_NAME}:.*#${APP_NAME}:${IMAGE_TAG}#g' deployment.yaml
            cat deployment.yaml

    - stage: Commit & Push Changes
      steps:
        - sh: |
            git config user.name "sunnyygautam"
            git config user.email "sunnykr910@gmail.com"
            git add deployment.yaml
            git commit -m "Update image tag to ${IMAGE_TAG}" || true
        - withCredentials:
            - gitUsernamePassword:
                credentialsId: github
                gitToolName: Default
        - sh: git push origin main
		
