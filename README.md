terraform_remote_state_bucket_name="silverton-tf-state-851725592494-us-east-1"
terraform_remote_state_bucket_key_prefix="supp-benefits-services/dev"
vpc_cidr        = ["100.124.0.0/16"]

do not hardcode this. Redis should be provisioned in "routable " subnet similar to documentDB.
please change this

vpc                                    = data.terraform_remote_state.vpc.outputs.vpc
