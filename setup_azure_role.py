#!/usr/bin/env python3
"""
One-Click Azure Custom Role Setup Script.
Generates a ready-to-use Azure Custom Role JSON with least-privilege read-only access.
"""

import json
import argparse
import sys
from datetime import datetime
from typing import Dict, Any


def generate_custom_role(
    subscription_id: str,
    role_name: str = "FinOps Auditor",
    description: str = "Least-privilege read-only role for Azure FinOps Elite MCP Server",
) -> Dict[str, Any]:
    """
    Generate Azure Custom Role definition with least-privilege access.
    
    Args:
        subscription_id: Azure subscription ID
        role_name: Name for the custom role
        description: Role description
    
    Returns:
        Custom role definition dictionary
    """
    role_definition = {
        "Name": role_name,
        "Id": None,  # Azure will assign this
        "IsCustom": True,
        "Description": description,
        "Actions": [
            # Cost Management - Read access
            "Microsoft.Consumption/*/read",
            "Microsoft.CostManagement/*/read",
            
            # Azure Advisor - Read access
            "Microsoft.Advisor/*/read",
            
            # Resource Management - Read access
            "Microsoft.Resources/subscriptions/read",
            "Microsoft.Resources/subscriptions/resourceGroups/read",
            "Microsoft.Resources/resources/read",
            
            # Compute - Read access for VMs and disks
            "Microsoft.Compute/disks/read",
            "Microsoft.Compute/virtualMachines/read",
            "Microsoft.Compute/virtualMachineScaleSets/read",
            
            # Network - Read access for public IPs and networking
            "Microsoft.Network/publicIPAddresses/read",
            "Microsoft.Network/networkInterfaces/read",
            "Microsoft.Network/loadBalancers/read",
            
            # Storage - Read access
            "Microsoft.Storage/storageAccounts/read",
            "Microsoft.Storage/storageAccounts/blobServices/containers/read",
        ],
        "NotActions": [],  # No exclusions
        "DataActions": [],  # No data plane access
        "NotDataActions": [],
        "AssignableScopes": [
            f"/subscriptions/{subscription_id}"
        ],
    }
    
    return role_definition


def save_role_definition(role_definition: Dict[str, Any], output_file: str) -> None:
    """
    Save role definition to JSON file.
    
    Args:
        role_definition: Role definition dictionary
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        json.dump(role_definition, f, indent=4)
    
    print(f"✅ Custom role definition saved to: {output_file}")


def generate_deployment_script(subscription_id: str, role_file: str) -> str:
    """
    Generate Azure CLI deployment script.
    
    Args:
        subscription_id: Azure subscription ID
        role_file: Path to role definition JSON file
    
    Returns:
        Deployment script content
    """
    script = f"""#!/bin/bash
# Azure FinOps Elite - Custom Role Deployment Script
# Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

set -e  # Exit on error

echo "🚀 Deploying Azure FinOps Elite Custom Role..."

# Set subscription context
echo "Setting subscription context..."
az account set --subscription {subscription_id}

# Create custom role
echo "Creating custom role..."
az role definition create --role-definition {role_file}

echo "✅ Custom role created successfully!"
echo ""
echo "Next steps:"
echo "1. Create Service Principal:"
echo "   az ad sp create-for-rbac --name azure-finops-elite --skip-assignment"
echo ""
echo "2. Assign the custom role to the Service Principal:"
echo "   az role assignment create --assignee <service-principal-id> --role 'FinOps Auditor' --scope /subscriptions/{subscription_id}"
echo ""
echo "3. Generate and upload certificate (see security_guide.md)"
"""
    
    return script


def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Generate Azure Custom Role for FinOps Elite MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate role for a single subscription
  python setup_azure_role.py --subscription-id xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
  
  # Generate role with custom name
  python setup_azure_role.py --subscription-id <sub-id> --role-name "My FinOps Role"
  
  # Generate role and deployment script
  python setup_azure_role.py --subscription-id <sub-id> --with-script
        """
    )
    
    parser.add_argument(
        '--subscription-id',
        required=True,
        help='Azure subscription ID'
    )
    
    parser.add_argument(
        '--role-name',
        default='FinOps Auditor',
        help='Custom role name (default: FinOps Auditor)'
    )
    
    parser.add_argument(
        '--description',
        default='Least-privilege read-only role for Azure FinOps Elite MCP Server',
        help='Role description'
    )
    
    parser.add_argument(
        '--output-file',
        default='finops_custom_role.json',
        help='Output file for role definition (default: finops_custom_role.json)'
    )
    
    parser.add_argument(
        '--with-script',
        action='store_true',
        help='Generate deployment script'
    )
    
    args = parser.parse_args()
    
    print("🔧 Azure FinOps Elite - One-Click Role Setup")
    print("=" * 60)
    print(f"Subscription ID: {args.subscription_id}")
    print(f"Role Name: {args.role_name}")
    print(f"Output File: {args.output_file}")
    print("=" * 60)
    print()
    
    # Generate custom role definition
    print("📝 Generating custom role definition...")
    role_definition = generate_custom_role(
        subscription_id=args.subscription_id,
        role_name=args.role_name,
        description=args.description,
    )
    
    # Save role definition
    save_role_definition(role_definition, args.output_file)
    
    # Generate deployment script if requested
    if args.with_script:
        script_file = args.output_file.replace('.json', '_deploy.sh')
        script_content = generate_deployment_script(args.subscription_id, args.output_file)
        
        with open(script_file, 'w') as f:
            f.write(script_content)
        
        # Make script executable on Unix systems
        try:
            import os
            os.chmod(script_file, 0o755)
        except Exception:
            pass
        
        print(f"✅ Deployment script saved to: {script_file}")
    
    print()
    print("📋 Role Permissions Summary:")
    print("  ✓ Cost Management (read-only)")
    print("  ✓ Azure Advisor (read-only)")
    print("  ✓ Resource metadata (read-only)")
    print("  ✓ Compute resources (read-only)")
    print("  ✓ Network resources (read-only)")
    print("  ✓ Storage accounts (read-only)")
    print()
    print("🔐 Security Features:")
    print("  ✓ Least-privilege access (read-only)")
    print("  ✓ No write permissions")
    print("  ✓ No data plane access")
    print("  ✓ Subscription-scoped")
    print()
    print("🚀 Next Steps:")
    print("  1. Review the generated role definition")
    
    if args.with_script:
        print(f"  2. Run the deployment script: ./{script_file.split('/')[-1]}")
    else:
        print(f"  2. Deploy the role: az role definition create --role-definition {args.output_file}")
    
    print("  3. Create Service Principal with certificate (see security_guide.md)")
    print("  4. Assign the role to the Service Principal")
    print("  5. Configure .env file with credentials")
    print()
    print("✅ Setup complete! For detailed instructions, see security_guide.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)
