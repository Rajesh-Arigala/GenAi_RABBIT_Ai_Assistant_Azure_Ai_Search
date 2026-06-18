# Retrieval Test Report
Generated at: 2026-06-17T21:11:46.409346+00:00

## Summary
- tests: 13
- modes_per_test: 1
- search_calls_expected: 13
- failures: 0
- categories: ['filter_test', 'sensitivity_test', 'specificity_test']

## sensitivity_test

### sensitivity_001_business_background
Question: Tell me about Rajesh's business background and leadership experience.

- hybrid: top pages: 01_Business_Skills, 00_Homepage, 00_Homepage
  first: 01_Business_Skills | Business Leadership — Rajesh Arigala | score=0.03279569745063782

### sensitivity_002_technical_capabilities
Question: What technical and cloud capabilities are shown in this portfolio?

- hybrid: top pages: 02_Tech_01_Technical_Skills, 02_Tech_01_Technical_Skills_04_GCP, 02_Tech_01_Technical_Skills_02_AWS
  first: 02_Tech_01_Technical_Skills | Technical Excellence | Rajesh Arigala | score=0.03333333507180214

### sensitivity_003_ai_platform_work
Question: What kind of AI platform engineering work has Rajesh built?

- hybrid: top pages: 00_Homepage, 00_Homepage, 00_Homepage
  first: 00_Homepage | Rajesh Arigala | AI & GenAI Systems · Business Integration! | score=0.03306011110544205

### sensitivity_004_deployment_work
Question: Which work is relevant to deploying machine learning systems into production?

- hybrid: top pages: 02_Tech_02_MLOps_03_MLOps_ML_Systems, 02_Tech_02_MLOps_03_MLOps_ML_Systems, 02_Tech_02_MLOps_02_Containers_02_Kubernetes_03_AWS_EKS_ML_Deployment
  first: 02_Tech_02_MLOps_03_MLOps_ML_Systems | MLOps & AI Systems Portfolio | ML Lifecycle Engineering | score=0.0313725508749485

### sensitivity_005_recruiter_summary
Question: Why is this profile relevant for AI engineer or MLOps engineer roles?

- hybrid: top pages: 00_Homepage, 00_Homepage, 02_Tech_02_MLOps_03_MLOps_ML_Systems
  first: 00_Homepage | Rajesh Arigala | AI & GenAI Systems · Business Integration! | score=0.03151364624500275

## specificity_test

### specificity_001_bpcl
Question: What experience does Rajesh have with BPCL?

- hybrid: top pages: 01_01_Business_Skill_BPCL, 01_01_Business_Skill_BPCL, 00_Homepage
  first: 01_01_Business_Skill_BPCL | BPCL — Mission-Critical Refinery Operations & Industrial Platform | score=0.03333333507180214

### specificity_002_kubernetes
Question: Which projects use Kubernetes?

- hybrid: top pages: 02_Tech_02_MLOps_02_Containers_02_Kubernetes_02_Multi_Pod_Flask_ML, 02_Tech_02_MLOps_02_Containers, 02_Tech_01_Technical_Skills_06_Kubernetes
  first: 02_Tech_02_MLOps_02_Containers_02_Kubernetes_02_Multi_Pod_Flask_ML | Kubernetes Project: Create Multiple Pods - EKS Deployment | score=0.03279569745063782

### specificity_003_azure_modules
Question: What are the Azure MLOps modules?

- hybrid: top pages: 03_02_03_AI_Project_Azure_Module_03, 03_02_03_AI_Project_Azure_Module_03, 02_Tech_02_MLOps_03_MLOps_ML_Systems
  first: 03_02_03_AI_Project_Azure_Module_03 | Azure ML Deployment Pipeline - Project Case Study | score=0.03128054738044739

### specificity_004_cicd
Question: Which pages discuss CI/CD pipelines?

- hybrid: top pages: 02_Tech_02_MLOps_01_CICD, 02_Tech_02_MLOps_01_CICD, 02_Tech_02_MLOps_01_CICD_Azure_DevOps_Pipeline
  first: 02_Tech_02_MLOps_01_CICD | CI/CD Automation & Platform Engineering | Multi-Cloud Portfolio | score=0.032258063554763794

### specificity_005_iac
Question: What infrastructure as code work is included?

- hybrid: top pages: 02_Tech_02_MLOps_04_IaC, 02_Tech_02_MLOps_04_IaC, 02_Tech_02_MLOps_04_IaC_02_Project_2
  first: 02_Tech_02_MLOps_04_IaC | Infrastructure as Code Portfolio | AWS CDK & Terraform | score=0.03253968432545662

## filter_test

### filter_001_business_section
Question: What business leadership examples are available?

- hybrid: top pages: 01_Business_Skills, 01_Business_Skills, 01_04_Business_Skill_R_Cafe
  first: 01_Business_Skills | Business Leadership — Rajesh Arigala | score=0.03333333507180214

### filter_002_ai_projects_section
Question: What AI platform projects are listed?

- hybrid: top pages: 03_04_AI_Project_GCP_Automation_Platform, 03_04_01_AI_Project_GCP_IaC_Details, 03_02_01_AI_Project_Azure_Module_01
  first: 03_04_AI_Project_GCP_Automation_Platform | AI GCP AUTOMATION PROJECT · End-to-End Enterprise AI Platform on GCP | score=0.03306011110544205

### filter_003_containers_section
Question: What container and orchestration projects are included?

- hybrid: top pages: 02_Tech_02_MLOps_02_Containers, 02_Tech_02_MLOps_02_Containers_01_Dockers, 02_Tech_02_MLOps_02_Containers_01_Dockers_03_Project_3
  first: 02_Tech_02_MLOps_02_Containers | Containers & Orchestration Portfolio | Docker & Kubernetes | score=0.03333333507180214
