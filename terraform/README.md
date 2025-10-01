# Terraform Set-up
This terraform script will set up all resources required for deploying the energy monitor Project.
To setup initial RDS run main.tf.
## Usage
1. Run main.tf with
bash
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