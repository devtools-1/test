#!/usr/bin/env python3
import os
import requests
import subprocess
import sys
from getpass import getpass

def create_github_repo(org_name, repo_name, token):
    """Create a new repository in the specified GitHub organization"""
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    data = {
        'name': repo_name,
        'private': False,  # Change to True if we want a private repo
        'auto_init': False
    }
    
    url = f'https://api.github.com/orgs/{org_name}/repos'
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully!")
        return response.json()['clone_url']
    else:
        print(f"Failed to create repository. Status code: {response.status_code}")
        print(f"Error message: {response.json().get('message', '')}")
        sys.exit(1)

def push_to_remote(repo_url, token):
    try:
        # Initialize git repository if not already initialized
        if not os.path.exists('.git'):
            subprocess.run(['git', 'init'], check=True)
        
        # Configure git
        subprocess.run(['git', 'config', 'user.name', 'GitHub Actions'], check=True)
        subprocess.run(['git', 'config', 'user.email', 'actions@github.com'], check=True)
        
        # Add all files
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are any files to commit
        status = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if not status.stdout:
            print("No changes to commit. Make sure there are files in the directory.")
            sys.exit(1)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
        
        # Check if remote exists and update it, or add if it doesn't exist
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], check=True) # Remove old reference locally
        except subprocess.CalledProcessError:
            pass  # Origin doesn't exist, which is fine
        
        # Modify repo_url to include token
        repo_url = repo_url.replace('https://', f'https://oauth2:{token}@')
        subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True) # Add new reference locally
        
        # Push to remote
        subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
        
        print("Successfully pushed to remote repository!")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def main():
    # Get required information
    org_name = input("Enter GitHub organization name: ")
    repo_name = input("Enter repository name: ")
    token = getpass("Enter your GitHub personal access token: ")
    
    # Create repository and get its URL
    repo_url = create_github_repo(org_name, repo_name, token)
    
    # Push local directory to remote repository
    push_to_remote(repo_url, token)  # Pass token to push_to_remote

if __name__ == "__main__":
    main()
