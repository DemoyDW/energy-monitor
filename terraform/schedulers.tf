# IAM role and policy for Eventbridge schedulers
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

resource "aws_iam_role_policy_attachment" "c19-energy-monitor-scheduler-role-attach" {
  role       = aws_iam_role.c19-energy-monitor-scheduler-role.name
  policy_arn = aws_iam_policy.c19-energy-monitor-scheduler-policy.arn
}


resource "aws_iam_policy" "c19-energy-monitor-scheduler-policy" {
  name = "c19-energy-monitor-scheduler-Policy"
  
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
             {
        "Action" : [
          "states:StartExecution"
        ],
        Effect   = "Allow"
        Resource = [aws_sfn_state_machine.c19-energy-summary-email-sf.arn,
                    aws_sfn_state_machine.c19-energy-outage-email-sf.arn]
      }
        ],
        
    })
}



# Eventbridge scheduler for reading ETL Lambda function 
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




# Eventbridge scheduler for outage ETL and email
resource "aws_scheduler_schedule" "c19-energy-monitor-outage-step-scheduler" {
  name        = "c19-energy-monitor-outage-ETL-scheduler"
  description = "Run outage ETL job every 5."

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(*/5 * * * ? *)"
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = aws_sfn_state_machine.c19-energy-outage-email-sf.arn
    role_arn = aws_iam_role.c19-energy-monitor-scheduler-role.arn
  }
}

# Eventbridge scheduler for summary email
resource "aws_scheduler_schedule" "c19-energy-monitor-summary-email-step-scheduler" {
  name        = "c19-energy-monitor-summary-email-step-scheduler"
  description = "Run outage ETL job every 5."

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression          = "cron(0 9 ? * 2 *)"
  schedule_expression_timezone = "Europe/London"

  target {
    arn      = aws_sfn_state_machine.c19-energy-summary-email-sf.arn
    role_arn = aws_iam_role.c19-energy-monitor-scheduler-role.arn
  }
}