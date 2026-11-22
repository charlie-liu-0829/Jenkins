pipeline {
    agent any

    environment {
        DB_HOST = '127.0.0.1'
        DB_PORT = '3306'
        DB_USER = 'root'
        DB_PASSWORD = 'Lym030829'
        DB_NAME = 'ecommerce_demo'
    }

    stages {
        stage('运行自动化测试') {
            steps {
                sh '''
                    set -eu

                    export JAVA_HOME="/opt/homebrew/opt/openjdk@21"
                    export PATH="/Users/charlieliu/miniforge3/envs/pytest/bin:$JAVA_HOME/bin:/opt/homebrew/bin:/usr/bin:/bin"

                    mkdir -p report
                    rm -f report/junit.xml

                    python --version
                    python -m pip install -r requirements.txt
                    python main.py --no-report --junitxml=report/junit.xml
                '''
            }
        }
    }

    post {
        always {
            script {
                if (fileExists('report/junit.xml')) {
                    junit testResults: 'report/junit.xml'
                }
            }

            allure(
                commandline: 'allure',
                includeProperties: false,
                jdk: '',
                report: 'report/html_report',
                results: [[path: 'report/json_report']]
            )

            emailext(
                mimeType: 'text/html',
                subject: "${env.JOB_NAME} #${env.BUILD_NUMBER}：${currentBuild.currentResult}",
                to: '18600988847@163.com',
                body: """
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.8;">
                        <h2>自动化测试构建通知</h2>
                        <p>任务名称：${env.JOB_NAME}</p>
                        <p>构建编号：#${env.BUILD_NUMBER}</p>
                        <p>构建状态：${currentBuild.currentResult}</p>
                        <p>
                            <a href="${env.BUILD_URL}allure/">
                                查看本次 Allure 测试报告
                            </a>
                        </p>
                        <p>
                            <a href="${env.BUILD_URL}testReport/">
                                查看 JUnit 测试统计
                            </a>
                        </p>
                        <p>
                            <a href="${env.BUILD_URL}">
                                查看构建详情
                            </a>
                        </p>
                    </body>
                    </html>
                """
            )
        }
    }
}