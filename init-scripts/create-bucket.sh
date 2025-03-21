#!/bin/bash

# Crear un bucket llamado "files" en S3
awslocal s3 mb s3://files

# Verificar que el bucket se ha creado
awslocal s3 ls