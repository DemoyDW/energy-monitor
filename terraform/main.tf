provider "aws" {
  region     = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
}

# # IAM role for Lambda execution
# data "aws_iam_policy_document" "assume_role" {
#   statement {
#     effect = "Allow"

#     principals {
#       type        = "Service"
#       identifiers = ["lambda.amazonaws.com"]
#     }

#     actions = ["sts:AssumeRole"]
#   }
# }

# resource "aws_iam_role" "c19-etl-lambda-role" {
#   name               = "c19-energy-etl-lambda-role"
#   assume_role_policy = data.aws_iam_policy_document.assume_role.json
# }

# # Lambda Function 
# resource "aws_lambda_function" "c19-energy-monitor-etl-lambda" {
#   function_name = "c19-energy-et-lambda"
#   role          = aws_iam_role.c19-etl-lambda-role.arn
#   package_type  = "Image"
#   image_uri     = "${aws_ecr_repository.example.repository_url}:latest"

#   environment {
#     variables = {
#       ACCESS_KEY = var.ACCESS_KEY,
#       SECRET_ACCESS_KEY = var.ACCESS_KEY,
#       REGION = var.REGION,
#       DB_PORT = var.DB_PORT,
#       DB_NAME = var.DB_NAME,
#       DB_USERNAME = var.DB_USERNAME,
#       DB_PASSWORD = var.DB_PASSWORD
#     }
#   }

#   memory_size = 512
#   timeout     = 30

#   architectures = ["arm64"] # Graviton support for better price/performance
# }

resource "aws_security_group" "c19-rds-sg" {
    name = "c19-energy-monitor-rds-sg"
    description = "Allows inbound traffic into the rds"
    vpc_id = var.VPC_ID
  
}

resource "aws_vpc_security_group_ingress_rule" "allow_all_traffic" {
    security_group_id = aws_security_group.c19-rds-sg.id
    cidr_ipv4         = "0.0.0.0/0"
    ip_protocol       = "tcp"
    from_port         = var.DB_PORT
    to_port           = var.DB_PORT
}

resource "aws_vpc_security_group_egress_rule" "allow_all_traffic_ipv4" {
  security_group_id = aws_security_group.c19-rds-sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp" 
  from_port         = var.DB_PORT
  to_port           = var.DB_PORT
}

resource "aws_db_subnet_group" "c19-subnet-groups" {
  name = "c19-energy-monitor-subnet-groups"
  subnet_ids = [var.VPC_PUBLIC_SUBNET_1, var.VPC_PUBLIC_SUBNET_2, var.VPC_PUBLIC_SUBNET_3]
}

resource "aws_db_instance" "c19-energy-monitor-rds" {
  allocated_storage    = 10
  identifier           = "c19-energy-monitor-rds"
  db_name              = var.DB_NAME
  engine               = "postgres"
  instance_class       = "db.t3.micro"
  username             = var.DB_USERNAME
  password             = var.DB_PASSWORD
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.c19-rds-sg.id]
  db_subnet_group_name = aws_db_subnet_group.c19-subnet-groups.name
  publicly_accessible = true
}

# DASHBOARD ECS TASK DEFINITION


resource "aws_ecr_repository" "c19-energy-monitor-readings" {
  name = "c19-energy-monitor-readings"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-energy-monitor-outages" {
  name = "c19-energy-monitor-outages"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-energy-monitor-summary" {
  name = "c19-energy-monitor-summary"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-energy-monitor-alert" {
  name = "c19-energy-monitor-alert"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_ecr_repository" "c19-energy-monitor-dashboard" {
  name = "c19-energy-monitor-dashboard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

