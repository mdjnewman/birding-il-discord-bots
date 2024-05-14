provider "google" {
  project = "birding-il"
  region  = "us-central1"
}

data "google_client_config" "current" {
}