# Terraform Set-up
This terraform script will set up all resources required for deploying the energy monitor Project.
 
## Usage
1. To setup initial RDS and ECRs, Terraform apply the main.tf and ecr.tf files (or create the ecr with matching details using the AWS UI). 
2. Populate the database by following the instructions in the database folder.
3. Upload the container images of the power/carbon ETL, outage ETL/email, newsletter, and dashboard. 
4. Finally, Terraform Apply and the remaining infrastructure will be created. 
# Inside terraform folder
terraform apply
## Requirements
1. A terraform.tfvars as follows
ACCESS_KEY={your_aws_key}
SECRET_KEY={your_aws_secret_key}
REGION={region}
DB_PORT={db_port}
DB_NAME={db_name}
DB_USERNAME={username}
DB_PASSWORD={password}
VPC_ID={vpc_id}
VPC_PUBLIC_SUBNET_1={public_subnet_1}
VPC_PUBLIC_SUBNET_2={public_subnet_2}
VPC_PUBLIC_SUBNET_3={public_subnet_3}