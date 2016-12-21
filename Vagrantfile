# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = 2

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.ssh.forward_agent = true

    config.vm.box = "ubuntu/trusty64"
    config.vm.network :forwarded_port, guest: 8000, host: 8000
    config.vm.network :forwarded_port, guest: 8001, host: 8001

    config.vm.provider "virtualbox" do |v|
        v.memory = 4096
        v.cpus = 2
    end

    config.vm.synced_folder ".", "/pleas/"

    config.vm.provision :shell do |sh|
        sh.privileged = false
        sh.path = "vagrant/bootstrap.sh"
    end
end
