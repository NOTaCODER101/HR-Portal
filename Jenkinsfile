pipeline {
    agent any

    stages {

        stage('Checkout'){
            steps{
                checkout scm
            }
        }

        stage('Build Docker Image'){
            steps{
                sh 'docker build -t branyr/flask-app:latest .'
            }
        }

        stage('Test inside Container'){
            steps {
                sh 'docker run --rm branyr/flask-app:latest pytest'
            }
        }

        stage('Push to Docker Hub') {
            steps{
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]){
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push branyr/flask-app:latest
                    '''
                }
            }
        }

    }

}