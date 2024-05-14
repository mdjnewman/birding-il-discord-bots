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

data "cloudinit_config" "bot_compute_cloudinit" {
  gzip          = false
  base64_encode = false

  part {
    filename     = "cloud-config.yaml"
    content_type = "text/cloud-config"

    content = file("${path.module}/cloud-config.yaml")
  }
}


resource "google_compute_instance" "bot_compute" {
  can_ip_forward      = false
  deletion_protection = false
  enable_display      = false
  machine_type        = "e2-micro"
  metadata = {
    user-data = "${data.cloudinit_config.bot_compute_cloudinit.rendered}"
  }
  name    = "birding-il-bot-compute"
  project = "birding-il"
  zone    = "us-central1-a"

  boot_disk {
    auto_delete = true
    source      = google_compute_disk.bot_compute_disk.id
  }

  network_interface {
    network            = "https://www.googleapis.com/compute/v1/projects/birding-il/global/networks/default"
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
  image                       = "https://www.googleapis.com/compute/v1/projects/cos-cloud/global/images/cos-109-17800-147-54"
  licenses                    = ["https://www.googleapis.com/compute/v1/projects/cos-cloud/global/licenses/cos-pcid", "https://www.googleapis.com/compute/v1/projects/cos-cloud/global/licenses/cos", "https://www.googleapis.com/compute/v1/projects/cos-cloud-shielded/global/licenses/shielded-cos"]
  physical_block_size_bytes   = 4096
  project                     = "birding-il"
  size                        = 10
  type                        = "pd-standard"
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

resource "random_id" "rare-bird-excludes-suffix" {
  byte_length = 8
}

resource "google_storage_bucket" "rare-bird-excludes" {
  name          = "${data.google_client_config.current.project}-rare-bird-excludes-${random_id.rare-bird-excludes-suffix.hex}"
  location      = "US"
  force_destroy = true

  public_access_prevention    = "enforced"
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_iam_member" "member" {
  bucket = google_storage_bucket.rare-bird-excludes.id
  role   = "roles/storage.objectViewer"
  member = google_service_account.compute_engine_service_account.member
}
