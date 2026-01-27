# ONAP GitOps Manifests (Minimal Setup)

This repository contains **pre-rendered, sanitized Kubernetes manifests** for a minimal ONAP deployment. These manifests are optimized for GitOps workflows using **ArgoCD** and have been verified on cluster environments (HPE15/HPE16). It is a self-contained "One-Click" deployment package.

## 🚀 Components Included
- **Strimzi Kafka Cluster**: 0.46.0+ in KRaft mode (no ZooKeeper).
- **PostgreSQL Cluster**: Primary and Replicas for Core and Policy components.
- **MariaDB Galera**: Minimal stateful setup.
- **ONAP Policy Framework**: Full suite (API, PAP, ACM, Apex, and 5 participants).
- **ONAP DCAE**: VES Collector.

## 🏗️ Architecture & GitOps Design

### Sync Waves
To ensure a stable "one-click" deployment, the manifests use **ArgoCD Sync Waves**:
1.  **Wave -5**: Infrastructure Foundation (`smo-storageclass.yaml`).
2.  **Wave -3**: RBAC and ServiceAccounts (`rbac.yaml`).
3.  **Wave -2**: Operators (`strimzi_operator.yaml`).
4.  **Wave 0**: Application Components (`*_full.yaml`).

### Storage Requirement
All stateful components use the `smo-storage` StorageClass. This repository **includes a lightweight NFS Provisioner** (`nfs-provisioner.yaml`) which automatically sets up a storage class named `smo-storage` backed by local directory storage on the nodes. No external storage configuration is required for a standard test environment.

## 🛠️ Deployment Instructions

### 1. Prerequisite: Create Namespaces
ArgoCD can create namespaces, but it is recommended to have them ready:
```bash
kubectl create namespace onap
kubectl create namespace strimzi-system
```

### 2. Connect to ArgoCD
Apply the parent application manifest to your cluster:
```bash
kubectl apply -f https://raw.githubusercontent.com/Jitmisra/argofinal/main/argo-parent-app.yaml
```

### 3. Verification
Once applied, ArgoCD will automatically sync the repository.
- **CRDs**: Strimzi CRDs (0.46.0) are included and will be applied automatically.
- **Storage**: An NFS Provisioner is included (`nfs-provisioner.yaml`) to auto-provision persistent volumes.
- **Connectivity**: If deploying to a remote private cluster, ensure your `kubeconfig` is correctly configured (e.g., via SSH tunnel).

## 📂 Repository Structure
- `rbac.yaml`: Consolidated ServiceAccounts and cluster-wide RBAC.
- `strimzi_operator.yaml`: Strimzi Operator deployment and mandatory ConfigMap.
- `postgres_full.yaml`: Databases, PVCs, and internal communication Services.
- `policy_full.yaml`: Complete Policy Framework deployment.
- `dcae_full.yaml`: DCAE components.
- `strimzi_full.yaml`: Kafka cluster definition.
- `kafka_nodepools.yaml`: Required CRDs for modern Strimzi setups.
- `nfs-provisioner.yaml`: Self-contained NFS storage provisioner.
- `strimzi_crds.yaml`: Full Strimzi 0.46.0 CRD definitions.

---
**Note**: These manifests are snapshots of a verified working state. They have been sanitized of cluster-specific UID/metadata to prevent sync conflicts in GitOps.
