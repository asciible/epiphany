## Epiphany backup and restore

### Introduction

Epiphany provides solution to create full or partial backup and restore for some of components. Those supported components are listed below:

- [Load Balancer](#load-balancer)
- [Logging](#logging)
- [Monitoring](#monitoring)
- [Postgresql](#postgresql)
- [RabbitMQ](#rabbitmq)
- [Kubernetes (only backup)](#kubernetes)

Backup is created directly on the machine where component is running, and it is moved to the ``repository`` host via
rsync. On the ``repository`` host backup files are stored in location ``/epibackup/mounted`` mounted on a local
filesystem. See [How to store backup](#2-how-to-store-backup) chapter.

## 1. How to perform backup

### Backup configuration file and command

Copy default configuration for backup from ``defaults/configuration/backup.yml`` into newly created backup.yml config
file, supply correct provider and enable backup for chosen components by setting up ``enabled`` parameter to ``true``.

```yaml
kind: configuration/backup
title: Backup Config
name: default
provider: azure
specification:
  components:
    load_balancer:
      enabled: true
    logging:
      enabled: false
    monitoring:
      enabled: true
    postgresql:
      enabled: true
    rabbitmq:
      enabled: false
# Kubernes recovery is not supported at this point.
# You may create backup by enabling this below, but recovery should be done manually according to Kubernetes documentation.
    kubernetes:
      enabled: false
```

Run ``epicli backup`` command:

```shell
epicli backup -f backup.yml -b build_folder
```

## 2. How to store backup

Backup location is defined in ``backup`` role as ``backup_destination_host`` and ``backup_destination_dir``. Default
backup location is defined on ``repository`` host inside location ``/epibackup/mounted/``. Use ``mounted`` location as mount
point and mount storage you want to use. This might be:

- Azure Blob Storage
- Amazon S3
- NAS
- Any other attached storage

Ensure that mounted location contains enough free space, is reliable and is well protected against disaster.

---
**NOTE**

If you don't attach any storage into the mount point location, be aware that backups will be stored on the local
machine's disk drive. This is not recommended.

---

## 3. How to perform recovery

### Recovery configuration file and command

Copy existing default configuration from ``defaults/configuration/recovery.yml`` into newly created recovery.yml config
file, supply correct provider and set ``enabled`` parameter for component to recovery. It's possible to choose snapshot
name by passing date and time part of snapshot name. If snapshot name is not provided, the latest one will be restored.

```yaml
kind: configuration/recovery
title: Recovery Config
name: default
provider: azure
specification:
  components:
    load_balancer:
      enabled: true
      snapshot_name: latest           #restore latest backup
    logging:
      enabled: true
      snapshot_name: 20200604-150829  #restore selected backup
    monitoring:
      enabled: false
      snapshot_name: latest
    postgresql:
      enabled: false
      snapshot_name: latest
    rabbitmq:
      enabled: false
      snapshot_name: latest
```

Run ``epicli recovery`` command:

```shell
epicli recovery -f recovery.yml -b build_folder
```

## 4. How backup and recovery work

### Load Balancer

Load balancer backup includes:

- Configuration files: ``/etc/haproxy/``
- SSL certificates: ``/etc/ssl/haproxy/``

Recovery includes all backed up files

### Logging

Logging backup includes:

- Elasticsearch database snapshot
- Elasticsearch configuration ``/etc/elasticsearch/``
- Kibana configuration ``/etc/kibana/``

Only single-node Elasticsearch backup is supported. Solution for multi-node Elasticsearch cluster will be added in
future release.

### Monitoring

Monitoring backup includes:

- Prometheus data snapshot
- Prometheus configuration ``/etc/prometheus/``
- Grafana data snapshot

Recovery includes all backed up configurations and snapshots.

### Postgresql

Postgresql backup includes:

- Database data and metadata dump using ``pg_dumpall``
- Configuration files: ``*.conf``

When multiple node configuration is used, and failover action has changed database cluster status (one node down,
switchover) it's still possible to create backup. But before database restore, cluster needs to be recovered by
running ``epicli apply`` and next ``epicli recovery`` to restore database data. By default, we don't support recovery
database configuration from backup since this needs to be done using ``epicli apply`` or manually by copying backed up
files accordingly to cluster state. The reason of this is that is very risky to restore configuration files among
different database cluster configurations.

### RabbitMQ

RabbitMQ backup includes:

- Messages definitions
- Configuration files: ``/etc/rabbitmq/``

Backup does not include RabbitMQ messages.

Recovery includes all backed up files and configurations.

### Kubernetes

Epiphany backup provides:

- Etcd snapshot
- Public Key Infrastructure ``/etc/kubernetes/pki``
- Kubeadm configuration files

Following features are not supported yet (use related documentation to do that manually):

- Kubernetes cluster recovery
- Backup and restore of data stored on persistent volumes described in [persistent storage](./PERSISTENT_STORAGE.md)
  documentation
