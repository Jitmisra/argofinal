import yaml
import subprocess
import json
import os
import time

# User's provided configuration (Absolute path)
USER_VALUES_FILE = "/home/agnik/.gemini/antigravity/brain/26d9bdd7-9c3c-47e8-b61e-34d768715a13/user_desired_values.yaml"

# Load the user's values content
with open(USER_VALUES_FILE, 'r') as f:
    user_values_content = f.read()

values_yaml = yaml.safe_load(user_values_content)
global_values = values_yaml.get('global', {})

# Map of Component Key in User YAML -> ArgoCD Application Name
COMPONENT_MAP = {
    'sdnc': 'onap-sdnc',
    'policy': 'onap-policy',
    'dcaegen2-services': 'onap-dcaegen2-services',
    'mariadb-galera': 'onap-mariadb-galera',
    'postgres': 'onap-postgres',
    'strimzi': 'onap-strimzi',
    'cps': 'onap-cps',
    'a1policymanagement': 'onap-a1policymanagement'
}

def get_enabled_status(component_key):
    comp_config = values_yaml.get(component_key, {})
    if isinstance(comp_config, dict):
        return comp_config.get('enabled', True)
    return True

to_patch = []
to_delete = []

for key, app_name in COMPONENT_MAP.items():
    if get_enabled_status(key):
        to_patch.append((key, app_name))
    else:
        to_delete.append(app_name)

print("\nApps to Patch (Inject Scoped Values):", [x[1] for x in to_patch])
print("Apps to Delete:", to_delete)

# 1. Delete Disabled Apps
for app in to_delete:
    print(f"Deleting app: {app}")
    cmd = f"kubectl delete application {app} -n argocd --ignore-not-found"
    subprocess.run(f"sshpass -p '1234' ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu 'export KUBECONFIG=~/.kube/config; {cmd}'", shell=True)

# 2. Patch Enabled Apps
for key, app in to_patch:
    print(f"Checking app: {app}")
    # Wait loop for app existence?
    # Better: Try once, log if missing. User can re-run.
    
    # Check if app exists
    check_cmd = f"kubectl get application {app} -n argocd --ignore-not-found"
    full_check_cmd = f"sshpass -p '1234' ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu 'export KUBECONFIG=~/.kube/config; {check_cmd}'"
    
    try:
        exists = subprocess.check_output(full_check_cmd, shell=True).decode().strip()
        if not exists:
            print(f"App {app} not found. Skipping (it might be creating).")
            continue
    except:
        continue

    print(f"Patching app: {app} with values from key '{key}'")
    
    # Construct scoped values
    scoped_values = {'global': global_values}
    comp_values = values_yaml.get(key, {})
    if isinstance(comp_values, dict):
        scoped_values.update(comp_values)
    
    scoped_values_str = yaml.dump(scoped_values)
    
    fetch_cmd = f"kubectl get application {app} -n argocd -o json"
    full_cmd = f"sshpass -p '1234' ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu 'export KUBECONFIG=~/.kube/config; {fetch_cmd}'"
    
    try:
        result = subprocess.check_output(full_cmd, shell=True)
        app_json = json.loads(result)
        
        sources = app_json['spec']['sources']
        helm_source_index = -1
        for idx, src in enumerate(sources):
            if 'chart' in src:
                helm_source_index = idx
                break
        
        if helm_source_index == -1:
            print(f"Could not find Helm source for {app}. Skipping.")
            continue
            
        if 'helm' not in sources[helm_source_index]:
             sources[helm_source_index]['helm'] = {}
        
        # INJECT
        sources[helm_source_index]['helm']['values'] = scoped_values_str
        
        # Apply
        modified_json_str = json.dumps(app_json)
        with open('patch_v2.json', 'w') as pf:
            pf.write(modified_json_str)
            
        apply_cmd = f"cat patch_v2.json | sshpass -p '1234' ssh -o StrictHostKeyChecking=no agnikmisra@hpe15.anuket.iol.unh.edu 'export KUBECONFIG=~/.kube/config; kubectl apply -f -'"
        subprocess.run(apply_cmd, shell=True)
        print(f"Successfully patched {app}")
        
    except Exception as e:
        print(f"Error processing {app}: {e}")
