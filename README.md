provider "aws" {
  region = "us-east-1"
}

provider "aws" {
  alias  = "crr"
  region = "us-west-1"
}

terraform {
  backend "s3" {
    region = "us-east-1"
  }
  required_version = ">= 1.5.7"
  required_providers {
    aws = "~> 4.67.0"
  }
}



  region = "us-east-1"
}

provider "aws" {
