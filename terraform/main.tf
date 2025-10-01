provider "aws" {
  region     = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
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


