resource "google_service_account" "compute_engine_service_account" {
  account_id   = "birding-il-compute-engine"
  display_name = "Birding IL Service Account for Compute"
}

resource "google_project_iam_member" "compute_engine_service_account_binding" {
  for_each = toset([
    "roles/artifactregistry.reader",
    "roles/logging.logWriter",
    "roles/secretmanager.secretAccessor"
  ])
  role    = each.key
  member  = "serviceAccount:${google_service_account.compute_engine_service_account.email}"
  project = google_service_account.compute_engine_service_account.project
}

resource "google_artifact_registry_repository" "artifact_repo" {
  cleanup_policy_dry_run = false
  format                 = "DOCKER"
  location               = "us"
  mode                   = "STANDARD_REPOSITORY"
  project                = "birding-il"
  repository_id          = "us.gcr.io"
}
