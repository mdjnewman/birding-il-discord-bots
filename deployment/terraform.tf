terraform {
  backend "gcs" {
    bucket = "birding-il-bots-bucket-tfstate"
    prefix = "terraform/state"
  }
  required_providers {
    random = {
      source = "hashicorp/random"
      version = "3.6.2"
    }
  }
}
