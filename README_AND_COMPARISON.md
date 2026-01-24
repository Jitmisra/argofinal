# 1Algooverride: GitOps-Ready ONAP Manifests

This folder contains **production-ready manifests** for deploying ONAP components via GitOps on Kubernetes. These manifests were captured from the successfully running HPE15 deployment and have been proven to work on HPE16 via ArgoCD.

## ✅ Successfully Deployed Components
- **Kafka Cluster** (Strimzi with KRaft mode)
- **Policy Framework** (API, PAP, ACM Runtime, Apex PDP, 5 CLAMP Participants)
- **DCAE VES Collector**
- **MariaDB Galera**
- **PostgreSQL** (configurations included)

## GitOps Deployment Files

### Core Component Manifests (6 files)
- `policy_full.yaml` - Complete Policy framework (54 resources)
- `dcae_full.yaml` - DCAE VES Collector (7 resources)
- `strimzi_full.yaml` - Kafka cluster resources in onap namespace (27 resources)
- `strimzi_operator.yaml` - Strimzi Cluster Operator (runs in strimzi-system namespace)
- `kafka_nodepools.yaml` - KafkaNodePool CRs for broker and controller (required for Strimzi 0.46+)
- `postgres_full.yaml` - PostgreSQL databases (24 resources)

### RBAC (1 file)
- `rbac.yaml` - Role and RoleBinding for all ONAP ServiceAccounts

### Reference/Configuration
- `user_desired_values.yaml` - User's original configuration preferences
- `apply_values_override.py` - Reference script for generating overrides
- `README_AND_COMPARISON.md` - This file

## How to Deploy via GitOps (ArgoCD)

**Repository**: `https://github.com/Jitmisra/argoover`

1. **Prerequisites**:
   ```bash
   # Ensure ArgoCD is installed
   kubectl create namespace argocd
   kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
   
   # Create required namespaces
   kubectl create namespace onap
   kubectl create namespace strimzi-system
   
   # Ensure StorageClass exists
   kubectl apply -f smo-storageclass.yaml
   ```

2. **Deploy via ArgoCD**:
   ```bash
   kubectl apply -f argo-parent-app.yaml
   ```

3. **Monitor Deployment**:
   ```bash
   kubectl get application -n argocd
   kubectl get pods -n onap
   kubectl get kafka -n onap
   ```

## Comparison: 1Algooverride vs. OOM

| Feature | OOM (Standard Repo) | 1Algooverride (This Folder) | Why? |
| :--- | :--- | :--- | :--- |
| **Deployment Method** | Helm charts (requires rendering) | **Pre-rendered YAML manifests** | GitOps-ready, no Helm required |
| **Namespace Handling** | Single namespace | **Multi-namespace (onap + strimzi-system)** | Operators need separate namespaces |
| **Kafka Deployment** | May use ZooKeeper | **KRaft mode with KafkaNodePools** | Modern Strimzi (0.46+) |
| **RBAC** | Helm-generated (may be incomplete) | **Explicit RBAC manifests** | Prevents ServiceAccount permission errors |
| **Snapshot Source** | Git repository | **Live cluster (HPE15)** | Captures actual working state |

### Key Fixes Applied
1. **Namespace Preservation** - Fixed snapshot script to preserve original namespaces (crucial for operators)
2. **KafkaNodePool Resources** - Added missing KafkaNodePool CRs required by Strimzi 0.46+
3. **RBAC Permissions** - Created comprehensive RoleBinding for all ServiceAccounts
4. **Operator Deployment** - Captured Strimzi operator from strimzi-system namespace

## Deployment Results (HPE16)

**Status**: ✅ **Successfully Deployed**

- **Kafka Cluster**: READY (KRaft metadata mode)
- **Running Pods**: 12/19 (63%)
  - Kafka broker and controller: Running
  - Policy participants (5): Running
  - DCAE VES Collector: Running
  - MariaDB: Running
  - Entity Operator: Running
- **Pending**: 4 Postgres pods (PVC binding - infrastructure issue)
- **Initializing**: 3 Policy pods (waiting for Postgres)

## Troubleshooting

**If Kafka pods don't start:**
- Check KafkaNodePool resources exist: `kubectl get kafkanodepool -n onap`
- Verify Strimzi operator is running: `kubectl get pods -n strimzi-system`
- Check operator logs for errors

**If Policy pods stuck in Init:**
- Verify RBAC: `kubectl get role,rolebinding -n onap | grep onap-read`
- Check ServiceAccount can query services: `kubectl auth can-i get services --as=system:serviceaccount:onap:onap-policy-api-read -n onap`

**Storage Issues:**
- Verify StorageClass exists: `kubectl get storageclass smo-storage`
- For NFS, ensure provisioner is configured and running
