# Website Link Inventory And Validation

Generated at: 2026-06-20T02:31:43.339564+00:00

## Purpose

This document records the extracted RajeshArigala.com webpage links used by RABBIT Assistant. It is the future reference point for source URLs, page IDs, link validation, and Azure AI Search metadata.

## Current Counts

| Item | Count |
|---|---:|
| Hierarchy URL records | 54 |
| Unique extracted website URLs | 54 |
| Canonical RAG document URLs | 53 |
| Approved chunk URL metadata records | 142 |
| Live link check result | 54 checked, 54 OK, 0 true 404 after normalization |

## Storage Pattern

- `hierarchy_registry.json` stores page slots, hierarchy, expected URLs, and placeholder status.
- `document_registry.json` stores canonical document URLs for the 53 RAG-ready pages.
- `approved_chunks_v1.jsonl` repeats `source_url` as retrievable metadata on each approved chunk.
- Azure AI Search stores `source_url` as metadata/retrievable field with each indexed chunk.
- Embeddings are generated from page/chunk text, not from the URL string itself.

## Link Safety Rule

RABBIT User Mode must render links only from validated source metadata. The LLM must not invent, rewrite, shorten, or place Markdown links inside answer prose. Public links are rendered separately by the UI.

## Normalization Notes

Some original site routes contain spaces, such as `buiss skills` and `tech skills`. The app now percent-encodes those paths for browser-safe links, for example `buiss%20skills`. One `.html` route redirects to its extensionless route and still returns HTTP 200.

## Extracted Webpage Links

