/**
 * This pipeline will build and deploy a Docker image with Kaniko
 * https://github.com/GoogleContainerTools/kaniko
 * without needing a Docker host
 *
 * You need to create a jenkins-docker-cfg secret with your docker config
 * as described in
 * https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/#create-a-secret-in-the-cluster-that-holds-your-authorization-token
 *
 * ie.
 * kubectl create secret docker-registry regcred --docker-server=https://index.docker.io/v1/ --docker-username=csanchez --docker-password=mypassword --docker-email=john@doe.com
 */

pipeline {
  agent {
    kubernetes {
      //cloud 'kubernetes'
      defaultContainer 'kaniko'
      yaml '''
        kind: Pod
        spec:
          containers:
          - name: kaniko
            image: gcr.io/kaniko-project/executor:v1.7.0-debug
            imagePullPolicy: Always
            command:
            - sleep
            args:
            - 99d
            env:
            - name: PYPI_USER
              valueFrom:
                secretKeyRef:
                  name: jenkins-pypi-secret
                  key: username
            - name: PYPI_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: jenkins-pypi-secret
                  key: password
            volumeMounts:
              - name: jenkins-docker-cfg
                mountPath: /kaniko/.docker
          volumes:
          - name: jenkins-docker-cfg
            projected:
              sources:
              - secret:
                  name: regcred-push
                  items:
                    - key: .dockerconfigjson
                      path: config.json
'''
    }
  }
  environment {
    DOCKER_HUB_ACCOUNT = 'dockerpush.env.liquidvu.com'
    DOCKER_IMAGE_NAME = 'dilcher-common-fe'
  }
  stages {
    stage('Build with Kaniko') {
      steps {
        checkout scm
        sh "/kaniko/executor -f \"`pwd`/pypi.Dockerfile\" -c \"`pwd`\" --no-push --build-arg pypiuser=\"\${PYPI_USER}\" --build-arg pypipass=\"\${PYPI_PASSWORD}\""
      }
    }
  }
}
