output "rds_endpoint" {
    description = "The endpoint of the RDS instance"
    value = aws_db_instance.c14-fahad-rahman-museum-db.endpoint
}