provider "aws" {
  region     = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
}

# IAM role for Lambda execution

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "c19-etl-lambda-role" {
  name               = "c19-energy-etl-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

# Lambda Function 

resource "aws_lambda_function" "c19-energy-generation-etl-lambda" {
  function_name = "c19-energy-generation-etl-lambda"
  role          = aws_iam_role.c19-etl-lambda-role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.c19-energy-monitor-readings.repository_url}:latest"

  environment {
    variables = {
      ACCESS_KEY = var.ACCESS_KEY,
      SECRET_ACCESS_KEY = var.ACCESS_KEY,
      REGION = var.REGION,
      DB_HOST = var.DB_HOST,
      DB_PORT = var.DB_PORT,
      DB_NAME = var.DB_NAME,
      DB_USERNAME = var.DB_USERNAME,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  memory_size = 512
  timeout     = 30

}

resource "aws_lambda_function" "c19-energy-outage-etl-lambda" {
  function_name = "c19-energy-outage-etl-lambda"
  role          = aws_iam_role.c19-etl-lambda-role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.c19-energy-monitor-outages.repository_url}:latest"
  
  environment {
    variables = {
      ACCESS_KEY = var.ACCESS_KEY,
      SECRET_ACCESS_KEY = var.ACCESS_KEY,
      REGION = var.REGION,
      DB_HOST = var.DB_HOST,
      DB_PORT = var.DB_PORT,
      DB_NAME = var.DB_NAME,
      DB_USERNAME = var.DB_USERNAME,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  memory_size = 512
  timeout     = 30

}




resource "aws_lambda_function" "c19-energy-summary-email-lambda" {
  function_name = "c19-energy-summary-etl-lambda"
  role          = aws_iam_role.c19-etl-lambda-role.arn
  package_type  = "Image"
  image_uri     = "${aws_ecr_repository.c19-energy-monitor-summary.repository_url}:latest"

  environment {
    variables = {
      ACCESS_KEY = var.ACCESS_KEY,
      SECRET_ACCESS_KEY = var.ACCESS_KEY,
      REGION = var.REGION,
      DB_HOST = var.DB_HOST,
      DB_PORT = var.DB_PORT,
      DB_NAME = var.DB_NAME,
      DB_USERNAME = var.DB_USERNAME,
      DB_PASSWORD = var.DB_PASSWORD
    }
  }

  memory_size = 512
  timeout     = 30

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

# IAM ROLE FOR TASK EXECUTION

resource "aws_iam_role" "c19-energy-task-execution-role" {
  name = "c19-energy-task-execution-role"
  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ecs-tasks.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
})
}

# DASHBOARD ECS TASK DEFINITION
resource "aws_ecs_task_definition" "c19-energy-monitor-dashboard" {
  family = "c19-energy-monitor-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu = "1024"
  memory = "3072"
  execution_role_arn = aws_iam_role.c19-energy-task-execution-role.arn
  container_definitions = jsonencode([
    {
        name = "c19-energy-monitor-dashboard"
        image = "${aws_ecr_repository.c19-energy-monitor-dashboard.repository_url}:latest"
        memory = 128
        essential = true,
        portMappings = [
          {
            containerPort = 8501
            hostPort      = 8501
            protocol      = "tcp"
          }
        ],
        logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c19-energy-monitor-dashboard"
                    awslogs-stream-prefix = "ecs"
                    awslogs-create-group = "true"
                    awslogs-region = "eu-west-2"
                }
            }
        environment = [
            {name = "DB_NAME", value = var.DB_NAME},
            {name = "DB_USERNAME", value = var.DB_USERNAME},
            {name = "DB_PASSWORD", value = var.DB_PASSWORD},
            {name = "DB_HOST", value = var.DB_HOST},
            {name = "DB_PORT", value = var.DB_PORT},
            {name = "AWS_ACCESS_KEY", value = var.ACCESS_KEY},
            {name = "AWS_SECRET_KEY", value = var.SECRET_KEY},
            {name = "AWS_REGION", value = var.REGION}
        ]
    }
  ])
  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
}

resource "aws_iam_role" "c19_energy_ecs_service_role" {
  name = "c19_energy_ecs_service_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
    }]
  })
}

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

resource "aws_ecr_repository" "c19-energy-monitor-dashboard" {
  name = "c19-energy-monitor-dashboard"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}



# eventbridge iam role for schedulers
resource "aws_iam_role" "c19-energy-monitor-scheduler-role" {
  name = "c19-energy-monitor-scheduler-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = ["scheduler.amazonaws.com"]
        }
      }
    ]
  })
}

# eventbridge iam policy for schedulers
resource "aws_iam_role_policy_attachment" "c19-energy-monitor-scheduler-role-attach" {
  role       = aws_iam_role.c19-energy-monitor-scheduler-role.name
  policy_arn = aws_iam_policy.c19-energy-monitor-scheduler-policy.arn
}

resource "aws_iam_policy" "c19-energy-monitor-scheduler-policy" {
  name = "c19-Scheduler-Lambda-Policy"
  
    policy = jsonencode({
        Version = "2012-10-17"
        Statement= [
            {
                "Action": [
                    "lambda:InvokeFunction"
                ],
                Effect = "Allow"
                Resource=[
                  aws_lambda_function.c19-energy-generation-etl-lambda.arn,
                  aws_lambda_function.c19-energy-outage-etl-lambda.arn
                  ]
            },
        ]
    })
}

# eventbridge scheduler for carbon/power reading ETL
resource "aws_scheduler_schedule" "c19-energy-monitor-reading-etl-scheduler" {
  name        = "c19-energy-monitor-reading-ETL-scheduler"
  description = "Run reading ETL job every 30 minutes at 5 past the hour."

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(5/30 * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = aws_lambda_function.c19-energy-generation-etl-lambda.arn
    role_arn = aws_iam_role.c19-energy-monitor-scheduler-role.arn
  }
}




# eventbridge scheduler for outage ETL (will be step function assigned, not Lambda)
resource "aws_scheduler_schedule" "c19-energy-monitor-outage-step-scheduler" {
  name        = "c19-energy-monitor-outage-ETL-scheduler"
  description = "Run outage ETL job every 5."

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(*/5 * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = aws_lambda_function.c19-energy-outage-etl-lambda.arn
    role_arn = aws_iam_role.c19-energy-monitor-scheduler-role.arn
  }
}