# IAM Role for task execution
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

# Dashboard ECS task definition
resource "aws_ecs_task_definition" "c19-energy-monitor-dashboard" {
  family = "c19-energy-monitor-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu = "1024"
  memory = "5120"
  execution_role_arn = aws_iam_role.c19-energy-task-execution-role.arn
  container_definitions = jsonencode([
    {
        name = "c19-energy-monitor-dashboard"
        image = "${aws_ecr_repository.c19-energy-monitor-dashboard.repository_url}:latest"
        memory = 5120
        essential = true,
        portMappings = [
          {
            containerPort = 8501
            hostPort      = 8501
            protocol      = "tcp"
          }
        ],
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

# IAM role for ECS 
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

# Policy attachment for ECS
resource "aws_iam_role_policy_attachment" "c19-energy-monitor-ecs-policy-attachment" {
  role = aws_iam_role.c19-energy-task-execution-role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"   
}

# Dashboard security group
resource "aws_security_group" "c19-energy-monitor-dashboard-sg" {
  name = "c19-energy-monitor-dashboard-sg"
  description = "Allows all internet access to the streamlit dashboard"
  vpc_id = var.VPC_ID

  ingress {
    from_port   = 8501
    to_port     = 8501
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS service 
resource "aws_ecs_service" "c19-energy-tracker-ecs-service" {
  name = "c19-energy-tracker-ecs-service"
  cluster = "arn:aws:ecs:eu-west-2:129033205317:cluster/c19-ecs-cluster"
  task_definition = aws_ecs_task_definition.c19-energy-monitor-dashboard.arn
  desired_count = "1"

  network_configuration {
    subnets = [var.VPC_PUBLIC_SUBNET_1, var.VPC_PUBLIC_SUBNET_2, var.VPC_PUBLIC_SUBNET_3]
    security_groups = [aws_security_group.c19-energy-monitor-dashboard-sg.id]
    assign_public_ip = true
  }

  capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 100
    base              = 1
  }
}