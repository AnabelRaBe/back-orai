library 'global-alm-pipeline-library'
pythonDevOpsPipeline (
    agent: "python",
    agentOptions: [
    'python': [
        'jnlp.resourceLimitMemory': '4000Mi',
        'jnlp.envVars': ['JAVA_OPTS': '-Xmx3536m']
      ]
    ],    
//    integrationBranch: 'development',
    fortify: [fortifyProperties:[
      "application": "python-orai-backorai",
      "version": "0.1.0",
      "bt": "none"] // Rest of values taken from setup.py
    ],
    pythonVersion: '3.10',
    sonar: [sonarInstanceName: 'SONAR_COMTECH', sonarProperties: [
            'sonar.python.version'             : '3.10',
            'sonar.projectKey'                 : 'sgt:sgt:orai:python-orai-backorai', 
            'sonar.sourceEncoding'             : 'UTF-8', 
            'sonar.sources'                    : 'backend',
            'sonar.tests'                      : 'test',
            'sonar.exclusions'                 : 'env/**/*, build/**/*'
    ]
    ] 
)



pipeline {
  agent none
  stages {
    stage ('zip') {
      agent any
      steps {
          sh 'printenv'	      
          sh 'curl -O https://nexusmaster.alm.europe.cloudcenter.corp/repository/pypi-internal/packages/python-orai-backorai/${VERSION}/${APPLICATION_NAME}-${VERSION}.tar.gz'
          sh 'ls -la'
          sh 'echo Descomprimimos artefacto Azure Function ${APPLICATION_NAME}-${VERSION}.tar.gz descargado de Nexus'
          sh 'tar -xf ${APPLICATION_NAME}-${VERSION}.tar.gz'
          sh 'ls -la ${APPLICATION_NAME}-${VERSION}'
	  //sh 'echo Instalamos dependencias'
	  //sh 'pip install -r requirements.txt --target ${APPLICATION_NAME}-${VERSION}/'
          sh 'echo Creamos carpeta de salida'
          sh 'mkdir -p output'
          sh 'echo Creamos ZIP ${APPLICATION_NAME}-${VERSION}.zip'
          sh 'cd ${APPLICATION_NAME}-${VERSION}/backend && zip -r ../../output/${APPLICATION_NAME}-${VERSION}.zip ./*'
	  //sh 'pip install -r requirements.txt'
          //sh 'zip -r output/${APPLICATION_NAME}-${VERSION}.zip .'
          stash name: "first-stash", includes: "output/*"
      }
    }

    stage ('Azure previo') {
      agent {
        label 'azure'
      }
      environment {
          AZURE_SPN3          = credentials('AZURE_SPN3')
          AZURE_PWD           = credentials('AZURE_PWD')
          STORAGE_ACCOUNT     = "innd1weustaportalcrit002"
          CONTAINER_RELEASES  = "releases"
          CONTAINER_CONFIG    = "config"
          FUNCTION_APP        = "innd1weuafaportalcrit001"
          RESOURCE_GROUP      = "innd1weursgportalcrit001"
          STORAGE_ACCOUNT_KEY = credentials('STORAGE_ACCOUNT_KEY') 
      }
      steps {
        container ('azure') {
          unstash 'first-stash'
          sh 'az --version'
          // sh 'az upgrade'
          // sh 'az --version'
          sh 'printenv'
          sh 'echo Artefacto Nexus ubicado en ${ARTIFACT_NEXUS_URL}'
          sh 'az --version'
          sh 'echo Login Azure con SPN3'
          sh 'az login --service-principal -u ${AZURE_SPN3} -p ${AZURE_PWD} --tenant "35595a02-4d6d-44ac-99e1-f9ab4cd872db"'
          sh 'echo Subimos configuración al contenedor ${CONTAINER_CONFIG} de ${STORAGE_ACCOUNT}'
          sh 'az storage blob upload --account-name ${STORAGE_ACCOUNT} --container-name ${CONTAINER_CONFIG} --name active.json --file config/active.json --account-key ${STORAGE_ACCOUNT_KEY} --auth-mode key' 
          sh 'echo Subimos zip al contenedor ${CONTAINER_RELEASES} de ${STORAGE_ACCOUNT}'
          sh 'az storage blob upload --account-name ${STORAGE_ACCOUNT} --container-name ${CONTAINER_RELEASES} --name ${APPLICATION_NAME}-${VERSION}.zip --file output/${APPLICATION_NAME}-${VERSION}.zip --account-key ${STORAGE_ACCOUNT_KEY} --auth-mode key' 
          sh 'echo Desplegamos app'
          sh 'az functionapp deployment source config-zip --resource-group ${RESOURCE_GROUP} --name ${FUNCTION_APP} --src output/${APPLICATION_NAME}-${VERSION}.zip --build-remote=true'
          sh 'az functionapp restart --resource-group ${RESOURCE_GROUP} --name ${FUNCTION_APP}'
// LOS SIGUIENTES COMANDOS REQUIEREN TENER UNA VERSIÓN MÁS ACTUAL DE AZ CLI (webapp / functionapp deploy no es compatible con la versión 2.4.0 que tenemos
//          withEnv([
//              "START=${sh(script:"date +'%Y-%m-%dT%H:%M:%SZ'", returnStdout: true).trim()}", 
//              "END=${sh(script:"date --date='1 hour' +'%Y-%m-%dT%H:%M:%SZ'", returnStdout: true).trim()}"
//          ]) {
//            sh 'echo $START'
//            sh 'echo $END'
//            sh 'RELEASE_SAS=$(az storage blob generate-sas --full-uri --account-name ${STORAGE_ACCOUNT} --account-key ${STORAGE_ACCOUNT_KEY} --container-name ${CONTAINER} --name ${APPLICATION_NAME}-${VERSION}.zip --https-only --permissions r --start $START --expiry $END)'
//            sh 'echo $RELEASE_SAS'
//            sh 'az functionapp deploy --resource-group ${RESOURCE_GROUP} --name ${FUNCTION_APP} --src-url $RELEASE_SAS --type zip'
//          }
        }
      }
    }
  }
}
