
# IAM role and policy for step functions
data "aws_iam_policy_document" "c19-energy-step-function-role-policy-assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = [
      "sts:AssumeRole",
    ]
  }
}

resource "aws_iam_role" "c19-energy-step-function-role" {
  name               = "c19-energy-step-function-role"
  assume_role_policy = data.aws_iam_policy_document.c19-energy-step-function-role-policy-assume_role.json
}

data "aws_iam_policy_document" "c19-energy-step-function-role-policy" {


  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    # resources = ["*"]

    resources = ["${aws_lambda_function.c19-energy-outage-etl-lambda.arn}:$LATEST", 
                "${aws_lambda_function.c19-energy-summary-email-lambda.arn}:$LATEST"]
  }

  statement {
    effect = "Allow"

    actions = [
      "ses:SendBulkEmail",
      "ses:SendEmail"
    ]

    resources = ["*"]
  }

}


resource "aws_iam_policy" "c19-energy-step-function-policy" {
  name        = "c19-energy-step-function-policy"
  description = "Policy for the bulk email-sending step functions."
  policy      = data.aws_iam_policy_document.c19-energy-step-function-role-policy.json
}

resource "aws_iam_role_policy_attachment" "c19-energy-step-function-policy-attachment" {
  role       = aws_iam_role.c19-energy-step-function-role.name
  policy_arn = aws_iam_policy.c19-energy-step-function-policy.arn
}

resource "aws_sfn_state_machine" "c19-energy-summary-email-sf" {
  name     = "c19-energy-summary-email-sf"
  role_arn = aws_iam_role.c19-energy-step-function-role.arn
  definition = <<EOF
{
  "Comment": "A description of my state machine",
  "StartAt": "Lambda Invoke",
  "States": {
    "Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Output": "{% $states.result.Payload %}",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:c19-energy-summary-email-lambda:$LATEST",
        "Payload": "{% $states.input %}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "SendBulkEmail"
    },
    "SendBulkEmail": {
      "Type": "Task",
      "Arguments": {
        "BulkEmailEntries": [
          {
            "Destination": {
              "ToAddresses": "{% $states.input.customer_emails %}"
            }
          }
        ],
        "DefaultContent": {
          "Template": {
            "TemplateContent": {
              "Subject": "Energy Summary",
              "Html": "{% $states.input.email_body %}"
            },
            "TemplateData": "{}"
          }
        },
        "FromEmailAddress": "sl-coaches@proton.me"
      },
      "Resource": "arn:aws:states:::aws-sdk:sesv2:sendBulkEmail",
      "End": true
    }
  },
  "QueryLanguage": "JSONata"
}
EOF
}


resource "aws_sfn_state_machine" "c19-energy-outage-email-sf" {
  name     = "c19-energy-outage-email-sf"
  role_arn = aws_iam_role.c19-energy-step-function-role.arn
  definition = <<EOF
  {
  "Comment": "A description of my state machine",
  "StartAt": "Lambda Invoke",
  "States": {
    "Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Output": "{% $states.result.Payload %}",
      "Arguments": {
        "FunctionName": "arn:aws:lambda:eu-west-2:129033205317:function:c19-energy-outage-etl-lambda:$LATEST",
        "Payload": "{% $states.input %}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Choice"
    },
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Next": "SendBulkEmail",
          "Condition": "{% $count($states.input.customer_emails) > 0 %}"
        }
      ],
      "Default": "Pass"
    },
    "SendBulkEmail": {
      "Type": "Task",
      "Arguments": {
        "BulkEmailEntries": [
          {
            "Destination": {
              "ToAddresses": "{% $states.input.customer_emails %}"
            }
          }
        ],
        "DefaultContent": {
          "Template": {
            "TemplateContent": {
              "Subject": "Power Outage Alert in your area!!",
              "Html": "{% $states.input.email_body %}"
            },
            "TemplateData": "{}"
          }
        },
        "FromEmailAddress": "sl-coaches@proton.me"
      },
      "Resource": "arn:aws:states:::aws-sdk:sesv2:sendBulkEmail",
      "End": true
    },
    "Pass": {
      "Type": "Pass",
      "End": true
    }
  },
  "QueryLanguage": "JSONata"
}
EOF
}