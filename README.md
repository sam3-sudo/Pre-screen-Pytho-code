data "aws_caller_identity" "this" {}
data "aws_region" "this" {}



data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.terraform_remote_state_bucket_name
    region = data.aws_region.this.name
    key    = local.terraform_remote_state_bucket_vpc_key
  }
}


data "aws_subnets" "non_routable_vpc_subnets" {
  filter {
    name   = "vpc-id"
    values = [local.vpc.vpc.id]
  }
  filter {
    name   = "tag:Name"
    values = ["supp-benefits-${var.logical_environment}-non-routable-golden-subnet-*"]
  }
}


data "aws_subnet" "non_routable_vpc_subnets" {
  for_each = toset(data.aws_subnets.non_routable_vpc_subnets.ids)
  id = each.value
}
