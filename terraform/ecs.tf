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