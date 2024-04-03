resource "google_service_account" "compute_engine_service_account" {
  account_id   = "birding-il-compute-engine"
  display_name = "Birding Illinois Service Account for Compute"
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


resource "google_compute_instance" "bot_compute" {
  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false
  machine_type        = "e2-micro"
  metadata = {
    gce-container-declaration = "spec:\n  restartPolicy: Always\n  containers:\n  - name: instance-20240401-024615\n    image: 'us.gcr.io/birding-il/birding-il-bots:latest'\n\n# This container declaration format is not public API and may change without notice. Please\n# use gcloud command-line tool or Google Cloud Console to run Containers on Google Compute Engine."
  }
  name    = "instance-20240401-024615"
  project = "birding-il"
  zone    = "us-central1-a"

  boot_disk {
    auto_delete = true
    source      = google_compute_disk.bot_compute_disk.id
  }

  network_interface {
    network            = "https://www.googleapis.com/compute/v1/projects/birding-il/global/networks/default"
    network_ip         = "10.128.0.2"
    stack_type         = "IPV4_ONLY"
    subnetwork         = "https://www.googleapis.com/compute/v1/projects/birding-il/regions/us-central1/subnetworks/default"
    subnetwork_project = "birding-il"
    access_config {
      network_tier = "STANDARD"
    }
  }

  reservation_affinity {
    type = "ANY_RESERVATION"
  }

  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    preemptible         = false
    provisioning_model  = "STANDARD"
  }

  service_account {
    email  = google_service_account.compute_engine_service_account.email
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
  }

  shielded_instance_config {
    enable_integrity_monitoring = true
    enable_secure_boot          = false
    enable_vtpm                 = true
  }
}

resource "google_compute_disk" "bot_compute_disk" {
  name = "instance-20240401-024615"

  enable_confidential_compute = false
  image                       = "https://www.googleapis.com/compute/v1/projects/cos-cloud/global/images/cos-stable-109-17800-147-38"
  licenses                    = ["https://www.googleapis.com/compute/v1/projects/cos-cloud/global/licenses/cos-pcid", "https://www.googleapis.com/compute/v1/projects/cos-cloud/global/licenses/cos", "https://www.googleapis.com/compute/v1/projects/cos-cloud-shielded/global/licenses/shielded-cos"]
  physical_block_size_bytes   = 4096
  project                     = "birding-il"
  size                        = 10
  type                        = "pd-balanced"
  zone                        = "us-central1-a"

  guest_os_features {
    type = "GVNIC"
  }
  guest_os_features {
    type = "SEV_CAPABLE"
  }
  guest_os_features {
    type = "SEV_LIVE_MIGRATABLE"
  }
  guest_os_features {
    type = "SEV_LIVE_MIGRATABLE_V2"
  }
  guest_os_features {
    type = "SEV_SNP_CAPABLE"
  }
  guest_os_features {
    type = "UEFI_COMPATIBLE"
  }
  guest_os_features {
    type = "VIRTIO_SCSI_MULTIQUEUE"
  }
}
P