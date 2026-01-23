# 1Algooverride: The Working Configuration
This folder contains the **exact** artifacts used to successfully deploy ONAP on the HPE15 cluster, bypassing the issues found in the standard OOM repository.

## 1. How to Use This Folder
If you need to redeploy or restore the environment, apply these files in the following order:

1.  **Apply RBAC Fixes (Pre-requisite)**
    *   `kubectl apply -f onap-read-role.yaml` (Creates the global `onap-read` role)
    *   `kubectl apply -f onap-read-bindings.yaml` (Binds Policy SAs to this role)
    *   `kubectl apply -f sdnc-serviceaccounts.yaml` (Pre-creates SDNC ServiceAccounts to prevent deadlocks)

2.  **Deploy SDNC (Manual Fix)**
    *   `kubectl apply -f sdnc_manual_fix.yaml` (Deploys SDNC with "nil pointer" fix and your values)

3.  **Values & Scripts**
    *   `user_desired_values.yaml`: The source of truth for your configuration.
    *   `apply_values_override.py`: The script we used to generate overrides (for reference).

4.  **Full Stack Snapshots (From HPE15)**
    *   `policy_full.yaml`: Complete snapshot of running Policy stack (54 resources).
    *   `dcae_full.yaml`: Snapshot of DCAE VES Collector (7 resources).
    *   `strimzi_full.yaml`: Snapshot of Kafka Cluster and Strimzi Operator (27 resources).
    *   `postgres_full.yaml`: Snapshot of shared databases (24 resources).
    *   *These files guarantee that HPE16 will match the working state of HPE15 exactly.*

---

## 2. Comparison: 1Algooverride vs. OOM

| Feature | OOM (Standard Repo) | 1Algooverride (This Folder) | Why it Changed? |
| :--- | :--- | :--- | :--- |
| **Deployment Method** | Helm / ArgoCD (GitOps) | **Local Manifest Injection** | Git permissions on HPE15 were broken; remote repo sync failed. |
| **Values Configuration** | Default `values.yaml` (All Enabled) | **User Custom (`user_desired_values.yaml`)** | You requested specific components (Policy/SDNC/VES only) and disabled others (CDS/Portal/Ingress). |
| **SDNC Chart** | Contains `nil pointer` bug in templates | **Patched Manifest (`sdnc_manual_fix.yaml`)** | The standard chart failed to render `global.ingress.provider`. We fixed it manually. |
| **Policy Permissions** | Restrictive (RBAC errors) | **Expanded Permissions (`onap-read-role`)** | Standard OOM roles were insufficient for the HPE15 K8s version, creating `Forbidden` errors. |
| **SDNC Init** | Circular Dependency (Job hangs) | **Pre-created ServiceAccounts** | Standard process deadlocked waiting for ServiceAccount creation. We pre-created them to unblock. |

### Summary of Changes
- **OOM** is the "Factory Default". It assumes a perfect environment and full permissions.
- **1Algooverride** is the "Field Modification". It strips down the defaults to your requirements, patches bugs found on the specific cluster (HPE15), and bypasses the broken CI/CD link.
