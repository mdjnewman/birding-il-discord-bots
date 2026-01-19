terraform {
  backend "gcs" {
    bucket = "birding-il-bots-bucket-tfstate"
    prefix = "terraform/state"
  }
  required_providers {
    random = {
      source = "hashicorp/random"
      version = "3.8.0"
    }
  }
}

provider "google" {
  project = "birding-il"
  region  = "us-central1"
}

data "google_client_config" "current" {
}