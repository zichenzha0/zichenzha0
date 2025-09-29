#!/usr/bin/env python3
"""
GitHub Profile Statistics Updater
Automatically updates README.md with latest GitHub statistics and activity data.
"""

import os
import re
import requests
import json
from datetime import datetime, timedelta
from github import Github
import time

class GitHubStatsUpdater:
    def __init__(self):
        self.username = os.getenv('USERNAME', 'ZhaoJackson')
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None
        self.readme_path = 'README.md'
        
    def get_github_stats(self):
        """Fetch comprehensive GitHub statistics."""
        try:
            if not self.github:
                print("⚠️  GitHub token not available, using public API with rate limits")
                return self._get_public_stats()
            
            user = self.github.get_user(self.username)
            repos = list(user.get_repos())
            
            # Calculate various statistics
            total_repos = len(repos)
            total_stars = sum(repo.stargazers_count for repo in repos)
            total_forks = sum(repo.forks_count for repo in repos)
            
            # Language statistics
            languages = {}
            total_size = 0
            
            for repo in repos:
                if not repo.fork:  # Only count original repositories
                    repo_languages = repo.get_languages()
                    for lang, size in repo_languages.items():
                        languages[lang] = languages.get(lang, 0) + size
                        total_size += size
            
            # Calculate language percentages
            language_percentages = {}
            for lang, size in languages.items():
                percentage = (size / total_size * 100) if total_size > 0 else 0
                language_percentages[lang] = round(percentage, 1)
            
            # Recent activity
            events = list(user.get_events()[:10])
            recent_commits = len([e for e in events if e.type == 'PushEvent'])
            
            stats = {
                'total_repos': total_repos,
                'total_stars': total_stars,
                'total_forks': total_forks,
                'followers': user.followers,
                'following': user.following,
                'public_repos': user.public_repos,
                'languages': language_percentages,
                'recent_commits': recent_commits,
                'profile_views': self._get_profile_views(),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error fetching GitHub stats: {e}")
            return self._get_fallback_stats()
    
    def _get_public_stats(self):
        """Fetch basic stats using public GitHub API."""
        try:
            response = requests.get(f'https://api.github.com/users/{self.username}')
            if response.status_code == 200:
                user_data = response.json()
                return {
                    'total_repos': user_data.get('public_repos', 0),
                    'followers': user_data.get('followers', 0),
                    'following': user_data.get('following', 0),
                    'profile_views': self._get_profile_views(),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')
                }
        except Exception as e:
            print(f"❌ Error with public API: {e}")
        
        return self._get_fallback_stats()
    
    def _get_fallback_stats(self):
        """Fallback stats when API calls fail."""
        return {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'profile_views': self._get_profile_views()
        }
    
    def _get_profile_views(self):
        """Get profile view count from assets/streak.txt or return placeholder."""
        try:
            with open('assets/streak.txt', 'r') as f:
                views = f.read().strip()
                return int(views) if views.isdigit() else 0
        except:
            return 0
    
    def update_profile_views(self, new_views=None):
        """Update profile views counter."""
        if new_views is None:
            # Increment existing count
            current_views = self._get_profile_views()
            new_views = current_views + 1
        
        try:
            os.makedirs('assets', exist_ok=True)
            with open('assets/streak.txt', 'w') as f:
                f.write(str(new_views))
            print(f"✅ Updated profile views to {new_views}")
        except Exception as e:
            print(f"❌ Error updating profile views: {e}")
    
    def update_readme(self):
        """Update README.md with latest statistics."""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stats = self.get_github_stats()
            
            # Update the statistics section
            updated_content = self._update_stats_section(content, stats)
            
            # Add last updated timestamp
            updated_content = self._add_timestamp(updated_content, stats['last_updated'])
            
            # Write back to file
            with open(self.readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            print("✅ README.md updated successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error updating README: {e}")
            return False
    
    def _update_stats_section(self, content, stats):
        """Update the statistics section with dynamic data."""
        
        # Remove any existing dynamic statistics section if present
        pattern = r'### 📈 Dynamic Repository Statistics.*?(?=##|\Z)'
        if '### 📈 Dynamic Repository Statistics' in content:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
        
        # Also remove any Language Usage Analytics section
        pattern2 = r'### 💻 Language Usage Analytics.*?(?=##|\Z)'
        if '### 💻 Language Usage Analytics' in content:
            content = re.sub(pattern2, '', content, flags=re.DOTALL)
        
        # Clean up any extra whitespace
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        return content
    
    def _add_timestamp(self, content, timestamp):
        """Add or update the last updated timestamp."""
        timestamp_line = f"\n---\n*🤖 Last updated: {timestamp}*\n"
        
        # Remove existing timestamp if present
        content = re.sub(r'\n---\n\*🤖 Last updated:.*?\*\n', '', content)
        
        # Add timestamp at the end
        return content.rstrip() + timestamp_line
    
    def run_daily_update(self):
        """Main method to run daily updates."""
        print("🚀 Starting GitHub profile update...")
        
        # Update profile views
        self.update_profile_views()
        
        # Update README with latest stats
        success = self.update_readme()
        
        if success:
            print("✅ Daily update completed successfully!")
        else:
            print("❌ Daily update failed!")
        
        return success

def main():
    """Main execution function."""
    updater = GitHubStatsUpdater()
    updater.run_daily_update()

if __name__ == "__main__":
    main()
