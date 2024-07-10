import os
import requests
import google.generativeai as genai
from django.core.management.base import BaseCommand
from evaluation.management.commands.prompts import CHATS

def get_file_content(file_url, headers):
    file_response = requests.get(file_url, headers=headers)
    if file_response.status_code == 200:
        return file_response.text
    return ""

class Command(BaseCommand):
    help = 'Evaluate a GitHub repository'

    def handle(self, *args, **kwargs):

        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        github_url = input("Enter the GitHub URL: ")
        experience_level = input("Enter the experience level (Junior/Senior): ").lower()

        if experience_level not in ['junior', 'senior']:
            self.stdout.write(self.style.ERROR("Invalid experience level. Please enter 'Junior' or 'Senior'."))
            return

        headers = {'Authorization': f'token {os.environ["GITHUB_TOKEN"]}'}

        if '/pull/' in github_url:
            # Pull request handling
            try:
                parts = github_url.split('/')
                owner = parts[-4]
                repo = parts[-3]
                pr_number = int(parts[-1])
            except (ValueError, IndexError):
                self.stdout.write(self.style.ERROR("Invalid GitHub URL format for pull request."))
                return

            api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch the pull request. Status code: {response.status_code}, Response: {response.text}"))
                return

            pr_data = response.json()
            pr_description = pr_data['body'] or ""


            comments_url = pr_data['comments_url']
            comments_response = requests.get(comments_url, headers=headers)
            pr_comments = "\n".join(comment['body'] for comment in comments_response.json()) if comments_response.status_code == 200 else ""

     
            files_url = pr_data['url'] + "/files"
            files_response = requests.get(files_url, headers=headers)
            file_changes = "\n".join(f"File: {file['filename']}\nChanges: {file['patch']}" for file in files_response.json() if 'patch' in file) if files_response.status_code == 200 else ""

            content_for_analysis = f"PR Description:\n{pr_description}\n\nPR Comments:\n{pr_comments}\n\nChanged Files:\n{file_changes}"

        else:
      
            try:
                parts = github_url.split('/')
                owner = parts[-2]
                repo = parts[-1]
            except (ValueError, IndexError):
                self.stdout.write(self.style.ERROR("Invalid GitHub URL format for repository."))
                return

            contents_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            contents_response = requests.get(contents_url, headers=headers)
            if contents_response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"Failed to fetch repository contents. Status code: {contents_response.status_code}, Response: {contents_response.text}"))
                return

            contents = contents_response.json()
            file_contents = ""
            bug_report = ""
            readme_content = ""

            for item in contents:
                if item['type'] == 'file':
                    file_content = get_file_content(item['download_url'], headers)
                    if item['name'].lower() == 'readme.md':
                        readme_content = file_content
                    elif item['name'].endswith(('.py', '.java')):
                        file_contents += f"File: {item['name']}\n{file_content}\n\n"
                        
                       
                        lines = file_content.split('\n')
                        for i, line in enumerate(lines):
                            if 'bug' in line.lower() or 'issue' in line.lower():
                                bug_report += f"File: {item['name']}, Line {i+1}: {line.strip()}\n"
            
            
            if readme_content:
                content_for_analysis = f"README File Content:\n{readme_content}\n\nBug Report:\n{bug_report}\n\nRepository Files:\n{file_contents}"
            else:
                content_for_analysis = f"Bug Report:\n{bug_report}\n\nRepository Files:\n{file_contents}"

        generation_config = {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(
        history= CHATS
)


        response = chat_session.send_message(f"GitHub URL: {github_url}\nExperience Level: {experience_level.capitalize()}\nCandidate's Submission:\n{content_for_analysis}")
        self.stdout.write(self.style.SUCCESS(response.text))

        while True:
            question = input("ANY QUESTIONS REGARDING MY FEEDBACK OR EVALUATION? (Type 'EXIT' to end the session): ").strip()
            if question.lower() == 'exit':
                self.stdout.write(self.style.SUCCESS("Session ended."))
                break
            else:
                follow_up_response = chat_session.send_message(question)
                self.stdout.write(self.style.SUCCESS(follow_up_response.text))


# the next part is to optimize the prompts to generate more accurate results