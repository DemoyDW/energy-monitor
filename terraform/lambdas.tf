
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

# Lambda Functions 
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
  function_name = "c19-energy-summary-email-lambda"
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