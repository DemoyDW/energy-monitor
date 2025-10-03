terraform {
  backend "s3" {
    bucket = "c19-energy-monitor-terraform-state"
    key = "terraform.tfstate"
    region = "eu-west-2"
  }
}