| Page ID | Depth | Section | Canonical Doc | Title | Browser-Safe URL | Raw URL |
|---|---:|---|---|---|---|---|
| `00_Homepage` | 0 | `00_Homepage` | yes | Rajesh Arigala - AI & GenAI Systems · Business Integration! | https://rajesharigala.com/ | https://rajesharigala.com/ |
| `01_Business_Skills` | 1 | `01_Business_Skills` | yes | Business Leadership — Rajesh Arigala | https://rajesharigala.com/buiss%20skills/buissness | https://rajesharigala.com/buiss skills/buissness |
| `02_Tech_01_Technical_Skills` | 1 | `02_Tech_01_Technical_Skills` | yes | Technical Excellence - Rajesh Arigala | https://rajesharigala.com/tech%20skills/skill | https://rajesharigala.com/tech skills/skill |
| `01_01_Business_Skill_BPCL` | 2 | `01_Business_Skills` | yes | BPCL — Mission-Critical Refinery Operations & Industrial Platform | https://rajesharigala.com/buiss%20skills/bpcl | https://rajesharigala.com/buiss skills/bpcl |
| `01_02_Business_Skill_Medtronic` | 2 | `01_Business_Skills` | yes | Medtronic India — Territory Business Leadership | https://rajesharigala.com/buiss%20skills/medtronic | https://rajesharigala.com/buiss skills/medtronic |
| `01_03_Business_Skill_SMAAT` | 2 | `01_Business_Skills` | yes | SMAAT India — Distributed Water Infrastructure Platform | https://rajesharigala.com/buiss%20skills/smaat | https://rajesharigala.com/buiss skills/smaat |
| `01_04_Business_Skill_R_Cafe` | 2 | `01_Business_Skills` | yes | R-Cafe by Red Rybbons — Built from Ground Zero | https://rajesharigala.com/buiss%20skills/r-cafe | https://rajesharigala.com/buiss skills/r-cafe |
| `01_05_Business_Skill_RedRybbons` | 2 | `01_Business_Skills` | yes | RedRybbons — Craft Innovation Platform | https://rajesharigala.com/buiss%20skills/redrybbons | https://rajesharigala.com/buiss skills/redrybbons |
| `01_06_Business_Skill_Law` | 2 | `01_Business_Skills` | yes | Supreme Court Advocacy — Constitutional Governance & AI Systems | https://rajesharigala.com/buiss%20skills/law | https://rajesharigala.com/buiss skills/law |
| `02_Tech_01_Technical_Skills_01_GitHub` | 2 | `02_Tech_01_Technical_Skills` | yes | GitHub & GitHub Actions - Rajesh Arigala | https://rajesharigala.com/tech%20skills/github | https://rajesharigala.com/tech skills/github |
| `02_Tech_01_Technical_Skills_02_AWS` | 2 | `02_Tech_01_Technical_Skills` | yes | AWS DevOps & Cloud - Rajesh Arigala | https://rajesharigala.com/tech%20skills/aws | https://rajesharigala.com/tech skills/aws |
| `02_Tech_01_Technical_Skills_03_Azure` | 2 | `02_Tech_01_Technical_Skills` | yes | Azure DevOps & Cloud - Rajesh Arigala | https://rajesharigala.com/tech%20skills/azure | https://rajesharigala.com/tech skills/azure |
| `02_Tech_01_Technical_Skills_04_GCP` | 2 | `02_Tech_01_Technical_Skills` | yes | Google Cloud DevOps - Rajesh Arigala | https://rajesharigala.com/tech%20skills/gcd | https://rajesharigala.com/tech skills/gcd |
| `02_Tech_01_Technical_Skills_05_Docker` | 2 | `02_Tech_01_Technical_Skills` | yes | Docker & Containerization - Rajesh Arigala | https://rajesharigala.com/tech%20skills/docker | https://rajesharigala.com/tech skills/docker |
| `02_Tech_01_Technical_Skills_06_Kubernetes` | 2 | `02_Tech_01_Technical_Skills` | yes | Kubernetes Container Orchestration - Rajesh Arigala | https://rajesharigala.com/tech%20skills/kubernetes | https://rajesharigala.com/tech skills/kubernetes |
| `02_Tech_01_Technical_Skills_07_MLflow` | 2 | `02_Tech_01_Technical_Skills` | yes | MLFlow ML Lifecycle Management - Rajesh Arigala | https://rajesharigala.com/tech%20skills/mlflow | https://rajesharigala.com/tech skills/mlflow |
| `02_Tech_02_MLOps` | 2 | `02_Tech_02_MLOps` | placeholder/no canonical doc yet | MLOps | https://rajesharigala.com/mlops/ml-ops | https://rajesharigala.com/mlops/ml-ops |
| `02_Tech_02_MLOps_01_CICD` | 2 | `02_Tech_02_MLOps_01_CICD` | yes | CI/CD Automation & Platform Engineering - Multi-Cloud Portfolio | https://rajesharigala.com/mlops/cicd | https://rajesharigala.com/mlops/cicd |
| `02_Tech_02_MLOps_02_Containers` | 2 | `02_Tech_02_MLOps_02_Containers` | yes | Containers & Orchestration Portfolio - Docker & Kubernetes | https://rajesharigala.com/mlops/ContainersOrchestration | https://rajesharigala.com/mlops/ContainersOrchestration |
| `02_Tech_02_MLOps_03_MLOps_ML_Systems` | 2 | `02_Tech_02_MLOps_03_MLOps_ML_Systems` | yes | MLOps & AI Systems Portfolio - ML Lifecycle Engineering | https://rajesharigala.com/mlops/mlops%2Csys | https://rajesharigala.com/mlops/mlops,sys |
| `02_Tech_02_MLOps_04_IaC` | 2 | `02_Tech_02_MLOps_04_IaC` | yes | Infrastructure as Code Portfolio - AWS CDK & Terraform | https://rajesharigala.com/mlops/infra-code | https://rajesharigala.com/mlops/infra-code |
| `03_01_AI_Project_MLflow_AWS_Platform` | 2 | `03_AI_Projects` | yes | MLflow ML Platform on AWS - Project Case Study | https://rajesharigala.com/mlops/ai1 | https://rajesharigala.com/mlops/ai1 |
| `03_02_AI_Project_Azure_MLOps_Platform` | 2 | `03_AI_Projects` | yes | Enterprise AI Platform on Azure - End-to-End Azure MLOps Pipelines | https://rajesharigala.com/ai-work/azure-mlops-platform | https://rajesharigala.com/ai-work/azure-mlops-platform |
| `03_03_AI_Project_AWS_SageMaker_MLOps_Platform` | 2 | `03_AI_Projects` | yes | Enterprise AI Platform on AWS · SageMaker MLOps Pipelines | https://rajesharigala.com/ai-work/ai-work3 | https://rajesharigala.com/ai-work/ai-work3 |
| `03_04_AI_Project_GCP_Automation_Platform` | 2 | `03_AI_Projects` | yes | AI GCP AUTOMATION PROJECT · End-to-End Enterprise AI Platform on GCP | https://rajesharigala.com/ai-work/ai-work4 | https://rajesharigala.com/ai-work/ai-work4 |
| `03_05_AI_Project_Kubeflow_MLOps_Platform` | 2 | `03_AI_Projects` | yes | Enterprise Kubeflow MLOps Platform - Open‑Source Kubernetes AI | https://rajesharigala.com/ai-work/ai-work5 | https://rajesharigala.com/ai-work/ai-work5 |
| `02_Tech_02_MLOps_01_CICD_AWS_CDK_IaC_Platform` | 3 | `02_Tech_02_MLOps_01_CICD` | yes | AWS CDK - Infrastructure as Code CI/CD Platform | https://rajesharigala.com/mlops/CI-CD/cicd-project5 | https://rajesharigala.com/mlops/CI-CD/cicd-project5 |
| `02_Tech_02_MLOps_01_CICD_AWS_DevOps_Pipeline` | 3 | `02_Tech_02_MLOps_01_CICD` | yes | AWS DevOps CI/CD Pipeline - Project Case Study | https://rajesharigala.com/mlops/CI-CD/aws-cicd-pipeline-devops | https://rajesharigala.com/mlops/CI-CD/aws-cicd-pipeline-devops |
| `02_Tech_02_MLOps_01_CICD_Azure_DevOps_Pipeline` | 3 | `02_Tech_02_MLOps_01_CICD` | yes | Azure DevOps CI/CD Pipeline as Code - Case Study | https://rajesharigala.com/mlops/CI-CD/azure-devops-ci-cd-pipeline-yaml | https://rajesharigala.com/mlops/CI-CD/azure-devops-ci-cd-pipeline-yaml |
| `02_Tech_02_MLOps_01_CICD_GCP_Cloud_Build_Pipeline` | 3 | `02_Tech_02_MLOps_01_CICD` | yes | Google Cloud Build CI/CD Pipeline - Project Case Study | https://rajesharigala.com/mlops/CI-CD/gcp-cloud-build-ci-cd-pipeline-yaml | https://rajesharigala.com/mlops/CI-CD/gcp-cloud-build-ci-cd-pipeline-yaml |
| `02_Tech_02_MLOps_01_CICD_GitHub_Actions_Pipeline` | 3 | `02_Tech_02_MLOps_01_CICD` | yes | GitHub Actions CI/CD Pipeline - Project Case Study | https://rajesharigala.com/mlops/CI-CD/github-actions-ci-cd-pipeline-yaml | https://rajesharigala.com/mlops/CI-CD/github-actions-ci-cd-pipeline-yaml |
| `02_Tech_02_MLOps_02_Containers_01_Dockers` | 3 | `02_Tech_02_MLOps_02_Containers` | yes | Docker Fundamentals & Projects Portfolio | https://rajesharigala.com/mlops/docker | https://rajesharigala.com/mlops/docker |
| `02_Tech_02_MLOps_02_Containers_02_Kubernetes` | 3 | `02_Tech_02_MLOps_02_Containers` | yes | Kubernetes Infrastructure & AWS EKS - Rajesh Arigala | https://rajesharigala.com/mlops/kubernetes | https://rajesharigala.com/mlops/kubernetes |
| `02_Tech_02_MLOps_03_MLOps_ML_Systems_MLflow_AWS_Project` | 3 | `02_Tech_02_MLOps_03_MLOps_ML_Systems` | yes | MLflow on AWS - CDK IaC + SageMaker Project Case Study | https://rajesharigala.com/mlops/ml-project4 | https://rajesharigala.com/mlops/ml-project4 |
| `02_Tech_02_MLOps_04_IaC_01_Project_1` | 3 | `02_Tech_02_MLOps_04_IaC` | yes | MLflow Platform Deployment on AWS ECS Fargate - Project Case Study | https://rajesharigala.com/mlops/infra%20project1 | https://rajesharigala.com/mlops/infra project1 |
| `02_Tech_02_MLOps_04_IaC_02_Project_2` | 3 | `02_Tech_02_MLOps_04_IaC` | yes | AWS CDK - Infrastructure as Code CI/CD Platform | https://rajesharigala.com/mlops/infra%20project2 | https://rajesharigala.com/mlops/infra project2 |
| `03_02_01_AI_Project_Azure_Module_01` | 3 | `03_AI_Projects` | yes | Azure ML Platform IaC - Project Case Study | https://rajesharigala.com/mlops/ai2/ai2.1 | https://rajesharigala.com/mlops/ai2/ai2.1 |
| `03_02_02_AI_Project_Azure_Module_02` | 3 | `03_AI_Projects` | yes | Azure ML Training Pipeline - Project Case Study | https://rajesharigala.com/mlops/ai2/ai2.2 | https://rajesharigala.com/mlops/ai2/ai2.2 |
| `03_02_03_AI_Project_Azure_Module_03` | 3 | `03_AI_Projects` | yes | Azure ML Deployment Pipeline - Project Case Study | https://rajesharigala.com/mlops/ai2/ai2.3 | https://rajesharigala.com/mlops/ai2/ai2.3 |
| `03_03_01_AI_Project_AWS_IaC_Details` | 3 | `03_AI_Projects` | yes | AWS AI Platform · IaC Pipeline (CDK + SageMaker) | https://rajesharigala.com/mlops/ai6/ai6.1 | https://rajesharigala.com/mlops/ai6/ai6.1 |
| `03_03_02_AI_Project_AWS_Training_Pipeline` | 3 | `03_AI_Projects` | yes | AWS SageMaker MLOps · Pipeline 2 (Train/Evaluate/Register) | https://rajesharigala.com/mlops/ai6/ai6.2 | https://rajesharigala.com/mlops/ai6/ai6.2 |
| `03_03_03_AI_Project_AWS_Deployment_Details` | 3 | `03_AI_Projects` | yes | AWS AI Deployment Pipeline · CDK · MLOps | https://rajesharigala.com/mlops/ai6/ai6.3 | https://rajesharigala.com/mlops/ai6/ai6.3 |
| `03_04_01_AI_Project_GCP_IaC_Details` | 3 | `03_AI_Projects` | yes | AI‑GCP Pipeline‑1 : Agent Platform Platform Foundation · Case Study | https://rajesharigala.com/mlops/ai4/ai4.1 | https://rajesharigala.com/mlops/ai4/ai4.1 |
| `03_04_02_AI_Project_GCP_Training_Pipeline` | 3 | `03_AI_Projects` | yes | AI‑GCP Pipeline‑2 · Agent Platform MLOps | https://rajesharigala.com/mlops/ai4/ai4.2 | https://rajesharigala.com/mlops/ai4/ai4.2 |
| `03_04_03_AI_Project_GCP_Deployment_Details` | 3 | `03_AI_Projects` | yes | AI‑GCP Pipeline‑3 : Agent Platform Deployment & Endpoints · Case Study | https://rajesharigala.com/mlops/ai4/ai4.3 | https://rajesharigala.com/mlops/ai4/ai4.3 |
| `03_05_01_AI_Project_Kubeflow_IaC_Details` | 3 | `03_AI_Projects` | yes | Kubeflow AI Platform · MLOps Foundation | https://rajesharigala.com/mlops/ai5/ai5.1 | https://rajesharigala.com/mlops/ai5/ai5.1 |
| `03_05_02_AI_Project_Kubeflow_Training_Pipeline` | 3 | `03_AI_Projects` | yes | Kubeflow ML Pipeline · MLOps case study | https://rajesharigala.com/mlops/ai5/ai5.2 | https://rajesharigala.com/mlops/ai5/ai5.2 |
| `03_05_03_AI_Project_Kubeflow_Deployment_Details` | 3 | `03_AI_Projects` | yes | AI‑Kubeflow Pipeline‑3 : Model Deployment & Serving (K8s Native) · Case Study | https://rajesharigala.com/mlops/ai5/ai5.3 | https://rajesharigala.com/mlops/ai5/ai5.3 |
| `02_Tech_02_MLOps_02_Containers_01_Dockers_01_NodeJS_App` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | Dockerized Node.js Application - Container Execution Layer | https://rajesharigala.com/mlops/Dockerized-Node.js-App | https://rajesharigala.com/mlops/Dockerized-Node.js-App |
| `02_Tech_02_MLOps_02_Containers_01_Dockers_02_Project_2` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | Dockerized ML Inference Service - Project Case Study | https://rajesharigala.com/mlops/docker-project2 | https://rajesharigala.com/mlops/docker-project2 |
| `02_Tech_02_MLOps_02_Containers_01_Dockers_03_Project_3` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | Docker Compose MLOps - Multi-Container ML Application | https://rajesharigala.com/mlops/docker-project3 | https://rajesharigala.com/mlops/docker-project3 |
| `02_Tech_02_MLOps_02_Containers_02_Kubernetes_01_ML_Inference_Minikube` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | Kubernetes ML Inference Deployment - Project Case Study | https://rajesharigala.com/mlops/kubernetes-ml-inference-minikube.html | https://rajesharigala.com/mlops/kubernetes-ml-inference-minikube.html |
| `02_Tech_02_MLOps_02_Containers_02_Kubernetes_02_Multi_Pod_Flask_ML` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | Kubernetes Project: Create Multiple Pods - EKS Deployment | https://rajesharigala.com/mlops/kubernetes-multi-pod-flask-ml | https://rajesharigala.com/mlops/kubernetes-multi-pod-flask-ml |
| `02_Tech_02_MLOps_02_Containers_02_Kubernetes_03_AWS_EKS_ML_Deployment` | 4 | `02_Tech_02_MLOps_02_Containers` | yes | AWS EKS ML Model Deployment - Project Case Study | https://rajesharigala.com/mlops/aws-eks-ml-deployment | https://rajesharigala.com/mlops/aws-eks-ml-deployment |
