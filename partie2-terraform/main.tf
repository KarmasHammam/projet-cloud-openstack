terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 2.1.0"
    }
  }
}

provider "openstack" {
  cloud    = "mycloud"
  insecure = true
}

resource "openstack_compute_instance_v2" "centos_vm" {
  name            = "centos-terraform"
  image_name      = "centos-7"
  flavor_name     = "m1.centos"
  key_pair        = "my-k"
  security_groups = ["default"]
  config_drive    = true

  network {
    name = "private"
  }

  metadata = {
    created_by  = "Terraform"
    project     = "Cloud Edge Computing"
    environment = "OpenStack DevStack"
  }
}

output "instance_name" {
  value = openstack_compute_instance_v2.centos_vm.name
}

output "instance_ip" {
  value = openstack_compute_instance_v2.centos_vm.access_ip_v4
}
