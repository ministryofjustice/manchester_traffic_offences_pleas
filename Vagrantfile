# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = 2

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.ssh.forward_agent = true

    config.vm.box = "ubuntu/trusty64"
    config.vm.network :forwarded_port, guest: 8000, host: 8000

    config.vm.provider "virtualbox" do |v|
        v.memory = 1024
        v.cpus = 2
    end

    config.vm.synced_folder ".", "/pleas/"
    config.vm.synced_folder "../manchester_traffic_offences_ops", "/ops/"
    config.vm.synced_folder "../froddd/moj_template/pkg/django_moj_template-0.23.1/moj_template", "/pleas/moj_template/"


    config.vm.provision :shell do |sh|
        sh.privileged = false
        sh.path = "vagrant/bootstrap.sh"
    end
end