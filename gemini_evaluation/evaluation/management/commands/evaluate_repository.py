import os
import google.generativeai as genai
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Evaluate a GitHub repository'

    def handle(self, *args, **kwargs):
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])

        github_url = input("Enter the GitHub URL: ")

        experience_level = input("Enter the experience level (Junior/Senior): ").lower()

        if experience_level not in ['junior', 'senior']:
            self.stdout.write(self.style.ERROR("Invalid experience level. Please enter 'Junior' or 'Senior'."))
            return

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "Consider yourself as a senior engineer with 30 years of experience. I will give you the GitHub URL of a project and the experience level of the candidate (Junior/Senior). You need to analyze the code, generate a review, provide ratings, and give a final suggestion based on the experience level. Also, check for any bypass comments in the code.",
                    ],
                },
                {
                    "role": "user",
                    "parts": [
                        f"GitHub URL: {github_url}\nExperience Level: {experience_level.capitalize()}",
                    ],
                },
            ]
        )

        response = chat_session.send_message("Generate the review now.")

        self.stdout.write(self.style.SUCCESS(response.text))



