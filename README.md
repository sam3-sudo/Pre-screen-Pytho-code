locals.tf 

locals {
  project = {
    name                 = var.project
    environment          = var.environment
    logical_environment  = var.logical_environment
    #api_gw_domain_name   = "${var.logical_environment}-api.supp-benefits-${var.environment}.aws.zilverton.com"
    resource_prefix_name = "${var.project}-${var.logical_environment}"
    account_id           = data.aws_caller_identity.this.account_id


    tags = {
      CostCenter   = "00000000"
      AssetOwner   = "Tim.Gibson@CignaHealthcare.com"
      ServiceNowBA = "AS1234"
      ServiceNowAS = var.config_id
      AssetName    = "supp-benefits-services"
      BackupOwner  = "TirumalaDurgaRao.Nallagachu@CignaHealthcare.com"
      Environment  = var.logical_environment
      SecurityReviewID = "RITM1851597"
    }

   # alarm_actions     = [data.aws_sns_topic.supp_benefits_alarm_funnel.arn]
  }

  application_name = "${var.project}-${var.logical_environment}-definition"
  #non_routable_subnets = data.aws_subnets.non_routable_vpc_subnets


  terraform_remote_state_bucket_vpc_key        = "${var.terraform_remote_state_bucket_key_prefix}/vpc-golden/terraform.tfstate"

  vpc                                          = data.terraform_remote_state.vpc.outputs.vpc


  tags = {
    AppName = local.application_name
    Purpose = "REST API service for Definition Service"
    LOB     = "SB"
    ART     = "Sales"
  }
  required_tags = {
    BusinessEntity         = "healthServices"
    ComplianceDataCategory = "none"
    DataClassification     = "internal"
    DataSubjectArea        = "product"
    LineOfBusiness         = "healthServices"
  }
  tags_v1 = merge({}, local.tags, local.project.tags, local.required_tags)

}
here is redis.tf 
 enabled                     = true
  tf_dev_mode_enabled         = true
  subsidiary_prefix           = "supp-benefits"
  product_name                = "definition"
  workload_name               = "cache"
  vpc_id                      = local.vpc.vpc.id
  external_access_enabled     = true
  external_access_cidr_blocks = var.vpc_cidr
  create_kms_key_redis        = true
  kms_key_arn_redis           = ""
  create_kms_key_secret       = true
  kms_key_arn_secret          = ""
  kms_key_accounts            = []
  kms_key_administrators      = var.kms_key_administrators
  engine_version              = "7.0"
  node_type                   = "cache.t3.small"
  redis_port                  = 6379
  num_read_replicas           = 2
  cluster_mode_enabled        = true
  num_node_groups             = 2
  create_parameter_group      = true
  parameter_overrides = {
    activedefrag                  = "yes"
    client-query-buffer-limit     = "536870912"
    cluster-allow-reads-when-down = "yes"
    databases                     = "8"
  }
  snapshot_retention_limit   = 30
  snapshot_window            = "04:40-06:40"
  initial_auth_token         = ""
  create_auth_token_rotation = true
  existing_secrets = [
  ]
  log_types             = ["slow-log"]
  log_format            = "text"
  log_retention_in_days = 14
  create_alarm          = true
  environment           = var.environment
  required_tags         = local.project.tags
  required_data_tags    = local.tags_v1
  optional_tags = {
    BackupOwner = "SandeepVarma.Buddaraja@cignahealthcare.com"
    Environment = var.environment
    Purpose     = "Cache-PubSub"
  }
  optional_data_tags = {}
}
