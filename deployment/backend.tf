terraform {
  backend "gcs" {
    bucket = "birding-il-bots-bucket-tfstate"
    prefix = "terraform/state"
  }
}
