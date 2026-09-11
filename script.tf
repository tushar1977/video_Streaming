# =========================================================
# Providers
# =========================================================
terraform {
  required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.53.0"
    }
  }
}

# assuming we have already sourced the rc file
provider "openstack" {
  auth_url = "https://10.30.16.55:13000"
}

# =========================================================
# Variables
# =========================================================
variable "image_name" {
  description = "Name of the Ubuntu image already registered in Glance"
  type        = string
  default     = "rhel-img" # change to match your actual image name
}

variable "flavor_name" {
  description = "Flavor to use for all other VMs"
  type        = string
  default     = "test-flavor"
}

variable "flavor_backend2" {
  description = "Flavor to use for specific backend2"
  type        = string
  default     = "C3a"
}
variable "root_volume_size" {
  description = "Root disk size (GB) for each VM"
  type        = number
  default     = 20
}

variable "security_groups" {
  description = "Security groups applied to all VMs"
  type        = list(string)
  default     = ["web-ssh"]
}

# One entry per VM: its own keypair name, its own public key, and its own fixed IP
variable "vms" {
  description = "Map of VM name => { keypair name, public key file, fixed IP }"
  type = map(object({
    keypair_name = string
    public_key   = string
    fixed_ip     = string
  }))
  default = {
    "ubuntu-vm-1" = {
      keypair_name = "tushar-terraform-1"
      public_key   = "/home/tushar/.ssh/tushar-terraform-1.pub"
      fixed_ip     = "192.168.1.41"
    }
    "ubuntu-vm-2" = {
      keypair_name = "tushar-terraform-2"
      public_key   = "/home/tushar/.ssh/tushar-terraform-2.pub"
      fixed_ip     = "192.168.1.42"
    }
    "ubuntu-vm-3" = {
      keypair_name = "tushar-terraform-3"
      public_key   = "/home/tushar/.ssh/tushar-terraform-3.pub"
      fixed_ip     = "192.168.1.43"
    }
  }
}

# =========================================================
# Network (single VPC for all three VMs)
# =========================================================
resource "openstack_networking_network_v2" "terra-vpc" {
  name           = "network_terra"
  admin_state_up = "true"
}

resource "openstack_networking_subnet_v2" "terra-subnet-1" {
  name            = "terra_subnet_1"
  network_id      = openstack_networking_network_v2.terra-vpc.id
  cidr            = "192.168.1.0/24"
  ip_version      = 4
  enable_dhcp     = true
  dns_nameservers = ["8.8.8.8"]
}

# =========================================================
# Keypairs — one distinct keypair per VM
# =========================================================
resource "openstack_compute_keypair_v2" "vm_keypairs" {
  for_each   = var.vms
  name       = each.value.keypair_name
  public_key = file(each.value.public_key)
}

# =========================================================
# Three Ubuntu VMs, each with its own keypair + fixed IP
# =========================================================
resource "openstack_compute_instance_v2" "ubuntu_vm" {
  for_each = var.vms

  name            = each.key
  flavor_name     = var.flavor_name
  key_pair        = openstack_compute_keypair_v2.vm_keypairs[each.key].name
  security_groups = var.security_groups

  block_device {
    uuid                  = data.openstack_images_image_v2.ubuntu.id
    source_type           = "image"
    destination_type      = "volume"
    volume_size           = var.root_volume_size
    boot_index            = 0
    delete_on_termination = true
  }

  network {
    uuid        = openstack_networking_network_v2.terra-vpc.id
    fixed_ip_v4 = each.value.fixed_ip
  }

  depends_on = [openstack_networking_subnet_v2.terra-subnet-1]
}

# Look up the Ubuntu image once, reused by all three instances
data "openstack_images_image_v2" "ubuntu" {
  name        = var.image_name
  most_recent = true
}

# =========================================================
# Outputs
# =========================================================
output "vm_ips" {
  description = "Fixed IPs assigned to each VM"
  value       = { for k, v in openstack_compute_instance_v2.ubuntu_vm : k => v.network[0].fixed_ip_v4 }
}

output "vm_keypairs" {
  description = "Keypair used by each VM"
  value       = { for k, v in var.vms : k => v.keypair_name }
}
