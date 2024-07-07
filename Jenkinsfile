pipeline {
    agent any

    environment {
        DOCKER_HUB_CREDENTIALS = credentials('DOCKER_CREDENTIALS') 
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/malekkammoun/Segmentation.git'
            }
        }

        stage('Build') {
            steps {
                script {
                    docker.build('my-flask-app:latest')
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    docker.image('my-flask-app:latest').inside {
                        sh 'pip install -r requirements.txt'
                        sh 'pytest'
                    }
                }
            }
        }

        stage('Push to DockerHub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'DOCKER_HUB_CREDENTIALS') {
                        docker.image('my-flask-app:latest').push('latest')
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
