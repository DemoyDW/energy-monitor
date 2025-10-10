# ECRs for Lambdas and ECS service
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








