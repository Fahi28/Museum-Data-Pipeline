provider "aws" {
    region = "eu-west-2"
}

resource "aws_security_group" "c14-fahad-museum-rds-security-group" {
    name = "c14-fahad-museum-rds-sg"
    description = "Security group for Museum Database"
    vpc_id = "vpc-0344763624ac09cb6"

    # postgres port allow
    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 65535
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "aws_security_group" "c14-fahad-museum-ec2-security-group" {
    name = "c14-fahad-museum-ec2-sg"
    description = "Security group for Museum Database"
    vpc_id = "vpc-0344763624ac09cb6"

    # postgres port allow
    ingress {
        from_port = 5432
        to_port = 5432
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        from_port = 22
        to_port = 22
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }

    egress {
        from_port = 0
        to_port = 65535
        protocol = "tcp"
        cidr_blocks = ["0.0.0.0/0"]
    }
}


data "aws_subnet" "public_subnet" {
    filter {
        name = "tag:Name"
        values = ["c14-public-subnet-1"]
    }
}

resource "aws_instance" "c14-fahad-museum" {
        ami           = "ami-0acc77abdfc7ed5a6"
        instance_type = "t2.nano"   
        subnet_id = data.aws_subnet.public_subnet.id

        key_name = "c14-fahad-museum"
        associate_public_ip_address = true

        vpc_security_group_ids = [aws_security_group.c14-fahad-museum-ec2-security-group.id]

        tags = {
          Name = "c14-fahad-museum-ec2"
        }
    }

resource "aws_db_instance" "c14-fahad-rahman-museum-db" {
  allocated_storage    = 20
  storage_type         = "gp3"
  engine               = "postgres"
  engine_version       = "16.3"
  identifier = "c14-fahad-musuem-db"
  instance_class       = "db.t4g.micro"
  username             = var.DB_USERNAME
  password             = var.DB_PASSWORD
  vpc_security_group_ids = [aws_security_group.c14-fahad-museum-rds-security-group.id]
  parameter_group_name = "default.postgres16"
  skip_final_snapshot  = true
  publicly_accessible = true
  db_subnet_group_name = "c14-public-subnet-group"
  
}

